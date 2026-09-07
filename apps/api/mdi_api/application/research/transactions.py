from __future__ import annotations

from contextvars import ContextVar, Token


_TRANSACTION_DEPTH: ContextVar[int] = ContextVar("mdi_transaction_depth", default=0)


def transaction_active() -> bool:
    """Return whether the current execution context owns a repository transaction."""

    return _TRANSACTION_DEPTH.get() > 0


def enter_transaction() -> Token[int]:
    """Record an infrastructure-owned transaction in the current execution context."""

    return _TRANSACTION_DEPTH.set(_TRANSACTION_DEPTH.get() + 1)


def exit_transaction(token: Token[int]) -> None:
    """Restore the transaction state captured before infrastructure entered."""

    _TRANSACTION_DEPTH.reset(token)


__all__ = ["transaction_active"]
