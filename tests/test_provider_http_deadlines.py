from __future__ import annotations

import asyncio
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import traceback
from uuid import uuid4

import pytest

from mdi_llm.providers import LLMProviderError, PlannerUserConfig
from mdi_llm.user_connection_provider import UserConnectionProvider


@pytest.fixture
def provider_server():
    stopping = threading.Event()
    requests: list[dict] = []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def do_POST(self):
            protocol, mode, *_ = self.path.strip("/").split("/")
            requests.append({"body": json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}"),
                             "method": self.command,
                             "authorization": self.headers.get("Authorization"), "api_key": self.headers.get("x-api-key")})
            content = '{"ok":true}'
            if mode == "answer":
                content = json.dumps({"contract_version": "1.0", "action": "ANSWER", "assistant_message": "RDF 描述原子对距离的统计分布。",
                    "research_objective": None, "selected_scope_ref_keys": [], "scientific_requirements": [],
                    "reusable_result_ref_keys": [], "clarification": None, "confidence": "HIGH"})
            if protocol == "anthropic":
                envelope = {"content": [{"type": "text", "text": content}], "stop_reason": "end_turn"}
            elif protocol == "openai_responses":
                envelope = {"output": [{"type": "message", "content": [{"type": "output_text", "text": content}]}], "status": "completed"}
            else:
                envelope = {"choices": [{"message": {"content": content}, "finish_reason": "stop"}]}
            body = json.dumps(envelope).encode()
            if mode == "invalid":
                body = b"private-http-test-key: not JSON"
            elif mode == "oversized":
                body = b" " * 2_000_001
            try:
                if mode == "slow-headers":
                    self.wfile.write(b"HTTP/1.1 200 OK\r\nX-Slow: ")
                    self.wfile.flush()
                    for _ in range(80):
                        self.wfile.write(b"x")
                        self.wfile.flush()
                        if stopping.wait(0.03):
                            return
                    self.wfile.write(b"\r\nContent-Type: application/json\r\n\r\n" + body)
                    return
                self.send_response(int(mode) if mode.isdigit() else 302 if mode == "redirect" else 200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                if mode == "redirect":
                    self.send_header("Location", "/openai_chat/normal/chat/completions")
                self.end_headers()
                if mode == "slow-body":
                    for byte in body:
                        self.wfile.write(bytes([byte]))
                        self.wfile.flush()
                        if stopping.wait(0.03):
                            return
                elif mode == "truncated":
                    self.wfile.write(body[:10])
                else:
                    self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                pass

        do_GET = do_POST

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=lambda: server.serve_forever(poll_interval=0.01), daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", requests
    finally:
        stopping.set()
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def connection(base_url: str, protocol: str, mode: str, timeout: float = 1.0):
    return UserConnectionProvider(protocol=protocol), PlannerUserConfig(
        provider="personal", model="local-http-fixture", api_key="private-http-test-key",
        base_url=f"{base_url}/{protocol}/{mode}", timeout_seconds=timeout,
    )


@pytest.mark.parametrize("protocol", ["openai_chat_json", "openai_chat", "openai_responses", "anthropic"])
def test_real_http_provider_preserves_protocol_and_keeps_credentials_out_of_payload(provider_server, protocol):
    base_url, requests = provider_server
    provider, config = connection(base_url, protocol, "normal")
    response = provider.complete_json(messages=[{"role": "user", "content": "Return JSON"}], user_config=config)
    assert response.raw_json == {"ok": True}
    assert len(requests) == 1
    assert "private-http-test-key" not in json.dumps(requests[0]["body"])
    assert (requests[0]["api_key"] if protocol == "anthropic" else requests[0]["authorization"]) == (
        "private-http-test-key" if protocol == "anthropic" else "Bearer private-http-test-key"
    )


@pytest.mark.parametrize("protocol", ["openai_chat_json", "openai_chat", "openai_responses", "anthropic"])
@pytest.mark.parametrize("mode", ["slow-headers", "slow-body"])
def test_real_http_trickle_cannot_extend_the_provider_deadline(provider_server, protocol, mode):
    base_url, requests = provider_server
    provider, config = connection(base_url, protocol, mode, timeout=1.0)
    started = time.monotonic()
    with pytest.raises(LLMProviderError) as caught:
        provider.complete_json(messages=[{"role": "user", "content": "Return JSON"}], user_config=config)
    elapsed = time.monotonic() - started
    assert caught.value.code == "PROVIDER_TIMEOUT"
    assert elapsed < 2.0, "A stream of partial bytes must not keep the provider call alive"
    assert len(requests) == 1
    assert "private-http-test-key" not in "".join(traceback.format_exception(caught.value))


@pytest.mark.parametrize("mode, code", [
    ("401", "PROVIDER_AUTH_FAILED"), ("429", "PROVIDER_RATE_LIMITED"), ("503", "EXTERNAL_UNAVAILABLE"),
    ("invalid", "PROVIDER_INVALID_RESPONSE"), ("truncated", "PROVIDER_INVALID_RESPONSE"),
    ("oversized", "PROVIDER_INVALID_RESPONSE"), ("redirect", "EXTERNAL_UNAVAILABLE"),
])
def test_real_http_failures_are_safe_and_do_not_replay_or_follow_redirects(provider_server, mode, code):
    base_url, requests = provider_server
    provider, config = connection(base_url, "openai_chat_json", mode)
    with pytest.raises(LLMProviderError) as caught:
        provider.complete_json(messages=[{"role": "user", "content": "Return JSON"}], user_config=config)
    assert caught.value.code == code
    assert len(requests) == 1
    assert "private-http-test-key" not in "".join(traceback.format_exception(caught.value))


def test_synchronous_provider_can_still_be_called_from_an_existing_event_loop(provider_server):
    base_url, _requests = provider_server
    provider, config = connection(base_url, "openai_chat_json", "normal")

    async def invoke():
        return provider.complete_json(messages=[{"role": "user", "content": "Return JSON"}], user_config=config)

    assert asyncio.run(invoke()).raw_json == {"ok": True}


@pytest.mark.parametrize("mode", ["slow-headers", "slow-body"])
def test_model_directory_get_cannot_extend_the_http_deadline(provider_server, mode):
    import urllib.request
    from mdi_llm.http_transport import read_provider_response

    base_url, requests = provider_server
    request = urllib.request.Request(f"{base_url}/openai_chat_json/{mode}/models", headers={"Authorization": "Bearer private-http-test-key"})
    started = time.monotonic()
    with pytest.raises(TimeoutError):
        read_provider_response(request, timeout=1.0, byte_limit=2_000_000)
    assert time.monotonic() - started < 2.0
    assert len(requests) == 1 and requests[0]["method"] == "GET"


@pytest.mark.parametrize("kind, code", [("deepseek", "DEEPSEEK_TIMEOUT"), ("compatible", "LLM_TIMEOUT")])
@pytest.mark.parametrize("mode", ["slow-headers", "slow-body"])
def test_platform_http_transports_share_the_absolute_deadline(provider_server, monkeypatch, kind, code, mode):
    from mdi_llm import providers

    base_url, requests = provider_server
    endpoint = f"{base_url}/openai_chat_json/{mode}"
    arguments = {"base_url": endpoint, "api_key": "private-http-test-key", "model": "local-http-fixture",
                 "messages": [{"role": "user", "content": "Return JSON"}], "max_tokens": 32, "timeout_seconds": 1.0}
    if kind == "compatible":
        # Endpoint authorization has separate tests; this transport fixture
        # allows only its own ephemeral listener and never changes app settings.
        def allow_fixture(value):
            assert value == endpoint
            return value
        monkeypatch.setattr(providers, "_validated_llm_base_url", allow_fixture)
        arguments["temperature"] = 0
    started = time.monotonic()
    with pytest.raises(LLMProviderError) as caught:
        (providers._post_deepseek_completion if kind == "deepseek" else providers._post_chat_completion)(**arguments)
    assert caught.value.code == code
    assert time.monotonic() - started < 2.0
    assert len(requests) == 1


@pytest.mark.parametrize("mode, turn_code, provider_calls", [
    ("401", "ORCHESTRATOR_PROVIDER_AUTH_FAILED", 1),
    ("429", "ORCHESTRATOR_PROVIDER_RATE_LIMITED", 1),
    ("503", "ORCHESTRATOR_PROVIDER_UNAVAILABLE", 1),
    ("invalid", "ORCHESTRATOR_INVALID_OUTPUT", 2),
    ("slow-body", "ORCHESTRATOR_TIMEOUT", 1),
])
def test_real_http_failure_finishes_worker_entry_and_retains_the_exact_turn(provider_server, monkeypatch, tmp_path, mode, turn_code, provider_calls):
    from mdi_api import user_models
    from mdi_api.application.research.worker_entrypoints import process_queued_turn
    from mdi_api.research_agent.llm.structured_client import DeepSeekStructuredLLMClient
    from tests.test_agent2_processor import foundation, processor, receive, structure

    base_url, requests = provider_server
    engine, owner, factory, objects, turns = foundation(tmp_path)
    ref = structure(objects)
    question = "保留这个精确结构版本的研究问题"
    turn = receive(turns, owner, question, refs=[ref])
    provider, config = connection(base_url, "openai_chat_json", mode, timeout=1.0)
    monkeypatch.setattr(user_models, "selection_for_turn", lambda _turn: {"user_id": owner.id, "provider": "personal", "model": config.model})
    monkeypatch.setattr(user_models, "resolve_user_selection", lambda *_args: (provider, config))
    handler = processor(factory, DeepSeekStructuredLLMClient(turn_id=str(turn.turn_id)))
    started = time.monotonic()
    try:
        with pytest.raises(Exception):
            process_queued_turn(str(turn.turn_id), processor=handler)
        assert time.monotonic() - started < 3.0
        with factory.session() as session:
            stored = session.agent2.research_turns.get(turn.turn_id)
            events = session.agent2.research_turn_events.list_for_turn(turn.turn_id)
            snapshot = session.agent2.research_context_snapshots.get_for_turn(turn.turn_id)
            assert session.agent2.research_turns.get_message(stored["user_message_id"])["content_summary"] == question
        assert stored["status"] == "FAILED" and stored["error_code"] == turn_code
        assert stored["completed_at"] is not None and stored["job_id"] is None
        assert stored["assistant_final_message_id"] is None
        assert str(ref.version_id) in json.dumps(snapshot, default=str)
        assert sum(row["event_type"] == "TURN_FAILED" for row in events) == 1
        assert "private-http-test-key" not in json.dumps([stored, events, snapshot], default=str)
        assert len(requests) == provider_calls
        assert process_queued_turn(str(turn.turn_id), processor=handler).outcome == "NOOP"
        assert len(requests) == provider_calls
    finally:
        engine.dispose()


def _process_http_turn(database_path: str, turn_id: str, base_url: str, mode: str):
    """Bind a loopback fixture only inside this isolated queue worker."""
    from sqlalchemy import create_engine
    from mdi_api import user_models
    from mdi_api.application.research.worker_entrypoints import process_queued_turn
    from mdi_api.research_agent.llm.structured_client import DeepSeekStructuredLLMClient
    from mdi_api.research_agent.orchestration.processor import AgentTurnProcessor
    from mdi_api.research_agent.registry_validation import build_default_agent2_registries
    from mdi_api.unit_of_work import RepositoryFactory

    factory = RepositoryFactory(create_engine(f"sqlite:///{Path(database_path).as_posix()}", connect_args={"check_same_thread": False}))
    provider, config = connection(base_url, "openai_chat_json", mode, timeout=1.0)
    original_selection, original_resolution = user_models.selection_for_turn, user_models.resolve_user_selection

    def selected(requested_turn):
        assert requested_turn == turn_id
        return {"user_id": "owner", "provider": "personal", "model": config.model}

    user_models.selection_for_turn = selected
    user_models.resolve_user_selection = lambda *_args: (provider, config)
    try:
        handler = AgentTurnProcessor(repository_factory=factory, registries=build_default_agent2_registries(),
            llm_client=DeepSeekStructuredLLMClient(turn_id=turn_id))
        return process_queued_turn(turn_id, processor=handler).status
    finally:
        user_models.selection_for_turn, user_models.resolve_user_selection = original_selection, original_resolution
        factory.engine.dispose()


@pytest.mark.integration
def test_real_rq_worker_processes_the_next_turn_after_http_deadline(provider_server, tmp_path):
    redis_url = os.getenv("MDI_TEST_REDIS_URL")
    if not redis_url:
        pytest.skip("Explicit MDI_TEST_REDIS_URL required; uses an isolated queue and database")
    from redis import Redis
    from rq import Queue, Worker
    from tests.test_agent2_processor import foundation, receive, structure

    base_url, requests = provider_server
    engine, owner, factory, objects, turns = foundation(tmp_path)
    source = structure(objects)
    failed = receive(turns, owner, "保留超时的研究问题", refs=[source])
    following = receive(turns, owner, "什么是 RDF？", refs=[source])
    database_path = str(engine.url.database)
    connection = Redis.from_url(redis_url)
    suffix = uuid4().hex
    queue = Queue(f"mdi-test-http-deadline-{suffix}", connection=connection)
    worker_name = f"mdi-test-http-deadline-{suffix}"
    receipts = [queue.enqueue(_process_http_turn, database_path, str(turn.turn_id), base_url, mode, job_timeout=30)
        for turn, mode in [(failed, "slow-body"), (following, "answer"), (failed, "slow-body")]]
    command = "from redis import Redis; from rq import SimpleWorker; import sys; SimpleWorker([sys.argv[2]],connection=Redis.from_url(sys.argv[1]),name=sys.argv[3]).work(burst=True,logging_level='CRITICAL')"
    try:
        child = subprocess.run([sys.executable, "-c", command, redis_url, queue.name, worker_name],
            env={**os.environ, "PYTHONPATH": os.pathsep.join(path for path in sys.path if path)},
            cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True, timeout=30)
        assert child.returncode == 0, child.stderr
        assert [receipt.get_status(refresh=True).value for receipt in receipts] == ["failed", "finished", "finished"]
        assert [receipts[1].return_value(), receipts[2].return_value()] == ["ANSWERED", "FAILED"]
        with factory.session() as session:
            original = session.agent2.research_turns.get(failed.turn_id)
            next_turn = session.agent2.research_turns.get(following.turn_id)
            events = session.agent2.research_turn_events.list_for_turn(failed.turn_id)
            assert session.agent2.research_turns.get_message(original["user_message_id"])["content_summary"] == "保留超时的研究问题"
        assert original["status"] == "FAILED" and original["error_code"] == "ORCHESTRATOR_TIMEOUT"
        assert next_turn["status"] == "ANSWERED" and next_turn["assistant_final_message_id"] is not None
        assert original["job_id"] is None and next_turn["job_id"] is None
        assert sum(event["event_type"] == "TURN_FAILED" for event in events) == 1
        assert len(requests) == 2
        assert "private-http-test-key" not in "\n".join(receipt.latest_result().exc_string or "" for receipt in receipts)
    finally:
        for receipt in receipts:
            queue.remove(receipt.id)
            receipt.delete()
        worker = Worker.find_by_key(f"rq:worker:{worker_name}", connection=connection)
        if worker:
            worker.register_death()
        connection.srem("rq:queues", queue.key)
        connection.close()
        engine.dispose()
