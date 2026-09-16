from __future__ import annotations

import hashlib
import json
import time
from datetime import date, datetime, timezone
from typing import Any, Mapping
from urllib.parse import quote
from uuid import uuid4

import httpx

from mdi_api.application.scientific_knowledge.service import candidate_from_snapshot
from mdi_api.domain.scientific_knowledge.contracts import (
    LiteratureAccessStatus,
    LiteratureProvider,
    LiteratureProviderRole,
    LiteraturePublicationStatus,
    LiteratureQuery,
    LiteratureRelation,
    LiteratureRelationType,
    LiteratureSearchCandidate,
    LiteratureSnapshot,
    normalize_doi,
)


OPENALEX_HOST = "api.openalex.org"
CROSSREF_HOST = "api.crossref.org"
_MAX_RESPONSE_BYTES = 4 * 1024 * 1024
_TIMEOUT_SECONDS = 12.0
_MAX_PROVIDER_ATTEMPTS = 2
_MAX_RETRY_DELAY_SECONDS = 5.0


class ScholarlyProviderError(RuntimeError):
    pass


def _raw_hash(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def _as_date(value: Any) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def _as_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _abstract_from_inverted_index(value: Any) -> str | None:
    if not isinstance(value, Mapping):
        return None
    positioned: list[tuple[int, str]] = []
    for word, positions in value.items():
        if not isinstance(word, str) or not isinstance(positions, list):
            continue
        for position in positions:
            if isinstance(position, int) and position >= 0:
                positioned.append((position, word))
    if not positioned:
        return None
    return " ".join(word for _position, word in sorted(positioned))


def _safe_source_url(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    candidate = value.strip()
    if not candidate.startswith("https://"):
        return None
    return candidate[:2000]


class _HttpProvider:
    provider: LiteratureProvider
    allowed_host: str

    def __init__(
        self,
        *,
        transport: httpx.BaseTransport | None = None,
        user_agent: str = "MaterialDataIntelligence/1.0 (scholarly metadata)",
    ) -> None:
        self._client = httpx.Client(
            transport=transport,
            timeout=_TIMEOUT_SECONDS,
            follow_redirects=False,
            headers={"Accept": "application/json", "User-Agent": user_agent},
        )

    def _get(self, url: str, *, params: Mapping[str, str | int] | None = None) -> Any:
        parsed = httpx.URL(url)
        if parsed.scheme != "https" or parsed.host != self.allowed_host:
            raise ScholarlyProviderError("provider URL is outside the allowlist")
        response = None
        for attempt in range(_MAX_PROVIDER_ATTEMPTS):
            response = self._client.get(url, params=params)
            retryable = response.status_code in {429, 502, 503, 504}
            if not retryable or attempt == _MAX_PROVIDER_ATTEMPTS - 1:
                break
            retry_after = response.headers.get("retry-after")
            try:
                delay = float(retry_after) if retry_after else 1.0
            except ValueError:
                delay = 1.0
            time.sleep(max(0.0, min(delay, _MAX_RETRY_DELAY_SECONDS)))
        assert response is not None
        if 300 <= response.status_code < 400:
            raise ScholarlyProviderError("provider redirects are not followed")
        if response.status_code == 429:
            raise ScholarlyProviderError("provider rate limited")
        response.raise_for_status()
        content_type = response.headers.get("content-type", "").lower()
        if "application/json" not in content_type:
            raise ScholarlyProviderError("provider returned unsupported content type")
        if len(response.content) > _MAX_RESPONSE_BYTES:
            raise ScholarlyProviderError("provider response exceeded size limit")
        payload = response.json()
        if not isinstance(payload, Mapping):
            raise ScholarlyProviderError("provider response must be a JSON object")
        return payload


class OpenAlexProvider(_HttpProvider):
    provider = LiteratureProvider.OPENALEX
    allowed_host = OPENALEX_HOST
    base_url = "https://api.openalex.org"

    def search(self, query: LiteratureQuery) -> list[LiteratureSearchCandidate]:
        text = " ".join(
            [
                *query.search_terms,
                *query.method_terms,
                *query.material_terms,
                *query.property_terms,
            ]
        )
        params: dict[str, str | int] = {
            "search": text[:1000],
            "per-page": query.maximum_results,
        }
        filters: list[str] = []
        if query.date_from:
            filters.append(f"from_publication_date:{query.date_from.isoformat()}")
        if query.date_to:
            filters.append(f"to_publication_date:{query.date_to.isoformat()}")
        if filters:
            params["filter"] = ",".join(filters)
        payload = self._get(f"{self.base_url}/works", params=params)
        results = payload.get("results")
        if not isinstance(results, list):
            raise ScholarlyProviderError("OpenAlex results are malformed")
        return [
            candidate
            for record in results[: query.maximum_results]
            if isinstance(record, Mapping)
            and (candidate := self._candidate(record)) is not None
        ]

    def lookup_doi(self, doi: str) -> LiteratureSearchCandidate | None:
        normalized = normalize_doi(doi)
        assert normalized is not None
        payload = self._get(
            f"{self.base_url}/works",
            params={"filter": f"doi:https://doi.org/{normalized}", "per-page": 2},
        )
        results = payload.get("results")
        if not isinstance(results, list) or not results:
            return None
        record = results[0]
        return self._candidate(record) if isinstance(record, Mapping) else None

    def _candidate(
        self, record: Mapping[str, Any]
    ) -> LiteratureSearchCandidate | None:
        provider_id = str(record.get("id") or "").strip()
        title = str(record.get("display_name") or record.get("title") or "").strip()
        if not provider_id or not title:
            return None
        ids = record.get("ids") if isinstance(record.get("ids"), Mapping) else {}
        doi_value = ids.get("doi") or record.get("doi")
        doi = normalize_doi(str(doi_value)) if doi_value else None
        authorships = record.get("authorships")
        authors: list[str] = []
        if isinstance(authorships, list):
            for item in authorships[:256]:
                author = item.get("author") if isinstance(item, Mapping) else None
                name = author.get("display_name") if isinstance(author, Mapping) else None
                if isinstance(name, str) and name.strip():
                    authors.append(name.strip())
        primary_location = (
            record.get("primary_location")
            if isinstance(record.get("primary_location"), Mapping)
            else {}
        )
        source = (
            primary_location.get("source")
            if isinstance(primary_location.get("source"), Mapping)
            else {}
        )
        open_access = (
            record.get("open_access")
            if isinstance(record.get("open_access"), Mapping)
            else {}
        )
        type_name = str(record.get("type") or "").lower()
        if bool(record.get("is_retracted")):
            status = LiteraturePublicationStatus.RETRACTED
        elif type_name == "review":
            status = LiteraturePublicationStatus.REVIEW
        elif type_name in {"preprint", "posted-content"}:
            status = LiteraturePublicationStatus.PREPRINT
        elif type_name in {"article", "journal-article"}:
            status = LiteraturePublicationStatus.PEER_REVIEWED_ARTICLE
        else:
            status = LiteraturePublicationStatus.UNKNOWN
        is_oa = bool(open_access.get("is_oa"))
        snapshot = LiteratureSnapshot(
            snapshot_id=uuid4(),
            work_id=uuid4(),
            provider=self.provider,
            provider_record_id=provider_id,
            provider_roles=[
                LiteratureProviderRole.DISCOVERY,
                LiteratureProviderRole.IDENTITY,
                LiteratureProviderRole.BIBLIOGRAPHIC_METADATA,
                LiteratureProviderRole.OPEN_ACCESS_LOCATION,
            ],
            title=title,
            authors=authors,
            venue=str(source.get("display_name") or "").strip() or None,
            publication_date=_as_date(record.get("publication_date")),
            publication_status=status,
            publication_type=type_name or None,
            doi=doi,
            abstract=_abstract_from_inverted_index(
                record.get("abstract_inverted_index")
            ),
            cited_by_count=record.get("cited_by_count")
            if isinstance(record.get("cited_by_count"), int)
            else None,
            access_status=(
                LiteratureAccessStatus.OPEN_ACCESS
                if is_oa
                else LiteratureAccessStatus.METADATA_ONLY
            ),
            source_url=_safe_source_url(primary_location.get("landing_page_url"))
            or _safe_source_url(record.get("id")),
            open_access_url=_safe_source_url(
                primary_location.get("pdf_url")
                or primary_location.get("landing_page_url")
            )
            if is_oa
            else None,
            license=str(primary_location.get("license") or "").strip() or None,
            provider_updated_at=_as_datetime(record.get("updated_date")),
            retrieved_at=datetime.now(timezone.utc),
            provider_field_sources={
                field: self.provider.value
                for field in (
                    "title",
                    "authors",
                    "venue",
                    "publication_date",
                    "publication_status",
                    "doi",
                    "abstract",
                    "open_access_url",
                )
            },
            raw_metadata_hash=_raw_hash(record),
        )
        return candidate_from_snapshot(snapshot)


class CrossrefProvider(_HttpProvider):
    provider = LiteratureProvider.CROSSREF
    allowed_host = CROSSREF_HOST
    base_url = "https://api.crossref.org"

    def search(self, query: LiteratureQuery) -> list[LiteratureSearchCandidate]:
        text = " ".join(
            [
                *query.search_terms,
                *query.method_terms,
                *query.material_terms,
                *query.property_terms,
            ]
        )
        params: dict[str, str | int] = {
            "query.bibliographic": text[:1000],
            "rows": query.maximum_results,
        }
        filters: list[str] = []
        if query.date_from:
            filters.append(f"from-pub-date:{query.date_from.isoformat()}")
        if query.date_to:
            filters.append(f"until-pub-date:{query.date_to.isoformat()}")
        if filters:
            params["filter"] = ",".join(filters)
        payload = self._get(f"{self.base_url}/works", params=params)
        message = payload.get("message")
        items = message.get("items") if isinstance(message, Mapping) else None
        if not isinstance(items, list):
            raise ScholarlyProviderError("Crossref items are malformed")
        return [
            candidate
            for record in items[: query.maximum_results]
            if isinstance(record, Mapping)
            and (candidate := self._candidate(record)) is not None
        ]

    def lookup_doi(self, doi: str) -> LiteratureSearchCandidate | None:
        normalized = normalize_doi(doi)
        assert normalized is not None
        payload = self._get(f"{self.base_url}/works/{quote(normalized, safe='')}")
        record = payload.get("message")
        return self._candidate(record) if isinstance(record, Mapping) else None

    def _candidate(
        self, record: Mapping[str, Any]
    ) -> LiteratureSearchCandidate | None:
        doi_value = record.get("DOI")
        if not doi_value:
            return None
        doi = normalize_doi(str(doi_value))
        assert doi is not None
        title_value = record.get("title")
        title = (
            str(title_value[0]).strip()
            if isinstance(title_value, list) and title_value
            else str(title_value or "").strip()
        )
        if not title:
            return None
        authors: list[str] = []
        for item in record.get("author") or []:
            if not isinstance(item, Mapping):
                continue
            name = " ".join(
                value.strip()
                for value in (str(item.get("given") or ""), str(item.get("family") or ""))
                if value.strip()
            )
            if name:
                authors.append(name)
        venue_value = record.get("container-title")
        venue = (
            str(venue_value[0]).strip()
            if isinstance(venue_value, list) and venue_value
            else None
        )
        type_name = str(record.get("type") or "").lower()
        subtype = str(record.get("subtype") or "").lower()
        relations = self._relations(record)
        relation_types = {item.relation_type for item in relations}
        if LiteratureRelationType.RETRACTS in relation_types:
            status = LiteraturePublicationStatus.RETRACTED
        elif subtype == "retraction":
            status = LiteraturePublicationStatus.RETRACTED
        elif subtype == "correction" or LiteratureRelationType.CORRECTS in relation_types:
            status = LiteraturePublicationStatus.CORRECTION
        elif type_name in {"posted-content", "preprint"}:
            status = LiteraturePublicationStatus.PREPRINT
        elif type_name == "journal-article":
            status = LiteraturePublicationStatus.PEER_REVIEWED_ARTICLE
        else:
            status = LiteraturePublicationStatus.UNKNOWN
        published = record.get("published")
        parts = (
            published.get("date-parts")
            if isinstance(published, Mapping)
            else None
        )
        publication_date = None
        if isinstance(parts, list) and parts and isinstance(parts[0], list):
            values = parts[0]
            try:
                publication_date = date(
                    int(values[0]),
                    int(values[1]) if len(values) > 1 else 1,
                    int(values[2]) if len(values) > 2 else 1,
                )
            except (TypeError, ValueError):
                publication_date = None
        licenses = record.get("license")
        license_url = None
        if isinstance(licenses, list) and licenses and isinstance(licenses[0], Mapping):
            license_url = _safe_source_url(licenses[0].get("URL"))
        abstract = record.get("abstract")
        snapshot = LiteratureSnapshot(
            snapshot_id=uuid4(),
            work_id=uuid4(),
            provider=self.provider,
            provider_record_id=doi,
            provider_roles=[
                LiteratureProviderRole.IDENTITY,
                LiteratureProviderRole.BIBLIOGRAPHIC_METADATA,
                LiteratureProviderRole.PUBLICATION_RELATIONS,
            ],
            title=title,
            authors=authors,
            venue=venue,
            publication_date=publication_date,
            publication_status=status,
            publication_type=type_name or None,
            doi=doi,
            abstract=str(abstract)[:40000] if isinstance(abstract, str) else None,
            access_status=(
                LiteratureAccessStatus.OPEN_ACCESS
                if license_url
                else LiteratureAccessStatus.METADATA_ONLY
            ),
            source_url=_safe_source_url(record.get("URL"))
            or f"https://doi.org/{doi}",
            license=license_url,
            provider_updated_at=None,
            retrieved_at=datetime.now(timezone.utc),
            provider_field_sources={
                field: self.provider.value
                for field in (
                    "title",
                    "authors",
                    "venue",
                    "publication_date",
                    "publication_status",
                    "doi",
                    "relations",
                    "license",
                )
            },
            raw_metadata_hash=_raw_hash(record),
        )
        candidate = candidate_from_snapshot(snapshot)
        return candidate.model_copy(
            update={
                "work": candidate.work.model_copy(update={"relations": relations})
            }
        )

    def _relations(self, record: Mapping[str, Any]) -> list[LiteratureRelation]:
        mapping = {
            "is-preprint-of": LiteratureRelationType.PREPRINT_OF,
            "has-preprint": LiteratureRelationType.PUBLISHED_VERSION_OF,
            "is-version-of": LiteratureRelationType.UPDATED_VERSION,
            "updates": LiteratureRelationType.CORRECTS,
            "is-correction-of": LiteratureRelationType.CORRECTS,
            "is-retraction-of": LiteratureRelationType.RETRACTS,
        }
        output: list[LiteratureRelation] = []
        relation_payload = (
            record.get("relation")
            if isinstance(record.get("relation"), Mapping)
            else {}
        )
        for key, values in relation_payload.items():
            relation_type = mapping.get(str(key).lower())
            if relation_type is None or not isinstance(values, list):
                continue
            for item in values[:8]:
                if not isinstance(item, Mapping):
                    continue
                target = item.get("id")
                if target:
                    output.append(
                        LiteratureRelation(
                            relation_type=relation_type,
                            target_identity=str(target),
                            provider=self.provider,
                        )
                    )
        return output[:32]


__all__ = [
    "CROSSREF_HOST",
    "OPENALEX_HOST",
    "CrossrefProvider",
    "OpenAlexProvider",
    "ScholarlyProviderError",
]
