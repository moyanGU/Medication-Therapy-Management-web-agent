import re

from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .models import SessionMemory
from .utils import error_response, success_response


def _normalize_session_id(session_id: str) -> str:
    normalized = (session_id or "").strip()
    if not normalized:
        raise ValueError("缺少 session_id")
    if len(normalized) > 128:
        raise ValueError("session_id 过长")
    if not re.match(r"^[a-zA-Z0-9:_-]+$", normalized):
        raise ValueError("session_id 格式不合法")
    return normalized


def _sanitize_messages(messages):
    if not isinstance(messages, list):
        return []
    sanitized = []
    for item in messages:
        if not isinstance(item, dict):
            continue
        role = str(item.get("role") or "").strip()
        content = str(item.get("content") or "").strip()
        if role not in ("user", "ai", "assistant", "system"):
            continue
        if not content:
            continue
        if len(content) > 2000:
            content = content[:2000]
        sanitized.append({"role": "ai" if role == "assistant" else role, "content": content})
    return sanitized[-60:]


def _require_user_id(request):
    user_id = getattr(request.user, "id", None)
    if not user_id:
        return None, error_response("需要登录", "AUTH_REQUIRED", 401)
    return user_id, None


def _build_session_memory_response(session_id: str, memory: SessionMemory | None):
    if memory:
        payload = {
            "summary": memory.summary,
            "messages": memory.messages,
            "updated_at": memory.updated_at.isoformat(),
        }
    else:
        payload = {}

    return {
        "session_id": session_id,
        "summary": str(payload.get("summary") or ""),
        "messages": payload.get("messages") if isinstance(payload.get("messages"), list) else [],
        "updated_at": payload.get("updated_at"),
    }


def _handle_session_memory_get(request, user_id):
    session_id_raw = request.query_params.get("session_id") or ""
    try:
        session_id = _normalize_session_id(session_id_raw)
    except ValueError as exc:
        return error_response(str(exc), "VALIDATION_ERROR", 400)

    memory = SessionMemory.objects.filter(user_id=user_id, session_id=session_id).first()
    return success_response(_build_session_memory_response(session_id, memory), "获取成功")


def _handle_session_memory_post(request, user_id):
    try:
        session_id = _normalize_session_id(str((request.data or {}).get("session_id") or ""))
    except ValueError as exc:
        return error_response(str(exc), "VALIDATION_ERROR", 400)

    messages = _sanitize_messages((request.data or {}).get("messages"))
    summary = str((request.data or {}).get("summary") or "").strip()
    if len(summary) > 4000:
        summary = summary[:4000]

    memory, _ = SessionMemory.objects.update_or_create(
        user_id=user_id,
        session_id=session_id,
        defaults={"summary": summary, "messages": messages},
    )
    return success_response(
        {"session_id": session_id, "updated_at": memory.updated_at.isoformat()},
        "保存成功",
    )


def _require_ai_enabled():
    if not getattr(settings, "BAICHUAN_M3_ENABLED", False):
        return error_response("AI 服务未启用", "AI_DISABLED", 503)
    return None


def _resolve_summarize_messages(memory, request):
    stored_messages = memory.messages if memory else []
    incoming_messages = _sanitize_messages((request.data or {}).get("messages"))
    messages = incoming_messages or stored_messages
    if not messages:
        return None, error_response("暂无可总结的对话内容", "VALIDATION_ERROR", 400)
    return messages, None


def _truncate_summary(summary_text: str) -> str:
    return summary_text[:4000] if summary_text and len(summary_text) > 4000 else summary_text


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def session_memory(request):
    user_id, error = _require_user_id(request)
    if error is not None:
        return error

    if request.method == "GET":
        return _handle_session_memory_get(request, user_id)
    return _handle_session_memory_post(request, user_id)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def session_memory_summarize(request):
    user_id, error = _require_user_id(request)
    if error is not None:
        return error

    error = _require_ai_enabled()
    if error is not None:
        return error

    try:
        session_id = _normalize_session_id(str((request.data or {}).get("session_id") or ""))
    except ValueError as exc:
        return error_response(str(exc), "VALIDATION_ERROR", 400)

    memory = SessionMemory.objects.filter(user_id=user_id, session_id=session_id).first()
    messages, error = _resolve_summarize_messages(memory, request)
    if error is not None:
        return error

    try:
        from apps.core.agents.memory_agent import SessionMemoryAgent

        agent = SessionMemoryAgent(user_id=user_id, session_id=session_id)
        summary_text = agent.summarize(messages)
    except Exception:
        return error_response("AI 生成失败", "AI_GENERATION_FAILED", 500)

    summary_text = _truncate_summary(summary_text)

    memory, created = SessionMemory.objects.update_or_create(
        user_id=user_id,
        session_id=session_id,
        defaults={"summary": summary_text, "messages": messages},
    )

    return success_response(
        {"session_id": session_id, "summary": summary_text, "updated_at": memory.updated_at.isoformat()},
        "生成成功",
    )
