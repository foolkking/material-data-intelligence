from __future__ import annotations

from mdi_llm import (
    DeepSeekProvider,
    LLMProviderError,
    find_sensitive_sentinels,
    redact_sensitive_payload,
    redact_sensitive_text,
)


def test_sensitive_payload_redaction_preserves_scientific_evidence() -> None:
    payload = {
        "facts": [
            {
                "sample_id": "mat-2",
                "band_gap": 2.41,
                "unit": "eV",
                "evidence_refs": ["ev-mat-2"],
                "source_object_version": "622ef3d7-301c-420a-aa75-7dda551cf7ef",
            }
        ],
        "api_key": "sk-live-sentinel-value-123456",
        "redis_url": "redis://:redis-secret@localhost:6379/0",
        "minio_endpoint": "http://minio:9000/project/artifact.json",
        "local_path": r"C:\Users\researcher\private\artifact.json",
    }

    assert {
        "credential_field",
        "credential_value",
        "storage_authority_field",
        "storage_url",
        "absolute_path",
    } == set(find_sensitive_sentinels(payload))

    safe = redact_sensitive_payload(payload)

    assert safe["facts"] == payload["facts"]
    assert find_sensitive_sentinels(safe) == ()
    assert safe["api_key"] == "***REDACTED***"
    assert safe["redis_url"] == "***REDACTED***"
    assert safe["minio_endpoint"] == "***REDACTED***"
    assert safe["local_path"] == "***REDACTED_PATH***"


def test_sensitive_text_redacts_embedded_storage_and_path_sentinels() -> None:
    text = (
        "provider failed: token=secret-token-value; "
        "redis://:pw@redis.internal:6379/0; "
        "MinIO endpoint: http://127.0.0.1:9000; "
        "C:/workspace/materials/raw.cif"
    )

    safe = redact_sensitive_text(text)

    assert find_sensitive_sentinels(safe) == ()
    assert "secret-token-value" not in safe
    assert "redis.internal" not in safe
    assert "127.0.0.1:9000" not in safe
    assert "C:/workspace" not in safe


def test_scientific_identifiers_and_units_are_not_sentinels() -> None:
    payload = {
        "result_id": "result-123",
        "sample_id": "mat-2",
        "value": 3.7,
        "unit": "angstrom",
        "evidence_refs": ["toolcall-1", "artifact-1"],
    }

    assert find_sensitive_sentinels(payload) == ()
    assert redact_sensitive_payload(payload) == payload


def test_provider_transport_and_error_summary_receive_sanitized_text() -> None:
    captured: dict[str, object] = {}

    def transport(**kwargs: object) -> dict[str, object]:
        captured.update(kwargs)
        return {
            "choices": [
                {
                    "message": {"content": '{"status":"ok"}'},
                    "finish_reason": "stop",
                }
            ]
        }

    DeepSeekProvider(transport=transport).complete_json(
        messages=[
            {
                "role": "user",
                "content": (
                    "Inspect C:/Users/researcher/private/raw.cif using "
                    "redis://:pw@redis.internal:6379/0 and "
                    "http://minio:9000/project/artifact.json"
                ),
            }
        ],
        purpose="PROVIDER_CONNECTION_TEST",
    )

    assert find_sensitive_sentinels(captured["messages"]) == ()
    assert "raw.cif" not in str(captured["messages"])
    assert "redis.internal" not in str(captured["messages"])
    assert "minio:9000" not in str(captured["messages"])

    error = LLMProviderError(
        "failure at /var/lib/mdi/private.json using token=runtime-secret"
    )
    assert find_sensitive_sentinels(error.safe_message) == ()
    assert "runtime-secret" not in error.safe_message
    assert "/var/lib/mdi" not in error.safe_message
