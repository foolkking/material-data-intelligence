from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, insert
from sqlalchemy.pool import StaticPool

from mdi_api.db import (
    agent2_scientific_report_snapshots,
    datasets,
    jobs,
    messages,
    metadata,
    organizations,
    project_configs,
    project_members,
    projects,
    reports,
    research_turns,
    scientific_objects,
    scientific_result_snapshots,
    sessions,
    users,
)
from mdi_api.routers import secured_runtime
from mdi_api.routers.auth import CurrentUser


def _coverage_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    metadata.create_all(engine)
    owner = CurrentUser(
        id="search-owner",
        email="owner@example.invalid",
        displayName="Owner",
        roles=[],
    )
    viewer = CurrentUser(
        id="search-viewer",
        email="viewer@example.invalid",
        displayName="Viewer",
        roles=[],
    )
    outsider = CurrentUser(
        id="search-outsider",
        email="outsider@example.invalid",
        displayName="Outsider",
        roles=[],
    )
    lifecycle_dates = {
        "active": datetime(2026, 8, 1, 12, tzinfo=timezone.utc),
        "archived": datetime(2026, 8, 2, 12, tzinfo=timezone.utc),
        "trashed": datetime(2026, 8, 3, 12, tzinfo=timezone.utc),
    }
    with engine.begin() as connection:
        connection.execute(
            insert(users),
            [
                {"id": user.id, "email": user.email, "display_name": user.displayName}
                for user in (owner, viewer, outsider)
            ],
        )
        connection.execute(insert(organizations), {"id": "org", "name": "Org"})
        connection.execute(
            insert(projects),
            [
                {
                    "id": f"project-{status}",
                    "organization_id": "org",
                    "name": f"Coverage {status}",
                    "description": "coverage matrix",
                    "created_by": owner.id,
                    "created_at": when,
                    "updated_at": when,
                }
                for status, when in lifecycle_dates.items()
            ]
            + [
                {
                    "id": "project-private",
                    "organization_id": "org",
                    "name": "Coverage private",
                    "description": "must not leak",
                    "created_by": outsider.id,
                    "created_at": lifecycle_dates["active"],
                    "updated_at": lifecycle_dates["active"],
                }
            ],
        )
        connection.execute(
            insert(project_members),
            [
                {
                    "project_id": f"project-{status}",
                    "user_id": viewer.id,
                    "role": "viewer",
                }
                for status in lifecycle_dates
            ],
        )

        report_lifecycle: dict[str, str] = {}
        for status, when in lifecycle_dates.items():
            project_id = f"project-{status}"
            dataset_id = f"dataset-{status}"
            session_id = f"session-{status}"
            job_id = f"job-{status}"
            report_id = f"report-{status}"
            object_id = uuid4()
            turn_id = uuid4()
            result_id = uuid4()
            connection.execute(
                insert(datasets),
                {
                    "id": dataset_id,
                    "project_id": project_id,
                    "name": f"Coverage dataset {status}",
                    "status": "archived" if status != "active" else "created",
                    "metadata_json": (
                        {"trashedAt": when.isoformat()} if status == "trashed" else {}
                    ),
                    "created_by": owner.id,
                    "created_at": when,
                    "updated_at": when,
                },
            )
            connection.execute(
                insert(scientific_objects),
                {
                    "id": object_id,
                    "project_id": project_id,
                    "kind": "structure",
                    "object_type": "structure",
                    "display_name": f"Coverage object {status}",
                    "lifecycle_status": status.upper(),
                    "created_by_user_id": owner.id,
                    "created_at": when,
                },
            )
            connection.execute(
                insert(sessions),
                {
                    "id": session_id,
                    "project_id": project_id,
                    "dataset_id": dataset_id,
                    "mode": "project",
                    "status": status,
                    "title_override": f"Coverage research {status}",
                    "created_by": owner.id,
                    "created_at": when,
                },
            )
            connection.execute(
                insert(messages),
                {
                    "id": f"message-{status}",
                    "session_id": session_id,
                    "role": "user",
                    "content_summary": f"Coverage question {status}",
                    "payload_json": {},
                    "created_at": when,
                },
            )
            connection.execute(
                insert(jobs),
                {
                    "id": job_id,
                    "project_id": project_id,
                    "dataset_id": dataset_id,
                    "kind": "analysis",
                    "status": "completed",
                    "created_by": owner.id,
                    "created_at": when,
                    "updated_at": when,
                },
            )
            connection.execute(
                insert(research_turns),
                {
                    "id": turn_id,
                    "project_id": project_id,
                    "research_session_id": session_id,
                    "sequence_no": 1,
                    "user_message_id": f"message-{status}",
                    "action_type": "ANALYZE",
                    "status": "COMPLETED",
                    "created_at": when,
                    "updated_at": when,
                },
            )
            connection.execute(
                insert(scientific_result_snapshots),
                {
                    "id": result_id,
                    "project_id": project_id,
                    "research_turn_id": turn_id,
                    "job_id": job_id,
                    "schema_version": "1.0",
                    "projection_version": "coverage/1.0",
                    "execution_status": "SUCCESS",
                    "relevance_status": "CURRENT",
                    "source_fingerprint": status[0] * 64,
                    "bundle_json": {"research_question": f"Coverage result {status}"},
                    "created_at": when,
                },
            )
            connection.execute(
                insert(reports),
                {
                    "id": report_id,
                    "project_id": project_id,
                    "dataset_id": dataset_id,
                    "job_id": job_id,
                    "title": f"Coverage report {status}",
                    "created_by": owner.id,
                    "created_at": when,
                },
            )
            connection.execute(
                insert(agent2_scientific_report_snapshots),
                {
                    "id": uuid4(),
                    "report_id": report_id,
                    "project_id": project_id,
                    "research_session_id": session_id,
                    "research_turn_id": turn_id,
                    "scientific_result_snapshot_id": result_id,
                    "scientific_interpretation_id": uuid4(),
                    "contract_version": "2.0",
                    "composer_version": "coverage",
                    "prompt_version": "coverage",
                    "source_fingerprint": status,
                    "relevance_at_generation": "CURRENT",
                    "grounding_status": "VALID",
                    "report_json": {"title": f"Coverage report {status}"},
                    "created_by": owner.id,
                    "created_at": when,
                },
            )
            report_lifecycle[report_id] = status.upper()

        connection.execute(
            insert(project_configs),
            [
                {
                    "project_id": "project-active",
                    "config_json": {
                        "scientificReportLifecycle": {
                            "report-active": report_lifecycle["report-active"]
                        }
                    },
                },
                {
                    "project_id": "project-archived",
                    "config_json": {
                        "archivedProject": True,
                        "scientificReportLifecycle": {
                            "report-archived": report_lifecycle["report-archived"]
                        },
                    },
                },
                {
                    "project_id": "project-trashed",
                    "config_json": {
                        "archivedProject": True,
                        "trashedProject": True,
                        "scientificReportLifecycle": {
                            "report-trashed": report_lifecycle["report-trashed"]
                        },
                    },
                },
            ],
        )
    return engine, viewer


@pytest.mark.parametrize(
    "kind",
    [
        "project",
        "dataset",
        "scientific_object",
        "research",
        "report",
        "result",
    ],
)
@pytest.mark.parametrize("status", ["active", "archived", "trashed"])
def test_search_covers_lifecycle_and_exact_spa_destinations(
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
    status: str,
) -> None:
    engine, viewer = _coverage_engine()
    monkeypatch.setattr(
        secured_runtime,
        "create_engine_from_settings",
        lambda _settings: engine,
    )
    monkeypatch.setattr(secured_runtime, "load_settings", lambda: SimpleNamespace())

    result = secured_runtime.search_product_secured(
        q="Coverage",
        kind=kind,
        status=status,
        current_user=viewer,
    )

    assert result["count"] == 1
    item = result["items"][0]
    item_status = item["status"].lower()
    if status == "active":
        assert item_status not in {"archived", "trashed", "purged"}
    else:
        assert item_status == status
    expected_ids = {
        "project": f"project-{status}",
        "dataset": f"dataset-{status}",
        "research": f"session-{status}",
        "report": f"report-{status}",
    }
    expected_id = expected_ids.get(kind)
    if expected_id is not None:
        assert item["id"] == expected_id
    expected_hrefs = {
        "project": f"/projects/project-{status}",
        "dataset": (
            f"/projects/project-{status}/data?dataset=dataset-{status}"
        ),
        "scientific_object": f"/projects/project-{status}/data?object=",
        "research": (
            f"/projects/project-{status}/research/session-{status}"
        ),
        "report": (
            f"/projects/project-{status}/reports/report-{status}"
        ),
        "result": (
            f"/projects/project-{status}/research/session-{status}?turn="
        ),
    }
    expected_href = expected_hrefs[kind]
    assert item["href"].startswith(expected_href)
    assert "private" not in item["id"]


def test_search_combines_project_type_status_and_inclusive_date_filters(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine, viewer = _coverage_engine()
    monkeypatch.setattr(
        secured_runtime,
        "create_engine_from_settings",
        lambda _settings: engine,
    )
    monkeypatch.setattr(secured_runtime, "load_settings", lambda: SimpleNamespace())

    result = secured_runtime.search_product_secured(
        q="Coverage",
        project_id="project-archived",
        kind="research",
        status="archived",
        date_from="2026-08-02",
        date_to="2026-08-02",
        current_user=viewer,
    )
    assert [item["id"] for item in result["items"]] == ["session-archived"]

    assert secured_runtime.search_product_secured(
        q="Coverage",
        project_id="project-archived",
        kind="research",
        status="archived",
        date_from="2026-08-03",
        current_user=viewer,
    )["items"] == []

    with pytest.raises(HTTPException) as invalid:
        secured_runtime.search_product_secured(
            q="Coverage",
            date_from="2026-08-03",
            date_to="2026-08-02",
            current_user=viewer,
        )
    assert invalid.value.status_code == 422
