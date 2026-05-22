import json
import logging
import re

from django.http import StreamingHttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .ai_llm import _looks_unhelpful_answer, _normalize_llm_answer
from .ai_runtime import classify_ai_exception, get_ai_runtime_config
from .utils import error_response, success_response

logger = logging.getLogger("mtm_helper")


def _parse_medication_guidance_request(request):
    data = request.data or {}
    question = str(data.get("question", "")).strip()
    medicine_id = data.get("medicine_id")
    stream_requested = str(data.get("stream", "")).lower() == "true"
    return question, medicine_id, stream_requested


def _validate_question(question: str):
    if not question:
        return error_response("请提供问题", "VALIDATION_ERROR", 400)
    if len(question) > 2000:
        return error_response("问题过长，请精简后再试", "VALIDATION_ERROR", 400)
    return None


def _load_medicine_context(medicine_id, user):
    if medicine_id is None or str(medicine_id).strip() == "":
        return None
    try:
        from apps.medicines.models import Medicine

        med = Medicine.objects.filter(id=medicine_id, user=user).first()
        if not med:
            return None
        return {
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
        return None


def _build_medication_agent(user_id, runtime_config):
    from apps.core.agents.medication_agent import MedicationAgent

    agent = MedicationAgent(user_id=user_id)
    agent.base_url = runtime_config.base_url
    agent.api_key = runtime_config.api_key
    agent.model = runtime_config.model
    agent.timeout_seconds = runtime_config.timeout_seconds
    return agent


def _check_medication_intent(question: str, medicine_context: dict | None, user_id, runtime_config):
    agent = _build_medication_agent(user_id, runtime_config)
    try:
        intent = agent.check_intent(question, medicine_context)
        return bool(intent.get("allowed")), str(intent.get("reason") or ""), None
    except Exception as e:
        logger.warning(f"[AI] classifier failed: {e}")
        allowed = agent._is_probably_medication_question(question, medicine_context)
        if allowed:
            return True, "", e
        return False, "当前仅支持药物信息与用药指导咨询", e


def _blocked_payload(reason: str):
    return {
        "blocked": True,
        "reason": reason or "当前仅支持药物信息与用药指导咨询",
        "answer": "当前仅支持药物信息与用药指导咨询，请改问具体药品的用法、用量、注意事项、相互作用或不良反应。",
    }


def _ndjson_single(payload: dict):
    def _gen():
        yield json.dumps(payload, ensure_ascii=False) + "\n"

    return StreamingHttpResponse(_gen(), content_type="application/x-ndjson")


def _run_medication_agent_stream(agent, question: str, medicine_context: dict | None):
    try:
        for chunk in agent.run_stream(question, medicine_context):
            yield chunk
    except Exception as e:
        logger.error(f"[AI] stream generation failed: {e}")
        fallback_answer = _fallback_medication_guidance_answer(question, medicine_context)
        yield (
            json.dumps(
                {
                    "error": classify_ai_exception(e),
                    "error_code": classify_ai_exception(e),
                    "fallback": fallback_answer,
                    "fallback_used": True,
                },
                ensure_ascii=False,
            )
            + "\n"
        )


def _run_medication_agent(agent, question: str, medicine_context: dict | None):
    try:
        answer = agent.run(question, medicine_context)
        return answer, False, None
    except Exception as e:
        logger.error(f"[AI] generation failed: {e}")
        answer = _fallback_medication_guidance_answer(question, medicine_context)
        return answer, True, "模型服务暂不可用，已返回通用用药建议"


def _fallback_medication_guidance_answer(question: str, medicine_context: dict | None) -> str:
    drug_name = None
    if isinstance(medicine_context, dict):
        name = medicine_context.get("name")
        if isinstance(name, str) and name.strip():
            drug_name = name.strip()

    q = (question or "").strip()
    q_compact = re.sub(r"\s+", "", q)
    is_aspirin = ("阿司匹林" in q_compact) or ("aspirin" in q.lower())
    is_ibuprofen = ("布洛芬" in q_compact) or ("ibuprofen" in q.lower())

    if is_aspirin:
        return (
            "阿司匹林的通用用药建议如下：\n"
            "1. 常见口服做法是餐后或随餐服用，并用足量温水送服，以减少胃部刺激。\n"
            "2. 不同适应证和规格差异很大，例如抗血小板与止痛退热的剂量并不相同，请先确认规格和用途。\n"
            "3. 如合并胃溃疡、消化道出血、阿司匹林过敏、哮喘、抗凝药同用或妊娠晚期，应先咨询医生。\n"
            "4. 若出现黑便、呕血、明显胃痛、呼吸困难或皮疹肿胀，应及时就医。\n\n"
            "如果你告诉我药品规格、用途，以及使用者年龄/既往病史，我可以继续按说明书要点帮你整理。"
        )

    if is_ibuprofen:
        return (
            "我可以给你布洛芬的通用用药指导，但需要先确认年龄、体重、药品规格和用途。\n"
            "一般建议饭后服用，避免与其他 NSAIDs 同服；如有胃病、肾功能问题、妊娠晚期或过敏史，应先咨询医生。"
        )

    drug_tip = f"（{drug_name}）" if drug_name else ""
    return (
        f"我可以提供药物{drug_tip}的通用用药指导，但还需要你补充药品名称、规格、用途、年龄体重，以及是否合并用药或特殊病史。"
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def medication_guidance(request):
    question, medicine_id, stream_requested = _parse_medication_guidance_request(request)

    error = _validate_question(question)
    if error is not None:
        return error

    runtime_config, error = get_ai_runtime_config()
    if error is not None:
        return error

    medicine_context = _load_medicine_context(medicine_id, request.user)
    allowed, reason, _ = _check_medication_intent(
        question,
        medicine_context,
        getattr(request.user, "id", None),
        runtime_config,
    )
    if not allowed:
        payload = _blocked_payload(reason)
        if stream_requested:
            return _ndjson_single(payload)
        return success_response(payload, "已拦截非用药咨询")

    agent = _build_medication_agent(getattr(request.user, "id", None), runtime_config)
    if stream_requested:
        return StreamingHttpResponse(
            _run_medication_agent_stream(agent, question, medicine_context),
            content_type="application/x-ndjson",
        )

    answer, fallback_used, message = _run_medication_agent(
        agent, question, medicine_context
    )
    if fallback_used:
        return success_response(
            {"blocked": False, "answer": answer, "fallback_used": True},
            message or "模型服务暂不可用，已返回通用用药建议",
        )

    answer = _normalize_llm_answer(answer)
    if _looks_unhelpful_answer(answer):
        answer = _fallback_medication_guidance_answer(question, medicine_context)
        fallback_used = True

    return success_response(
        {"blocked": False, "answer": answer, "fallback_used": fallback_used},
        "生成成功",
    )
