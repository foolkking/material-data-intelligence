"""SQLAlchemy scientific workspace persistence."""

from __future__ import annotations

from typing import Any, Mapping

from sqlalchemy import and_, func, insert, or_, select, update
from sqlalchemy.engine import Connection
from sqlalchemy.exc import IntegrityError

from mdi_schemas import (
    ScientificWorkspace,
    WorkspaceLayoutRevision,
    WorkspaceLayoutState,
    WorkspacePanel,
    WorkspaceSelectionContext,
    WORKSPACE_MAX_LAYOUT_REVISIONS,
    WORKSPACE_MAX_PANELS,
)
from mdi_api.application.workspaces.ports import (
    WorkspaceCapacityError,
    WorkspaceConflictError,
    WorkspaceNotFoundError,
)
from mdi_api.db import (
    analysis_intents,
    analysis_plans,
    artifacts,
    capability_eligibility_resolutions,
    capability_planning_decisions,
    capability_planning_executions,
    data_profiles,
    datasets,
    dependency_execution_records,
    jobs,
    scientific_interpretations,
    scientific_workspaces,
    tool_calls,
    workspace_layout_revisions,
    workspace_panels,
)
from mdi_api.infrastructure.persistence.base import _SqlAlchemyRepository, _row_to_json_dict
from mdi_api.infrastructure.persistence.workspace_common import (
    _WORKSPACE_UNSET,
    _enforce_workspace_project,
    _parse_workspace,
    _parse_workspace_layout_revision,
    _parse_workspace_panel,
    _prepare_workspace_update,
    _validate_layout_panel_membership,
    _validate_panel_project_scope,
    _validate_workspace_create_aggregate,
    _workspace_layout_record,
    _workspace_layout_values,
    _workspace_panel_record,
    _workspace_panel_values,
    _workspace_record,
    _workspace_source_identity,
    _workspace_values,
)

class SqlAlchemyWorkspaceRepository(_SqlAlchemyRepository):
    def create_workspace(
        self,
        workspace: ScientificWorkspace | Mapping[str, Any],
        *,
        panels: list[WorkspacePanel | Mapping[str, Any]] | tuple[WorkspacePanel | Mapping[str, Any], ...] = (),
        initial_layout: WorkspaceLayoutRevision | Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        parsed = _parse_workspace(workspace)
        parsed_panels = tuple(_parse_workspace_panel(panel) for panel in panels)
        parsed_layout = None if initial_layout is None else _parse_workspace_layout_revision(initial_layout)
        _validate_workspace_create_aggregate(parsed, parsed_panels, parsed_layout)
        values = _workspace_values(parsed)

        def run(connection: Connection) -> None:
            existing = connection.execute(
                select(scientific_workspaces).where(
                    or_(
                        scientific_workspaces.c.workspace_id == parsed.workspaceId,
                        and_(
                            scientific_workspaces.c.project_id == parsed.projectId,
                            scientific_workspaces.c.source_job_id == parsed.sourceJobId,
                        ),
                    )
                )
            ).mappings().first()
            if existing is not None:
                self._assert_create_compatible(connection, existing, parsed, parsed_panels, parsed_layout)
                return
            try:
                with connection.begin_nested():
                    connection.execute(insert(scientific_workspaces).values(**values))
                    for panel in parsed_panels:
                        connection.execute(insert(workspace_panels).values(**_workspace_panel_values(panel)))
                    if parsed_layout is not None:
                        connection.execute(
                            insert(workspace_layout_revisions).values(**_workspace_layout_values(parsed_layout))
                        )
            except IntegrityError as exc:
                existing = connection.execute(
                    select(scientific_workspaces).where(
                        and_(
                            scientific_workspaces.c.project_id == parsed.projectId,
                            scientific_workspaces.c.source_job_id == parsed.sourceJobId,
                        )
                    )
                ).mappings().first()
                if existing is None:
                    raise WorkspaceConflictError("WORKSPACE_CREATE_CONFLICT") from exc
                self._assert_create_compatible(connection, existing, parsed, parsed_panels, parsed_layout)

        self._with_connection(run)
        return self.get(parsed.workspaceId, project_id=parsed.projectId)

    create = create_workspace

    def get(self, workspace_id: str, *, project_id: str | None = None) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            row = connection.execute(
                select(scientific_workspaces).where(scientific_workspaces.c.workspace_id == workspace_id)
            ).mappings().first()
            if row is None:
                raise WorkspaceNotFoundError()
            normalized = _row_to_json_dict(row)
            _enforce_workspace_project(normalized["project_id"], project_id)
            return self._aggregate_record(connection, normalized)

        return self._with_connection(run)

    def get_by_project_job(self, project_id: str, source_job_id: str) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            row = connection.execute(
                select(scientific_workspaces).where(
                    and_(
                        scientific_workspaces.c.project_id == project_id,
                        scientific_workspaces.c.source_job_id == source_job_id,
                    )
                )
            ).mappings().first()
            if row is None:
                raise WorkspaceNotFoundError()
            return self._aggregate_record(connection, _row_to_json_dict(row))

        return self._with_connection(run)

    get_by_project_and_job = get_by_project_job

    def list_by_project(self, project_id: str) -> list[dict[str, Any]]:
        def run(connection: Connection) -> list[dict[str, Any]]:
            rows = connection.execute(
                select(scientific_workspaces)
                .where(scientific_workspaces.c.project_id == project_id)
                .order_by(scientific_workspaces.c.updated_at.desc(), scientific_workspaces.c.workspace_id)
            ).mappings().all()
            return [self._aggregate_record(connection, _row_to_json_dict(row)) for row in rows]

        return self._with_connection(run)

    def list_projection_metadata_by_project(self, project_id: str) -> list[dict[str, Any]]:
        """Load bounded Workspace list metadata in one SQL statement."""
        artifact_count = (
            select(func.count())
            .select_from(artifacts)
            .where(artifacts.c.job_id == scientific_workspaces.c.source_job_id)
            .scalar_subquery()
        )
        tool_call_count = (
            select(func.count())
            .select_from(tool_calls)
            .where(tool_calls.c.job_id == scientific_workspaces.c.source_job_id)
            .scalar_subquery()
        )
        interpretation_count = (
            select(func.count())
            .select_from(scientific_interpretations)
            .where(scientific_interpretations.c.job_id == scientific_workspaces.c.source_job_id)
            .scalar_subquery()
        )
        panel_count = (
            select(func.count())
            .select_from(workspace_panels)
            .where(workspace_panels.c.workspace_id == scientific_workspaces.c.workspace_id)
            .scalar_subquery()
        )
        source = (
            scientific_workspaces
            .outerjoin(jobs, jobs.c.id == scientific_workspaces.c.source_job_id)
            .outerjoin(datasets, datasets.c.id == scientific_workspaces.c.dataset_id)
            .outerjoin(data_profiles, data_profiles.c.id == scientific_workspaces.c.profile_id)
            .outerjoin(analysis_intents, analysis_intents.c.id == scientific_workspaces.c.intent_id)
            .outerjoin(analysis_plans, analysis_plans.c.id == scientific_workspaces.c.plan_id)
            .outerjoin(
                capability_planning_executions,
                capability_planning_executions.c.job_id == scientific_workspaces.c.source_job_id,
            )
            .outerjoin(
                capability_planning_decisions,
                capability_planning_decisions.c.id
                == capability_planning_executions.c.decision_id,
            )
            .outerjoin(
                capability_eligibility_resolutions,
                capability_eligibility_resolutions.c.id
                == capability_planning_decisions.c.resolution_id,
            )
            .outerjoin(
                dependency_execution_records,
                dependency_execution_records.c.job_id
                == scientific_workspaces.c.source_job_id,
            )
        )
        statement = (
            select(
                scientific_workspaces,
                jobs.c.id.label("current_job_id"),
                jobs.c.status.label("current_job_status"),
                datasets.c.id.label("current_dataset_id"),
                data_profiles.c.id.label("current_profile_id"),
                data_profiles.c.profile_json.label("current_profile_json"),
                analysis_intents.c.id.label("current_intent_id"),
                analysis_intents.c.intent_hash.label("current_intent_hash"),
                analysis_plans.c.id.label("current_plan_id"),
                analysis_plans.c.plan_hash.label("current_plan_hash"),
                capability_planning_executions.c.id.label("current_capability_execution_id"),
                capability_planning_decisions.c.id.label("current_decision_id"),
                capability_eligibility_resolutions.c.id.label("current_resolution_id"),
                dependency_execution_records.c.outcome.label("dependency_outcome"),
                artifact_count.label("artifact_count"),
                tool_call_count.label("tool_call_count"),
                interpretation_count.label("interpretation_count"),
                panel_count.label("panel_count"),
            )
            .select_from(source)
            .where(scientific_workspaces.c.project_id == project_id)
            .order_by(
                scientific_workspaces.c.updated_at.desc(),
                scientific_workspaces.c.workspace_id,
            )
        )
        return self._fetch_all_dicts(statement)

    def save_panel(
        self,
        panel: WorkspacePanel | Mapping[str, Any],
        *,
        project_id: str | None = None,
    ) -> dict[str, Any]:
        parsed = _parse_workspace_panel(panel)

        def run(connection: Connection) -> dict[str, Any]:
            workspace = self._workspace_row(connection, parsed.workspaceId, for_update=True)
            _enforce_workspace_project(workspace["project_id"], project_id)
            _validate_panel_project_scope(parsed, workspace["project_id"])
            existing = connection.execute(
                select(workspace_panels).where(
                    and_(
                        workspace_panels.c.workspace_id == parsed.workspaceId,
                        workspace_panels.c.panel_id == parsed.panelId,
                    )
                )
            ).mappings().first()
            if existing is not None:
                normalized = _row_to_json_dict(existing)
                if normalized["panel_state_hash"] != parsed.panelStateHash:
                    raise WorkspaceConflictError("WORKSPACE_PANEL_IMMUTABLE_CONFLICT")
                return _workspace_panel_record(normalized)
            count = connection.execute(
                select(func.count()).select_from(workspace_panels).where(
                    workspace_panels.c.workspace_id == parsed.workspaceId
                )
            ).scalar_one()
            if int(count) >= WORKSPACE_MAX_PANELS:
                raise WorkspaceCapacityError("PANEL_CAP_EXCEEDED")
            try:
                with connection.begin_nested():
                    connection.execute(insert(workspace_panels).values(**_workspace_panel_values(parsed)))
            except IntegrityError as exc:
                existing = connection.execute(
                    select(workspace_panels).where(
                        and_(
                            workspace_panels.c.workspace_id == parsed.workspaceId,
                            workspace_panels.c.panel_id == parsed.panelId,
                        )
                    )
                ).mappings().first()
                if existing is None or existing["panel_state_hash"] != parsed.panelStateHash:
                    raise WorkspaceConflictError("WORKSPACE_PANEL_IMMUTABLE_CONFLICT") from exc
            row = connection.execute(
                select(workspace_panels).where(
                    and_(
                        workspace_panels.c.workspace_id == parsed.workspaceId,
                        workspace_panels.c.panel_id == parsed.panelId,
                    )
                )
            ).mappings().one()
            return _workspace_panel_record(_row_to_json_dict(row))

        return self._with_connection(run)

    def save_panels(
        self,
        panels: list[WorkspacePanel | Mapping[str, Any]] | tuple[WorkspacePanel | Mapping[str, Any], ...],
        *,
        project_id: str | None = None,
    ) -> list[dict[str, Any]]:
        parsed = tuple(_parse_workspace_panel(panel) for panel in panels)
        if len({(panel.workspaceId, panel.panelId) for panel in parsed}) != len(parsed):
            raise WorkspaceConflictError("WORKSPACE_PANEL_DUPLICATE")
        return [self.save_panel(panel, project_id=project_id) for panel in parsed]

    def get_panel(
        self,
        workspace_id: str,
        panel_id: str,
        *,
        project_id: str | None = None,
    ) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            workspace = self._workspace_row(connection, workspace_id)
            _enforce_workspace_project(workspace["project_id"], project_id)
            row = connection.execute(
                select(workspace_panels).where(
                    and_(
                        workspace_panels.c.workspace_id == workspace_id,
                        workspace_panels.c.panel_id == panel_id,
                    )
                )
            ).mappings().first()
            if row is None:
                raise WorkspaceNotFoundError("WORKSPACE_PANEL_NOT_FOUND")
            return _workspace_panel_record(_row_to_json_dict(row))

        return self._with_connection(run)

    def list_panels(self, workspace_id: str, *, project_id: str | None = None) -> list[dict[str, Any]]:
        def run(connection: Connection) -> list[dict[str, Any]]:
            workspace = self._workspace_row(connection, workspace_id)
            _enforce_workspace_project(workspace["project_id"], project_id)
            rows = connection.execute(
                select(workspace_panels)
                .where(workspace_panels.c.workspace_id == workspace_id)
                .order_by(workspace_panels.c.ordinal, workspace_panels.c.panel_id)
            ).mappings().all()
            return [_workspace_panel_record(_row_to_json_dict(row)) for row in rows]

        return self._with_connection(run)

    def append_layout_revision(
        self,
        revision: WorkspaceLayoutRevision | Mapping[str, Any],
        *,
        expected_revision: int,
        project_id: str | None = None,
    ) -> dict[str, Any]:
        parsed = _parse_workspace_layout_revision(revision)

        def run(connection: Connection) -> dict[str, Any]:
            workspace = self._workspace_row(connection, parsed.workspaceId, for_update=True)
            _enforce_workspace_project(workspace["project_id"], project_id)
            existing = connection.execute(
                select(workspace_layout_revisions).where(
                    and_(
                        workspace_layout_revisions.c.workspace_id == parsed.workspaceId,
                        workspace_layout_revisions.c.revision == parsed.revision,
                    )
                )
            ).mappings().first()
            if existing is not None:
                if existing["semantic_hash"] != parsed.semanticHash:
                    raise WorkspaceConflictError("WORKSPACE_LAYOUT_IMMUTABLE_CONFLICT")
                if int(workspace["revision"]) != parsed.revision:
                    raise WorkspaceConflictError("WORKSPACE_REVISION_MISMATCH")
                return _workspace_layout_record(_row_to_json_dict(existing))
            self._validate_new_layout(connection, workspace, parsed, expected_revision)
            result = connection.execute(
                update(scientific_workspaces)
                .where(
                    and_(
                        scientific_workspaces.c.workspace_id == parsed.workspaceId,
                        scientific_workspaces.c.revision == expected_revision,
                    )
                )
                .values(
                    revision=parsed.revision,
                    active_panel_id=parsed.layout.activePanelId,
                    pinned_selection_json=None if parsed.selection is None else parsed.selection.model_dump(mode="json"),
                    updated_at=parsed.createdAt,
                )
            )
            if result.rowcount != 1:
                raise WorkspaceConflictError("WORKSPACE_REVISION_MISMATCH")
            try:
                with connection.begin_nested():
                    connection.execute(
                        insert(workspace_layout_revisions).values(**_workspace_layout_values(parsed))
                    )
            except IntegrityError as exc:
                raise WorkspaceConflictError("WORKSPACE_LAYOUT_IMMUTABLE_CONFLICT") from exc
            return _workspace_layout_record(_workspace_layout_values(parsed))

        return self._with_connection(run)

    def get_layout_revision(
        self,
        workspace_id: str,
        revision: int,
        *,
        project_id: str | None = None,
    ) -> dict[str, Any]:
        def run(connection: Connection) -> dict[str, Any]:
            workspace = self._workspace_row(connection, workspace_id)
            _enforce_workspace_project(workspace["project_id"], project_id)
            row = connection.execute(
                select(workspace_layout_revisions).where(
                    and_(
                        workspace_layout_revisions.c.workspace_id == workspace_id,
                        workspace_layout_revisions.c.revision == revision,
                    )
                )
            ).mappings().first()
            if row is None:
                raise WorkspaceNotFoundError("WORKSPACE_LAYOUT_REVISION_NOT_FOUND")
            return _workspace_layout_record(_row_to_json_dict(row))

        return self._with_connection(run)

    def get_current_layout(self, workspace_id: str, *, project_id: str | None = None) -> dict[str, Any] | None:
        def run(connection: Connection) -> dict[str, Any] | None:
            workspace = self._workspace_row(connection, workspace_id)
            _enforce_workspace_project(workspace["project_id"], project_id)
            row = connection.execute(
                select(workspace_layout_revisions).where(
                    and_(
                        workspace_layout_revisions.c.workspace_id == workspace_id,
                        workspace_layout_revisions.c.revision == workspace["revision"],
                    )
                )
            ).mappings().first()
            return None if row is None else _workspace_layout_record(_row_to_json_dict(row))

        return self._with_connection(run)

    def list_layout_revisions(
        self,
        workspace_id: str,
        *,
        project_id: str | None = None,
    ) -> list[dict[str, Any]]:
        def run(connection: Connection) -> list[dict[str, Any]]:
            workspace = self._workspace_row(connection, workspace_id)
            _enforce_workspace_project(workspace["project_id"], project_id)
            rows = connection.execute(
                select(workspace_layout_revisions)
                .where(workspace_layout_revisions.c.workspace_id == workspace_id)
                .order_by(workspace_layout_revisions.c.revision)
            ).mappings().all()
            return [_workspace_layout_record(_row_to_json_dict(row)) for row in rows]

        return self._with_connection(run)

    def update_workspace(
        self,
        workspace_id: str,
        *,
        expected_revision: int,
        project_id: str | None = None,
        title: str | object = _WORKSPACE_UNSET,
        active_panel_id: str | None | object = _WORKSPACE_UNSET,
        pinned_selection: WorkspaceSelectionContext | Mapping[str, Any] | None | object = _WORKSPACE_UNSET,
        layout: WorkspaceLayoutState | Mapping[str, Any] | None = None,
        layout_revision: WorkspaceLayoutRevision | Mapping[str, Any] | None = None,
        created_by: str | None = None,
    ) -> dict[str, Any]:
        def run(connection: Connection) -> bool:
            workspace = self._workspace_row(connection, workspace_id, for_update=True)
            _enforce_workspace_project(workspace["project_id"], project_id)
            if int(workspace["revision"]) != expected_revision:
                raise WorkspaceConflictError("WORKSPACE_REVISION_MISMATCH")
            current_layout_row = connection.execute(
                select(workspace_layout_revisions).where(
                    and_(
                        workspace_layout_revisions.c.workspace_id == workspace_id,
                        workspace_layout_revisions.c.revision == expected_revision,
                    )
                )
            ).mappings().first()
            panel_rows = connection.execute(
                select(workspace_panels)
                .where(workspace_panels.c.workspace_id == workspace_id)
                .order_by(workspace_panels.c.ordinal, workspace_panels.c.panel_id)
            ).mappings().all()
            current_record = _workspace_record(
                workspace,
                [_row_to_json_dict(row) for row in panel_rows],
                None if current_layout_row is None else _row_to_json_dict(current_layout_row),
            )
            next_revision, next_title = _prepare_workspace_update(
                workspace_record=current_record,
                current_layout=None if current_layout_row is None else _workspace_layout_record(current_layout_row),
                panel_records=[_workspace_panel_record(row) for row in panel_rows],
                expected_revision=expected_revision,
                title=title,
                active_panel_id=active_panel_id,
                pinned_selection=pinned_selection,
                layout=layout,
                layout_revision=layout_revision,
                created_by=created_by,
            )
            if next_revision is None:
                return False
            self._validate_new_layout(connection, workspace, next_revision, expected_revision)
            result = connection.execute(
                update(scientific_workspaces)
                .where(
                    and_(
                        scientific_workspaces.c.workspace_id == workspace_id,
                        scientific_workspaces.c.revision == expected_revision,
                    )
                )
                .values(
                    title=next_title,
                    active_panel_id=next_revision.layout.activePanelId,
                    pinned_selection_json=(
                        None
                        if next_revision.selection is None
                        else next_revision.selection.model_dump(mode="json")
                    ),
                    revision=next_revision.revision,
                    updated_at=next_revision.createdAt,
                )
            )
            if result.rowcount != 1:
                raise WorkspaceConflictError("WORKSPACE_REVISION_MISMATCH")
            try:
                with connection.begin_nested():
                    connection.execute(
                        insert(workspace_layout_revisions).values(**_workspace_layout_values(next_revision))
                    )
            except IntegrityError as exc:
                raise WorkspaceConflictError("WORKSPACE_LAYOUT_IMMUTABLE_CONFLICT") from exc
            return True

        self._with_connection(run)
        return self.get(workspace_id, project_id=project_id)

    update = update_workspace

    def _workspace_row(
        self,
        connection: Connection,
        workspace_id: str,
        *,
        for_update: bool = False,
    ) -> dict[str, Any]:
        statement = select(scientific_workspaces).where(
            scientific_workspaces.c.workspace_id == workspace_id
        )
        if for_update:
            statement = statement.with_for_update()
        row = connection.execute(statement).mappings().first()
        if row is None:
            raise WorkspaceNotFoundError()
        return _row_to_json_dict(row)

    def _aggregate_record(self, connection: Connection, workspace: Mapping[str, Any]) -> dict[str, Any]:
        panel_rows = connection.execute(
            select(workspace_panels)
            .where(workspace_panels.c.workspace_id == workspace["workspace_id"])
            .order_by(workspace_panels.c.ordinal, workspace_panels.c.panel_id)
        ).mappings().all()
        layout_row = connection.execute(
            select(workspace_layout_revisions).where(
                and_(
                    workspace_layout_revisions.c.workspace_id == workspace["workspace_id"],
                    workspace_layout_revisions.c.revision == workspace["revision"],
                )
            )
        ).mappings().first()
        return _workspace_record(
            workspace,
            [_row_to_json_dict(row) for row in panel_rows],
            None if layout_row is None else _row_to_json_dict(layout_row),
        )

    def _validate_new_layout(
        self,
        connection: Connection,
        workspace: Mapping[str, Any],
        revision: WorkspaceLayoutRevision,
        expected_revision: int,
    ) -> None:
        if int(workspace["revision"]) != expected_revision:
            raise WorkspaceConflictError("WORKSPACE_REVISION_MISMATCH")
        count = int(connection.execute(
            select(func.count()).select_from(workspace_layout_revisions).where(
                workspace_layout_revisions.c.workspace_id == revision.workspaceId
            )
        ).scalar_one())
        if count >= WORKSPACE_MAX_LAYOUT_REVISIONS:
            raise WorkspaceCapacityError("REVISION_CAP_EXCEEDED")
        initial = count == 0 and revision.revision == int(workspace["revision"]) == expected_revision
        if not initial and revision.revision != expected_revision + 1:
            raise WorkspaceConflictError("WORKSPACE_LAYOUT_REVISION_SEQUENCE_INVALID")
        panel_ids = set(connection.execute(
            select(workspace_panels.c.panel_id).where(workspace_panels.c.workspace_id == revision.workspaceId)
        ).scalars().all())
        _validate_layout_panel_membership(revision.layout, panel_ids)

    def _assert_create_compatible(
        self,
        connection: Connection,
        existing: Mapping[str, Any],
        requested: ScientificWorkspace,
        panels: tuple[WorkspacePanel, ...],
        layout: WorkspaceLayoutRevision | None,
    ) -> None:
        normalized = _row_to_json_dict(existing)
        if _workspace_source_identity(normalized) != _workspace_source_identity(_workspace_values(requested)):
            raise WorkspaceConflictError("WORKSPACE_SEMANTIC_CONFLICT")
        for panel in panels:
            row = connection.execute(
                select(workspace_panels.c.panel_state_hash).where(
                    and_(
                        workspace_panels.c.workspace_id == requested.workspaceId,
                        workspace_panels.c.panel_id == panel.panelId,
                    )
                )
            ).scalar_one_or_none()
            if row != panel.panelStateHash:
                raise WorkspaceConflictError("WORKSPACE_SEMANTIC_CONFLICT")
        if layout is not None:
            semantic_hash = connection.execute(
                select(workspace_layout_revisions.c.semantic_hash).where(
                    and_(
                        workspace_layout_revisions.c.workspace_id == requested.workspaceId,
                        workspace_layout_revisions.c.revision == layout.revision,
                    )
                )
            ).scalar_one_or_none()
            if semantic_hash != layout.semanticHash:
                raise WorkspaceConflictError("WORKSPACE_SEMANTIC_CONFLICT")

__all__ = ["SqlAlchemyWorkspaceRepository"]
