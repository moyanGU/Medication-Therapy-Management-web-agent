import json
import logging
import re

import requests

logger = logging.getLogger("mtm_helper")


def _build_llm_headers(api_key: str) -> dict:
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return headers


def _build_llm_payload(
    *,
    model: str,
    messages: list[dict],
    temperature: float,
    max_tokens: int,
    response_format: dict | None = None,
    stream: bool = False,
) -> dict:
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if response_format is not None:
        payload["response_format"] = response_format
    if stream:
        payload["stream"] = True
    return payload


def _parse_openai_chat_content(data, *, url: str, index: int, urls: list[str]):
    choices = data.get("choices") if isinstance(data, dict) else None
    if not isinstance(choices, list) or not choices:
        fallback_hint = json.dumps(data, ensure_ascii=False)[:300] if isinstance(data, dict) else ""
        if index < len(urls) - 1:
            logger.warning(
                "[LLMProxy] empty choices on primary endpoint, retrying fallback",
                extra={"url": url, "response_preview": fallback_hint},
            )
        return None, f"llm_empty_choices:{fallback_hint}"

    msg = (choices[0] or {}).get("message") or {}
    content = msg.get("content")
    if isinstance(content, str) and content.strip():
        return content, None

    reasoning_content = msg.get("reasoning_content")
    if isinstance(reasoning_content, str) and reasoning_content.strip():
        return reasoning_content, None

    if isinstance(content, str):
        return None, "llm_empty_content"
    return None, "llm_invalid_content"


def _normalize_openai_base_url(raw: str) -> str:
    base = (raw or "").strip().rstrip("/")
    if not base:
        return ""
    if base.endswith("/v1"):
        return base
    return f"{base}/v1"


def _build_openai_chat_completion_urls(raw: str) -> list[str]:
    base = (raw or "").strip().rstrip("/")
    if not base:
        return []
    if base.endswith("/v1"):
        candidates = [f"{base}/chat/completions", f"{base[:-3]}/chat/completions"]
    else:
        candidates = [f"{base}/v1/chat/completions", f"{base}/chat/completions"]
    deduped: list[str] = []
    for url in candidates:
        if url and url not in deduped:
            deduped.append(url)
    return deduped


def _extract_json_object(text: str) -> dict | None:
    if not text:
        return None
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


def _openai_chat_completion_stream(
    *,
    base_url: str,
    api_key: str,
    model: str,
    messages: list[dict],
    temperature: float,
    max_tokens: int,
    timeout_seconds: float,
):
    headers = _build_llm_headers(api_key)
    payload = _build_llm_payload(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
    )

    urls = _build_openai_chat_completion_urls(base_url)
    if not urls:
        raise RuntimeError("llm_invalid_base_url")

    last_error: str | None = None
    for url in urls:
        try:
            with requests.post(
                url, headers=headers, json=payload, timeout=timeout_seconds, stream=True
            ) as resp:
                if resp.status_code >= 300:
                    body_text = str(getattr(resp, "text", "") or "")
                    last_error = f"llm_http_error:{resp.status_code}:{body_text[:200]}"
                    continue

                for line in resp.iter_lines():
                    if line:
                        line_str = line.decode("utf-8")
                        if line_str.startswith("data: "):
                            data_str = line_str[6:]
                            if data_str == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                                delta = data.get("choices", [{}])[0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield json.dumps({"chunk": content}, ensure_ascii=False) + "\n"
                            except Exception:
                                pass
                return
        except Exception as exc:
            last_error = f"llm_request_exception:{type(exc).__name__}:{str(exc)[:120]}"
            continue

    yield json.dumps({"error": last_error or "llm_invalid_response"}, ensure_ascii=False) + "\n"


def _openai_chat_completion(
    *,
    base_url: str,
    api_key: str,
    model: str,
    messages: list[dict],
    temperature: float,
    max_tokens: int,
    timeout_seconds: float,
    response_format: dict | None = None,
) -> str:
    headers = _build_llm_headers(api_key)
    payload = _build_llm_payload(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        response_format=response_format,
    )

    urls = _build_openai_chat_completion_urls(base_url)
    if not urls:
        raise RuntimeError("llm_invalid_base_url")

    last_error: str | None = None
    for index, url in enumerate(urls):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=timeout_seconds)
        except Exception as exc:
            last_error = f"llm_request_exception:{type(exc).__name__}:{str(exc)[:120]}"
            continue

        body_text = str(getattr(resp, "text", "") or "")
        if resp.status_code >= 300:
            last_error = f"llm_http_error:{resp.status_code}:{body_text[:200]}"
            continue

        try:
            data = resp.json()
        except Exception:
            last_error = "llm_invalid_json"
            continue

        content, parse_error = _parse_openai_chat_content(
            data, url=url, index=index, urls=urls
        )
        if content is not None:
            return content
        last_error = parse_error

    raise RuntimeError(last_error or "llm_invalid_response")


def _normalize_llm_answer(text: str) -> str:
    t = (text or "").strip()
    t = re.sub(r"^```[a-zA-Z0-9_-]*\n", "", t).strip()
    t = re.sub(r"\n```$", "", t).strip()
    if t.startswith("**") and t.count("**") == 1:
        t = t[2:].lstrip()
    return t


def _looks_unhelpful_answer(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return True
    t2 = re.sub(r"[\*`\s]", "", t)
    refusal_markers = [
        "无法直接提供",
        "无法提供",
        "不能提供",
        "不便提供",
        "无法回答",
        "我不能",
        "我无法",
    ]
    if len(t2) <= 40 and any(m in t2 for m in refusal_markers):
        return True

    if t.rstrip().endswith(("，", "、", ",", ";", "：", ":", "（", "(")):
        return True

    has_number = bool(re.search(r"\d", t))
    mentions_dose = any(k in t for k in ("剂量", "用量", "mg", "毫克"))
    mentions_age_weight = bool(re.search(r"(根据|取决于).{0,12}(年龄|体重)", t))
    if len(t2) <= 200 and (mentions_age_weight or mentions_dose) and not has_number:
        return True
    return False
