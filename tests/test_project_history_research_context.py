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
            "user_message_id": "message-3",
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
                "researchTurnStatus": "COMPLETED",
                "contextKind": "RESEARCH_TURN",
            },
        }


def test_research_context_prefers_exact_turn_message_over_timestamp_guess() -> None:
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    started_at = datetime(2026, 8, 21, 8, 0, 0)
    turn_id = uuid4()

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
        connection.execute(insert(jobs), {
            "id": "job-modern",
            "project_id": "project-1",
            "kind": "analysis",
            "status": "completed",
            "created_by": "user-1",
            "created_at": started_at + timedelta(minutes=3),
        })
        connection.execute(insert(messages), [
            {
                "id": "message-exact",
                "session_id": "session-1",
                "role": "user",
                "content_summary": "Use the exact historical structure version.",
                "created_at": started_at + timedelta(minutes=1),
            },
            {
                "id": "message-newer",
                "session_id": "session-1",
                "role": "user",
                "content_summary": "Now ask about a different sample.",
                "created_at": started_at + timedelta(minutes=2),
            },
        ])
        connection.execute(insert(research_session_runs), {
            "session_id": "session-1",
            "job_id": "job-modern",
            "created_at": started_at + timedelta(minutes=3),
        })
        connection.execute(insert(research_turns), {
            "id": turn_id,
            "project_id": "project-1",
            "research_session_id": "session-1",
            "sequence_no": 1,
            "user_message_id": "message-exact",
            "status": "COMPLETED",
            "job_id": "job-modern",
        })

        result = _read_research_context_by_run(connection, "project-1")

    assert result["job-modern"] == {
        "sessionId": "session-1",
        "userQuestion": "Use the exact historical structure version.",
        "researchTurnId": str(turn_id),
        "researchTurnStatus": "COMPLETED",
        "contextKind": "RESEARCH_TURN",
    }


def test_research_context_uses_direct_turn_relation_without_legacy_run_binding() -> None:
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    started_at = datetime(2026, 8, 21, 8, 0, 0)
    turn_id = uuid4()

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
        connection.execute(insert(jobs), {
            "id": "job-direct-turn",
            "project_id": "project-1",
            "kind": "analysis",
            "status": "completed",
            "created_by": "user-1",
            "created_at": started_at + timedelta(minutes=2),
        })
        connection.execute(insert(messages), {
            "id": "message-direct-turn",
            "session_id": "session-1",
            "role": "user",
            "content_summary": "Resume the exact scientific result.",
            "created_at": started_at + timedelta(minutes=1),
        })
        connection.execute(insert(research_turns), {
            "id": turn_id,
            "project_id": "project-1",
            "research_session_id": "session-1",
            "sequence_no": 1,
            "user_message_id": "message-direct-turn",
            "status": "COMPLETED",
            "job_id": "job-direct-turn",
            "created_at": started_at + timedelta(minutes=2),
        })

        result = _read_research_context_by_run(connection, "project-1")

    assert result["job-direct-turn"] == {
        "sessionId": "session-1",
        "userQuestion": "Resume the exact scientific result.",
        "researchTurnId": str(turn_id),
        "researchTurnStatus": "COMPLETED",
        "contextKind": "RESEARCH_TURN",
    }


def test_research_context_does_not_use_cross_session_exact_message() -> None:
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    started_at = datetime(2026, 8, 21, 8, 0, 0)

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
        connection.execute(insert(sessions), [
            {
                "id": "session-1",
                "project_id": "project-1",
                "mode": "project",
                "status": "active",
                "created_by": "user-1",
                "created_at": started_at,
            },
            {
                "id": "session-2",
                "project_id": "project-1",
                "mode": "project",
                "status": "active",
                "created_by": "user-1",
                "created_at": started_at,
            },
        ])
        connection.execute(insert(jobs), {
            "id": "job-modern",
            "project_id": "project-1",
            "kind": "analysis",
            "status": "completed",
            "created_by": "user-1",
            "created_at": started_at + timedelta(minutes=3),
        })
        connection.execute(insert(messages), [
            {
                "id": "message-other-session",
                "session_id": "session-2",
                "role": "user",
                "content_summary": "Do not disclose this question.",
                "created_at": started_at + timedelta(minutes=1),
            },
            {
                "id": "message-local",
                "session_id": "session-1",
                "role": "user",
                "content_summary": "Use the bounded session fallback.",
                "created_at": started_at + timedelta(minutes=2),
            },
        ])
        connection.execute(insert(research_session_runs), {
            "session_id": "session-1",
            "job_id": "job-modern",
            "created_at": started_at + timedelta(minutes=3),
        })
        connection.execute(insert(research_turns), {
            "id": uuid4(),
            "project_id": "project-1",
            "research_session_id": "session-1",
            "sequence_no": 1,
            "user_message_id": "message-other-session",
            "status": "COMPLETED",
            "job_id": "job-modern",
        })

        result = _read_research_context_by_run(connection, "project-1")

    assert result["job-modern"]["userQuestion"] == "Use the bounded session fallback."


def test_research_context_fails_closed_for_cross_project_turn_relation() -> None:
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    started_at = datetime(2026, 8, 21, 8, 0, 0)
    cross_project_turn_id = uuid4()

    with engine.begin() as connection:
        connection.execute(insert(users), {
            "id": "user-1",
            "email": "researcher@example.invalid",
            "display_name": "Researcher",
            "is_active": True,
        })
        connection.execute(insert(organizations), {"id": "org-1", "name": "Research"})
        connection.execute(insert(projects), [
            {
                "id": "project-1",
                "organization_id": "org-1",
                "name": "Authorized project",
                "created_by": "user-1",
            },
            {
                "id": "project-2",
                "organization_id": "org-1",
                "name": "Other project",
                "created_by": "user-1",
            },
        ])
        connection.execute(insert(sessions), [
            {
                "id": "session-1",
                "project_id": "project-1",
                "mode": "project",
                "status": "active",
                "created_by": "user-1",
                "created_at": started_at,
            },
            {
                "id": "session-2",
                "project_id": "project-2",
                "mode": "project",
                "status": "active",
                "created_by": "user-1",
                "created_at": started_at,
            },
        ])
        connection.execute(insert(messages), [
            {
                "id": "message-local",
                "session_id": "session-1",
                "role": "user",
                "content_summary": "Use only the authorized history.",
                "created_at": started_at + timedelta(minutes=1),
            },
            {
                "id": "message-cross-project",
                "session_id": "session-2",
                "role": "user",
                "content_summary": "Do not disclose this other project turn.",
                "created_at": started_at + timedelta(minutes=1),
            },
        ])
        connection.execute(insert(jobs), {
            "id": "legacy-shared-job",
            "project_id": "project-1",
            "kind": "analysis",
            "status": "completed",
            "created_by": "user-1",
            "created_at": started_at + timedelta(minutes=2),
        })
        connection.execute(insert(research_session_runs), {
            "session_id": "session-1",
            "job_id": "legacy-shared-job",
            "created_at": started_at + timedelta(minutes=2),
        })
        connection.execute(insert(research_turns), {
            "id": cross_project_turn_id,
            "project_id": "project-2",
            "research_session_id": "session-2",
            "sequence_no": 1,
            "user_message_id": "message-cross-project",
            "status": "COMPLETED",
            "job_id": "legacy-shared-job",
            "created_at": started_at + timedelta(minutes=2),
        })

        result = _read_research_context_by_run(connection, "project-1")

    assert result["legacy-shared-job"] == {
        "sessionId": "session-1",
        "userQuestion": "Use only the authorized history.",
        "contextKind": "LEGACY_SESSION_RUN",
    }
