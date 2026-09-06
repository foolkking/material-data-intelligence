"""Auditable lifecycle retention and purge policy.

Scientific provenance is intentionally more durable than user-facing
visibility.  The product currently has no automatic trash expiry worker, so
automatic purge is explicitly disabled.  Manual purge is only eligible after
the server has confirmed that no protected dependency remains.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


RETENTION_POLICY_SCHEMA_VERSION = "phase14r-retention/1.0"
PurgeMode = Literal["automatic", "manual"]


@dataclass(frozen=True)
class RetentionPolicy:
    """The immutable product policy used by lifecycle endpoints."""

    automatic_purge_enabled: bool = False
    referenced_provenance: str = "PROTECTED_INDEFINITELY"
    unreferenced_trash: str = "MANUAL_OWNER_PURGE"
    manual_purge_requires_zero_dependencies: bool = True

    def as_dict(self, *, manual_purge_supported: bool = True) -> dict[str, Any]:
        return {
            "schemaVersion": RETENTION_POLICY_SCHEMA_VERSION,
            "automaticPurge": "ENABLED" if self.automatic_purge_enabled else "DISABLED",
            "referencedProvenance": self.referenced_provenance,
            "unreferencedTrash": (
                self.unreferenced_trash
                if manual_purge_supported
                else "PROTECTED_ENTITY_RETENTION"
            ),
            "manualPurge": (
                "SERVER_ZERO_DEPENDENCY_ONLY"
                if manual_purge_supported
                else "NOT_SUPPORTED_FOR_ENTITY"
            ),
            "manualPurgeRequiresZeroDependencies": (
                self.manual_purge_requires_zero_dependencies
                if manual_purge_supported
                else False
            ),
        }


DEFAULT_RETENTION_POLICY = RetentionPolicy()


def retention_policy_snapshot(
    *,
    manual_purge_supported: bool = True,
) -> dict[str, Any]:
    """Return a detached, API-safe representation of the current policy."""

    return DEFAULT_RETENTION_POLICY.as_dict(
        manual_purge_supported=manual_purge_supported
    )


def evaluate_purge(
    dependency_count: int,
    *,
    mode: PurgeMode,
) -> dict[str, Any]:
    """Evaluate a purge request without mutating any lifecycle state.

    ``automatic`` is always fail-closed because no scheduler is authorized to
    expire trash in the current product.  ``manual`` remains available only
    for content with zero server-derived dependencies.
    """

    if dependency_count < 0:
        raise ValueError("dependency_count must be non-negative")

    if mode == "automatic":
        return {
            "eligible": False,
            "reason": "AUTOMATIC_PURGE_DISABLED",
            "dependencyCount": dependency_count,
            "policy": retention_policy_snapshot(),
        }

    if dependency_count:
        return {
            "eligible": False,
            "reason": "PROTECTED_DEPENDENCIES_PRESENT",
            "dependencyCount": dependency_count,
            "policy": retention_policy_snapshot(),
        }

    return {
        "eligible": True,
        "reason": "NO_PROTECTED_DEPENDENCIES",
        "dependencyCount": 0,
        "policy": retention_policy_snapshot(),
    }
