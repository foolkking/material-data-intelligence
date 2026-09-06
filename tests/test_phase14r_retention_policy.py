from __future__ import annotations

import pytest

from mdi_api.lifecycle_policy import (
    RETENTION_POLICY_SCHEMA_VERSION,
    evaluate_purge,
    retention_policy_snapshot,
)


def test_retention_policy_disables_automatic_expiry() -> None:
    policy = retention_policy_snapshot()

    assert policy == {
        "schemaVersion": RETENTION_POLICY_SCHEMA_VERSION,
        "automaticPurge": "DISABLED",
        "referencedProvenance": "PROTECTED_INDEFINITELY",
        "unreferencedTrash": "MANUAL_OWNER_PURGE",
        "manualPurge": "SERVER_ZERO_DEPENDENCY_ONLY",
        "manualPurgeRequiresZeroDependencies": True,
    }
    decision = evaluate_purge(0, mode="automatic")
    assert decision["eligible"] is False
    assert decision["reason"] == "AUTOMATIC_PURGE_DISABLED"


def test_manual_purge_requires_zero_server_derived_dependencies() -> None:
    protected = evaluate_purge(3, mode="manual")
    assert protected["eligible"] is False
    assert protected["reason"] == "PROTECTED_DEPENDENCIES_PRESENT"
    assert protected["policy"]["automaticPurge"] == "DISABLED"

    empty = evaluate_purge(0, mode="manual")
    assert empty["eligible"] is True
    assert empty["reason"] == "NO_PROTECTED_DEPENDENCIES"

    protected_entity = retention_policy_snapshot(manual_purge_supported=False)
    assert protected_entity["manualPurge"] == "NOT_SUPPORTED_FOR_ENTITY"
    assert protected_entity["unreferencedTrash"] == "PROTECTED_ENTITY_RETENTION"
    assert protected_entity["manualPurgeRequiresZeroDependencies"] is False


def test_retention_policy_rejects_invalid_dependency_counts() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        evaluate_purge(-1, mode="manual")
