from __future__ import annotations

from fastapi import HTTPException
import pytest
from sqlalchemy import create_engine, insert
from sqlalchemy.pool import StaticPool

from mdi_api.db import metadata, organizations, projects, users
from mdi_api.database import RepositoryFactory
from mdi_api.routers.auth import CurrentUser
from mdi_api.routers.secured_planner import get_planner_interpretation_evidence_secured
from mdi_api.routers.scientific_reports import (
    ScientificReportLifecycleRequest,
    ScientificReportOrganizationRequest,
    ScientificReportRevisionRequest,
    compare_scientific_report_revisions,
    create_scientific_report_revision,
    get_scientific_report_by_id,
    get_scientific_report_dependency_impact,
    list_scientific_report_revisions,
    update_scientific_report_lifecycle,
    update_scientific_report_organization,
)


def _user() -> CurrentUser:
    return CurrentUser(
        id="authorized-user",
        email="authorized@example.invalid",
        displayName="Authorized User",
        roles=[],
    )


def test_interpretation_evidence_rejects_cross_project_job_relation(monkeypatch: pytest.MonkeyPatch) -> None:
    """A guessed interpretation id cannot bridge two project scopes."""

    monkeypatch.setattr(
        "mdi_api.routers.secured_planner.get_planner_interpretation_evidence",
        lambda _interpretation_id: {
            "interpretationId": "interpretation-cross-project",
            "jobId": "job-authorized-project",
            "projectId": "project-other",
            "evidenceItems": [{"evidenceItemId": "private-evidence"}],
        },
    )
    monkeypatch.setattr(
        "mdi_api.routers.secured_planner._require_job",
        lambda _job_id, _current_user: {
            "jobId": "job-authorized-project",
            "projectId": "project-authorized",
        },
    )

    with pytest.raises(HTTPException) as raised:
        get_planner_interpretation_evidence_secured(
            "interpretation-cross-project",
            _user(),
        )

    # Keep the response indistinguishable from a missing resource so the
    # mismatch cannot become an oracle for cross-project identifiers.
    assert raised.value.status_code == 404
    assert raised.value.detail == "依据所属运行不存在。"


def test_interpretation_evidence_accepts_matching_project_relation(monkeypatch: pytest.MonkeyPatch) -> None:
    evidence = {
        "interpretationId": "interpretation-authorized",
        "jobId": "job-authorized-project",
        "projectId": "project-authorized",
        "evidenceItems": [{"evidenceItemId": "authorized-evidence"}],
    }
    monkeypatch.setattr(
        "mdi_api.routers.secured_planner.get_planner_interpretation_evidence",
        lambda _interpretation_id: evidence,
    )
    monkeypatch.setattr(
        "mdi_api.routers.secured_planner._require_job",
        lambda _job_id, _current_user: {
            "jobId": "job-authorized-project",
            "projectId": "project-authorized",
        },
    )

    assert (
        get_planner_interpretation_evidence_secured("interpretation-authorized", _user())
        == evidence
    )


def test_exact_report_routes_reject_cross_project_user_before_projection_or_mutation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import mdi_api.routers.scientific_reports as report_routes

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    metadata.create_all(engine)
    owner = _user()
    stranger = CurrentUser(
        id="report-stranger",
        email="report-stranger@example.invalid",
        displayName="Report Stranger",
        roles=[],
    )
    with engine.begin() as connection:
        connection.execute(insert(users), [
            {
                "id": owner.id,
                "email": owner.email,
                "display_name": owner.displayName,
                "is_active": True,
            },
            {
                "id": stranger.id,
                "email": stranger.email,
                "display_name": stranger.displayName,
                "is_active": True,
            },
        ])
        connection.execute(insert(organizations), {"id": "org", "name": "Org"})
        connection.execute(insert(projects), {
            "id": "report-project",
            "organization_id": "org",
            "name": "Private report project",
            "created_by": owner.id,
        })

    downstream: list[str] = []

    class FakeReportService:
        def __init__(self, _factory: object) -> None:
            pass

        @staticmethod
        def get_by_report_id(_report_id: str) -> dict[str, str]:
            return {
                "report_id": "report-private",
                "project_id": "report-project",
                "title": "PRIVATE_REPORT_TITLE",
            }

        def __getattr__(self, name: str):
            def call(*_args: object, **_kwargs: object) -> dict[str, str]:
                downstream.append(name)
                return {"unexpected": name}

            return call

    monkeypatch.setattr(
        report_routes,
        "create_repository_factory",
        lambda: RepositoryFactory(engine),
    )
    monkeypatch.setattr(report_routes, "ScientificReportService", FakeReportService)

    cases = [
        lambda: get_scientific_report_by_id("report-private", stranger),
        lambda: update_scientific_report_lifecycle(
            "report-private",
            ScientificReportLifecycleRequest(lifecycle="ARCHIVED"),
            stranger,
        ),
        lambda: update_scientific_report_organization(
            "report-private",
            ScientificReportOrganizationRequest(title="LEAK"),
            stranger,
        ),
        lambda: get_scientific_report_dependency_impact(
            "report-private",
            stranger,
        ),
        lambda: create_scientific_report_revision(
            "report-private",
            ScientificReportRevisionRequest(reason="USER_REVISION"),
            stranger,
        ),
        lambda: list_scientific_report_revisions("report-private", stranger),
        lambda: compare_scientific_report_revisions(
            "report-private",
            current_user=stranger,
        ),
    ]

    for invoke in cases:
        with pytest.raises(HTTPException) as denied:
            invoke()
        assert denied.value.status_code == 403
        assert "PRIVATE_REPORT_TITLE" not in str(denied.value.detail)
        assert "report-private" not in str(denied.value.detail)
    assert downstream == []
