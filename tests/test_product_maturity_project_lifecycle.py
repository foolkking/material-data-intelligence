from __future__ import annotations

from sqlalchemy import create_engine, insert, select
from sqlalchemy.pool import StaticPool

from mdi_api.db import metadata, project_members
from mdi_api.unit_of_work import RepositoryFactory


def test_new_project_persists_explicit_owner_membership() -> None:
    """New projects must participate in the same membership boundary as reads."""

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    metadata.create_all(engine)
    with engine.begin() as connection:
        # The repository creates the actor and organization as part of save.
        RepositoryFactory(engine).create_repositories().projects.save(
            {
                "projectId": "project_lifecycle_owner",
                "organizationId": "org_lifecycle",
                "name": "Lifecycle owner project",
                "createdBy": "user_lifecycle_owner",
            }
        )
        membership = connection.execute(
            select(project_members.c.role).where(
                project_members.c.project_id == "project_lifecycle_owner",
                project_members.c.user_id == "user_lifecycle_owner",
            )
        ).scalar_one()

    assert membership == "owner"
    RepositoryFactory(engine).create_repositories().projects.save(
        {
            "projectId": "project_lifecycle_owner",
            "organizationId": "org_lifecycle",
            "name": "Lifecycle owner project renamed",
            "createdBy": "user_lifecycle_owner",
        }
    )
    with engine.connect() as connection:
        assert connection.execute(
            select(project_members.c.role).where(
                project_members.c.project_id == "project_lifecycle_owner",
                project_members.c.user_id == "user_lifecycle_owner",
            )
        ).scalar_one() == "owner"
    engine.dispose()
