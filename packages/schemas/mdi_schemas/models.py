from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class ArtifactType(str, Enum):
    plotly_json = "plotly_json"
    plotly_html = "plotly_html"
    preview_png = "preview_png"
    figure_svg = "figure_svg"
    figure_pdf = "figure_pdf"
    matterviz_html = "matterviz_html"
    matterviz_snapshot_png = "matterviz_snapshot_png"
    structure_json = "structure_json"
    trajectory_json = "trajectory_json"
    trajectory_summary_json = "trajectory_summary_json"
    trajectory_report_json = "trajectory_report_json"
    trajectory_manifest_json = "trajectory_manifest_json"
    phonon_band_json = "phonon_band_json"
    phonon_band_dos_json = "phonon_band_dos_json"
    phonon_compatibility_json = "phonon_compatibility_json"
    phonon_dos_json = "phonon_dos_json"
    phonon_summary_json = "phonon_summary_json"
    phonon_report_json = "phonon_report_json"
    phonon_manifest_json = "phonon_manifest_json"
    phonon_animation_json = "phonon_animation_json"
    phonon_animation_summary_json = "phonon_animation_summary_json"
    phonon_animation_manifest_json = "phonon_animation_manifest_json"
    reciprocal_lattice_json = "reciprocal_lattice_json"
    brillouin_zone_json = "brillouin_zone_json"
    kpath_json = "kpath_json"
    brillouin_zone_manifest_json = "brillouin_zone_manifest_json"
    volumetric_grid_json = "volumetric_grid_json"
    volumetric_payload_json = "volumetric_payload_json"
    volumetric_field_json = "volumetric_field_json"
    volumetric_dataset_json = "volumetric_dataset_json"
    volumetric_manifest_json = "volumetric_manifest_json"
    volumetric_structure_overlay_json = "volumetric_structure_overlay_json"
    volumetric_binary = "volumetric_binary"
    metrics_json = "metrics_json"
    table_json = "table_json"
    table_csv = "table_csv"
    quality_issues_json = "quality_issues_json"
    summary_md = "summary_md"
    report_md = "report_md"
    report_html = "report_html"
    recipe_json = "recipe_json"
    analysis_plan_json = "analysis_plan_json"


class DisplayTarget(str, Enum):
    overview = "overview"
    composition = "composition"
    structure = "structure"
    trajectory = "trajectory"
    volumetric = "volumetric"
    phonon = "phonon"
    ml = "ml"
    artifacts = "artifacts"
    report = "report"


class ToolCategory(str, Enum):
    visualization = "visualization"
    analysis = "analysis"
    parser = "parser"
    report = "report"
    utility = "utility"


class ToolDomain(str, Enum):
    dataset = "dataset"
    table = "table"
    viz = "viz"
    composition = "composition"
    structure = "structure"
    trajectory = "trajectory"
    phonon = "phonon"
    electronic = "electronic"
    simulation = "simulation"
    ml = "ml"
    generation = "generation"
    external = "external"


class ImplementationSource(str, Enum):
    pymatviz = "pymatviz"
    pymatviz_composed = "pymatviz_composed"
    matterviz = "matterviz"
    plotly_custom = "plotly_custom"
    platform_builtin = "platform_builtin"
    plugin = "plugin"


class MaterialObjectType(str, Enum):
    Composition = "Composition"
    Structure = "Structure"
    Atoms = "Atoms"
    Molecule = "Molecule"
    DataFrame = "DataFrame"
    PhononBand = "PhononBand"
    PhononDos = "PhononDos"
    PhononEigenvector = "PhononEigenvector"
    Trajectory = "Trajectory"
    VolumetricData = "VolumetricData"
    ElementValueMap = "ElementValueMap"
    RawUnsupported = "RawUnsupported"


class JobStatus(str, Enum):
    created = "created"
    queued = "queued"
    running = "running"
    partial_success = "partial_success"
    completed = "completed"
    failed = "failed"
    cancel_requested = "cancel_requested"
    cancelled = "cancelled"


class JobEventStatus(str, Enum):
    info = "info"
    running = "running"
    success = "success"
    warning = "warning"
    error = "error"


class ToolCallStatus(str, Enum):
    planned = "planned"
    running = "running"
    completed = "completed"
    failed = "failed"
    skipped = "skipped"


class JobEvent(BaseModel):
    id: str
    jobId: str
    seq: int
    eventType: str
    status: JobEventStatus
    message: str
    progress: float | None = None
    payload: dict[str, Any] | None = None
    createdAt: str


class ToolInputOption(BaseModel):
    name: str
    requiredObjectTypes: list[MaterialObjectType] = Field(default_factory=list)
    requiredFields: list[dict[str, Any]] = Field(default_factory=list)
    description: str


class ToolInputSchema(BaseModel):
    inputOptions: list[ToolInputOption] = Field(default_factory=list)
    periodicity: Literal["periodic_required", "non_periodic_allowed", "any"] | None = None


class ToolOutputSchema(BaseModel):
    primaryArtifactType: ArtifactType
    secondaryArtifactTypes: list[ArtifactType] = Field(default_factory=list)
    displayTarget: DisplayTarget


class RegisteredTool(BaseModel):
    toolId: str
    name: str
    category: ToolCategory
    domain: ToolDomain
    implementationSource: ImplementationSource
    description: str
    version: str
    adapter: str
    inputSchema: ToolInputSchema
    paramsSchema: dict[str, Any] = Field(default_factory=dict)
    outputSchema: ToolOutputSchema
    artifactTypes: list[ArtifactType]
    costLevel: Literal["low", "medium", "high"] = "low"
    defaultTimeoutSec: int = 30
    maxTimeoutSec: int = 120
    cachePolicy: Literal["reuse", "refresh", "no_cache"] = "reuse"
    permissions: list[str] = Field(default_factory=list)
    resourceLimits: dict[str, int] = Field(default_factory=dict)
    source: dict[str, Any] = Field(default_factory=dict)
    stage: Literal["mvp", "v1", "v2"] = "mvp"


class InputRef(BaseModel):
    refType: Literal["dataset", "profile", "normalized_object", "dataframe_column", "artifact"]
    ref: str
    fieldRole: str | None = None
    columnName: str | None = None
    objectType: MaterialObjectType | None = None


class ToolExecutionRequest(BaseModel):
    jobId: str
    stepId: str
    toolId: str
    inputRefs: list[InputRef]
    params: dict[str, Any] = Field(default_factory=dict)
    artifactTypes: list[ArtifactType]


class ToolCall(BaseModel):
    id: str
    jobId: str
    stepId: str
    toolId: str
    status: ToolCallStatus
    params: dict[str, Any] = Field(default_factory=dict)
    artifactIds: list[str] = Field(default_factory=list)
    error: dict[str, Any] | None = None
    idempotencyKey: str | None = None
    attempt: int = 1


class ArtifactMetadata(BaseModel):
    toolId: str | None = None
    toolVersion: str | None = None
    adapterVersion: str | None = None
    inputHashes: list[str] = Field(default_factory=list)
    paramsHash: str | None = None
    profileId: str | None = None
    recipeId: str | None = None
    reportId: str | None = None
    createdAt: str
    provenance: dict[str, Any] = Field(default_factory=dict)


class Artifact(BaseModel):
    id: str
    projectId: str
    datasetId: str | None = None
    jobId: str
    toolCallId: str | None = None
    type: ArtifactType
    name: str
    version: str
    storageKey: str
    storageProvider: str | None = None
    bucket: str | None = None
    previewKey: str | None = None
    sizeBytes: int
    contentType: str | None = None
    contentHash: str
    sha256: str | None = None
    createdAt: str | None = None
    metadata: ArtifactMetadata


class AnalysisStep(BaseModel):
    stepId: str
    toolId: str
    purpose: str
    reason: str
    inputRefs: list[InputRef]
    params: dict[str, Any] = Field(default_factory=dict)
    output: dict[str, Any]
    constraints: dict[str, Any] | None = None


class ExpectedArtifact(BaseModel):
    name: str
    type: ArtifactType
    fromStepId: str | None = None


class AnalysisPlan(BaseModel):
    schemaVersion: Literal["0.1"] = "0.1"
    goal: str
    datasetId: str
    profileId: str
    toolRegistryVersion: str
    assumptions: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    steps: list[AnalysisStep]
    expectedArtifacts: list[ExpectedArtifact] = Field(default_factory=list)


class DataProfileSemanticRole(BaseModel):
    role: Literal[
        "material_formula",
        "sample_identity",
        "regression_target",
        "regression_prediction",
        "regression_uncertainty",
        "classification_target",
        "classification_prediction",
        "class_probability",
        "material_property",
    ]
    authority: Literal["explicit_metadata", "user_declared", "canonical_name", "alias_match", "bounded_pattern"]
    groupId: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class DataProfileSemanticColumn(BaseModel):
    objectId: str
    column: str
    dtype: str
    roles: list[DataProfileSemanticRole] = Field(default_factory=list)
    missingCount: int = Field(default=0, ge=0)
    uniqueCount: int = Field(default=0, ge=0)
    finiteCount: int | None = Field(default=None, ge=0)
    nonFiniteCount: int | None = Field(default=None, ge=0)
    rowsInspected: int = Field(default=0, ge=0)
    totalRows: int = Field(default=0, ge=0)
    unit: str | None = None
    ambiguities: list[str] = Field(default_factory=list)


class DataProfileSemanticSeriesBinding(BaseModel):
    seriesId: str
    predictionColumn: str | None = None
    uncertaintyColumns: list[str] = Field(default_factory=list)


class DataProfileSemanticGroup(BaseModel):
    groupId: str
    kind: Literal["regression", "classification", "class_probability"]
    targetColumns: list[str] = Field(default_factory=list)
    predictionColumns: list[str] = Field(default_factory=list)
    uncertaintyColumns: list[str] = Field(default_factory=list)
    probabilityColumns: list[str] = Field(default_factory=list)
    classes: list[str] = Field(default_factory=list)
    seriesBindings: list[DataProfileSemanticSeriesBinding] = Field(default_factory=list)
    status: Literal["COMPLETE", "INCOMPLETE", "AMBIGUOUS"]
    reasons: list[str] = Field(default_factory=list)


class DataProfileResourceSemantic(BaseModel):
    objectId: str
    objectType: str
    objectHash: str
    kind: str
    facts: dict[str, Any] = Field(default_factory=dict)
    capabilities: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class DataProfileAnalysisReadiness(BaseModel):
    capability: str
    dataStatus: Literal["READY", "MISSING_REQUIRED_DATA", "AMBIGUOUS", "UNSUPPORTED_DATA_KIND"]
    platformStatus: Literal["AVAILABLE", "NOT_IMPLEMENTED", "NOT_EVALUATED"]
    reasons: list[str] = Field(default_factory=list)
    requiredSemantics: list[str] = Field(default_factory=list)
    matchingGroups: list[str] = Field(default_factory=list)


class DataProfileSampleIdentity(BaseModel):
    policy: Literal["explicit_column", "object_hash_row_index"]
    explicitColumn: str | None = None
    fallbackPolicy: Literal["dataset_version_object_hash_row_index"] = "dataset_version_object_hash_row_index"
    datasetVersion: str
    objectIds: list[str] = Field(default_factory=list)


class DataProfileCoverage(BaseModel):
    policy: Literal["complete", "deterministic_bounded_sample"]
    rowsInspected: int = Field(default=0, ge=0)
    totalRows: int = Field(default=0, ge=0)
    columnsInspected: int = Field(default=0, ge=0)
    totalColumns: int = Field(default=0, ge=0)
    limits: dict[str, int] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class DataProfileCoordinationStructureReadiness(BaseModel):
    objectId: str
    objectHash: str = Field(pattern=r"^[0-9a-f]{64}$")
    periodic: bool
    latticeStatus: Literal["VALID", "MISSING", "INVALID"]
    siteCount: int = Field(ge=0)
    speciesOccupancyStatus: Literal["ORDERED_FULL_OCCUPANCY", "DISORDERED", "PARTIAL_OCCUPANCY", "UNSUPPORTED"]
    disorderStatus: Literal["ORDERED", "DISORDERED", "UNKNOWN"]
    partialOccupancyStatus: Literal["ABSENT", "PRESENT", "UNKNOWN"]
    coordinationInputStatus: Literal["READY", "MISSING_REQUIRED_DATA", "AMBIGUOUS", "UNSUPPORTED_DATA_KIND"]
    reasons: list[str] = Field(default_factory=list)


class DataProfileCoordinationReadiness(BaseModel):
    contractVersion: Literal["1.0"] = "1.0"
    periodicStructurePresent: bool
    eligibleStructureCount: int = Field(ge=0, le=32)
    structures: list[DataProfileCoordinationStructureReadiness] = Field(default_factory=list, max_length=32)
    status: Literal["READY", "MISSING_REQUIRED_DATA", "AMBIGUOUS", "UNSUPPORTED_DATA_KIND"]
    reasons: list[str] = Field(default_factory=list)


class DataProfile(BaseModel):
    schemaVersion: Literal["0.1"] = "0.1"
    profileId: str
    datasetId: str
    version: str
    datasetType: str
    files: list[dict[str, Any]] = Field(default_factory=list)
    objects: list[dict[str, Any]] = Field(default_factory=list)
    structureSummary: dict[str, Any] | None = None
    tableSummary: dict[str, Any] | None = None
    phononSummary: dict[str, Any] | None = None
    trajectorySummary: dict[str, Any] | None = None
    qualityIssues: list[dict[str, Any]] = Field(default_factory=list)
    recommendedTasks: list[dict[str, Any]] = Field(default_factory=list)
    profileContractVersion: Literal["2.0", "2.1"] | None = None
    semanticRulesVersion: str | None = None
    semanticHash: str | None = None
    semanticColumns: list[DataProfileSemanticColumn] = Field(default_factory=list)
    semanticGroups: list[DataProfileSemanticGroup] = Field(default_factory=list)
    resourceSemantics: list[DataProfileResourceSemantic] = Field(default_factory=list)
    analysisReadiness: list[DataProfileAnalysisReadiness] = Field(default_factory=list)
    sampleIdentity: DataProfileSampleIdentity | None = None
    profileCoverage: DataProfileCoverage | None = None
    coordinationReadiness: DataProfileCoordinationReadiness | None = None
    createdAt: str


class VisualizationRecipeStep(BaseModel):
    stepId: str
    toolId: str
    toolVersion: str
    inputBindings: dict[str, str] = Field(default_factory=dict)
    params: dict[str, Any] = Field(default_factory=dict)
    artifactTypes: list[ArtifactType] = Field(default_factory=list)


class VisualizationRecipe(BaseModel):
    schemaVersion: Literal["0.1"] = "0.1"
    recipeId: str
    name: str
    version: str
    projectId: str
    sourceJobId: str | None = None
    sourcePlanId: str | None = None
    inputRequirements: list[dict[str, Any]] = Field(default_factory=list)
    steps: list[VisualizationRecipeStep] = Field(default_factory=list)
    environment: dict[str, Any] = Field(default_factory=dict)
