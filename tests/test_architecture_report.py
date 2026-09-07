from __future__ import annotations

from scripts.architecture_report import build_architecture_report


def test_architecture_report_preserves_frozen_worker_and_queue_contracts() -> None:
    report = build_architecture_report()

    assert report["status"] == "PASS"
    assert report["queueIdentity"]["status"] == "PASS"
    assert report["queueIdentity"]["queueNames"] == [
        "mdi-agent-turns",
        "mdi-agent-plans",
        "mdi-jobs",
        "mdi-agent-results",
        "mdi-agent-interpretations",
        "mdi-agent-reports",
    ]
    assert len(report["handlerResolution"]) == 6
    assert all(item["status"] == "PASS" for item in report["handlerResolution"])


def test_architecture_report_is_deterministic_and_has_no_forbidden_edges() -> None:
    first = build_architecture_report()
    second = build_architecture_report()

    assert first == second
    assert first["forbiddenEdges"] == []
    assert first["compatibilityDirection"]["canonicalToCompatibility"] == []
    assert first["toolAdapterIdentity"]["status"] == "PASS"


def test_architecture_report_includes_frontend_dynamic_and_launcher_inventory() -> None:
    report = build_architecture_report()

    dynamic_kinds = {item["kind"] for item in report["dynamicReferences"]}
    assert "next-dynamic-import" in dynamic_kinds
    assert "worker-url" in dynamic_kinds
    assert "worker" in report["launcherReferences"]
    assert "api" in report["launcherReferences"]

