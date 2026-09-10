from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable

from mdi_api.research_agent.context.provenance import (
    ContextAuthorityClass,
    ContextFreshness,
)

@dataclass(frozen=True)
class RetrievedMemory:
    """A bounded, authorized memory candidate; payloads remain references."""

    candidate_id: str
    source: str
    display_label: str
    result_id: str | None = None
    turn_id: str | None = None
    finding_ref: str | None = None
    exact_version: str | None = None
    stale: bool = False
    authorized: bool = True
    score: tuple[int, int, int] = (0, 0, 0)
    project_id: str | None = None
    source_ref: str | None = None
    authority_class: str = ContextAuthorityClass.MEMORY.value
    freshness: str = ContextFreshness.CURRENT.value
    epistemic_status: str = "OBSERVED"
    pinned: bool = False
    provenance_refs: tuple[str, ...] = ()


class ResearchMemoryRetriever:
    """Deterministic lexical/entity retrieval with no vector-store dependency."""

    _TOKENS = re.compile(r"[\w.:-]+", re.UNICODE)

    def retrieve(
        self,
        *,
        message: str,
        candidates: Iterable[RetrievedMemory],
        limit: int = 16,
        project_id: str | None = None,
    ) -> list[RetrievedMemory]:
        query = {token.lower() for token in self._TOKENS.findall(message or "")}
        ranked: list[RetrievedMemory] = []
        for candidate in candidates:
            if not candidate.authorized:
                continue
            if project_id is not None and candidate.project_id not in {None, project_id}:
                continue
            if candidate.freshness in {
                ContextFreshness.INVALIDATED.value,
                ContextFreshness.SOURCE_MISSING.value,
            }:
                continue
            haystack = f"{candidate.display_label} {candidate.finding_ref or ''}".lower()
            lexical = sum(1 for token in query if token and token in haystack)
            # Pinned/explicit candidates can be represented by a negative
            # recency score supplied by the caller; identity and authorization
            # remain deterministic regardless of lexical overlap.
            freshness_penalty = 1 if candidate.freshness in {
                ContextFreshness.STALE.value,
                ContextFreshness.UNKNOWN.value,
            } else 0
            authority_penalty = 0 if candidate.authority_class != ContextAuthorityClass.MEMORY.value else 1
            ranked.append((candidate, lexical, freshness_penalty, authority_penalty))
        ranked.sort(
            key=lambda item: (
                -item[1],
                item[2],
                item[3],
                0 if item[0].pinned else 1,
                item[0].score,
                item[0].candidate_id,
            ),
        )
        return [item[0] for item in ranked[: max(0, min(limit, 64))]]
