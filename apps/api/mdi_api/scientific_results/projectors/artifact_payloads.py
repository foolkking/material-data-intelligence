from __future__ import annotations

from typing import Any, Literal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class _Payload(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    schema_version: str = Field(validation_alias=AliasChoices("schema_version", "schemaVersion"))


class _RdfNormalization(BaseModel):
    model_config = ConfigDict(extra="allow")
    number_density_per_angstrom3: float


class _RdfCurve(BaseModel):
    model_config = ConfigDict(extra="allow")
    r_angstrom: list[float]
    g_r: list[float]
    normalization: _RdfNormalization


class _RdfLimits(BaseModel):
    model_config = ConfigDict(extra="allow")
    bin_count: int = Field(ge=1)


class RdfArtifactPayload(_Payload):
    schema_version: Literal["phase10e7.rdf.v1"] = Field(validation_alias=AliasChoices("schema_version", "schemaVersion"))
    artifact_type: Literal["structure.rdf"] = Field(validation_alias="artifactType")
    structureCount: int = Field(ge=1)
    rdf: _RdfCurve
    limits: _RdfLimits


class _XrdPattern(BaseModel):
    model_config = ConfigDict(extra="allow")
    peaks: list[dict[str, Any]]
    peak_count: int = Field(ge=0)


class _Radiation(BaseModel):
    model_config = ConfigDict(extra="allow")
    wavelength_angstrom: float = Field(gt=0)


class TheoreticalXrdArtifactPayload(_Payload):
    schema_version: Literal["phase10e4.xrd_pattern.v1"] = Field(validation_alias=AliasChoices("schema_version", "schemaVersion"))
    artifact_type: Literal["structure.xrd"] = Field(validation_alias="artifactType")
    radiation: _Radiation
    pattern: _XrdPattern


class _XrdResidualSummary(BaseModel):
    model_config = ConfigDict(extra="allow")
    matchedCount: int = Field(ge=0)
    meanSignedDeltaTwoTheta: float | None
    maeDeltaTwoTheta: float | None
    rmseDeltaTwoTheta: float | None
    maxAbsoluteDeltaTwoTheta: float | None
    unit: Literal["degree"]


class _XrdCoverage(BaseModel):
    model_config = ConfigDict(extra="allow")
    unmatchedExperimentalPeaks: int = Field(ge=0)
    unmatchedTheoreticalPeaks: int = Field(ge=0)


class XrdComparisonArtifactPayload(_Payload):
    schema_version: Literal["phase10n3.experimental_xrd_comparison.v1"] = Field(validation_alias=AliasChoices("schema_version", "schemaVersion"))
    artifact_type: Literal["structure.experimental_xrd_comparison"] = Field(validation_alias="artifactType")
    residualSummary: _XrdResidualSummary
    coverage: _XrdCoverage


class _RegressionMetrics(BaseModel):
    model_config = ConfigDict(extra="allow")
    sampleCount: int = Field(ge=1)
    mae: float
    rmse: float
    r2: float | None
    meanSignedError: float
    medianAbsoluteError: float


class _RegressionEvaluation(BaseModel):
    model_config = ConfigDict(extra="allow")
    taskId: str = Field(min_length=1)
    unit: str | None = None
    metrics: _RegressionMetrics


class RegressionEvaluationArtifactPayload(_Payload):
    schema_version: Literal["phase10k3.materials_ml_regression.v1"] = Field(validation_alias=AliasChoices("schema_version", "schemaVersion"))
    artifact_type: Literal["ml.regression_evaluation"] = Field(validation_alias="artifactType")
    evaluations: list[_RegressionEvaluation] = Field(min_length=1)


class _MsdCoverage(BaseModel):
    model_config = ConfigDict(extra="allow")
    frames: int = Field(ge=2)
    atoms: int = Field(ge=1)
    validLags: int = Field(ge=1)


class MsdArtifactPayload(_Payload):
    schema_version: Literal["phase10n4.trajectory_msd.v1"] = Field(validation_alias=AliasChoices("schema_version", "schemaVersion"))
    artifact_type: Literal["trajectory.msd"] = Field(validation_alias="artifactType")
    lagTimesPs: list[float] = Field(min_length=1)
    totalMsdAngstrom2: list[float] = Field(min_length=1)
    coverage: _MsdCoverage


class _DiffusionEstimate(BaseModel):
    model_config = ConfigDict(extra="allow")
    available: bool
    value: float | None
    unit: Literal["angstrom^2/picosecond"]


class _DiffusionFit(BaseModel):
    model_config = ConfigDict(extra="allow")
    rSquared: float | None
    rmseAngstrom2: float | None


class _RegimeDiagnostic(BaseModel):
    model_config = ConfigDict(extra="allow")
    status: str = Field(min_length=1)


class DiffusionArtifactPayload(_Payload):
    schema_version: Literal["phase10n4.trajectory_diffusion.v1"] = Field(validation_alias=AliasChoices("schema_version", "schemaVersion"))
    artifact_type: Literal["trajectory.diffusion"] = Field(validation_alias="artifactType")
    diffusionEstimate: _DiffusionEstimate
    fit: _DiffusionFit
    regimeDiagnostic: _RegimeDiagnostic


class PhononBandSummaryPayload(_Payload):
    schema_version: Literal["phase10h.phonon_summary.v1"] = Field(validation_alias=AliasChoices("schema_version", "schemaVersion"))
    branch_count: int = Field(ge=1)
    qpoint_count: int = Field(ge=1)
    frequency_unit: Literal["terahertz"]
    frequency_min: float
    frequency_max: float
    imaginary_mode_count: int = Field(ge=0)


class PhononDosSummaryPayload(_Payload):
    schema_version: Literal["phase10h2.phonon_dos_summary.v1"] = Field(validation_alias=AliasChoices("schema_version", "schemaVersion"))
    frequency_unit: Literal["terahertz"]
    frequency_min: float
    frequency_max: float
    observed_integral: float
    projection_count: int = Field(ge=0)


class PhononBandDosSummaryPayload(_Payload):
    schema_version: Literal["phase10h.phonon_band_dos_summary.v1"] = Field(validation_alias=AliasChoices("schema_version", "schemaVersion"))
    frequency_unit: Literal["terahertz"]
    frequency_min: float
    frequency_max: float
    dos_integral: float
    imaginary_band_mode_count: int = Field(ge=0)


PRODUCTION_PAYLOAD_ADAPTERS: dict[str, type[_Payload]] = {
    "phase10e7.rdf.v1": RdfArtifactPayload,
    "phase10e4.xrd_pattern.v1": TheoreticalXrdArtifactPayload,
    "phase10n3.experimental_xrd_comparison.v1": XrdComparisonArtifactPayload,
    "phase10k3.materials_ml_regression.v1": RegressionEvaluationArtifactPayload,
    "phase10n4.trajectory_msd.v1": MsdArtifactPayload,
    "phase10n4.trajectory_diffusion.v1": DiffusionArtifactPayload,
    "phase10h.phonon_summary.v1": PhononBandSummaryPayload,
    "phase10h2.phonon_dos_summary.v1": PhononDosSummaryPayload,
    "phase10h.phonon_band_dos_summary.v1": PhononBandDosSummaryPayload,
}


def validate_production_payload(schema_version: str, payload: dict[str, Any]) -> None:
    adapter = PRODUCTION_PAYLOAD_ADAPTERS.get(schema_version)
    if adapter is not None:
        adapter.model_validate(payload)
