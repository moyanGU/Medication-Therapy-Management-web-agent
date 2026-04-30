import json
from apps.core.agents.base import BaseAgent

class SessionMemoryAgent(BaseAgent):
    """
    负责提取和总结 MTM 服务单对话记忆的子代理
    """

    def get_system_prompt(self) -> str:
        return (
            "你是一个严谨的临床用药助理，请将以下对话总结为“会话记忆”，用于后续连续对话。\n"
            "要求：\n"
            "1) 只保留对后续用药管理/MTM服务有帮助的事实与结论；\n"
            "2) 包括：用户背景与目标、关键药品/剂量/频次、已确认的计划、未解决问题、下一步建议；\n"
            "3) 不要编造；不包含隐私敏感信息（如身份证、住址）；\n"
            "4) 用中文输出，控制在 400 字以内。\n"
        )

    def summarize(self, messages: list) -> str:
        """
        接收历史对话消息，返回摘要字符串
        """
        transcript_lines = []
        for item in messages[-40:]:
            role = "用户" if item.get("role") == "user" else "助手"
            transcript_lines.append(f"{role}：{item.get('content')}")
        transcript = "\n".join(transcript_lines)
        
        self._check_config()
        from apps.core.views import _openai_chat_completion, _normalize_llm_answer
        
        text = _openai_chat_completion(
            base_url=self.base_url,
            api_key=self.api_key,
            model=self.model,
            messages=[
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": transcript}
            ],
            temperature=0.1,
            max_tokens=512,
            timeout_seconds=self.timeout_seconds,
        )
        
        return _normalize_llm_answer(str(text or "")).strip()
