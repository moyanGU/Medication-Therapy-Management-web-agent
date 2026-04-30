import json
import logging
import time

import requests
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .ai_llm import _normalize_openai_base_url

logger = logging.getLogger("mtm_helper")


def _json_error(message: str, error_type: str, status_code: int):
    return JsonResponse({"error": {"message": message, "type": error_type}}, status=status_code)


def _get_page_agent_config():
    if not getattr(settings, "BAICHUAN_M3_ENABLED", False):
        return None, None, None, None, _json_error("AI 服务未启用", "service_unavailable", 503)

    base_url = getattr(settings, "BAICHUAN_M3_API_BASE_URL", "")
    api_key = getattr(settings, "BAICHUAN_M3_API_KEY", "")
    model = getattr(settings, "BAICHUAN_M3_MODEL", "")
    timeout_seconds = float(getattr(settings, "BAICHUAN_M3_TIMEOUT_SECONDS", 30))

    if not base_url or not model:
        return None, None, None, None, _json_error("AI 服务配置缺失", "config_error", 503)

    return base_url, api_key, model, timeout_seconds, None


def _build_page_agent_headers(api_key: str) -> dict:
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return headers


def _get_page_agent_url(base_url: str) -> str:
    return f"{_normalize_openai_base_url(base_url)}/chat/completions"


def _build_page_agent_proxy_payload(data: dict) -> dict:
    messages = data.get("messages")
    if not isinstance(messages, list) or not messages:
        raise ValueError("messages 必须为非空数组")
    if len(messages) > 20:
        raise ValueError("messages 数量超过限制")

    tools = data.get("tools")
    if tools is not None and not isinstance(tools, list):
        raise ValueError("tools 必须为数组")
    if isinstance(tools, list) and len(tools) > 20:
        raise ValueError("tools 数量超过限制")

    payload = {
        "model": getattr(settings, "BAICHUAN_M3_MODEL", ""),
        "messages": messages,
        "temperature": data.get("temperature", 0.1),
        "tool_choice": data.get("tool_choice", "required"),
        "parallel_tool_calls": bool(data.get("parallel_tool_calls", False)),
    }

    if tools:
        payload["tools"] = tools

    max_tokens = data.get("max_tokens")
    if isinstance(max_tokens, int) and max_tokens > 0:
        max_limit = int(getattr(settings, "BAICHUAN_M3_MAX_OUTPUT_TOKENS", 1024))
        payload["max_tokens"] = min(max_tokens, max_limit)

    return payload


def _extract_page_agent_tool_name(tool_choice) -> str:
    if isinstance(tool_choice, dict):
        function = tool_choice.get("function")
        if (
            tool_choice.get("type") == "function"
            and isinstance(function, dict)
            and isinstance(function.get("name"), str)
        ):
            return function["name"].strip()
    return ""


def _select_page_agent_tool(payload: dict) -> dict | None:
    tools = payload.get("tools")
    if not isinstance(tools, list) or not tools:
        return None

    selected_name = _extract_page_agent_tool_name(payload.get("tool_choice"))
    if selected_name:
        for tool in tools:
            function = tool.get("function") if isinstance(tool, dict) else None
            if isinstance(function, dict) and function.get("name") == selected_name:
                return tool
        raise ValueError(f"未找到 tool_choice 指定的工具：{selected_name}")

    first_tool = tools[0]
    return first_tool if isinstance(first_tool, dict) else None


def _extract_page_agent_tool_meta(tool_spec: dict):
    function = tool_spec.get("function") if isinstance(tool_spec, dict) else {}
    tool_name = str(function.get("name") or "AgentOutput").strip() or "AgentOutput"
    description = str(function.get("description") or "").strip()
    parameters = function.get("parameters")
    if not isinstance(parameters, dict):
        parameters = {"type": "object"}
    return tool_name, description, parameters


def _build_page_agent_fallback_instruction(tool_spec: dict) -> str:
    tool_name, description, parameters = _extract_page_agent_tool_meta(tool_spec)
    return (
        "你当前运行在一个不支持 function calling 的模型兼容层。"
        f"请直接模拟一次对工具 {tool_name} 的调用，并只输出该工具参数对应的 JSON 对象。"
        "禁止输出 markdown、代码块、解释、前后缀、思考过程或任何非 JSON 内容。"
        "输出的第一个字符必须是 {，最后一个字符必须是 }。"
        f"\n工具描述：{description or '无'}"
        f"\n参数 JSON Schema：{json.dumps(parameters, ensure_ascii=False)}"
        "\n如果字段无法确定，请给出最保守、最可执行且满足 schema 的值。"
    )


def _normalize_page_agent_messages(messages: list[dict]):
    system_parts = []
    normalized_messages = []
    for message in messages:
        if not isinstance(message, dict):
            continue
        if message.get("role") == "system":
            content = message.get("content")
            if content:
                system_parts.append(str(content))
            continue
        normalized_messages.append(message)
    return system_parts, normalized_messages


def _build_page_agent_fallback_messages(messages: list[dict], tool_spec: dict) -> list[dict]:
    instruction = _build_page_agent_fallback_instruction(tool_spec)
    system_parts, normalized_messages = _normalize_page_agent_messages(messages)
    return [
        {"role": "system", "content": "\n\n".join(part for part in [instruction, *system_parts] if part)},
        *normalized_messages,
    ]


def _build_page_agent_fallback_response(
    *,
    model: str,
    tool_name: str,
    arguments: dict,
    upstream_text: str,
) -> dict:
    return {
        "id": f"chatcmpl-page-agent-fallback-{int(time.time() * 1000)}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": upstream_text,
                    "tool_calls": [
                        {
                            "id": "call_page_agent_fallback",
                            "type": "function",
                            "function": {
                                "name": tool_name,
                                "arguments": json.dumps(arguments, ensure_ascii=False),
                            },
                        }
                    ],
                },
                "finish_reason": "tool_calls",
            }
        ],
    }


def _extract_json_object(text: str) -> dict | None:
    try:
        import re

        if not text:
            return None
        m = re.search(r"\{[\s\S]*\}", text)
        if not m:
            return None
        return json.loads(m.group(0))
    except Exception:
        return None


def _execute_page_agent_fallback(
    *,
    base_url: str,
    api_key: str,
    model: str,
    timeout_seconds: float,
    payload: dict,
) -> dict:
    tool_spec = _select_page_agent_tool(payload)
    if not tool_spec:
        raise ValueError("未找到可用工具")

    tool_name, _, _ = _extract_page_agent_tool_meta(tool_spec)
    fallback_messages = _build_page_agent_fallback_messages(payload["messages"], tool_spec)
    max_tokens = int(payload.get("max_tokens") or getattr(settings, "BAICHUAN_M3_MAX_OUTPUT_TOKENS", 1024))
    from apps.core import views as core_views

    upstream_text = core_views._openai_chat_completion(
        base_url=base_url,
        api_key=api_key,
        model=model,
        messages=fallback_messages,
        temperature=float(payload.get("temperature", 0.1)),
        max_tokens=max_tokens,
        timeout_seconds=timeout_seconds,
    )
    arguments = _extract_json_object(upstream_text)
    if not isinstance(arguments, dict):
        raise ValueError("上游模型未返回可解析的 JSON 工具参数")
    return _build_page_agent_fallback_response(
        model=model,
        tool_name=tool_name,
        arguments=arguments,
        upstream_text=upstream_text,
    )


def _handle_page_agent_tools_fallback(*, base_url: str, api_key: str, model: str, timeout_seconds: float, payload: dict):
    try:
        body = _execute_page_agent_fallback(
            base_url=base_url,
            api_key=api_key,
            model=model,
            timeout_seconds=timeout_seconds,
            payload=payload,
        )
        return JsonResponse(body, status=200, safe=isinstance(body, dict))
    except requests.RequestException:
        return _json_error("上游模型服务请求失败", "upstream_error", 502)
    except RuntimeError:
        return _json_error("上游模型返回错误", "upstream_error", 502)
    except ValueError as exc:
        return _json_error(str(exc), "invalid_response_error", 502)


def _proxy_page_agent_upstream(*, url: str, headers: dict, payload: dict, timeout_seconds: float):
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=timeout_seconds)
    except requests.RequestException:
        return _json_error("上游模型服务请求失败", "upstream_error", 502)

    try:
        body = resp.json()
    except ValueError:
        return _json_error("上游模型响应格式错误", "bad_gateway", 502)

    return JsonResponse(body, status=resp.status_code, safe=isinstance(body, dict))


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def page_agent_chat_completions(request):
    base_url, api_key, model, timeout_seconds, error = _get_page_agent_config()
    if error is not None:
        return error

    try:
        payload = _build_page_agent_proxy_payload(request.data or {})
    except ValueError as exc:
        return _json_error(str(exc), "invalid_request_error", 400)

    headers = _build_page_agent_headers(api_key)
    url = _get_page_agent_url(base_url)
    if payload.get("tools"):
        return _handle_page_agent_tools_fallback(
            base_url=base_url,
            api_key=api_key,
            model=model,
            timeout_seconds=timeout_seconds,
            payload=payload,
        )

    return _proxy_page_agent_upstream(
        url=url, headers=headers, payload=payload, timeout_seconds=timeout_seconds
    )
