from __future__ import annotations

import json
from statistics import median, quantiles
from time import perf_counter
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, insert
from sqlalchemy.pool import StaticPool

from mdi_api.db import (
    datasets,
    metadata,
    organizations,
    project_members,
    projects,
    users,
)
from mdi_api.routers.auth import CurrentUser
from mdi_api.routers import secured_runtime


def _search_engine(
    *,
    project_count: int = 125,
    private_project_count: int = 1,
):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    metadata.create_all(engine)
    viewer = CurrentUser(
        id="search-viewer",
        email="search-viewer@example.invalid",
        displayName="Search viewer",
        roles=[],
    )
    owner = CurrentUser(
        id="search-owner",
        email="search-owner@example.invalid",
        displayName="Search owner",
        roles=[],
    )
    outsider = CurrentUser(
        id="search-outsider",
        email="search-outsider@example.invalid",
        displayName="Search outsider",
        roles=[],
    )
    base = datetime(2026, 9, 5, tzinfo=timezone.utc)
    project_rows = [
        {
            "id": f"paged-project-{index:03d}",
            "organization_id": "search-org",
            "name": f"Paged scientific project {index:03d}",
            "description": "authorized pagination fixture",
            "created_by": owner.id,
            # Deliberately identical timestamps force the stable identity
            # tiebreaker to carry pagination across page boundaries.
            "created_at": base,
            "updated_at": base,
        }
        for index in range(project_count)
    ]
    private_project_rows = [
        {
            "id": (
                "private-paged-project"
                if index == 0
                else f"private-paged-project-{index:03d}"
            ),
            "organization_id": "search-org",
            "name": f"Paged scientific project private {index:03d}",
            "description": "must not leak",
            "created_by": outsider.id,
            "created_at": base + timedelta(days=1, seconds=index),
            "updated_at": base + timedelta(days=1, seconds=index),
        }
        for index in range(private_project_count)
    ]
    with engine.begin() as connection:
        connection.execute(
            insert(users),
            [
                {
                    "id": user.id,
                    "email": user.email,
                    "display_name": user.displayName,
                    "is_active": True,
                }
                for user in (viewer, owner, outsider)
            ],
        )
        connection.execute(
            insert(organizations),
            {"id": "search-org", "name": "Search organization"},
        )
        connection.execute(insert(projects), project_rows)
        connection.execute(
            insert(project_members),
            [
                {
                    "project_id": row["id"],
                    "user_id": viewer.id,
                    "role": "viewer",
                }
                for row in project_rows
            ],
        )
        connection.execute(insert(projects), private_project_rows)
    return engine, viewer


def test_authorized_global_search_continuation_is_stable_and_deduplicated(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, viewer = _search_engine()
    monkeypatch.setattr(
        secured_runtime,
        "create_engine_from_settings",
        lambda _settings: engine,
    )
    monkeypatch.setattr(secured_runtime, "load_settings", lambda: SimpleNamespace())

    cursor: str | None = None
    observed: list[str] = []
    page_sizes: list[int] = []
    while True:
        page = secured_runtime.search_product_secured(
            q="Paged scientific project",
            kind="project",
            limit=23,
            cursor=cursor,
            current_user=viewer,
        )
        page_sizes.append(len(page["items"]))
        observed.extend(item["id"] for item in page["items"])
        cursor = page["nextCursor"]
        if cursor is None:
            break

    assert page_sizes == [23, 23, 23, 23, 23, 10]
    assert len(observed) == 125
    assert len(set(observed)) == 125
    assert observed == [f"paged-project-{index:03d}" for index in range(124, -1, -1)]
    assert "private-paged-project" not in observed


def test_global_search_keyset_is_stable_when_newer_data_arrives(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, viewer = _search_engine()
    monkeypatch.setattr(
        secured_runtime,
        "create_engine_from_settings",
        lambda _settings: engine,
    )
    monkeypatch.setattr(secured_runtime, "load_settings", lambda: SimpleNamespace())

    first = secured_runtime.search_product_secured(
        q="Paged scientific project",
        kind="project",
        limit=23,
        current_user=viewer,
    )
    assert first["nextCursor"]

    with engine.begin() as connection:
        connection.execute(
            insert(projects),
            {
                "id": "paged-project-newer",
                "organization_id": "search-org",
                "name": "Paged scientific project newer",
                "description": "arrived after page one",
                "created_by": "search-owner",
                "created_at": datetime(2026, 9, 6, tzinfo=timezone.utc),
                "updated_at": datetime(2026, 9, 6, tzinfo=timezone.utc),
            },
        )
        connection.execute(
            insert(project_members),
            {
                "project_id": "paged-project-newer",
                "user_id": viewer.id,
                "role": "viewer",
            },
        )

    observed = [item["id"] for item in first["items"]]
    cursor = first["nextCursor"]
    while cursor:
        page = secured_runtime.search_product_secured(
            q="Paged scientific project",
            kind="project",
            limit=23,
            cursor=cursor,
            current_user=viewer,
        )
        observed.extend(item["id"] for item in page["items"])
        cursor = page["nextCursor"]

    assert len(observed) == 125
    assert len(set(observed)) == 125
    assert "paged-project-newer" not in observed
    assert observed == [
        f"paged-project-{index:03d}"
        for index in range(124, -1, -1)
    ]


def test_global_keyset_orders_mixed_entity_kinds_without_duplicates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, viewer = _search_engine(project_count=40)
    shared_time = datetime(2026, 9, 5, tzinfo=timezone.utc)
    with engine.begin() as connection:
        connection.execute(
            insert(datasets),
            [
                {
                    "id": f"paged-dataset-{index:03d}",
                    "project_id": f"paged-project-{index:03d}",
                    "name": f"Paged scientific dataset {index:03d}",
                    "status": "profile_ready",
                    "metadata_json": {},
                    "created_by": "search-owner",
                    "created_at": shared_time,
                    "updated_at": shared_time,
                }
                for index in range(40)
            ],
        )
    monkeypatch.setattr(
        secured_runtime,
        "create_engine_from_settings",
        lambda _settings: engine,
    )
    monkeypatch.setattr(secured_runtime, "load_settings", lambda: SimpleNamespace())

    cursor: str | None = None
    identities: list[tuple[str, str]] = []
    while True:
        page = secured_runtime.search_product_secured(
            q="Paged scientific",
            limit=17,
            cursor=cursor,
            current_user=viewer,
        )
        identities.extend((item["kind"], item["id"]) for item in page["items"])
        cursor = page["nextCursor"]
        if cursor is None:
            break

    assert len(identities) == 80
    assert len(set(identities)) == 80
    assert identities == sorted(identities, reverse=True)


def test_large_authorized_search_corpus_is_bounded_and_qualified(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, viewer = _search_engine(
        project_count=1_000,
        private_project_count=250,
    )
    monkeypatch.setattr(
        secured_runtime,
        "create_engine_from_settings",
        lambda _settings: engine,
    )
    monkeypatch.setattr(secured_runtime, "load_settings", lambda: SimpleNamespace())

    durations_ms: list[float] = []
    for _sample in range(30):
        started = perf_counter()
        response = secured_runtime.search_product_secured(
            q="Paged scientific project",
            kind="project",
            limit=100,
            current_user=viewer,
        )
        durations_ms.append((perf_counter() - started) * 1_000)
        assert len(response["items"]) == 100
        assert all(not item["id"].startswith("private-") for item in response["items"])
        assert len(json.dumps(response, ensure_ascii=False).encode("utf-8")) < 64 * 1_024

    p50_ms = median(durations_ms)
    p95_ms = quantiles(durations_ms, n=20, method="inclusive")[18]
    print(
        "CO-047 search qualification: "
        f"corpus=1250 authorized=1000 private=250 "
        f"p50_ms={p50_ms:.2f} p95_ms={p95_ms:.2f} "
        f"max_ms={max(durations_ms):.2f}"
    )

    # A generous integration guard catches accidental unbounded loading while
    # leaving normal shared-CI scheduling variance out of the release signal.
    assert p95_ms < 500


def test_global_search_cursor_is_bound_to_user_and_filters(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, viewer = _search_engine()
    monkeypatch.setattr(
        secured_runtime,
        "create_engine_from_settings",
        lambda _settings: engine,
    )
    monkeypatch.setattr(secured_runtime, "load_settings", lambda: SimpleNamespace())

    first = secured_runtime.search_product_secured(
        q="Paged scientific project",
        kind="project",
        status="all",
        limit=5,
        current_user=viewer,
    )
    assert first["nextCursor"]
    continued = secured_runtime.search_product_secured(
        q="Paged scientific project",
        kind="project",
        limit=5,
        cursor=first["nextCursor"],
        current_user=viewer,
    )
    assert len(continued["items"]) == 5

    with pytest.raises(HTTPException) as changed_query:
        secured_runtime.search_product_secured(
            q="different",
            kind="project",
            limit=5,
            cursor=first["nextCursor"],
            current_user=viewer,
        )
    assert changed_query.value.status_code == 422

    outsider = CurrentUser(
        id="search-outsider",
        email="search-outsider@example.invalid",
        displayName="Search outsider",
        roles=[],
    )
    with pytest.raises(HTTPException) as changed_user:
        secured_runtime.search_product_secured(
            q="Paged scientific project",
            kind="project",
            limit=5,
            cursor=first["nextCursor"],
            current_user=outsider,
        )
    assert changed_user.value.status_code == 422
