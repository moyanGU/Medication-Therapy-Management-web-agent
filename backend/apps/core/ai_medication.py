import json
import logging
import re

from django.conf import settings
from django.http import StreamingHttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .ai_llm import _looks_unhelpful_answer, _normalize_llm_answer
from .utils import error_response, success_response

logger = logging.getLogger("mtm_helper")


def _fallback_medication_guidance_answer(question: str, medicine_context: dict | None) -> str:
    drug_name = None
    if isinstance(medicine_context, dict):
        name = medicine_context.get("name")
        if isinstance(name, str) and name.strip():
            drug_name = name.strip()

    q = (question or "").strip()
    q_compact = re.sub(r"\s+", "", q)
    is_ibuprofen = ("布洛芬" in q_compact) or ("ibuprofen" in q.lower())

    if is_ibuprofen:
        return (
            "我可以给你布洛芬（Ibuprofen）的通用用药指导，但需要先确认几个关键信息，避免给出不合适的剂量：\n"
            "1）使用者年龄/体重（儿童剂量按体重计算）\n"
            "2）药品规格与剂型（如 0.2g 片、缓释、混悬液等）\n"
            "3）用途（退烧/止痛）与是否合并胃病、肾病、哮喘、正在备孕/怀孕等\n\n"
            "一般用法要点（请以说明书为准）：\n"
            "- 成人常见 OTC 剂量：200–400mg/次，间隔约 6–8 小时按需；24 小时内不建议超过 1200mg（处方可更高需医生指导）。\n"
            "- 尽量随餐或餐后服用，减少胃部刺激；避免与其他 NSAIDs（如双氯芬酸、萘普生）同服。\n"
            "- 慎用/避免：消化道溃疡或出血史、严重肾功能不全、对阿司匹林/NSAIDs 过敏、妊娠晚期等。\n"
            "- 何时就医：黑便/呕血、严重腹痛、呼吸困难/皮疹肿胀、持续高热或疼痛不缓解。\n\n"
            "你把“规格（比如 0.2g/片）+ 年龄/体重 + 主要症状（退烧/止痛）”告诉我，我再按更贴近说明书的方式给出服用建议。"
        )

    drug_tip = f"（{drug_name}）" if drug_name else ""
    return (
        f"我可以提供药物{drug_tip}的用药指导，但需要你补充信息后才能更准确：\n"
        "1）药品名称/规格/剂型（如 0.25g 胶囊、缓释片、口服液等）\n"
        "2）使用者年龄/体重，是否怀孕/哺乳\n"
        "3）用途（退烧/止痛/抗过敏等）与既往病史（胃病、肝肾功能、哮喘、出血倾向）\n"
        "4）正在使用的其他药物（尤其抗凝药、其他止痛药、激素、降压药等）\n\n"
        "先给通用安全要点：尽量按说明书剂量与间隔服用，避免重复成分/同类药叠加；若出现过敏、严重胃痛/黑便、头晕乏力明显或症状持续不缓解，请及时就医。"
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def medication_guidance(request):
    question = str((request.data or {}).get("question", "")).strip()
    medicine_id = (request.data or {}).get("medicine_id")
    stream_requested = str(request.data.get("stream", "")).lower() == "true"

    if not question:
        return error_response("请提供问题", "VALIDATION_ERROR", 400)
    if len(question) > 2000:
        return error_response("问题过长，请精简后再试", "VALIDATION_ERROR", 400)

    if not getattr(settings, "BAICHUAN_M3_ENABLED", False):
        return error_response("AI 服务未启用", "AI_DISABLED", 503)

    base_url = getattr(settings, "BAICHUAN_M3_API_BASE_URL", "")
    model = getattr(settings, "BAICHUAN_M3_MODEL", "")
    if not base_url or not model:
        return error_response("AI 服务配置缺失", "AI_CONFIG_MISSING", 503)

    medicine_context = None
    if medicine_id is not None and str(medicine_id).strip() != "":
        try:
            from apps.medicines.models import Medicine

            med = Medicine.objects.filter(id=medicine_id, user=request.user).first()
            if med:
                medicine_context = {
                    "id": med.id,
                    "name": med.name,
                    "specification": med.specification,
                    "manufacturer": med.manufacturer,
                    "medicine_type": med.medicine_type,
                    "is_prescription": bool(med.is_prescription),
                    "storage_conditions": med.storage_conditions,
                    "description": med.description,
                }
        except Exception as e:
            logger.warning(f"[AI] medicine_context load failed: {e}")

    try:
        from apps.core.agents.medication_agent import MedicationAgent

        agent = MedicationAgent(user_id=getattr(request.user, "id", None))
        intent = agent.check_intent(question, medicine_context)
        allowed = intent["allowed"]
        reason = intent["reason"]
    except Exception as e:
        logger.warning(f"[AI] classifier failed: {e}")
        allowed = True
        reason = ""

    if not allowed:
        resp_data = {
            "blocked": True,
            "reason": reason
            or "当前仅支持药物信息与用药指导咨询（不支持诊断/检查/疾病治疗方案）。",
            "answer": "当前仅支持药物信息与用药指导咨询。请将问题改为具体药物的用法用量、注意事项、相互作用、不良反应等。",
        }
        if stream_requested:
            def _gen():
                yield json.dumps(resp_data, ensure_ascii=False) + "\n"

            return StreamingHttpResponse(_gen(), content_type="application/x-ndjson")
        return success_response(resp_data, "已拦截非用药咨询")

    fallback_used = False

    try:
        from apps.core.agents.medication_agent import MedicationAgent

        agent = MedicationAgent(user_id=getattr(request.user, "id", None))

        if stream_requested:
            def _stream_generator():
                try:
                    for chunk in agent.run_stream(question, medicine_context):
                        yield chunk
                except Exception as e:
                    logger.error(f"[AI] stream generation failed: {e}")
                    fallback_answer = _fallback_medication_guidance_answer(question, medicine_context)
                    yield (
                        json.dumps(
                            {"error": "generation_failed", "fallback": fallback_answer},
                            ensure_ascii=False,
                        )
                        + "\n"
                    )

            return StreamingHttpResponse(_stream_generator(), content_type="application/x-ndjson")

        answer = agent.run(question, medicine_context)
    except Exception as e:
        logger.error(f"[AI] generation failed: {e}")
        answer = _fallback_medication_guidance_answer(question, medicine_context)
        fallback_used = True
        return success_response(
            {"blocked": False, "answer": answer, "fallback_used": fallback_used},
            "模型服务暂不可用，已返回通用用药建议",
        )

    answer = _normalize_llm_answer(answer)
    if _looks_unhelpful_answer(answer):
        answer = _fallback_medication_guidance_answer(question, medicine_context)
        fallback_used = True

    return success_response(
        {"blocked": False, "answer": answer, "fallback_used": fallback_used}, "生成成功"
    )

