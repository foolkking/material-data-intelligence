from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading
import time
import urllib.error

import pytest

from mdi_llm.http_transport import InvalidProviderResponse, ProviderStreamCancelled
from mdi_llm.providers import LLMProviderError, PlannerUserConfig
from mdi_llm.streaming import CompletionStreamDecoder
from mdi_llm.user_connection_provider import UserConnectionProvider


def event(value) -> bytes:
    return b"data: " + (value.encode() if isinstance(value, str) else json.dumps(value, ensure_ascii=False).encode()) + b"\r\n\r\n"


def completion_events(protocol: str, content: str) -> list[bytes]:
    pieces = [content[:13], content[13:]]
    if protocol in {"openai_chat", "openai_chat_json"}:
        return [event({"choices": [{"delta": {"reasoning_content": "hidden reasoning"}}]})] + [
            event({"choices": [{"index": 0, "delta": {"content": text}}]}) for text in pieces
        ] + [event({"choices": [{"delta": {}, "finish_reason": "stop"}]}), event("[DONE]")]
    if protocol == "openai_responses":
        return [event({"type": "response.reasoning_text.delta", "delta": "hidden reasoning"}),
                event({"type": "response.output_item.added", "item": {"id": "msg1", "type": "message", "role": "assistant"}})] + [
            event({"type": "response.output_text.delta", "item_id": "msg1", "delta": text}) for text in pieces
        ] + [event({"type": "response.completed", "response": {"status": "completed", "output": [{"type": "message", "content": [{"type": "output_text", "text": content}]}]}})]
    return [event({"type": "content_block_start", "index": 0, "content_block": {"type": "thinking"}}),
            event({"type": "content_block_delta", "index": 0, "delta": {"type": "thinking_delta", "thinking": "hidden reasoning"}}),
            event({"type": "content_block_start", "index": 1, "content_block": {"type": "text", "text": ""}})] + [
        event({"type": "content_block_delta", "index": 1, "delta": {"type": "text_delta", "text": text}}) for text in pieces
    ] + [event({"type": "message_delta", "delta": {"stop_reason": "end_turn"}}), event({"type": "message_stop"})]


@pytest.mark.parametrize("protocol", ["openai_chat_json", "openai_chat", "openai_responses", "anthropic"])
def test_streams_public_text_across_utf8_boundaries_without_reasoning_or_tools(monkeypatch, protocol):
    content = json.dumps({"action": "ANSWER", "assistant_message": "**材料**：0.043419 Å⁻³ 🧪"}, ensure_ascii=False)
    body = b"".join(completion_events(protocol, content))
    seen = []
    requests = []

    def transport(request, **kwargs):
        requests.append(json.loads(request.data))
        for byte in body:
            kwargs["on_chunk"](bytes([byte]))
        return body

    monkeypatch.setattr("mdi_llm.user_connection_provider.read_provider_response", transport)
    provider = UserConnectionProvider(protocol=protocol)
    result = provider.complete_json(messages=[{"role": "user", "content": "JSON"}], user_config=PlannerUserConfig(
        provider="personal", model="fixture", api_key="test-private-key", base_url="https://example.invalid",
    ), on_content=seen.append)
    assert result.raw_json == json.loads(content)
    assert "".join(seen) == content and len(seen) == 2
    assert "hidden reasoning" not in "".join(seen)
    assert requests[0]["stream"] is True
    assert "test-private-key" not in json.dumps(requests)


def test_stream_eof_without_completion_is_never_a_success():
    decoder = CompletionStreamDecoder("openai_chat", lambda _text: None)
    raw = event({"choices": [{"delta": {"content": '{"ok":true}'}}]})
    decoder.feed(raw)
    with pytest.raises(InvalidProviderResponse):
        decoder.finish(raw)


def test_stream_error_uses_machine_code_and_never_echoes_private_provider_text():
    decoder = CompletionStreamDecoder("anthropic", lambda _text: None)
    with pytest.raises(LLMProviderError) as caught:
        decoder.feed(event({"type": "error", "error": {"type": "rate_limit_error", "message": "private key and provider internals"}}))
    assert caught.value.code == "PROVIDER_RATE_LIMITED"
    assert "private" not in str(caught.value)


def test_plain_json_gateway_is_not_replayed_as_a_fake_stream():
    seen = []
    decoder = CompletionStreamDecoder("openai_chat", seen.append)
    raw = b'{"choices":[{"message":{"content":"{\\"ok\\":true}"},"finish_reason":"stop"}]}'
    decoder.feed(raw)
    assert decoder.finish(raw)["choices"][0]["finish_reason"] == "stop"
    assert seen == []


@pytest.mark.parametrize("protocol,packet", [
    ("openai_chat", {"choices": "private malformed body"}),
    ("openai_chat", {"choices": ["private malformed choice"]}),
    ("openai_chat", {"choices": [{"delta": []}]}),
    ("openai_chat", {"choices": [{"delta": {"content": ["private"]}}]}),
    ("openai_chat", {"choices": [{"finish_reason": {"private": True}}]}),
    ("openai_responses", {"type": "response.output_item.added", "item": ["private"]}),
    ("openai_responses", {"type": "response.output_text.delta", "item_id": ["private"], "delta": "bad"}),
    ("openai_responses", {"type": "response.failed", "response": ["private"]}),
    ("anthropic", {"type": ["private"]}),
    ("anthropic", {"type": "content_block_start", "index": True, "content_block": {"type": "text"}}),
    ("anthropic", {"type": "content_block_delta", "index": ["private"], "delta": {}}),
    ("anthropic", {"type": "message_delta", "usage": "private"}),
])
def test_malformed_stream_frames_fail_with_a_safe_invalid_response(protocol, packet):
    decoder = CompletionStreamDecoder(protocol, lambda _text: None)
    with pytest.raises(InvalidProviderResponse) as caught:
        decoder.feed(event(packet))
    assert "private" not in str(caught.value)


@pytest.mark.parametrize("raw", [b'data: \xff\n\n', b'data: \xe4'])
def test_broken_utf8_is_an_invalid_provider_response(monkeypatch, raw):
    def transport(_request, **kwargs):
        kwargs["on_chunk"](raw)
        return raw

    monkeypatch.setattr("mdi_llm.user_connection_provider.read_provider_response", transport)
    with pytest.raises(LLMProviderError) as caught:
        UserConnectionProvider(protocol="openai_chat").complete_json(
            messages=[], user_config=PlannerUserConfig(provider="personal", model="fixture", base_url="https://example.invalid"),
            on_content=lambda _text: None,
        )
    assert caught.value.code == "PROVIDER_INVALID_RESPONSE"


def test_gateway_rejecting_stream_falls_back_once_without_replaying_text(monkeypatch):
    requests = []
    seen = []

    def transport(request, **kwargs):
        payload = json.loads(request.data)
        requests.append(payload)
        if payload.get("stream"):
            raise urllib.error.HTTPError("", 400, "private upstream body", {}, None)
        return b'{"choices":[{"message":{"content":"{\\"ok\\":true}"},"finish_reason":"stop"}]}'

    monkeypatch.setattr("mdi_llm.user_connection_provider.read_provider_response", transport)
    result = UserConnectionProvider(protocol="openai_chat").complete_json(
        messages=[], user_config=PlannerUserConfig(provider="personal", model="fixture", base_url="https://example.invalid"), on_content=seen.append,
    )
    assert result.raw_json == {"ok": True} and len(requests) == 2
    assert requests[0]["stream"] is True and "stream" not in requests[1] and not seen


@pytest.fixture
def streaming_server():
    observed = threading.Event()
    stopping = threading.Event()
    state = {"observed_before_finish": False, "requests": 0, "stall": False}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def do_POST(self):
            state["requests"] += 1
            self.rfile.read(int(self.headers["Content-Length"]))
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.end_headers()
            frames = completion_events("openai_chat", '{"ok":true}')
            try:
                self.wfile.write(b"".join(frames[:2]))
                self.wfile.flush()
                state["observed_before_finish"] = observed.wait(1)
                if state["stall"]:
                    while not stopping.wait(0.03):
                        self.wfile.write(b": heartbeat\n\n")
                        self.wfile.flush()
                else:
                    self.wfile.write(b"".join(frames[2:]))
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=lambda: server.serve_forever(poll_interval=0.01), daemon=True)
    thread.start()
    config = PlannerUserConfig(provider="personal", model="fixture", api_key="test-key", base_url=f"http://127.0.0.1:{server.server_port}", timeout_seconds=1.5)
    try:
        yield config, observed, state
    finally:
        stopping.set()
        observed.set()
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_real_http_stream_delivers_text_while_provider_is_still_generating(streaming_server):
    config, observed, state = streaming_server
    result = UserConnectionProvider(protocol="openai_chat").complete_json(
        messages=[{"role": "user", "content": "JSON"}], user_config=config, on_content=lambda _text: observed.set(),
    )
    assert state["observed_before_finish"] is True
    assert result.raw_json == {"ok": True} and state["requests"] == 1


def test_real_stream_heartbeats_cannot_extend_the_complete_deadline(streaming_server):
    config, observed, state = streaming_server
    state["stall"] = True
    started = time.monotonic()
    with pytest.raises(LLMProviderError) as caught:
        UserConnectionProvider(protocol="openai_chat").complete_json(
            messages=[{"role": "user", "content": "JSON"}], user_config=config, on_content=lambda _text: observed.set(),
        )
    assert caught.value.code == "PROVIDER_TIMEOUT"
    assert time.monotonic() - started < 2.5 and state["requests"] == 1


def test_cancel_callback_closes_provider_without_retry(streaming_server):
    config, _observed, state = streaming_server

    def cancel(_text):
        raise ProviderStreamCancelled()

    with pytest.raises(ProviderStreamCancelled):
        UserConnectionProvider(protocol="openai_chat").complete_json(
            messages=[{"role": "user", "content": "JSON"}], user_config=config, on_content=cancel,
        )
    assert state["requests"] == 1
