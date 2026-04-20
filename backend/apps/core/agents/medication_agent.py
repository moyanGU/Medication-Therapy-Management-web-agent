import json
import re
import logging
from apps.core.agents.base import BaseAgent

logger = logging.getLogger("mtm_helper.agents.medication")

class MedicationAgent(BaseAgent):
    """
    负责用药指导与问答的子代理
    """

    def get_system_prompt(self) -> str:
        return (
            "你是 MTM-用药助手的用药指导助手。\n"
            "你只能回答药物信息与用药指导相关内容，不做疾病诊断、不判断病情严重程度、不替代医生。\n"
            "如果用户的问题包含疾病诊断/检查/治疗方案请求，请拒绝并引导其改问用药问题。\n"
            "不要仅用一句话拒答（例如‘无法提供/无法直接提供’）；当关键信息不足以给出具体剂量时，请给出通用用药原则并提出澄清问题。\n"
            "回答时请尽量结构化：用法用量（一般信息）、禁忌/慎用人群、相互作用、常见不良反应、漏服/过量处理、储存方式、何时就医（仅基于用药风险）。\n"
            "避免给出超出说明书或权威指南的精确个体化剂量；需要关键信息时，先提出澄清问题。"
        )

    def _is_probably_medication_question(self, question: str, medicine_context: dict | None) -> bool:
        q = (question or "").strip()
        if not q:
            return False
        if isinstance(medicine_context, dict) and medicine_context:
            return True

        q_compact = re.sub(r"\s+", "", q).lower()
        keyword_hits = [
            "药", "用药", "服用", "剂量", "用法", "用量", "禁忌", "副作用", "相互作用",
            "饭前", "饭后", "一次", "每日", "多久", "aspirin", "amoxicillin", "ibuprofen",
            "paracetamol", "acetaminophen", "阿司匹林", "阿莫西林", "布洛芬", "头孢", "对乙酰氨基酚",
        ]
        return any(k in q_compact for k in keyword_hits)

    def check_intent(self, question: str, medicine_context: dict | None) -> dict:
        """
        判断是否属于用药咨询范围
        """
        classifier_messages = [
            {
                "role": "system",
                "content": (
                    "You are a strict content classifier for a medication guidance app. "
                    "Decide whether the user request is ONLY about medications and medication use guidance. "
                    "Allowed: drug names, dosage, frequency, timing, interactions, contraindications, side effects, "
                    "missed dose, storage, pregnancy/children/elderly precautions related to a medication. "
                    "Disallowed: diagnosis, differential diagnosis, lab/imaging, treatment plan for diseases, "
                    "medical record interpretation, emergency triage, prognosis. "
                    "Answer directly. Do not include analysis. "
                    "Return ONLY a JSON object with keys: allowed (boolean), reason (string). "
                    "No markdown. No code fences. "
                    'Example allowed: {"allowed": true, "reason": ""}. '
                    'Example disallowed: {"allowed": false, "reason": "short reason"}.'
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "question": question,
                        "medicine_context": medicine_context,
                    },
                    ensure_ascii=False,
                ),
            },
        ]
        
        self._check_config()
        from apps.core.views import _openai_chat_completion, _extract_json_object
        
        try:
            try:
                cls_text = _openai_chat_completion(
                    base_url=self.base_url,
                    api_key=self.api_key,
                    model=self.model,
                    messages=classifier_messages,
                    temperature=0.0,
                    max_tokens=256,
                    timeout_seconds=self.timeout_seconds,
                    response_format={"type": "json_object"},
                )
            except Exception as e:
                logger.info(f"[AI] classifier response_format fallback: {e}")
                cls_text = _openai_chat_completion(
                    base_url=self.base_url,
                    api_key=self.api_key,
                    model=self.model,
                    messages=classifier_messages,
                    temperature=0.0,
                    max_tokens=256,
                    timeout_seconds=self.timeout_seconds,
                )

            cls_obj = _extract_json_object(cls_text) or {}
            allowed = bool(cls_obj.get("allowed"))
            reason = str(cls_obj.get("reason", "")).strip() or ""
        except Exception as e:
            logger.warning(f"[AI] classifier failed: {e}")
            allowed = self._is_probably_medication_question(question, medicine_context)
            reason = "" if allowed else "分类失败，且问题不符合用药咨询范围"

        if not allowed and self._is_probably_medication_question(question, medicine_context):
            allowed = True
            reason = ""
            
        return {"allowed": allowed, "reason": reason}
