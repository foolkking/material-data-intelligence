from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from mdi_api.config import ApiSettings
from mdi_api import main


def test_lifespan_migration_guard_fails_before_recovery(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = ApiSettings(
        runtime_profile="same-stack",
        agent2_startup_recovery_enabled=True,
    )
    calls: list[str] = []

    monkeypatch.setattr(main, "load_settings", lambda: settings)
    monkeypatch.setattr(
        "mdi_api.migration_head.migration_head_guard_required",
        lambda _settings: True,
    )

    def reject_stale_database(_settings: ApiSettings) -> None:
        calls.append("migration")
        raise RuntimeError("DATABASE_MIGRATION_HEAD_MISMATCH")

    monkeypatch.setattr(
        "mdi_api.migration_head.validate_database_migration_head",
        reject_stale_database,
    )
    monkeypatch.setattr(
        "mdi_api.research_agent.recovery.run_startup_recovery",
        lambda *_args, **_kwargs: calls.append("recovery"),
    )

    with pytest.raises(RuntimeError, match="DATABASE_MIGRATION_HEAD_MISMATCH"):
        with TestClient(main.create_app()):
            pass

    assert calls == ["migration"]


def test_lifespan_recovery_failure_does_not_block_admission(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    settings = ApiSettings(
        runtime_profile="local",
        agent2_startup_recovery_enabled=True,
    )
    monkeypatch.setattr(main, "load_settings", lambda: settings)
    monkeypatch.setattr(
        "mdi_api.migration_head.migration_head_guard_required",
        lambda _settings: False,
    )

    def fail_recovery(*_args: object, **_kwargs: object) -> None:
        raise ConnectionError("simulated recovery queue outage")

    monkeypatch.setattr(
        "mdi_api.research_agent.recovery.run_startup_recovery",
        fail_recovery,
    )

    with caplog.at_level("ERROR"):
        with TestClient(main.create_app()) as client:
            response = client.get("/health")

    assert response.status_code == 200
    assert "research_startup_recovery_failed" in caplog.text


def test_each_app_lifespan_uses_its_own_settings_snapshot(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = [
        ApiSettings(
            runtime_profile="local",
            agent2_startup_recovery_enabled=True,
            agent2_startup_recovery_stale_minutes=11,
            agent2_startup_recovery_limit=21,
        ),
        ApiSettings(
            runtime_profile="local",
            agent2_startup_recovery_enabled=True,
            agent2_startup_recovery_stale_minutes=12,
            agent2_startup_recovery_limit=22,
        ),
    ]
    calls: list[tuple[ApiSettings, int, int]] = []

    monkeypatch.setattr(main, "load_settings", lambda: settings.pop(0))
    monkeypatch.setattr(
        "mdi_api.migration_head.migration_head_guard_required",
        lambda _settings: False,
    )

    def record_recovery(
        active: ApiSettings,
        *,
        stale_minutes: int,
        limit: int,
    ) -> dict[str, int]:
        calls.append((active, stale_minutes, limit))
        return {
            "productCandidates": 0,
            "qualificationRetained": 0,
            "accepted": 0,
            "attention": 0,
        }

    monkeypatch.setattr(
        "mdi_api.research_agent.recovery.run_startup_recovery",
        record_recovery,
    )
    first = main.create_app()
    second = main.create_app()

    with TestClient(first):
        pass
    with TestClient(second):
        pass

    assert [(stale, limit) for _, stale, limit in calls] == [(11, 21), (12, 22)]
    assert calls[0][0] is not calls[1][0]
