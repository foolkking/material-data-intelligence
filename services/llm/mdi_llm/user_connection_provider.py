"""Explicit, bounded request protocols for user-owned structured model calls."""

from __future__ import annotations

import json
import re
import socket
import urllib.error
import urllib.request
from typing import Any
from .http_transport import InvalidProviderResponse, ProviderStreamCancelled, read_provider_response
from .providers import LLMProviderError, PlannerRawResponse, PlannerUserConfig, _parse_llm_json


def _http_failure(status: int) -> tuple[str, str]:
    if status in {401, 403}:
        return ("模型服务拒绝了连接认证，请检查模型设置中的密钥和使用权限。", "PROVIDER_AUTH_FAILED")
    if status == 429:
        return ("模型服务当前请求过多，请稍后重试。", "PROVIDER_RATE_LIMITED")
    if status in {400, 404, 405, 422}:
        return ("模型服务不支持当前请求，请检查所选模型和请求协议。", "PROVIDER_REQUEST_REJECTED")
    return ("模型服务暂时不可用，请稍后重试。", "EXTERNAL_UNAVAILABLE")


def _envelope_failure(response: dict[str, Any]) -> None:
    error = response.get("error")
    if not isinstance(error, dict):
        return
    # Only documented machine fields classify envelope errors. Free-form
    # upstream messages are neither interpreted nor copied into exceptions.
    kind = error.get("type") or error.get("code")
    status = {
        "rate_limit_error": 429, "rate_limit_exceeded": 429, "insufficient_quota": 429,
        "authentication_error": 401, "invalid_api_key": 401,
        "permission_error": 403, "permission_denied": 403,
        "invalid_request_error": 400, "not_found_error": 404,
    }.get(kind) if isinstance(kind, str) else None
    message, code = _http_failure(status or 503)
    raise LLMProviderError(message, code=code)


class UserConnectionProvider:
    def __init__(self, *, protocol: str, transport: Any = None):
        self.protocol = protocol
        self.transport = transport

    def complete_json(self, *, messages: list[dict[str, str]], user_config: PlannerUserConfig, purpose: str | None = None, on_content: Any = None) -> PlannerRawResponse:
        config = user_config
        headers = {"Content-Type": "application/json", "Accept": "application/json", "User-Agent": "MDI/1.0"}
        payload: dict[str, Any] = {"model": config.model}
        if self.protocol in {"openai_chat_json", "openai_chat"}:
            path = "/chat/completions"
            headers["Authorization"] = f"Bearer {config.api_key}"
            payload.update(messages=messages, max_tokens=config.max_tokens, temperature=0)
            if self.protocol == "openai_chat_json":
                payload["response_format"] = {"type": "json_object"}
        elif self.protocol == "openai_responses":
            path = "/responses"
            headers["Authorization"] = f"Bearer {config.api_key}"
            payload.update(input=messages, max_output_tokens=config.max_tokens, store=False)
        elif self.protocol == "anthropic":
            path = "/messages"
            headers.update({"x-api-key": config.api_key or "", "anthropic-version": "2023-06-01"})
            payload.update(system="\n\n".join(item["content"] for item in messages if item["role"] == "system"),
                           messages=[item for item in messages if item["role"] != "system"], max_tokens=config.max_tokens, temperature=0)
        else:
            raise LLMProviderError("不支持的模型请求协议。", code="PROVIDER_NOT_ALLOWED")
        if on_content is not None:
            payload["stream"] = True
            headers["Accept"] = "text/event-stream"
        response_received = False
        try:
            if self.transport:
                response = self.transport(path=path, headers=headers, payload=payload)
                response_received = True
            else:
                request = urllib.request.Request(f"{(config.base_url or '').rstrip('/')}{path}", data=json.dumps(payload).encode(), headers=headers, method="POST")
                from .streaming import CompletionStreamDecoder
                decoder = CompletionStreamDecoder(self.protocol, on_content) if on_content is not None else None
                raw = read_provider_response(request, timeout=config.timeout_seconds, byte_limit=2_000_000, on_chunk=decoder.feed if decoder else None)
                response_received = True
                if len(raw) > 2_000_000:
                    raise ValueError("response too large")
                response = decoder.finish(raw) if decoder else json.loads(raw)
            if not isinstance(response, dict):
                raise ValueError("invalid response envelope")
            _envelope_failure(response)
            if self.protocol == "anthropic":
                content = "".join(item.get("text", "") for item in response.get("content", []) if item.get("type") == "text")
                finish = response.get("stop_reason")
            elif self.protocol == "openai_responses":
                content = "".join(part.get("text", "") for item in response.get("output", []) if item.get("type") == "message" for part in item.get("content", []) if part.get("type") == "output_text")
                finish = response.get("status")
            else:
                choice = response["choices"][0]
                content = choice["message"]["content"]
                finish = choice.get("finish_reason")
            if finish in {"length", "max_tokens", "incomplete"}:
                raise LLMProviderError("模型输出达到长度上限，本次响应不完整。请缩小问题范围后重试。", code="PROVIDER_OUTPUT_TRUNCATED")
            if not isinstance(content, str) or not content.strip():
                raise ValueError("no content")
            # A verified gateway signature can arrive in a successful HTTP
            # completion. Do not classify arbitrary prose mentioning HTTP 429.
            gateway_error = re.fullmatch(r"(?:⚠\ufe0f?\s*)?所有模型均不可用:\s*HTTP (\d{3})", content.strip())
            if gateway_error:
                message, code = _http_failure(int(gateway_error.group(1)))
                raise LLMProviderError(message, code=code)
            parsed = _parse_llm_json(content)
            if not isinstance(parsed, dict):
                raise ValueError("not a structured object")
            return PlannerRawResponse(raw_json=parsed, raw_text=content, model=str(config.model), finish_reason=finish)
        except urllib.error.HTTPError as exc:
            status = exc.code
            if on_content is not None and status in {400, 404, 405, 422}:
                return self.complete_json(messages=messages, user_config=user_config, purpose=purpose)
            error = _http_failure(status)
            raise LLMProviderError(error[0], code=error[1], status_code=status) from None
        except (TimeoutError, socket.timeout):
            raise LLMProviderError("模型响应超时，请稍后重试或选择其他可用模型。", code="PROVIDER_TIMEOUT") from None
        except urllib.error.URLError as exc:
            timed_out = isinstance(exc.reason, (TimeoutError, socket.timeout))
            raise LLMProviderError("模型响应超时，请稍后重试。" if timed_out else "暂时无法连接模型服务，请稍后重试。", code="PROVIDER_TIMEOUT" if timed_out else "EXTERNAL_UNAVAILABLE") from None
        except InvalidProviderResponse:
            raise LLMProviderError("模型服务已响应，但未返回完整有效的结构化内容。", code="PROVIDER_INVALID_RESPONSE") from None
        except LLMProviderError:
            raise
        except ProviderStreamCancelled:
            raise
        except Exception:
            # Transport/parse exceptions may contain upstream bodies or credentials.
            # Do not include their chain in worker tracebacks or task failure logs.
            if response_received:
                raise LLMProviderError("模型服务已响应，但未返回有效的结构化内容。", code="PROVIDER_INVALID_RESPONSE") from None
            raise LLMProviderError("暂时无法连接模型服务，请稍后重试。", code="EXTERNAL_UNAVAILABLE") from None
