import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict

from django.conf import settings

logger = logging.getLogger("mtm_helper.agents")

class BaseAgent(ABC):
    """
    后端领域专家子代理基类 (Sub-Agent Base)
    """

    def __init__(self, user_id: int, session_id: str = None):
        self.user_id = user_id
        self.session_id = session_id
        self.base_url = getattr(settings, "BAICHUAN_M3_API_BASE_URL", "")
        self.api_key = getattr(settings, "BAICHUAN_M3_API_KEY", "")
        self.model = getattr(settings, "BAICHUAN_M3_MODEL", "")
        self.timeout_seconds = float(getattr(settings, "BAICHUAN_M3_TIMEOUT_SECONDS", 45.0))

    def _check_config(self):
        if not self.base_url or not self.model:
            raise ValueError("AI 服务配置缺失")

    @abstractmethod
    def get_system_prompt(self) -> str:
        pass

    def _get_views_module(self):
        from apps.core import views

        return views

    def run(self, user_input: str, context: Dict[str, Any] = None) -> str:
        """
        非流式执行子代理任务
        """
        self._check_config()
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": json.dumps({"input": user_input, "context": context or {}}, ensure_ascii=False)},
        ]

        logger.info(f"[{self.__class__.__name__}] Run start", extra={"user_id": self.user_id})
        try:
            views = self._get_views_module()
            return views._openai_chat_completion(
                base_url=self.base_url,
                api_key=self.api_key,
                model=self.model,
                messages=messages,
                temperature=0.1,
                max_tokens=2048,
                timeout_seconds=self.timeout_seconds,
            )
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] Run failed: {e}")
            raise

    def run_stream(self, user_input: str, context: Dict[str, Any] = None):
        """
        流式执行子代理任务
        """
        self._check_config()
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": json.dumps({"input": user_input, "context": context or {}}, ensure_ascii=False)},
        ]

        logger.info(f"[{self.__class__.__name__}] Stream start", extra={"user_id": self.user_id})
        try:
            views = self._get_views_module()
            for chunk in views._openai_chat_completion_stream(
                base_url=self.base_url,
                api_key=self.api_key,
                model=self.model,
                messages=messages,
                temperature=0.1,
                max_tokens=2048,
                timeout_seconds=self.timeout_seconds,
            ):
                yield chunk
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] Stream failed: {e}")
            raise
