"""Durable execution-lease contracts.

The Job row is the single ownership authority.  Redis delivery and worker
heartbeats are deliberately excluded from this contract.
"""

from __future__ import annotations

from dataclasses import dataclass


class ExecutionLeaseError(RuntimeError):
    """Base class for durable ownership failures."""


class ExecutionLeaseUnavailable(ExecutionLeaseError):
    """The Job is not currently claimable."""


class ExecutionLeaseLost(ExecutionLeaseError):
    """The caller is no longer the current durable execution owner."""


@dataclass(frozen=True)
class ExecutionLease:
    job_id: str
    owner: str
    attempt: int
    claimed_at: str
    renewed_at: str
    expires_at: str
    reclaimed: bool


__all__ = [
    "ExecutionLease",
    "ExecutionLeaseError",
    "ExecutionLeaseLost",
    "ExecutionLeaseUnavailable",
]
