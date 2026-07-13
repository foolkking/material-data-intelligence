# 共享 Schema 规范

## Phase 10F-25 Addendum: renderer-local view state

`phase10f25.viewer_view_state.v1` is a frontend-local inert JSON download bound
to canonical scene schema/resource identity. It records one finite perspective
camera state, an application-owned preset, exactly three bounded X/Y/Z clipping
planes, and unit-cell/supercell-boundary/lattice-axis visibility. It contains no
Three.js objects, callback, shader, URL, or executable content.

The contract does not change `phase10f18.viewer_scene.v2`, lattice vectors,
periodic identities, topology, measurements, AnalysisPlan, or backend runtime.
Replay validates scene identity, finite coordinates, zoom, plane order, and
current displayed-scene bounds before renderer use.

## Phase 10F-24 Addendum: renderer-local supercell display state

`phase10f24.viewer_supercell_state.v1` is a frontend-local inert JSON download. It records canonical scene identity, strict `[a,b,c]` expansion, fixed `positive_octant` origin, visibility, counts, render tier, caps, warnings, and no-mutation/security flags. Replay requires matching scene schema and resource identity. It does not modify `phase10f18.viewer_scene.v2`, create a structure resource, or grant execution authority.

Displayed instances remain `site_index@[image_offset]`, ordered by image offset then canonical site index. Axes are 1 through 3, total cells at most 27, displayed atoms at most 2048, and displayed bonds at most 8192. Measurement artifacts include applied expansion as view provenance.

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

## Phase 10F-9 Addendum: Viewer Scene Contract Fixture Validator

Phase 10F-9 implements a low-risk, renderer-free validation slice for the Phase 10F-8 draft. This addendum records the implemented fixture and validator contract; it does not implement `structure.viewer_3d`, a renderer, WebGL, Three.js, planner routing, Tool Registry runtime behavior, or a runtime API route.

Implemented validator location:

- `packages/artifact-core/mdi_artifact_core/viewer_scene_contract.py`

Implemented fixture pack:

- `docs/phase10f/fixtures/viewer_scene_v1/`

Implemented test:

- `tests/test_viewer_scene_contract_fixtures.py`

Validator result shape:

```json
{
  "valid": true,
  "errors": [],
  "warnings": [],
  "caps": {
    "max_sites": 256,
    "max_bonds": 2048,
    "max_species": 32,
    "max_cell_expansion": [1, 1, 1],
    "max_scene_json_bytes": 1000000
  }
}
```

Implemented error codes:

- `VIEWER_SCENE_KIND_INVALID`
- `VIEWER_SCENE_VERSION_INVALID`
- `VIEWER_SCENE_SCHEMA_VERSION_INVALID`
- `VIEWER_SCENE_REQUIRED_FIELD_MISSING`
- `VIEWER_SCENE_SECURITY_FIELD_INVALID`
- `VIEWER_SCENE_EXTERNAL_URL_NOT_ALLOWED`
- `VIEWER_SCENE_COORDINATE_NON_FINITE`
- `VIEWER_SCENE_LATTICE_VECTOR_INVALID`
- `VIEWER_SCENE_SITE_LIMIT_EXCEEDED`
- `VIEWER_SCENE_BOND_LIMIT_EXCEEDED`
- `VIEWER_SCENE_SPECIES_LIMIT_EXCEEDED`
- `VIEWER_SCENE_CELL_EXPANSION_LIMIT_EXCEEDED`
- `VIEWER_SCENE_JSON_BYTES_LIMIT_EXCEEDED`
- `VIEWER_SCENE_EXTERNAL_RESOURCE_REFERENCE`
- `VIEWER_SCENE_EXECUTABLE_FIELD`
- `VIEWER_SCENE_FORBIDDEN_STRING_CONTENT`

Implemented warning codes:

- `VIEWER_SCENE_CAP_NEAR_LIMIT`

Manifest fixture schema version:

- `phase10f9.viewer_scene_manifest.v1`

Expected-results schema version:

- `phase10f9.viewer_scene_expected_results.v1`

Security boundary:

- fixtures are inert JSON only;
- no real external URLs are allowed;
- no artifact JavaScript or HTML is allowed;
- invalid external-resource and executable-field cases use safe placeholders;
- renderer evidence and browser/API evidence remain deferred.

## Phase 10F-10 Addendum: Viewer Scene JSON-only Preview Surface

Phase 10F-10 implements a frontend JSON-only preview surface for the already-defined `viewer_scene.v1` contract. This addendum records the implemented preview contract; it does not implement `structure.viewer_3d`, a renderer, WebGL, Three.js, planner routing, Tool Registry runtime behavior, or a production runtime API route.

Implemented preview location:

- `apps/web/app/components/PlannerWorkbench.tsx`

Implemented frontend evidence:

- `apps/web/app/components/PlannerWorkbench.test.tsx`

Supported viewer scene identity:

```json
{
  "kind": "viewer_scene",
  "version": "viewer_scene.v1",
  "schema_version": "phase10f8.viewer_scene.v1"
}
```

Supported manifest identity:

```json
{
  "schema_version": "phase10f9.viewer_scene_manifest.v1",
  "artifact_kind": "viewer_scene",
  "artifact_version": "viewer_scene.v1"
}
```

Preview fields surfaced through stable selectors:

- artifact kind;
- artifact version;
- schema version;
- validation state;
- error codes;
- warning codes;
- site count;
- bond count;
- species count;
- coordinate basis;
- lattice presence;
- manifest preview mode;
- renderer required;
- executable assets;
- external resources.

Security boundary:

- preview is inert JSON summary and raw JSON detail only;
- no artifact JavaScript is executed;
- no HTML renderer is added;
- no external resources are loaded;
- no canvas, iframe, WebGL path, Three.js dependency, renderer bundle, adapter, planner route, or runtime route is added.

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

## Phase 10F-12 Addendum: minimal viewer scene adapter artifacts

Phase 10F-12 adds the executable `structure.viewer_scene` adapter. It emits
inert `viewer_scene.v1` JSON data for JSON-only preview and future renderer
handoff. It does not emit WebGL, Three.js, MatterViz renderer bundles, canvas
viewer assets, iframe viewers, artifact JavaScript, HTML payloads, external
URLs, remote textures, notebooks, scripts, or external API references.

Required artifacts:

- `viewer_scene.json`: canonical inert scene artifact.
- `viewer_scene_manifest.json`: canonical JSON-only manifest.
- `summary.md`: human-readable input, scene, caps, preview, security, and deferred-scope summary.
- `recipe.json`: reproducible deterministic execution recipe.

`viewer_scene.json` must include:

- `kind: "viewer_scene"`
- `version: "viewer_scene.v1"`
- `schema_version: "phase10f8.viewer_scene.v1"`
- source metadata
- metadata with formula, site count, species count, preview mode, and renderer-required false
- scene data with `coordinate_basis: "cartesian_angstrom"`
- declarative site records with finite `xyz` coordinates and optional finite `frac` coordinates
- finite lattice vectors and parameters
- optional non-authoritative bounded bonds
- caps aligned to Phase 10F contract
- validation state and warnings
- provenance with `deterministic: true`
- security flags with no JavaScript, no external URLs, no renderer required, no remote assets, and no HTML

`viewer_scene_manifest.json` must include:

- `schema_version: "phase10f9.viewer_scene_manifest.v1"`
- `artifact_kind: "viewer_scene"`
- `artifact_version: "viewer_scene.v1"`
- `preview_mode: "json_only"`
- `renderer_required: false`
- `executable_assets: "none"`
- `external_resources: "none"`
- local logical artifact references only

The adapter validates both JSON artifacts with the canonical validator before
export. If validation fails, the tool call must fail with a typed error rather
than saving a successful artifact set.

## Phase 10F-14 Addendum: frontend validated renderer model

Phase 10F-14 does not change `viewer_scene.v1`. It adds frontend-only types
after canonical validation and whitelist mapping:

```ts
type RenderVector3 = readonly [number, number, number];

type ValidatedRenderScene = {
  readonly contractVersion: "viewer_scene.v1";
  readonly schemaVersion: "phase10f8.viewer_scene.v1";
  readonly atoms: readonly RenderAtom[];
  readonly bonds: readonly RenderBond[];
  readonly lattice: RenderLattice;
  readonly warnings: readonly string[];
};
```

The mapper is renderer-owned and immutable. It rechecks contract identity,
security flags, finite values, site/bond/species caps, cell expansion, JSON
bytes, indices, lattice shape, nesting, strings, safe colors, and radii. Raw
artifact fields are never spread into Three.js, DOM, CSS, module imports,
textures, shaders, callbacks, or URLs. These types are frontend display models;
they do not alter persisted artifacts, Tool Registry, AnalysisPlan, Job, or
QueueWorkerRuntime contracts.

## Phase 10F-15 Addendum: formal minimal viewer identity and metrics

`structure.viewer_3d` is the formal product capability. Its backend adapter
emits the same canonical artifacts as `structure.viewer_scene`:

- `viewer_scene.json` (`phase10f8.viewer_scene.v1`)
- `viewer_scene_manifest.json` (`phase10f9.viewer_scene_manifest.v1`)
- `summary.md`
- `recipe.json`

No HTML, JavaScript, renderer, shader, texture, or external asset is embedded.
Browser renderer availability is separate from backend job success.

The frontend-only evidence model adds `ViewerRendererMetrics` with atom, bond,
species, instanced-mesh, lattice-edge, draw-call, geometry, material, triangle,
line, initialization-time, and first-frame fields. Metrics are not persisted
into the canonical artifact and do not change the viewer scene contract.

Canonical, adapter, and renderer hard caps remain aligned at 256 sites, 2048
bonds, 32 species, cell expansion `[1, 1, 1]`, and 1,000,000 JSON bytes.
Renderer-side truncation is prohibited.

## Phase 10F-16 Addendum: frontend inspection state and measurements

Phase 10F-16 does not change `viewer_scene.v1`. Frontend-only inspection state
contains a mode (`inspect`, `distance`, `angle`, or `dihedral`), up to four
canonical site indices, and one active site index. Instanced picking maps through
an application-owned immutable `instanceId -> siteIndex` array.

Distance uses two displayed canonical Cartesian positions in angstrom. Angle is
A-B-C in degrees. Dihedral is signed A-B-C-D in `[-180, 180]` degrees. Degenerate
or non-finite inputs produce typed frontend failures. No minimum-image periodic
correction, inferred chemistry, or persisted measurement artifact is added.

PNG export is a frontend-local view capture bounded to 4096 by 4096 and
16,777,216 effective pixels. It does not alter Artifact, Recipe, AnalysisPlan,
Job, Tool Registry, QueueWorkerRuntime, or canonical scene schemas.

## Phase 10F-17 Addendum: periodic frontend identity and view state

Phase 10F-17 does not change `viewer_scene.v1`. Frontend-only identity is
`PeriodicSiteRef { siteIndex, imageOffset: [i,j,k] }`, where the integer offset
translates the canonical site by row lattice vectors. Supercell repeat, derived
replicas, resolved minimum-image offsets, and measurement history are local view
state and are never persisted into canonical artifacts.

Minimum-image search is finite and typed: radius at most 4, at most 729
candidates, deterministic lexicographic ties, finite/condition checks, and no
silent direct-distance fallback. Derived display caps are 2048 sites and 8192
bonds with repeat axes 1 through 3. Canonical bonds lack endpoint image offsets,
so only provable same-cell bond replication is rendered.

## Phase 10F-18 Addendum: canonical periodic bond topology

Adapters now emit `viewer_scene.v2` / `phase10f18.viewer_scene.v2`. A periodic
bond contains strict `from` and `to` endpoints, each with canonical `site_index`
and integer `image_offset`, plus Cartesian displacement, angstrom distance,
allowlisted source, and authority flag. The normalized source image is zero and
the target image is relative. Reverse-equivalent edges share one stable key.

`distance_cutoff` topology is always non-authoritative. Distances are checked
against row-vector lattice translation within `1e-5` angstrom. Canonical bonds
are capped at 2048, endpoint components at absolute value 3, and renderer-local
derived bonds at 8192. `viewer_scene.v1` remains valid but missing offsets mean
same-cell only; no cross-boundary topology is inferred or migrated.

## Phase 10F-19 Addendum: periodic scene capabilities and manifest v2

`viewer_scene.v2` adds a required, exact `capabilities` object. It declares
periodic structure/bonds, cross-boundary bonds, and the emitted neighbor graph;
trajectory, phonon, and volumetric capabilities are false. Bond fields,
identity, offsets, distance tolerance, and caps are unchanged. v1 is unchanged.

New adapter output uses `phase10f19.viewer_assets_manifest.v2` with
`scene_contract = phase10f18.viewer_scene.v2`, `periodic_topology = true`,
`renderer_included = false`, and `webgl_included = false`. Historical
`phase10f9.viewer_scene_manifest.v1` remains readable.

## Phase 10F-20 Addendum: viewer schema lifecycle

The application-owned compatibility registry recognizes exactly three scene
contracts. `phase10d1.viewer_scene.v1` is deprecated read-only and JSON-only;
it is rejected before renderer mapping. `phase10f8.viewer_scene.v1` is supported
legacy same-cell and cannot claim periodic endpoints. `phase10f18.viewer_scene.v2`
is current and is the only default production output.

Manifest v1 contracts remain inert compatibility records. The current
`phase10f19.viewer_assets_manifest.v2` must pair with v2 and cannot include a
renderer, WebGL, executable, or external asset. No automatic conversion exists:
missing endpoint image offsets and capabilities are never inferred.

## Phase 10F-22 Addendum: frontend accessibility contract

Phase 10F-22 does not change any persisted schema. The validated renderer owns
its focusable region, bounded keyboard camera actions, semantic scene summary,
polite state announcements, and capped periodic-neighbor table. Artifact values
remain inert text/data and cannot provide roles, ARIA attributes, shortcuts,
event handlers, focus targets, CSS, or live-region policy.

The semantic summary reports the validated formula, canonical site/species and
bond counts, lattice, cross-boundary/self-periodic topology counts, render tier,
periodic selection identity, and warnings. It is frontend state only and is not
written to Artifacts, Recipes, AnalysisPlans, or Jobs.

## Phase 10F-23 Addendum: local measurement artifact

`phase10f23.viewer_measurement.v1` is a frontend-local inert JSON download. It
records source scene schema/resource/formula, measurement kind and coordinate
mode, two to four exact `PeriodicSiteRef` points, rounded value/unit/precision,
policy warnings, and explicit false structure/topology mutation flags. It is not
a backend Artifact contract and grants no execution authority.

## Phase 10F-26 Addendum: local scientific export contracts

`phase10f26.viewer_export_state.v1` is a frontend-local inert view-state
download. It records validated scene identity, renderer-local supercell repeat,
camera, clipping, display flags, up to twenty bounded measurements, optional
selected-site summary, and an exact export request. It explicitly declares that
the screenshot is not scientific source data and that structure/topology were
not mutated.

`phase10f26.viewer_export_manifest.v1` lists exactly `viewer.png`,
`viewer_export_state.json`, and `viewer_export_summary.md` in deterministic
order, with media type, byte size, and SHA-256. It declares no renderer,
JavaScript, or external asset. Both schemas are local downloads, not persisted
backend Artifact types and not executable Tool Registry or AnalysisPlan inputs.

Export requests allow only PNG/JSON/Markdown, light/dark/transparent background,
DPR 1 or 2, and application-owned overlay booleans. Effective dimensions and
memory are capped before allocation. No canonical viewer scene, periodic bond,
manifest v2, planner, adapter, or runtime contract changes.

## Phase 10F-27 Addendum: formal viewer product identity

`structure.viewer_3d` is the unique formal product tool for generating the
current inert `phase10f18.viewer_scene.v2` and
`phase10f19.viewer_assets_manifest.v2` pair. Its registry owner is
`platform_builtin_manifest.yaml`, its adapter is `StructureViewer3DAdapter`,
and its artifacts contain no renderer code. Explicit scene-data export remains
`structure.viewer_scene`; both producers share the same canonical schema and
validation semantics. No scene, manifest, AnalysisPlan, or runtime schema is
changed by formal registration.

## Phase 10G Addendum: trajectory contract family

The inert trajectory family is `phase10g.trajectory.v1`,
`phase10g.trajectory_frame.v1`, `phase10g.trajectory_summary.v1`, and
`phase10g.trajectory_manifest.v1`. Atom identity is stable zero-based index;
frame identity is zero-based contiguous index. Atom count, order, species, and
occupancy 1.0 remain fixed across frames.

Coordinates are trajectory-wide fractional or Cartesian. Lattice vectors are
rows and `cartesian = f0*a + f1*b + f2*c`. Fixed trajectories use one top-level
lattice; variable trajectories require one per frame. Wrapped, unwrapped, and
unknown semantics are retained without validator mutation. Time, velocities,
forces, total-system energy, and temperature use closed canonical units; stress,
partial occupancy, partial PBC, arbitrary properties, and variable atom count
are deferred.

The JSON contract has hard atom/frame/value/byte/metadata bounds, content-derived
SHA-256 identity, exact field allowlists, deterministic serialization, and no
executable or external reference. It does not modify static viewer scenes and
does not register or authorize a parser, adapter, trajectory tool, or viewer.

## Phase 10G-1 Addendum: parser report and artifact types

`phase10g.trajectory_parse_report.v1` is a bounded inert parser audit containing
detected format, frame/atom counts, coordinate/lattice modes, detected approved
properties, unit conversions, source-ID reorder state, warning codes, input
SHA-256, and deterministic=true. It excludes source content, paths, stack,
environment, URLs, and executable data.

The shared artifact enum adds `trajectory_json`, `trajectory_summary_json`,
`trajectory_report_json`, and `trajectory_manifest_json`. The canonical manifest
hashes trajectory and summary; artifact listing supplies report and manifest
identity without a circular manifest self-hash. No static viewer schema changes.
