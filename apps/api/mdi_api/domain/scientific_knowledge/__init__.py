"""Scientific literature identity and evidence contracts."""

from .contracts import (
    LiteratureEvidence,
    LiteratureEvidenceScope,
    LiteratureProvider,
    LiteraturePublicationStatus,
    LiteratureQuery,
    LiteratureSearchCandidate,
    LiteratureSnapshot,
    LiteratureWork,
    normalize_doi,
)

__all__ = [
    "LiteratureEvidence",
    "LiteratureEvidenceScope",
    "LiteratureProvider",
    "LiteraturePublicationStatus",
    "LiteratureQuery",
    "LiteratureSearchCandidate",
    "LiteratureSnapshot",
    "LiteratureWork",
    "normalize_doi",
]
