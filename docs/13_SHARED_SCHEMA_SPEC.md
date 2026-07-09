# 共享 Schema 规范

## Phase 10F-8 Addendum: Viewer Scene Artifact Contract Draft

Phase 10F-8 plans a renderer-neutral `viewer_scene` artifact contract. This is a documentation-level schema draft only; it does not implement `structure.viewer_3d`, does not add a renderer, and does not change Tool Registry or planner runtime behavior.

### `viewer_scene.json`

Draft identity:

```json
{
  "kind": "viewer_scene",
  "version": "viewer_scene.v1",
  "schema_version": "phase10f8.viewer_scene.v1"
}
```

Required top-level fields:

- `kind`
- `version`
- `schema_version`
- `source`
- `metadata`
- `scene`
- `validation`
- `caps`
- `warnings`
- `provenance`
- `security`

Security-critical fields:

```json
{
  "security": {
    "contains_javascript": false,
    "external_urls": [],
    "external_urls_allowed": false,
    "artifact_supplied_js_allowed": false,
    "renderer_required": false,
    "remote_assets_allowed": false,
    "html_allowed": false
  }
}
```

The artifact is inert JSON. It must not contain embedded JavaScript, HTML, executable callbacks, external URLs, remote textures, renderer bundle references, notebook payloads, or external script references. JSON-only preview is allowed; renderer evidence and implementation remain future scope.

### Viewer Scene Manifest

Draft identity:

```json
{
  "kind": "viewer_scene_manifest",
  "version": "viewer_scene_manifest.v1",
  "schema_version": "phase10f8.viewer_scene_manifest.v1",
  "entry_artifact": "viewer_scene.json",
  "renderer": {
    "included": false,
    "required": false,
    "renderer_type": "none"
  }
}
```

The manifest is an inert artifact index. It must not load external assets or declare a renderer bundle. Phase 10D `viewer_assets_manifest.json` remains the existing implemented artifact; Phase 10F-8 only plans a future compatibility bridge.

## 1. 本阶段目标

收敛前端、后端、Worker、Agent 和 Tool Registry 共同使用的核心类型，避免每个设计文件重复定义不同版本的 `ArtifactType`、`DisplayTarget`、`ToolCategory`、`DataProfile`、`AnalysisPlan`、`JobEvent` 和 `Recipe`。

本文件是实现阶段的类型基线。后续代码应优先从本文件拆分 JSON Schema，再派生 TypeScript 类型和 Python Pydantic model。

## 2. 设计原则

- 单一命名源：跨服务枚举只在本文件定义。
- JSON Schema first：前端 TypeScript 和后端 Python model 都从共享 JSON Schema 派生。
- 轻量 Profile：Data Profile 存摘要，完整大列表进入 normalized object / object storage。
- Artifact 一等化：图、表格、指标、质量问题、报告和 Recipe 都是 Artifact。
- Secret 不入 Schema 产物：Recipe 和 Artifact 只保存 provider requirement，不保存具体 SecretRef。

## 3. 共享枚举

```ts
type ArtifactType =
  | "plotly_json"
  | "plotly_html"
  | "preview_png"
  | "figure_svg"
  | "figure_pdf"
  | "matterviz_html"
  | "matterviz_snapshot_png"
  | "structure_json"
  | "metrics_json"
  | "table_json"
  | "table_csv"
  | "quality_issues_json"
  | "summary_md"
  | "report_md"
  | "report_html"
  | "recipe_json"
  | "analysis_plan_json";

type DisplayTarget =
  | "overview"
  | "composition"
  | "structure"
  | "trajectory"
  | "phonon"
  | "ml"
  | "artifacts"
  | "report";

type ToolCategory =
  | "visualization"
  | "analysis"
  | "parser"
  | "report"
  | "utility";

type ToolDomain =
  | "table"
  | "viz"
  | "composition"
  | "structure"
  | "trajectory"
  | "phonon"
  | "electronic"
  | "simulation"
  | "ml"
  | "generation"
  | "external";

type ImplementationSource =
  | "pymatviz"
  | "pymatviz_composed"
  | "matterviz"
  | "plotly_custom"
  | "platform_builtin"
  | "plugin";

type MaterialObjectType =
  | "Composition"
  | "Structure"
  | "Atoms"
  | "Molecule"
  | "DataFrame"
  | "PhononBand"
  | "PhononDos"
  | "Trajectory"
  | "ElementValueMap"
  | "RawUnsupported";

type FieldRole =
  | "formula"
  | "target"
  | "prediction"
  | "uncertainty"
  | "label"
  | "structure_id";

type StructurePeriodicityRequirement =
  | "periodic_required"
  | "non_periodic_allowed"
  | "any";

type ObjectPeriodicity =
  | "periodic"
  | "non_periodic"
  | "mixed"
  | "unknown";
```

## 4. Data Asset 与 Normalized Object

```ts
type DataAsset = {
  id: string;
  projectId: string;
  datasetId: string;
  fileName: string;
  mediaType: string;
  detectedFormat:
    | "cif"
    | "poscar"
    | "xyz"
    | "extxyz"
    | "csv"
    | "json_limited"
    | "phonopy"
    | "trajectory"
    | "archive"
    | "unknown";
  storageKey: string;
  status: "uploaded" | "parsing" | "profile_ready" | "failed" | "unsupported";
};

type NormalizedObject = {
  id: string;
  datasetId: string;
  objectType: MaterialObjectType;
  sourceFileIds: string[];
  storageKey: string;
  metadataKey?: string;
  previewKey?: string;
  metadata: Record<string, unknown>;
  hash: string;
};
```

## 5. Shared References

```ts
type InputRef = {
  refType: "dataset" | "profile" | "normalized_object" | "dataframe_column" | "artifact";
  ref: string;
  fieldRole?: FieldRole;
  columnName?: string;
  objectType?: MaterialObjectType;
};
```

## 6. Data Profile

```ts
type DataProfile = {
  schemaVersion: "0.1";
  profileId: string;
  datasetId: string;
  version: string;
  datasetType:
    | "structure_collection"
    | "ml_results"
    | "mixed_material_dataset"
    | "trajectory"
    | "phonon"
    | "unknown";
  files: FileProfile[];
  objects: ObjectProfile[];
  structureSummary?: StructureSummary;
  tableSummary?: TableSummary;
  phononSummary?: Record<string, unknown>;
  trajectorySummary?: Record<string, unknown>;
  qualityIssues: QualityIssue[];
  recommendedTasks: RecommendedTask[];
  createdAt: string;
};

type FileProfile = {
  fileId: string;
  fileName: string;
  detectedFormat: string;
  parseStatus: "success" | "partial" | "failed" | "unsupported";
  errorCode?: string;
  errorMessage?: string;
};

type ObjectProfile = {
  objectId: string;
  objectType: MaterialObjectType;
  count: number;
  sourceFileIds: string[];
  periodicity?: ObjectPeriodicity;
};

type QualityIssue = {
  severity: "info" | "warning" | "error";
  code: string;
  message: string;
  refs: Array<{
    type: "file" | "object" | "row" | "column" | "artifact";
    id: string;
  }>;
};

type RecommendedTask = {
  taskId: string;
  label: string;
  stage: "mvp" | "v1" | "v2";
  taskType:
    | "composition_overview"
    | "structure_quality"
    | "ml_evaluation"
    | "phonon_analysis"
    | "trajectory_viewer"
    | "domain_extension";
  availableNow: boolean;
  requiredTools: string[];
  reason: string;
};

type StructureSummary = {
  nStructures: number;
  formulaStats: {
    total: number;
    uniqueCount: number;
    topFormulas: Array<{ formula: string; count: number }>;
    formulasObjectRef?: string;
  };
  elements: string[];
  chemicalSystemStats: {
    uniqueCount: number;
    topChemicalSystems: Array<{ chemSys: string; count: number }>;
  };
  atomCountStats: { min: number; median: number; max: number };
  latticeStats?: Record<string, { min: number; median: number; max: number }>;
  spacegroupDistribution?: Record<string, number>;
  hasForces: boolean;
  hasMagmoms: boolean;
  representativeStructureIds: string[];
};

type TableSummary = {
  nRows: number;
  nColumns: number;
  columns: Array<{
    name: string;
    dtype: "string" | "number" | "boolean" | "category" | "datetime" | "unknown";
    inferredRole?: FieldRole;
    missingCount: number;
    uniqueCount?: number;
  }>;
  inferredTask?: "regression" | "classification" | "unknown";
};
```

## 7. Tool Registry

```ts
type ToolInputSchema = {
  inputOptions: ToolInputOption[];
  periodicity?: StructurePeriodicityRequirement;
};

type ToolInputOption = {
  name: string;
  requiredObjectTypes?: MaterialObjectType[];
  requiredFields?: Array<{
    role: FieldRole;
    dtype?: "string" | "number" | "category";
  }>;
  description: string;
};

type ToolOutputSchema = {
  primaryArtifactType: ArtifactType;
  secondaryArtifactTypes: ArtifactType[];
  displayTarget: DisplayTarget;
};

type RegisteredTool = {
  toolId: string;
  name: string;
  category: ToolCategory;
  domain: ToolDomain;
  implementationSource: ImplementationSource;
  description: string;
  version: string;
  adapter: string;
  inputSchema: ToolInputSchema;
  paramsSchema: Record<string, unknown>;
  outputSchema: ToolOutputSchema;
  artifactTypes: ArtifactType[];
  costLevel: "low" | "medium" | "high";
  defaultTimeoutSec: number;
  maxTimeoutSec: number;
  cachePolicy: "reuse" | "refresh" | "no_cache";
  permissions: string[];
  resourceLimits: {
    maxRows?: number;
    maxStructures?: number;
    maxAtomsPerStructure?: number;
    maxFrames?: number;
  };
};
```

Example:

```json
{
  "toolId": "composition.ptable_heatmap",
  "category": "visualization",
  "domain": "composition",
  "implementationSource": "pymatviz",
  "inputSchema": {
    "inputOptions": [
      {
        "name": "formula_column",
        "requiredFields": [{ "role": "formula", "dtype": "string" }],
        "description": "Use formulas from a table column."
      },
      {
        "name": "composition_objects",
        "requiredObjectTypes": ["Composition"],
        "description": "Use normalized Composition objects."
      },
      {
        "name": "element_value_map",
        "requiredObjectTypes": ["ElementValueMap"],
        "description": "Use an element-to-value mapping."
      }
    ]
  }
}
```

## 8. Analysis Plan

```ts
type AnalysisPlan = {
  schemaVersion: "0.1";
  goal: string;
  datasetId: string;
  profileId: string;
  toolRegistryVersion: string;
  assumptions: string[];
  warnings: string[];
  steps: AnalysisStep[];
  expectedArtifacts: ExpectedArtifact[];
};

type PersistedAnalysisPlan = {
  id: string;
  projectId: string;
  datasetId?: string;
  profileId?: string;
  jobId?: string;
  planSource: "llm" | "deterministic" | "imported" | string;
  plannerProvider?: string;
  analysisPlan: AnalysisPlan;
  planHash: string; // sha256(canonical_json(AnalysisPlan))
  validationStatus: "validated" | "rejected";
  createdBy: string;
  createdAt: string;
  updatedAt: string;
};

type AnalysisStep = {
  stepId: string;
  toolId: string;
  purpose: string;
  reason: string;
  inputRefs: InputRef[];
  params: Record<string, unknown>;
  output: {
    artifactTypes: ArtifactType[];
    displayTarget: DisplayTarget;
  };
  constraints?: {
    timeoutSec?: number;
    maxRows?: number;
    maxStructures?: number;
    requiresConfirmation?: boolean;
  };
};

type ExpectedArtifact = {
  name: string;
  type: ArtifactType;
  fromStepId?: string;
};
```

## 9. Job 与事件

```ts
type JobStatus =
  | "created"
  | "queued"
  | "running"
  | "partial_success"
  | "completed"
  | "failed"
  | "cancel_requested"
  | "cancelled";

type Job = {
  id: string;
  projectId: string;
  datasetId?: string;
  planId?: string;
  kind: "analysis" | "parse" | "render" | "export" | string;
  status: JobStatus;
  createdBy?: string;
  createdAt?: string;
  updatedAt?: string;
};

type JobEvent = {
  id: string;
  jobId: string;
  seq: number;
  eventType: string;
  status: "info" | "running" | "success" | "warning" | "error";
  message: string;
  progress?: number;
  payload?: Record<string, unknown>;
  createdAt: string;
};
```

## 10. ToolCall 与执行请求

```ts
type ToolExecutionRequest = {
  jobId: string;
  stepId: string;
  toolId: string;
  inputRefs: InputRef[];
  params: Record<string, unknown>;
  artifactTypes: ArtifactType[];
};
```

## 11. Artifact、Recipe 与 Report

```ts
type Artifact = {
  id: string;
  projectId: string;
  datasetId?: string;
  jobId: string;
  toolCallId?: string;
  type: ArtifactType;
  name: string;
  version: string;
  storageKey: string;
  storageProvider?: "local" | "s3" | "minio";
  bucket?: string;
  previewKey?: string;
  sizeBytes: number;
  contentType?: string;
  contentHash: string;
  sha256?: string;
  createdAt?: string;
  metadata: ArtifactMetadata;
};

type ArtifactMetadata = {
  toolId?: string;
  toolVersion?: string;
  adapterVersion?: string;
  inputHashes: string[];
  paramsHash?: string;
  profileId?: string;
  recipeId?: string;
  reportId?: string;
  createdAt: string;
  provenance: Record<string, unknown>;
};

type VisualizationRecipe = {
  schemaVersion: "0.1";
  recipeId: string;
  name: string;
  version: string;
  projectId: string;
  sourceJobId?: string;
  sourcePlanId?: string;
  inputRequirements: Array<{
    role: "structures" | "formulas" | "dataframe" | "target" | "prediction" | "uncertainty";
    objectType?: string;
    fieldRole?: string;
    required: boolean;
  }>;
  steps: RecipeStep[];
  environment: RecipeEnvironment;
};

type RecipeStep = {
  stepId: string;
  toolId: string;
  toolVersion: string;
  inputBindings: Record<string, string>;
  params: Record<string, unknown>;
  artifactTypes: ArtifactType[];
};

type RecipeEnvironment = {
  pythonVersion?: string;
  pymatvizVersion?: string;
  pymatgenVersion?: string;
  aseVersion?: string;
  plotlyVersion?: string;
  mattervizVersion?: string;
  llmProviderRequirement?: "openai-compatible";
  modelClass?: "reasoning" | "general";
};
```

## 12. Config 与 Secret

```ts
type LlmExecutionProfile = {
  providerPolicy: "runner_user_byok" | "system_hosted" | "project_default";
  provider?: string;
  model?: string;
  maxCostPerJob: number;
};

type SecretRef = {
  id: string;
  scopeType: "user" | "project" | "organization" | "system";
  scopeId: string;
  provider: "openai" | "anthropic" | "gemini" | "deepseek" | "custom";
  status: "active" | "revoked" | "expired";
  encryptedRef: string;
  lastUsedAt?: string;
};
```

MVP LLM Secret resolution:

1. `job_runner_user_secret`
2. `project_default_system_provider`
3. `system_hosted_key`

Recipe must not save a concrete `SecretRef`; it only stores provider/model requirements.

## Phase 4 Addendum: persistence hardening schema

- `JobStatus` is fixed to `created`, `queued`, `running`, `partial_success`,
  `completed`, `failed`, `cancel_requested`, and `cancelled`.
- The production transition validator allows `created -> queued -> running`,
  `created -> running` for the local synchronous worker path,
  `running -> partial_success/completed/failed/cancel_requested`,
  `partial_success -> completed/failed`, `failed -> queued`, and
  `cancel_requested -> cancelled`.
- `ToolCallStatus` is fixed to `planned`, `running`, `completed`, `failed`,
  and `skipped`. Legacy `created` ToolCall inputs are normalized to `planned`
  at the repository boundary.
- `tool_calls` now carries `idempotency_key` and `attempt`; `(job_id, step_id)`
  is unique, and `(job_id, idempotency_key)` is unique when the key is present.
- `job_events` keeps `(job_id, seq)` as the SSE resume cursor. Repository
  append operations assign monotonic per-job `seq`; SQLite tests use an
  in-process lock, while PostgreSQL runtime should use transaction-level row
  locking or an equivalent sequence allocation strategy.
- `artifacts` must carry `storage_provider`, `bucket`, `storage_key`,
  `content_type`, `size_bytes`, `sha256`, `preview_key`, and `created_at`.
  Local artifacts use `storage_provider = "local"` and may omit `bucket`;
  S3/MinIO mappings require a bucket.

## Phase 9C Addendum: UI-only workspace view models

Phase 9C adds frontend-only view model names for the AI assistant workspace.
These types do not change the persisted backend schema, Alembic migrations,
AnalysisPlan JSON, Tool Registry manifests, or JobEvent database contract.

```ts
type MainWorkspaceTab =
  | "agent_process"
  | "conversation_plan"
  | "results_export";

type ConversationChunkKind =
  | "user_request"
  | "system_response"
  | "plan_preview"
  | "validation_result"
  | "run_status"
  | "result_reference";

type ConversationChunkView = {
  id: string;
  kind: ConversationChunkKind;
  title: string;
  summary: string;
  createdAt: string;
  status: "idle" | "running" | "success" | "warning" | "error";
  relatedJobId?: string;
  relatedPlanId?: string;
  relatedStepId?: string;
  relatedToolCallId?: string;
  relatedArtifactIds: string[];
  userVisiblePayload: Record<string, unknown>;
  developerPayload?: Record<string, unknown>;
};

type DataContextViewerState = {
  datasetId?: string;
  profileId?: string;
  status:
    | "empty"
    | "loading"
    | "profiling"
    | "ready"
    | "partial_error"
    | "unsupported";
  detectedKind?: "table" | "structure" | "composition" | "archive" | "mixed" | "unsupported";
  summary: Record<string, unknown>;
  qualityIssues: Array<{
    severity: "info" | "warning" | "error";
    message: string;
    ref?: string;
  }>;
};

type SelectedResultContext = {
  chunkId?: string;
  jobId?: string;
  planId?: string;
  planHash?: string;
  stepId?: string;
  toolCallId?: string;
  artifactId?: string;
  resultKind?:
    | "report"
    | "material_3d"
    | "metrics"
    | "table_summary"
    | "artifact_gallery"
    | "recipe"
    | "export";
};
```

Phase 9C UI state also includes `leftPanelWidth`, `leftPanelCollapsed`,
`activeMainTab`, `selectedChunkId`, `selectedResultArtifactId`,
`datasetDialogOpen`, `modelDialogOpen`, and `developerMode`. These fields are
frontend interaction state only. They must not be treated as server-side
business facts.

Security constraints still apply:

- API keys and Secret values must not enter UI persistence, JobEvents,
  Artifacts, Reports, Recipes, or export packages.
- Raw provider prompts and raw completions are not part of these UI view
  models.
- Chunk selection only changes frontend presentation context; execution
  remains controlled by validated and persisted AnalysisPlans.

## Phase 10E-4 Addendum: static XRD artifact contracts

Phase 10E-4 adds the executable `structure.xrd` adapter. It emits static,
deterministic artifacts only and does not introduce renderer authority,
external URL loading, notebook/script execution, experimental fitting, or
Rietveld refinement.

Required artifacts:

- `xrd_pattern.json`: numeric XRD pattern contract.
- `xrd_plot.json`: static stem-chart JSON contract.
- `summary.md`: human-readable method/result/security summary.
- `recipe.json`: reproducible deterministic execution recipe.

`xrd_pattern.json` must include:

- `schema_version: "phase10e4.xrd_pattern.v1"`
- `tool_id: "structure.xrd"`
- source metadata
- structure summary
- normalized parameters
- radiation and two-theta range
- sorted peak records with rounded two-theta, intensity, d-spacing, and optional HKL metadata
- limits / truncation metadata
- warnings
- security flags with `contains_javascript: false`, `external_urls: []`, and `external_urls_allowed: false`

`xrd_plot.json` must include:

- `schema_version: "phase10e4.static_chart.v1"`
- `tool_id: "structure.xrd"`
- `chart_type: "stem"`
- x/y axis metadata
- deterministic series values
- source/result metadata
- the same no-JavaScript and no-external-URL security flags

## Phase 10E-7 Addendum: static RDF artifact contracts

Phase 10E-7 adds the executable `structure.rdf` adapter. It emits static,
deterministic artifacts only and does not introduce renderer authority,
external URL loading, notebook/script execution, trajectory RDF, experimental
PDF fitting, scattering refinement, phonon DOS, or local-environment
classification.

Required artifacts:

- `rdf.json`: numeric radial distribution function contract.
- `rdf_plot.json`: static line-chart JSON contract.
- `summary.md`: human-readable method/result/security summary.
- `recipe.json`: reproducible deterministic execution recipe.

`rdf.json` must include:

- `schema_version: "phase10e7.rdf.v1"`
- `tool_id: "structure.rdf"`
- source metadata
- periodic structure summary including PBC and volume
- normalized parameters
- global `rdf.r_angstrom`, `rdf.g_r`, `rdf.counts`, and `rdf.bin_edges_angstrom`
- `rdf.normalization.method: "number_density"`
- optional ordered `partial_rdf` records
- limits / truncation metadata
- warnings
- security flags with `contains_javascript: false`, `external_urls: []`, and `external_urls_allowed: false`

`rdf_plot.json` must include:

- `schema_version: "phase10e7.static_chart.v1"`
- `tool_id: "structure.rdf"`
- `chart_type: "line"`
- x/y axis metadata
- deterministic series values
- source/result metadata
- the same no-JavaScript and no-external-URL security flags
