"""SQLAlchemy recipe and report persistence implementations."""

from __future__ import annotations

from typing import Any, Mapping

from sqlalchemy import delete, insert, select
from sqlalchemy.engine import Connection

from mdi_schemas import VisualizationRecipe
from mdi_api.db import reports, visualization_recipes
from mdi_api.infrastructure.persistence.base import (
    _SqlAlchemyRepository,
    _json_copy,
    _model_to_record,
    _required_id,
    _iso,
)
from mdi_api.infrastructure.persistence.sql_common import ensure_user

class SqlAlchemyRecipeRepository(_SqlAlchemyRepository):
    def save(self, recipe: VisualizationRecipe | Mapping[str, Any]) -> dict[str, Any]:
        record = _model_to_record(recipe)
        recipe_id = _required_id(record, "recipeId")
        created_by = str(record.get("createdBy") or record.get("created_by") or "user_local")
        values = {
            "id": recipe_id,
            "project_id": str(record["projectId"]),
            "source_job_id": record.get("sourceJobId"),
            "name": str(record.get("name") or recipe_id),
            "recipe_json": _json_copy(record),
            "created_by": created_by,
        }

        def run(connection: Connection) -> None:
            ensure_user(connection, user_id=created_by)
            connection.execute(delete(visualization_recipes).where(visualization_recipes.c.id == recipe_id))
            connection.execute(insert(visualization_recipes).values(**values))

        self._with_connection(run)
        return self.get(recipe_id)

    def create_immutable(self, recipe: Mapping[str, Any]) -> dict[str, Any]:
        record = _json_copy(recipe)
        recipe_id = _required_id(record, "recipeId")
        created_by = str(record.get("createdBy") or record.get("created_by") or "user_local")
        values = {
            "id": recipe_id,
            "project_id": str(record["projectId"]),
            "source_job_id": record.get("sourceJobId"),
            "name": str(record.get("name") or recipe_id),
            "recipe_json": record,
            "created_by": created_by,
        }

        def run(connection: Connection) -> None:
            existing = connection.execute(
                select(visualization_recipes.c.recipe_json).where(visualization_recipes.c.id == recipe_id)
            ).scalar_one_or_none()
            if existing is not None:
                _assert_immutable_delivery_compatible(_json_copy(existing), record, kind="Recipe")
                return
            ensure_user(connection, user_id=created_by)
            connection.execute(insert(visualization_recipes).values(**values))

        self._with_connection(run)
        return self.get(recipe_id)

    def get(self, recipe_id: str) -> dict[str, Any]:
        row = self._fetch_one_dict(select(visualization_recipes).where(visualization_recipes.c.id == recipe_id))
        return _recipe_from_row(row)

    def list_for_job(self, job_id: str) -> list[dict[str, Any]]:
        statement = (
            select(visualization_recipes)
            .where(visualization_recipes.c.source_job_id == job_id)
            .order_by(visualization_recipes.c.created_at, visualization_recipes.c.id)
        )
        return [_recipe_from_row(row) for row in self._fetch_all_dicts(statement)]

    def list_by_project(self, project_id: str) -> list[dict[str, Any]]:
        statement = (
            select(visualization_recipes)
            .where(visualization_recipes.c.project_id == project_id)
            .order_by(visualization_recipes.c.created_at.desc(), visualization_recipes.c.id)
        )
        return [_recipe_from_row(row) for row in self._fetch_all_dicts(statement)]

class SqlAlchemyReportRepository(_SqlAlchemyRepository):
    def save(self, report: Mapping[str, Any]) -> dict[str, Any]:
        record = _json_copy(report)
        report_id = _required_id(record, "reportId")
        created_by = str(record.get("createdBy") or record.get("created_by") or "user_local")
        job_id_value = record.get("jobId") or record.get("sourceJobId")
        if not job_id_value:
            raise ValueError("Report record is missing jobId/sourceJobId")
        job_id = str(job_id_value)
        values = {
            "id": report_id,
            "project_id": str(record["projectId"]),
            "dataset_id": record.get("datasetId"),
            "job_id": job_id,
            "version": str(record.get("version") or "1"),
            "title": str(record.get("title") or record.get("name") or report_id),
            "markdown_key": record.get("markdownKey") or record.get("markdownArtifactKey"),
            "html_key": record.get("htmlKey") or record.get("htmlArtifactKey"),
            "report_json": record,
            "created_by": created_by,
        }

        def run(connection: Connection) -> None:
            ensure_user(connection, user_id=created_by)
            connection.execute(delete(reports).where(reports.c.id == report_id))
            connection.execute(insert(reports).values(**values))

        self._with_connection(run)
        return self.get(report_id)

    def create_immutable(self, report: Mapping[str, Any]) -> dict[str, Any]:
        record = _json_copy(report)
        report_id = _required_id(record, "reportId")
        created_by = str(record.get("createdBy") or record.get("created_by") or "user_local")
        job_id_value = record.get("jobId") or record.get("sourceJobId")
        if not job_id_value:
            raise ValueError("Report record is missing jobId/sourceJobId")
        values = {
            "id": report_id,
            "project_id": str(record["projectId"]),
            "dataset_id": record.get("datasetId"),
            "job_id": str(job_id_value),
            "version": str(record.get("version") or "1"),
            "title": str(record.get("title") or record.get("name") or report_id),
            "markdown_key": record.get("markdownKey") or record.get("markdownArtifactKey"),
            "html_key": record.get("htmlKey") or record.get("htmlArtifactKey"),
            "report_json": record,
            "created_by": created_by,
        }

        def run(connection: Connection) -> None:
            existing = connection.execute(
                select(reports.c.report_json).where(reports.c.id == report_id)
            ).scalar_one_or_none()
            if existing is not None:
                _assert_immutable_delivery_compatible(_json_copy(existing), record, kind="Report")
                return
            ensure_user(connection, user_id=created_by)
            connection.execute(insert(reports).values(**values))

        self._with_connection(run)
        return self.get(report_id)

    def get(self, report_id: str) -> dict[str, Any]:
        return _report_from_row(self._fetch_one_dict(select(reports).where(reports.c.id == report_id)))

    def list_for_job(self, job_id: str) -> list[dict[str, Any]]:
        statement = select(reports).where(reports.c.job_id == job_id).order_by(reports.c.created_at, reports.c.id)
        return [_report_from_row(row) for row in self._fetch_all_dicts(statement)]

    def list_by_project(self, project_id: str) -> list[dict[str, Any]]:
        statement = select(reports).where(reports.c.project_id == project_id).order_by(reports.c.created_at.desc(), reports.c.id)
        return [_report_from_row(row) for row in self._fetch_all_dicts(statement)]

def _recipe_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    recipe = _json_copy(row.get("recipe_json") or {})
    recipe.setdefault("recipeId", row["id"])
    recipe.setdefault("id", row["id"])
    recipe.setdefault("projectId", row["project_id"])
    recipe.setdefault("sourceJobId", row["source_job_id"])
    recipe.setdefault("name", row["name"])
    recipe["createdAt"] = _iso(row["created_at"])
    return recipe

def _report_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    report = _json_copy(row.get("report_json") or {})
    report.setdefault("id", row["id"])
    report.setdefault("reportId", row["id"])
    report.setdefault("projectId", row["project_id"])
    report.setdefault("datasetId", row["dataset_id"])
    report.setdefault("jobId", row["job_id"])
    report.setdefault("sourceJobId", row["job_id"])
    report.setdefault("version", row["version"])
    report.setdefault("title", row["title"])
    report.setdefault("markdownKey", row["markdown_key"])
    report.setdefault("htmlKey", row["html_key"])
    report["createdBy"] = report.get("createdBy") or row["created_by"]
    report["createdAt"] = report.get("createdAt") or _iso(row["created_at"])
    return report

def _assert_immutable_delivery_compatible(
    existing: Mapping[str, Any],
    candidate: Mapping[str, Any],
    *,
    kind: str,
) -> None:
    identity_fields = (
        "requestHash",
        "compositionHash",
        "reportId",
        "recipeId",
        "projectId",
        "sourceJobId",
        "workspaceId",
    )
    if any(existing.get(field) != candidate.get(field) for field in identity_fields):
        raise ValueError(f"{kind} immutable snapshot conflict")

__all__ = ["SqlAlchemyRecipeRepository", "SqlAlchemyReportRepository"]
