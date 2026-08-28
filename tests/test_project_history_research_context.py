from __future__ import annotations

from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy import create_engine, insert

from mdi_api.db import (
    jobs,
    messages,
    metadata,
    organizations,
    projects,
    research_turns,
    research_session_runs,
    sessions,
    users,
)
from mdi_api.routers.project_history import _read_research_context_by_run


def test_research_context_maps_each_run_to_its_preceding_user_turn() -> None:
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    started_at = datetime(2026, 8, 21, 8, 0, 0)
    coordination_turn_id = uuid4()

    with engine.begin() as connection:
        connection.execute(insert(users), {
            "id": "user-1",
            "email": "researcher@example.invalid",
            "display_name": "Researcher",
            "is_active": True,
        })
        connection.execute(insert(organizations), {"id": "org-1", "name": "Research"})
        connection.execute(insert(projects), {
            "id": "project-1",
            "organization_id": "org-1",
            "name": "Materials project",
            "created_by": "user-1",
        })
        connection.execute(insert(sessions), {
            "id": "session-1",
            "project_id": "project-1",
            "mode": "project",
            "status": "active",
            "created_by": "user-1",
            "created_at": started_at,
        })
        connection.execute(insert(jobs), [
            {
                "id": "job-rdf",
                "project_id": "project-1",
                "kind": "analysis",
                "status": "completed",
                "created_by": "user-1",
                "created_at": started_at + timedelta(minutes=1),
            },
            {
                "id": "job-coordination",
                "project_id": "project-1",
                "kind": "analysis",
                "status": "completed",
                "created_by": "user-1",
                "created_at": started_at + timedelta(minutes=3),
            },
        ])
        connection.execute(insert(messages), [
            {
                "id": "message-1",
                "session_id": "session-1",
                "role": "user",
                "content_summary": "Show the radial distribution function.",
                "created_at": started_at + timedelta(seconds=30),
            },
            {
                "id": "message-2",
                "session_id": "session-1",
                "role": "agent",
                "content_summary": "RDF analysis started.",
                "created_at": started_at + timedelta(minutes=1, seconds=10),
            },
            {
                "id": "message-3",
                "session_id": "session-1",
                "role": "user",
                "content_summary": "Inspect the local coordination environment.",
                "created_at": started_at + timedelta(minutes=2),
            },
        ])
        connection.execute(insert(research_session_runs), [
            {
                "session_id": "session-1",
                "job_id": "job-rdf",
                "created_at": started_at + timedelta(minutes=1),
            },
            {
                "session_id": "session-1",
                "job_id": "job-coordination",
                "created_at": started_at + timedelta(minutes=3),
            },
        ])
        connection.execute(insert(research_turns), {
            "id": coordination_turn_id,
            "project_id": "project-1",
            "research_session_id": "session-1",
            "sequence_no": 1,
            "user_message_id": "message-1",
            "status": "COMPLETED",
            "job_id": "job-coordination",
        })

        assert _read_research_context_by_run(connection, "project-1") == {
            "job-rdf": {
                "sessionId": "session-1",
                "userQuestion": "Show the radial distribution function.",
                "contextKind": "LEGACY_SESSION_RUN",
            },
            "job-coordination": {
                "sessionId": "session-1",
                "userQuestion": "Inspect the local coordination environment.",
                "researchTurnId": str(coordination_turn_id),
                "contextKind": "RESEARCH_TURN",
            },
        }
