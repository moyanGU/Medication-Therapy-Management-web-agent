"""核心应用视图"""

from .views_ai import (
    _build_openai_chat_completion_urls,
    _build_page_agent_fallback_messages,
    _build_page_agent_fallback_response,
    _build_page_agent_proxy_payload,
    _execute_page_agent_fallback,
    _extract_json_object,
    _extract_page_agent_tool_name,
    _fallback_medication_guidance_answer,
    _looks_unhelpful_answer,
    _normalize_llm_answer,
    _normalize_openai_base_url,
    _normalize_session_id,
    _openai_chat_completion,
    _openai_chat_completion_stream,
    _sanitize_messages,
    _select_page_agent_tool,
    agent_permission_matrix,
    medication_guidance,
    page_agent_chat_completions,
    session_memory,
    session_memory_summarize,
)
from .views_dashboard import dashboard_summary
from .views_system import api_docs, clear_cache, diagnostics, health_check, ping, system_info

