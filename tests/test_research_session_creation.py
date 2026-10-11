from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, func, insert, select, update

from mdi_api.db import datasets, metadata, organizations, project_members, projects, sessions, users
from mdi_api.routers.auth import CurrentUser
from mdi_api.routers import research


@pytest.fixture
def creation_store(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite:///{(tmp_path / 'sessions.sqlite').as_posix()}", connect_args={"timeout": 20})
    metadata.create_all(engine)
    people = [CurrentUser(id=name, email=f"{name}@example.invalid", displayName=name, roles=[]) for name in ("owner", "member")]
    with engine.begin() as connection:
        connection.execute(insert(users), [dict(id=p.id, email=p.email, display_name=p.displayName, is_active=True) for p in people])
        connection.execute(insert(organizations), dict(id="org", name="Org"))
        connection.execute(insert(projects), [dict(id=p, organization_id="org", name=p, created_by="owner") for p in ("project", "other")])
        connection.execute(insert(project_members), dict(project_id="project", user_id="member", role="researcher"))
        connection.execute(insert(datasets), [dict(id=d, project_id="project", name=d, created_by="owner", status="created") for d in ("dataset-a", "dataset-b")])
    monkeypatch.setattr(research, "create_engine_from_settings", lambda _: engine)
    monkeypatch.setattr(research, "load_settings", lambda: SimpleNamespace())
    yield engine, people
    engine.dispose()


def test_lost_creation_response_replays_one_session_without_overwriting_edits(creation_store):
    engine, (owner, _) = creation_store
    request = research.ResearchSessionCreate(title="Original", datasetId="dataset-a", creationKey=str(uuid4()))
    first = research.create_session("project", request, owner)
    with engine.begin() as connection:
        connection.execute(update(sessions).where(sessions.c.id == first["id"]).values(title_override="Renamed", status="archived", is_pinned=True))
    second = research.create_session("project", request, owner)
    assert second["id"] == first["id"]
    assert second["creationKey"] == str(request.creationKey)
    assert (second["title"], second["status"], second["pinned"]) == ("Renamed", "archived", True)
    with engine.connect() as connection:
        assert connection.scalar(select(func.count()).select_from(sessions)) == 1


def test_concurrent_creation_retries_return_one_durable_session(creation_store):
    engine, (owner, _) = creation_store
    request = research.ResearchSessionCreate(title="Concurrent", creationKey=str(uuid4()))
    barrier = Barrier(4)
    def submit(_):
        barrier.wait(timeout=10)
        return research.create_session("project", request, owner)["id"]
    with ThreadPoolExecutor(max_workers=4) as pool:
        ids = list(pool.map(submit, range(4)))
    assert len(set(ids)) == 1
    with engine.connect() as connection:
        assert connection.scalar(select(func.count()).select_from(sessions)) == 1


def test_creation_identity_is_scoped_to_account_project_and_dataset(creation_store):
    _, (owner, member) = creation_store
    key = str(uuid4())
    ids = [research.create_session(p, research.ResearchSessionCreate(title="Same", datasetId=d, creationKey=key), user)["id"]
           for p, d, user in [("project", None, owner), ("other", None, owner), ("project", None, member), ("project", "dataset-a", owner), ("project", "dataset-b", owner)]]
    assert len(set(ids)) == 5


def test_replay_rechecks_current_write_authority(creation_store):
    engine, (_, member) = creation_store
    request = research.ResearchSessionCreate(creationKey=str(uuid4()))
    research.create_session("project", request, member)
    with engine.begin() as connection:
        connection.execute(update(project_members).where(project_members.c.user_id == member.id).values(role="viewer"))
    with pytest.raises(HTTPException) as denied:
        research.create_session("project", request, member)
    assert denied.value.status_code == 403


def test_legacy_creation_without_key_still_creates_distinct_sessions(creation_store):
    _, (owner, _) = creation_store
    request = research.ResearchSessionCreate(title="Same")
    assert research.create_session("project", request, owner)["id"] != research.create_session("project", request, owner)["id"]
