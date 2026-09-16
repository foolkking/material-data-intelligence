from __future__ import annotations

from typing import Protocol

from mdi_api.domain.scientific_knowledge.contracts import (
    LiteratureProvider,
    LiteratureQuery,
    LiteratureSearchCandidate,
)


class ScholarlyProvider(Protocol):
    provider: LiteratureProvider

    def search(self, query: LiteratureQuery) -> list[LiteratureSearchCandidate]: ...

    def lookup_doi(self, doi: str) -> LiteratureSearchCandidate | None: ...


__all__ = ["ScholarlyProvider"]
