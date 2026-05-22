import json
import logging
import time

import requests
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .ai_llm import _build_openai_chat_completion_urls, _normalize_openai_base_url
from .ai_runtime import (
    build_ai_failure_response,
    build_ai_openai_error_body,
    build_ai_runtime_error,
    get_ai_runtime_config,
)

logger = logging.getLogger("mtm_helper")


def _json_error(message: str, error_type: str, status_code: int):
    error_code = str(error_type or "").upper()
    return JsonResponse(
        {
            "success": False,
            "message": message,
            "error_code": error_code,
            "status_code": status_code,
            "error": {
                "message": message,
                "type": str(error_type or "").lower(),
                "code": error_code,
            },
        },
        status=status_code,
    )


def _ai_response_to_json_error(response):
    return JsonResponse(
        build_ai_openai_error_body(response),
        status=response.status_code,
        safe=True,
    )


def _get_page_agent_config():
    runtime_config, error = get_ai_runtime_config()
    if error is not None:
        return None, None, None, None, _ai_response_to_json_error(error)

    return (
        runtime_config.base_url,
        runtime_config.api_key,
        runtime_config.model,
        runtime_config.timeout_seconds,
        None,
    )


def _build_page_agent_headers(api_key: str) -> dict:
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return headers


def _get_page_agent_url(base_url: str) -> str:
    return f"{_normalize_openai_base_url(base_url)}/chat/completions"


def _validate_page_agent_messages(messages):
    if not isinstance(messages, list) or not messages:
        raise ValueError("messages 必须为非空数组")
    if len(messages) > 20:
        raise ValueError("messages 数量超过限制")
    return messages


def _validate_page_agent_tools(tools):
    if tools is None:
        return None
    if not isinstance(tools, list):
        raise ValueError("tools 必须为数组")
    if len(tools) > 20:
        raise ValueError("tools 数量超过限制")
    return tools


def _apply_page_agent_max_tokens(payload: dict, raw_value):
    if not isinstance(raw_value, int) or raw_value <= 0:
        return
    max_limit = int(getattr(settings, "BAICHUAN_M3_MAX_OUTPUT_TOKENS", 1024))
    payload["max_tokens"] = min(raw_value, max_limit)


def _build_page_agent_proxy_payload(data: dict) -> dict:
    messages = _validate_page_agent_messages(data.get("messages"))
    tools = _validate_page_agent_tools(data.get("tools"))
    raw_tool_choice = data.get("tool_choice", "required")
    if isinstance(raw_tool_choice, dict):
        upstream_tool_choice = "required"
    elif isinstance(raw_tool_choice, str) and raw_tool_choice.strip():
        upstream_tool_choice = raw_tool_choice.strip()
    else:
        upstream_tool_choice = "required"

    payload = {
        "model": "",
        "messages": messages,
        "temperature": data.get("temperature", 0.1),
        "parallel_tool_calls": bool(data.get("parallel_tool_calls", False)),
    }

    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = upstream_tool_choice
        payload["_tool_choice_spec"] = raw_tool_choice

    _apply_page_agent_max_tokens(payload, data.get("max_tokens"))

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

    selected_name = _extract_page_agent_tool_name(
        payload.get("_tool_choice_spec", payload.get("tool_choice"))
    )
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
        f"请直接模拟一次对工具 {tool_name} 的调用，并且只输出该工具参数对应的 JSON 对象。"
        "禁止输出 markdown、代码块、解释、前后缀、思考过程或任何非 JSON 内容。"
        "输出的第一个字符必须是 {，最后一个字符必须是 }。"
        f"\n工具描述：{description or '无'}"
        f"\n参数 JSON Schema：{json.dumps(parameters, ensure_ascii=False)}"
        "\n如字段无法确定，请给出最保守、最可执行且满足 schema 的值。"
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
        {
            "role": "system",
            "content": "\n\n".join(
                part for part in [instruction, *system_parts] if part
            ),
        },
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
    max_tokens = int(
        payload.get("max_tokens")
        or getattr(settings, "BAICHUAN_M3_MAX_OUTPUT_TOKENS", 1024)
    )
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


def _handle_page_agent_tools_fallback(
    *, base_url: str, api_key: str, model: str, timeout_seconds: float, payload: dict
):
    try:
        body = _execute_page_agent_fallback(
            base_url=base_url,
            api_key=api_key,
            model=model,
            timeout_seconds=timeout_seconds,
            payload=payload,
        )
        return JsonResponse(body, status=200, safe=isinstance(body, dict))
    except (requests.RequestException, RuntimeError) as exc:
        response = build_ai_failure_response(
            exc,
            trace={"endpoint": "page_agent_tools_fallback"},
        )
        return _ai_response_to_json_error(response)
    except ValueError as exc:
        return _json_error(str(exc), "ai_invalid_response", 502)


def _proxy_page_agent_upstream(
    *, base_url: str, headers: dict, payload: dict, timeout_seconds: float
):
    from apps.core import views as core_views

    urls = _build_openai_chat_completion_urls(base_url)
    if not urls:
        return _ai_response_to_json_error(build_ai_runtime_error("AI_CONFIG_MISSING"))

    upstream_payload = {
        key: value for key, value in payload.items() if not str(key).startswith("_")
    }
    last_body = None
    last_status = 502
    for index, url in enumerate(urls):
        try:
            resp = core_views.requests.post(
                url, headers=headers, json=upstream_payload, timeout=timeout_seconds
            )
        except requests.RequestException as exc:
            response = build_ai_failure_response(
                exc,
                trace={"endpoint": "page_agent_proxy", "url": url},
            )
            last_body = build_ai_openai_error_body(response)
            last_status = response.status_code
            continue

        try:
            body = resp.json()
        except ValueError:
            response = build_ai_runtime_error("AI_INVALID_RESPONSE")
            last_body = build_ai_openai_error_body(response)
            last_status = response.status_code
            continue

        last_body = body
        last_status = resp.status_code
        if isinstance(body, dict) and isinstance(body.get("choices"), list) and body.get("choices"):
            return JsonResponse(body, status=resp.status_code, safe=True)
        if isinstance(body, dict) and isinstance(body.get("error"), dict):
            response = build_ai_runtime_error("AI_INVALID_RESPONSE")
            return JsonResponse(
                build_ai_openai_error_body(response, upstream=body.get("error")),
                status=response.status_code,
                safe=True,
            )
        if index < len(urls) - 1:
            continue
        return JsonResponse(body, status=resp.status_code, safe=isinstance(body, dict))

    if last_body is None:
        response = build_ai_runtime_error("AI_UPSTREAM_UNAVAILABLE")
        last_body = build_ai_openai_error_body(response)
        last_status = response.status_code

    return JsonResponse(last_body, status=last_status, safe=isinstance(last_body, dict))


def _page_agent_proxy_has_tool_calls(response) -> bool:
    if getattr(response, "status_code", 0) < 200 or getattr(response, "status_code", 0) >= 300:
        return False

    try:
        body = json.loads(response.content.decode("utf-8"))
    except Exception:
        return False

    if not isinstance(body, dict):
        return False

    choices = body.get("choices")
    if not isinstance(choices, list) or not choices:
        return False

    first_choice = choices[0] if isinstance(choices[0], dict) else {}
    message = first_choice.get("message") if isinstance(first_choice, dict) else {}
    tool_calls = message.get("tool_calls") if isinstance(message, dict) else None
    return isinstance(tool_calls, list) and bool(tool_calls)


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

    payload["model"] = model
    headers = _build_page_agent_headers(api_key)
    if payload.get("tools"):
        proxy_response = _proxy_page_agent_upstream(
            base_url=base_url,
            headers=headers,
            payload=payload,
            timeout_seconds=timeout_seconds,
        )
        if _page_agent_proxy_has_tool_calls(proxy_response):
            return proxy_response

        fallback_response = _handle_page_agent_tools_fallback(
            base_url=base_url,
            api_key=api_key,
            model=model,
            timeout_seconds=timeout_seconds,
            payload=payload,
        )
        return fallback_response

    return _proxy_page_agent_upstream(
        base_url=base_url,
        headers=headers,
        payload=payload,
        timeout_seconds=timeout_seconds,
    )
