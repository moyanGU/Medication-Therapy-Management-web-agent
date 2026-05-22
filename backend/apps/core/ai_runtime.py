import logging
import socket
from dataclasses import dataclass
from urllib.parse import urlparse

import requests
from django.conf import settings

from .utils import error_response

logger = logging.getLogger("mtm_helper")

AI_ERROR_STATUS_CODES = {
    "AI_DISABLED": 503,
    "AI_CONFIG_MISSING": 503,
    "AI_UPSTREAM_UNAVAILABLE": 503,
    "AI_UPSTREAM_TIMEOUT": 504,
    "AI_INVALID_RESPONSE": 502,
}


AI_ERROR_MESSAGES = {
    "AI_DISABLED": "AI 服务未启用",
    "AI_CONFIG_MISSING": "AI 服务配置缺失",
    "AI_UPSTREAM_UNAVAILABLE": "AI 上游服务不可用",
    "AI_UPSTREAM_TIMEOUT": "AI 上游服务响应超时",
    "AI_INVALID_RESPONSE": "AI 上游返回了不可解析的响应",
}


@dataclass(frozen=True)
class AIRuntimeConfig:
    base_url: str
    api_key: str
    model: str
    timeout_seconds: float
    source: str = "primary"


def build_ai_runtime_error(error_code: str):
    status_code = AI_ERROR_STATUS_CODES.get(error_code, 500)
    return error_response(
        AI_ERROR_MESSAGES.get(error_code, "AI 服务异常"),
        error_code,
        status_code,
    )


def build_ai_openai_error_body(response, *, upstream: dict | None = None):
    error_code = str(response.data.get("error_code") or "")
    body = {
        "success": False,
        "message": response.data.get("message"),
        "error_code": error_code,
        "status_code": response.status_code,
        "error": {
            "message": response.data.get("message"),
            "type": error_code.lower(),
            "code": error_code,
        },
    }
    if upstream is not None:
        body["error"]["upstream"] = upstream
    return body


def _build_primary_runtime_config():
    if not getattr(settings, "BAICHUAN_M3_ENABLED", False):
        return None, build_ai_runtime_error("AI_DISABLED")

    base_url = str(getattr(settings, "BAICHUAN_M3_API_BASE_URL", "") or "").strip()
    model = str(getattr(settings, "BAICHUAN_M3_MODEL", "") or "").strip()
    if not base_url or not model:
        return None, build_ai_runtime_error("AI_CONFIG_MISSING")

    return (
        AIRuntimeConfig(
            base_url=base_url,
            api_key=str(getattr(settings, "BAICHUAN_M3_API_KEY", "") or "").strip(),
            model=model,
            timeout_seconds=float(getattr(settings, "BAICHUAN_M3_TIMEOUT_SECONDS", 30) or 30),
            source="primary",
        ),
        None,
    )


def get_ai_fallback_runtime_config():
    base_url = str(getattr(settings, "AI_FALLBACK_API_BASE_URL", "") or "").strip()
    model = str(getattr(settings, "AI_FALLBACK_MODEL", "") or "").strip()
    if not base_url or not model:
        return None

    return AIRuntimeConfig(
        base_url=base_url,
        api_key=str(getattr(settings, "AI_FALLBACK_API_KEY", "") or "").strip(),
        model=model,
        timeout_seconds=float(getattr(settings, "AI_FALLBACK_TIMEOUT_SECONDS", 30) or 30),
        source="fallback",
    )


def _parse_host_port(raw_url: str):
    parsed = urlparse((raw_url or "").strip())
    if not parsed.hostname:
        return None
    if parsed.port:
        return parsed.hostname, int(parsed.port)
    if parsed.scheme == "https":
        return parsed.hostname, 443
    if parsed.scheme == "http":
        return parsed.hostname, 80
    return None


def is_localhost_ai_base_url(base_url: str) -> bool:
    try:
        host_port = _parse_host_port(base_url)
        host = host_port[0] if host_port else ""
        return host in {"127.0.0.1", "localhost", "::1"}
    except Exception:
        return False


def is_ai_upstream_reachable(base_url: str, timeout_seconds: float = 0.3) -> bool:
    host_port = _parse_host_port(base_url)
    if not host_port:
        return False

    host, port = host_port
    if host not in {"127.0.0.1", "localhost", "::1"}:
        return True

    try:
        with socket.create_connection((host, port), timeout=timeout_seconds):
            return True
    except Exception:
        return False


def get_ai_runtime_config():
    primary_config, primary_error = _build_primary_runtime_config()
    fallback_config = get_ai_fallback_runtime_config()

    if primary_config is not None:
        if (
            is_localhost_ai_base_url(primary_config.base_url)
            and not is_ai_upstream_reachable(primary_config.base_url)
            and fallback_config is not None
        ):
            logger.info("[AI] primary localhost upstream unavailable; using fallback", extra={
                "primary_base_url": primary_config.base_url,
                "fallback_base_url": fallback_config.base_url,
                "fallback_model": fallback_config.model,
            })
            return fallback_config, None
        return primary_config, None

    if fallback_config is not None:
        return fallback_config, None

    return None, primary_error


def classify_ai_exception(exc) -> str:
    if isinstance(exc, requests.Timeout):
        return "AI_UPSTREAM_TIMEOUT"
    if isinstance(exc, requests.RequestException):
        return "AI_UPSTREAM_UNAVAILABLE"

    text = str(exc or "").strip()
    if text.startswith("llm_request_exception:Timeout") or text.startswith(
        "llm_request_exception:ReadTimeout"
    ):
        return "AI_UPSTREAM_TIMEOUT"
    if text.startswith("llm_request_exception:"):
        return "AI_UPSTREAM_UNAVAILABLE"
    if text.startswith("llm_http_error:"):
        if ":504:" in text or ":408:" in text:
            return "AI_UPSTREAM_TIMEOUT"
        if ":400:" in text or ":401:" in text or ":403:" in text or ":404:" in text:
            return "AI_INVALID_RESPONSE"
        return "AI_UPSTREAM_UNAVAILABLE"
    if text in {"llm_invalid_json", "llm_invalid_response", "llm_empty_content"}:
        return "AI_INVALID_RESPONSE"
    if text.startswith("llm_empty_choices:") or text.startswith("llm_invalid_"):
        return "AI_INVALID_RESPONSE"
    return "AI_UPSTREAM_UNAVAILABLE"


def build_ai_failure_response(exc, *, trace: dict | None = None):
    error_code = classify_ai_exception(exc)
    log_payload = {"error_code": error_code, "error": str(exc or "")}
    if trace:
        log_payload.update(trace)
    logger.warning("[AI] runtime failure", extra=log_payload)
    return build_ai_runtime_error(error_code)
