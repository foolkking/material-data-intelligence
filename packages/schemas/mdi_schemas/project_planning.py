"""Project-scoped, controlled scientific work without a sample dataset.

Reference data is declared separately from user material versions. Parameters
remain in the ordinary validated steps; this contract never supplies arbitrary
files, executable code, or network access to an adapter.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from .dependency_planning import AnalysisPlanV02, ArtifactLineageRecord, DependencyBinding, StrictDependencyModel


class PlatformReferenceSource(StrictDependencyModel):
    referenceId: str = Field(pattern=r"^[a-z][a-z0-9_.-]{2,95}$")
    version: str = Field(min_length=1, max_length=64)
    contentHash: str = Field(pattern=r"^[0-9a-f]{64}$")


class ReferencePublication(StrictDependencyModel):
    name: str = Field(min_length=1, max_length=256)
    url: str = Field(pattern=r"^https://[^\s@]+$", max_length=1024)
    version: str | None = Field(default=None, max_length=64)
    license: str | None = Field(default=None, max_length=128)
    use: str | None = Field(default=None, max_length=512)


class ReferenceProperty(StrictDependencyModel):
    label: str = Field(min_length=1, max_length=128)
    unit: str | None = Field(default=None, max_length=64)
    definition: str = Field(min_length=1, max_length=2048)
    coverage: str = Field(min_length=1, max_length=512)
    citation: str | None = Field(default=None, max_length=1024)


class PlatformReferenceDescription(PlatformReferenceSource):
    name: str = Field(min_length=1, max_length=256)
    sources: list[ReferencePublication] = Field(min_length=1, max_length=8)
    properties: dict[str, ReferenceProperty] = Field(default_factory=dict, max_length=8)


class AnalysisPlanV04(AnalysisPlanV02):
    schemaVersion: Literal["0.4"] = "0.4"
    scope: Literal["PROJECT"] = "PROJECT"
    projectId: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,159}$")
    datasetId: None = None
    profileId: None = None
    referenceSources: list[PlatformReferenceSource] = Field(default_factory=list, max_length=8)
    # Initial project tools are independent bounded operations. Material and
    # artifact compositions continue to use their existing source contracts.
    dependencyBindings: list[DependencyBinding] = Field(default_factory=list, max_length=0)

    @model_validator(mode="after")
    def validate_project_inputs(self) -> "AnalysisPlanV04":
        identities = [item.referenceId for item in self.referenceSources]
        if identities != sorted(set(identities)):
            raise ValueError("Platform references must have unique sorted identities.")
        if any(step.inputRefs for step in self.steps):
            raise ValueError("Project-scoped plans cannot bind sample, profile or artifact inputs.")
        if any(step.output.get("sourceObjectVersionIds") for step in self.steps):
            raise ValueError("Project-scoped steps cannot claim material source versions.")
        return self


class ProjectArtifactLineageRecord(ArtifactLineageRecord):
    schemaVersion: Literal["1.2"] = "1.2"
    planSchemaVersion: Literal["0.4"] = "0.4"
    datasetId: None = None
    datasetVersion: None = None
    profileId: None = None
    profileSemanticHash: None = None
    referenceSources: list[PlatformReferenceSource] = Field(default_factory=list, max_length=8)

    @model_validator(mode="after")
    def validate_reference_identity(self) -> "ProjectArtifactLineageRecord":
        identities = [item.referenceId for item in self.referenceSources]
        if identities != sorted(set(identities)):
            raise ValueError("Platform references must have unique sorted identities.")
        return self


__all__ = ["AnalysisPlanV04", "PlatformReferenceSource", "ProjectArtifactLineageRecord"]
