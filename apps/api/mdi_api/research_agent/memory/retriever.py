from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable


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


class ResearchMemoryRetriever:
    """Deterministic lexical/entity retrieval with no vector-store dependency."""

    _TOKENS = re.compile(r"[\w.:-]+", re.UNICODE)

    def retrieve(self, *, message: str, candidates: Iterable[RetrievedMemory], limit: int = 16) -> list[RetrievedMemory]:
        query = {token.lower() for token in self._TOKENS.findall(message or "")}
        ranked: list[RetrievedMemory] = []
        for candidate in candidates:
            if not candidate.authorized:
                continue
            haystack = f"{candidate.display_label} {candidate.finding_ref or ''}".lower()
            lexical = sum(1 for token in query if token and token in haystack)
            # Pinned/explicit candidates can be represented by a negative
            # recency score supplied by the caller; identity and authorization
            # remain deterministic regardless of lexical overlap.
            ranked.append((candidate, lexical))
        ranked.sort(key=lambda item: (-item[1], item[0].score, item[0].candidate_id))
        return [item[0] for item in ranked[: max(0, min(limit, 64))]]
