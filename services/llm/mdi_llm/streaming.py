"""Decode public text from bounded provider SSE, never reasoning or tool input."""

from __future__ import annotations

import codecs
import json
from typing import Any, Callable

from .http_transport import InvalidProviderResponse
from .providers import LLMProviderError


class CompletionStreamDecoder:
    def __init__(self, protocol: str, on_content: Callable[[str], None]) -> None:
        self.protocol = protocol
        self.on_content = on_content
        self.decoder = codecs.getincrementaldecoder("utf-8")("strict")
        self.pending = ""
        self.data: list[str] = []
        self.sse = False
        self.completed = False
        self.text = ""
        self.finish_reason: str | None = None
        self.usage: dict[str, Any] = {}
        self.text_blocks: set[int] = set()
        self.message_items: set[str] = set()
        self.response: dict[str, Any] | None = None

    def feed(self, chunk: bytes) -> None:
        try:
            self.pending += self.decoder.decode(chunk)
        except UnicodeDecodeError:
            raise InvalidProviderResponse("Invalid provider stream encoding") from None
        if len(self.pending) > 524_288:
            raise InvalidProviderResponse("Provider stream frame exceeded its limit")
        while "\n" in self.pending:
            line, self.pending = self.pending.split("\n", 1)
            line = line.rstrip("\r")
            if line.startswith("\ufeff"):
                line = line[1:]
            if line.startswith("data:"):
                self.sse = True
                self.data.append(line[5:].removeprefix(" "))
            elif not line and self.data:
                value = "\n".join(self.data)
                self.data.clear()
                self._event(value)

    def _append(self, text: Any) -> None:
        if not isinstance(text, str):
            raise InvalidProviderResponse("Invalid provider text delta")
        if not text:
            return
        if self.completed:
            raise InvalidProviderResponse("Provider sent text after completion")
        self.text += text
        if len(self.text) > 524_288:
            raise InvalidProviderResponse("Provider text exceeded its limit")
        self.on_content(text)

    def _event(self, data: str) -> None:
        if data == "[DONE]" and self.protocol in {"openai_chat", "openai_chat_json"}:
            self.completed = True
            self.finish_reason = self.finish_reason or "stop"
            return
        try:
            packet = json.loads(data)
        except (TypeError, ValueError):
            raise InvalidProviderResponse("Invalid provider stream event") from None
        if not isinstance(packet, dict):
            raise InvalidProviderResponse("Invalid provider stream envelope")
        if packet.get("type") is not None and not isinstance(packet["type"], str):
            raise InvalidProviderResponse("Invalid provider event type")
        if packet.get("error") or packet.get("type") in {"error", "response.failed"}:
            response = self._object(packet.get("response"))
            error = self._object(packet.get("error") or response.get("error"))
            kind = error.get("type") or error.get("code")
            code, message = {
                "rate_limit_error": ("PROVIDER_RATE_LIMITED", "模型服务当前请求过多，请稍后重试。"),
                "rate_limit_exceeded": ("PROVIDER_RATE_LIMITED", "模型服务当前请求过多，请稍后重试。"),
                "insufficient_quota": ("PROVIDER_RATE_LIMITED", "模型服务当前请求过多，请稍后重试。"),
                "authentication_error": ("PROVIDER_AUTH_FAILED", "模型服务拒绝了连接认证，请检查模型设置。"),
                "invalid_api_key": ("PROVIDER_AUTH_FAILED", "模型服务拒绝了连接认证，请检查模型设置。"),
            }.get(str(kind), ("EXTERNAL_UNAVAILABLE", "模型流式响应中断，请稍后重试。"))
            raise LLMProviderError(message, code=code)
        if self.protocol in {"openai_chat", "openai_chat_json"}:
            if isinstance(packet.get("usage"), dict):
                self.usage = packet["usage"]
            choices = packet.get("choices", [])
            if not isinstance(choices, list):
                raise InvalidProviderResponse("Invalid provider choices")
            for value in choices:
                if not isinstance(value, dict):
                    raise InvalidProviderResponse("Invalid provider choice")
                choice = self._object(value)
                index = choice.get("index", 0)
                if type(index) is not int or index < 0:
                    raise InvalidProviderResponse("Invalid provider choice index")
                if index != 0:
                    continue
                delta = self._object(choice.get("delta"))
                if delta.get("content") is not None:
                    self._append(delta["content"])
                if choice.get("finish_reason") is not None:
                    if not isinstance(choice["finish_reason"], str):
                        raise InvalidProviderResponse("Invalid provider finish reason")
                    self.finish_reason = choice["finish_reason"]
                    self.completed = True
        elif self.protocol == "openai_responses":
            kind = packet.get("type")
            if kind == "response.output_item.added":
                item = self._object(packet.get("item"))
                if item.get("type") == "message" and item.get("role") == "assistant" and isinstance(item.get("id"), str):
                    self.message_items.add(item["id"])
            elif kind == "response.output_text.delta":
                item_id = packet.get("item_id")
                if not isinstance(item_id, str):
                    raise InvalidProviderResponse("Missing provider message identity")
                if item_id in self.message_items:
                    self._append(packet.get("delta"))
            elif kind in {"response.completed", "response.incomplete"}:
                response = packet.get("response")
                if not isinstance(response, dict):
                    raise InvalidProviderResponse("Missing final provider response")
                self.response = response
                self.completed = True
        elif self.protocol == "anthropic":
            kind = packet.get("type")
            if kind == "content_block_start":
                block = self._object(packet.get("content_block"))
                index = packet.get("index")
                if type(index) is not int or index < 0:
                    raise InvalidProviderResponse("Invalid provider content index")
                if block.get("type") == "text":
                    self.text_blocks.add(index)
                    self._append(block.get("text", ""))
            elif kind == "content_block_delta":
                index = packet.get("index")
                if type(index) is not int or index < 0:
                    raise InvalidProviderResponse("Invalid provider content index")
                delta = self._object(packet.get("delta"))
                if index in self.text_blocks and delta.get("type") == "text_delta":
                    self._append(delta.get("text"))
            elif kind == "message_delta":
                reason = self._object(packet.get("delta")).get("stop_reason")
                if reason is not None and not isinstance(reason, str):
                    raise InvalidProviderResponse("Invalid provider stop reason")
                self.finish_reason = reason or self.finish_reason
                self.usage.update(self._object(packet.get("usage")))
            elif kind == "message_stop":
                self.completed = True

    def finish(self, raw: bytes) -> dict[str, Any]:
        try:
            self.decoder.decode(b"", final=True)
        except UnicodeDecodeError:
            raise InvalidProviderResponse("Incomplete provider stream encoding") from None
        if not self.sse:
            # Some compatible gateways return an ordinary JSON response even
            # when stream=true. Its content is delivered once, without replay.
            try:
                value = json.loads(raw)
            except (UnicodeDecodeError, ValueError):
                raise InvalidProviderResponse("Invalid provider response") from None
            if not isinstance(value, dict):
                raise InvalidProviderResponse("Invalid provider response")
            return value
        if not self.completed:
            raise InvalidProviderResponse("Provider stream ended before completion")
        if self.protocol == "openai_responses":
            if self.response is None:
                raise InvalidProviderResponse("Missing final provider response")
            return self.response
        if self.protocol == "anthropic":
            if not self.finish_reason:
                raise InvalidProviderResponse("Missing provider stop reason")
            return {"content": [{"type": "text", "text": self.text}], "stop_reason": self.finish_reason, "usage": self.usage}
        return {"choices": [{"message": {"content": self.text}, "finish_reason": self.finish_reason}], "usage": self.usage}

    @staticmethod
    def _object(value: Any) -> dict[str, Any]:
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise InvalidProviderResponse("Invalid provider stream object")
        return value
