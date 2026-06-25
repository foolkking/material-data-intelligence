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
    Trajectory = "Trajectory"
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
    status: Literal["created", "running", "completed", "failed"]
    params: dict[str, Any] = Field(default_factory=dict)
    artifactIds: list[str] = Field(default_factory=list)
    error: dict[str, Any] | None = None


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
    previewKey: str | None = None
    sizeBytes: int
    contentHash: str
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


class AnalysisPlan(BaseModel):
    schemaVersion: Literal["0.1"] = "0.1"
    goal: str
    datasetId: str
    profileId: str
    toolRegistryVersion: str
    assumptions: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    steps: list[AnalysisStep]
    expectedArtifacts: list[dict[str, Any]] = Field(default_factory=list)


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
    createdAt: str


class VisualizationRecipe(BaseModel):
    schemaVersion: Literal["0.1"] = "0.1"
    recipeId: str
    name: str
    version: str
    projectId: str
    sourceJobId: str | None = None
    sourcePlanId: str | None = None
    inputRequirements: list[dict[str, Any]] = Field(default_factory=list)
    steps: list[dict[str, Any]] = Field(default_factory=list)
    environment: dict[str, Any] = Field(default_factory=dict)
