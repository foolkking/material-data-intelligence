"""Concrete repository bundle composition."""

from __future__ import annotations

from dataclasses import dataclass
from sqlalchemy.engine import Connection, Engine

from mdi_api.infrastructure.persistence.memory import (
    InMemoryDataProfileRepository,
    InMemoryDatasetRepository,
    InMemoryProjectRepository,
)
from mdi_api.infrastructure.persistence.memory_analysis_plans import InMemoryAnalysisPlanRepository
from mdi_api.infrastructure.persistence.memory_artifacts import InMemoryArtifactRepository
from mdi_api.infrastructure.persistence.memory_dependency import InMemoryDependencyExecutionRepository
from mdi_api.infrastructure.persistence.memory_interpretation import InMemoryScientificInterpretationRepository
from mdi_api.infrastructure.persistence.memory_jobs import (
    InMemoryJobEventRepository,
    InMemoryJobRepository,
    InMemoryToolCallRepository,
)
from mdi_api.infrastructure.persistence.memory_planning import (
    InMemoryAnalysisIntentRepository,
    InMemoryCapabilityPlanningRepository,
)
from mdi_api.infrastructure.persistence.memory_reports import InMemoryRecipeRepository, InMemoryReportRepository
from mdi_api.infrastructure.persistence.memory_workspace import InMemoryWorkspaceRepository
from mdi_api.infrastructure.persistence.sqlalchemy import (
    SqlAlchemyDataProfileRepository,
    SqlAlchemyDatasetRepository,
    SqlAlchemyProjectRepository,
)
from mdi_api.infrastructure.persistence.sqlalchemy_analysis_plans import SqlAlchemyAnalysisPlanRepository
from mdi_api.infrastructure.persistence.sqlalchemy_artifacts import SqlAlchemyArtifactRepository
from mdi_api.infrastructure.persistence.sqlalchemy_dependency import SqlAlchemyDependencyExecutionRepository
from mdi_api.infrastructure.persistence.sqlalchemy_interpretation import SqlAlchemyScientificInterpretationRepository
from mdi_api.infrastructure.persistence.sqlalchemy_jobs import (
    SqlAlchemyJobEventRepository,
    SqlAlchemyJobRepository,
    SqlAlchemyToolCallRepository,
)
from mdi_api.infrastructure.persistence.sqlalchemy_planning import (
    SqlAlchemyAnalysisIntentRepository,
    SqlAlchemyCapabilityPlanningRepository,
)
from mdi_api.infrastructure.persistence.sqlalchemy_reports import SqlAlchemyRecipeRepository, SqlAlchemyReportRepository
from mdi_api.infrastructure.persistence.sqlalchemy_workspace import SqlAlchemyWorkspaceRepository

@dataclass
class InMemoryRepositoryBundle:
    projects: "InMemoryProjectRepository"
    datasets: "InMemoryDatasetRepository"
    data_profiles: "InMemoryDataProfileRepository"
    analysis_intents: "InMemoryAnalysisIntentRepository"
    capability_planning: "InMemoryCapabilityPlanningRepository"
    dependency_execution: "InMemoryDependencyExecutionRepository"
    analysis_plans: "InMemoryAnalysisPlanRepository"
    jobs: "InMemoryJobRepository"
    job_events: "InMemoryJobEventRepository"
    tool_calls: "InMemoryToolCallRepository"
    artifacts: "InMemoryArtifactRepository"
    recipes: "InMemoryRecipeRepository"
    reports: "InMemoryReportRepository"
    interpretations: "InMemoryScientificInterpretationRepository"
    workspaces: "InMemoryWorkspaceRepository"

    @classmethod
    def create(cls) -> "InMemoryRepositoryBundle":
        datasets = InMemoryDatasetRepository()
        jobs = InMemoryJobRepository()
        analysis_plans_repository = InMemoryAnalysisPlanRepository(jobs)
        return cls(
            projects=InMemoryProjectRepository(),
            datasets=datasets,
            data_profiles=InMemoryDataProfileRepository(datasets),
            analysis_intents=InMemoryAnalysisIntentRepository(),
            capability_planning=InMemoryCapabilityPlanningRepository(),
            dependency_execution=InMemoryDependencyExecutionRepository(analysis_plans_repository),
            analysis_plans=analysis_plans_repository,
            jobs=jobs,
            job_events=InMemoryJobEventRepository(),
            tool_calls=InMemoryToolCallRepository(),
            artifacts=InMemoryArtifactRepository(),
            recipes=InMemoryRecipeRepository(),
            reports=InMemoryReportRepository(),
            interpretations=InMemoryScientificInterpretationRepository(),
            workspaces=InMemoryWorkspaceRepository(),
        )


@dataclass
class SqlAlchemyRepositoryBundle:
    projects: "SqlAlchemyProjectRepository"
    datasets: "SqlAlchemyDatasetRepository"
    data_profiles: "SqlAlchemyDataProfileRepository"
    analysis_intents: "SqlAlchemyAnalysisIntentRepository"
    capability_planning: "SqlAlchemyCapabilityPlanningRepository"
    dependency_execution: "SqlAlchemyDependencyExecutionRepository"
    analysis_plans: "SqlAlchemyAnalysisPlanRepository"
    jobs: "SqlAlchemyJobRepository"
    job_events: "SqlAlchemyJobEventRepository"
    tool_calls: "SqlAlchemyToolCallRepository"
    artifacts: "SqlAlchemyArtifactRepository"
    recipes: "SqlAlchemyRecipeRepository"
    reports: "SqlAlchemyReportRepository"
    interpretations: "SqlAlchemyScientificInterpretationRepository"
    workspaces: "SqlAlchemyWorkspaceRepository"

    @classmethod
    def create(cls, bind: Engine | Connection) -> "SqlAlchemyRepositoryBundle":
        return cls(
            projects=SqlAlchemyProjectRepository(bind),
            datasets=SqlAlchemyDatasetRepository(bind),
            data_profiles=SqlAlchemyDataProfileRepository(bind),
            analysis_intents=SqlAlchemyAnalysisIntentRepository(bind),
            capability_planning=SqlAlchemyCapabilityPlanningRepository(bind),
            dependency_execution=SqlAlchemyDependencyExecutionRepository(bind),
            analysis_plans=SqlAlchemyAnalysisPlanRepository(bind),
            jobs=SqlAlchemyJobRepository(bind),
            job_events=SqlAlchemyJobEventRepository(bind),
            tool_calls=SqlAlchemyToolCallRepository(bind),
            artifacts=SqlAlchemyArtifactRepository(bind),
            recipes=SqlAlchemyRecipeRepository(bind),
            reports=SqlAlchemyReportRepository(bind),
            interpretations=SqlAlchemyScientificInterpretationRepository(bind),
            workspaces=SqlAlchemyWorkspaceRepository(bind),
        )


__all__ = ["InMemoryRepositoryBundle", "SqlAlchemyRepositoryBundle"]
