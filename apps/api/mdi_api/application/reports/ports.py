"""Persistence contracts for recipes and generated reports."""

from __future__ import annotations

from typing import Any, Mapping, Protocol

from mdi_schemas import VisualizationRecipe


class RecipeRepository(Protocol):
    def save(self, recipe: VisualizationRecipe | Mapping[str, Any]) -> dict[str, Any]:
        ...

    def create_immutable(self, recipe: Mapping[str, Any]) -> dict[str, Any]:
        ...

    def get(self, recipe_id: str) -> dict[str, Any]:
        ...

    def list_for_job(self, job_id: str) -> list[dict[str, Any]]:
        ...

    def list_by_project(self, project_id: str) -> list[dict[str, Any]]:
        ...


class ReportRepository(Protocol):
    def save(self, report: Mapping[str, Any]) -> dict[str, Any]:
        ...

    def create_immutable(self, report: Mapping[str, Any]) -> dict[str, Any]:
        ...

    def get(self, report_id: str) -> dict[str, Any]:
        ...

    def list_for_job(self, job_id: str) -> list[dict[str, Any]]:
        ...

    def list_by_project(self, project_id: str) -> list[dict[str, Any]]:
        ...


__all__ = ["RecipeRepository", "ReportRepository"]
