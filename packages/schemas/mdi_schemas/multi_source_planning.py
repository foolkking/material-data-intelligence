"""Explicit source ownership for cross-dataset AnalysisPlan 0.3.

The inherited dataset/profile pair identifies the Job's routing context. It
does not assign that dataset to other inputs: every source version has its own
dataset, and every profile input names an exact persisted profile.
"""

from __future__ import annotations

from typing import Any, Literal, Mapping
from uuid import UUID

from pydantic import ConfigDict, Field, model_validator

from .dependency_planning import (
    AnalysisPlanV02,
    ArtifactLineageRecord,
    StrictDependencyModel,
    _safe_identifier,
    topological_order,
)
from .models import AnalysisStep, InputRef, MaterialObjectType


SCIENTIFIC_OBJECT_EXECUTION_TYPES = {
    "structure.crystal": "Structure", "structure.atomic": "Atoms",
    "trajectory.atomic": "Trajectory", "materials.dataset": "DataFrame",
    "materials.table": "DataFrame", "electronic.band_structure": "ElectronicBand",
    "electronic.dos": "ElectronicDos", "volumetric.field": "VolumetricData",
    "volumetric.charge_density": "VolumetricData", "phonon.band_structure": "PhononBand",
    "phonon.dos": "PhononDos", "diffraction.xrd.experimental": "DataFrame",
    "diffraction.xrd.theoretical": "Structure",
}


class AnalysisSourceContext(StrictDependencyModel):
    datasetId: str = Field(min_length=1, max_length=160)
    profileId: str = Field(min_length=1, max_length=160)

    @model_validator(mode="after")
    def validate_identity(self) -> "AnalysisSourceContext":
        _safe_identifier(self.datasetId, field="datasetId")
        _safe_identifier(self.profileId, field="profileId")
        return self


class AnalysisSourceVersion(StrictDependencyModel):
    objectId: UUID
    versionId: UUID
    datasetId: str = Field(min_length=1, max_length=160)
    objectType: MaterialObjectType

    @model_validator(mode="after")
    def validate_identity(self) -> "AnalysisSourceVersion":
        _safe_identifier(self.datasetId, field="datasetId")
        return self


class MultiSourceInputRef(InputRef):
    model_config = ConfigDict(extra="forbid", frozen=True)


class MultiSourceAnalysisStep(AnalysisStep):
    model_config = ConfigDict(extra="forbid", frozen=True)
    inputRefs: list[MultiSourceInputRef] = Field(max_length=64)


class AnalysisPlanV03(AnalysisPlanV02):
    schemaVersion: Literal["0.3"] = "0.3"
    steps: list[MultiSourceAnalysisStep] = Field(min_length=1, max_length=8)
    sourceContexts: list[AnalysisSourceContext] = Field(min_length=2, max_length=8)
    sourceVersions: list[AnalysisSourceVersion] = Field(min_length=2, max_length=64)

    @model_validator(mode="after")
    def validate_sources(self) -> "AnalysisPlanV03":
        datasets = [item.datasetId for item in self.sourceContexts]
        profiles = [item.profileId for item in self.sourceContexts]
        if datasets != sorted(set(datasets)) or len(profiles) != len(set(profiles)):
            raise ValueError("Source contexts require unique sorted datasets and distinct profiles.")
        contexts = {item.datasetId: item for item in self.sourceContexts}
        routing = contexts.get(self.datasetId)
        if routing is None or routing.profileId != self.profileId:
            raise ValueError("Job routing context must name one declared dataset/profile pair.")
        version_ids = [str(item.versionId) for item in self.sourceVersions]
        if version_ids != sorted(set(version_ids)):
            raise ValueError("Source versions must be unique and sorted by exact version identity.")
        if {item.datasetId for item in self.sourceVersions} != set(contexts):
            raise ValueError("Source contexts must cover exactly the source version datasets.")
        versions = {str(item.versionId): item for item in self.sourceVersions}
        steps = {item.stepId: item for item in self.steps}
        ancestry: dict[str, set[str]] = {}
        used: set[str] = set()
        for step_id in topological_order(self.steps, self.dependencyBindings):
            step = steps[step_id]
            declared = step.output.get("sourceObjectVersionIds")
            if (
                not isinstance(declared, list)
                or not declared
                or not all(isinstance(item, str) and item in versions for item in declared)
                or len(declared) != len(set(declared))
            ):
                raise ValueError("Every step must declare its exact known sourceObjectVersionIds.")
            direct: set[str] = set()
            profile_refs: list[str] = []
            has_persisted_artifact = False
            for ref in step.inputRefs:
                if ref.refType == "normalized_object":
                    source = versions.get(ref.ref)
                    if source is None or ref.objectType != source.objectType:
                        raise ValueError("Normalized input must match a declared exact source version and type.")
                    direct.add(ref.ref)
                elif ref.refType == "profile":
                    profile_refs.append(ref.ref)
                elif ref.refType == "artifact":
                    has_persisted_artifact = True
                else:
                    raise ValueError("Multi-source plans require exact version, profile or artifact inputs.")
            inherited = {
                source_id
                for binding in self.dependencyBindings
                if binding.consumerStepId == step_id
                for source_id in ancestry[binding.producerStepId]
            }
            expected = direct | inherited
            # Persisted artifacts have authoritative lineage outside the plan.
            # The Worker must additionally verify their declared source set.
            if not expected.issubset(declared) or (
                not has_persisted_artifact and expected != set(declared)
            ):
                raise ValueError("Step source coverage differs from its inputs and dependency ancestry.")
            step_datasets = {versions[item].datasetId for item in declared}
            allowed_profiles = {f"profile:{contexts[item].profileId}" for item in step_datasets}
            if len(profile_refs) != len(set(profile_refs)) or not set(profile_refs).issubset(allowed_profiles):
                raise ValueError("Profile input must name an exact profile belonging to this step's sources.")
            ancestry[step_id] = set(declared)
            used.update(declared)
        if used != set(versions):
            raise ValueError("Source version inventory may not contain unused material versions.")
        return self


def step_source_inventory(plan: AnalysisPlanV03, step_id: str) -> tuple[list[AnalysisSourceContext], list[AnalysisSourceVersion]]:
    step = next(item for item in plan.steps if item.stepId == step_id)
    ids = set(step.output["sourceObjectVersionIds"])
    versions = [item for item in plan.sourceVersions if str(item.versionId) in ids]
    datasets = {item.datasetId for item in versions}
    return [item for item in plan.sourceContexts if item.datasetId in datasets], versions


class MultiSourceArtifactLineageRecord(ArtifactLineageRecord):
    """Additive lineage contract; historical 1.0 hashes remain unchanged."""

    schemaVersion: Literal["1.1"] = "1.1"
    planSchemaVersion: Literal["0.3"] = "0.3"
    sourceContexts: list[AnalysisSourceContext] = Field(min_length=1, max_length=8)
    sourceVersions: list[AnalysisSourceVersion] = Field(min_length=1, max_length=64)

    @model_validator(mode="after")
    def validate_source_ownership(self) -> "MultiSourceArtifactLineageRecord":
        datasets = [item.datasetId for item in self.sourceContexts]
        versions = [str(item.versionId) for item in self.sourceVersions]
        profiles = [item.profileId for item in self.sourceContexts]
        if datasets != sorted(set(datasets)) or versions != sorted(set(versions)) or len(profiles) != len(set(profiles)):
            raise ValueError("Artifact source inventories must have unique sorted identities.")
        if {item.datasetId for item in self.sourceVersions} != set(datasets):
            raise ValueError("Artifact contexts must cover exactly its source datasets.")
        if len(datasets) == 1:
            if self.datasetId != datasets[0] or self.profileId != profiles[0]:
                raise ValueError("Artifact ownership must match its single source context.")
        elif any(value is not None for value in (self.datasetId, self.profileId, self.datasetVersion, self.profileSemanticHash)):
            raise ValueError("Combined artifacts cannot claim a single dataset or profile.")
        return self


def parse_artifact_lineage(value: ArtifactLineageRecord | Mapping[str, Any]) -> ArtifactLineageRecord:
    payload = value.model_dump(mode="json") if isinstance(value, ArtifactLineageRecord) else dict(value)
    if payload.get("schemaVersion") == "1.2":
        from .project_planning import ProjectArtifactLineageRecord
        return ProjectArtifactLineageRecord.model_validate(payload)
    if payload.get("schemaVersion") == "1.1":
        return MultiSourceArtifactLineageRecord.model_validate(payload)
    return ArtifactLineageRecord.model_validate(payload)


__all__ = ["AnalysisPlanV03", "AnalysisSourceContext", "AnalysisSourceVersion", "MultiSourceArtifactLineageRecord",
           "step_source_inventory", "parse_artifact_lineage"]
