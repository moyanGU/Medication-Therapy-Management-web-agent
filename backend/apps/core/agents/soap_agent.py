import json
from apps.core.agents.base import BaseAgent
from apps.core.views import _extract_json_object

class SoapAgent(BaseAgent):
    """
    专门负责 MTM 服务单 SOAP 药历生成的子代理
    """

    def get_system_prompt(self) -> str:
        return (
            "你是一个专业的临床药师（SOAP 生成子代理）。请根据提供的患者问诊信息与病史，生成标准的 SOAP 药历结构草稿。\n"
            "S (Subjective): 患者主诉、病史、药物过敏史、生活习惯等。\n"
            "O (Objective): 整理后的客观用药情况。\n"
            "A (Assessment): 药物治疗问题评估分析。\n"
            "P (Plan): 建议的干预方案。\n"
            "请严格返回 JSON 格式，必须包含 keys: subjective, objective, assessment, plan。"
        )

    def generate(self, context_data: dict) -> dict:
        """
        接收 MTM 服务单上下文，返回 SOAP 字典
        """
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": json.dumps(context_data, ensure_ascii=False)},
        ]
        
        self._check_config()
        from apps.core.views import _openai_chat_completion
        
        text = _openai_chat_completion(
            base_url=self.base_url,
            api_key=self.api_key,
            model=self.model,
            messages=messages,
            temperature=0.1,
            max_tokens=2048,
            timeout_seconds=self.timeout_seconds,
            response_format={"type": "json_object"}
        )
        
        obj = _extract_json_object(text)
        if not obj:
            raise ValueError("AI 未返回合法的 SOAP 数据")
        return obj
