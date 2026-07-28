# 共享 Schema 规范

## Phase 10K-2 Dataset Materials Explorer product artifact

`dataset.materials_explorer` consumes exactly one validated Material Data
Profile 2.0 and its explicitly bound canonical table and optional Structure
resources. Profile 2.0 remains the semantic-role and sample-identity authority;
the adapter does not infer another formula, property, split, or resource-role
contract. The deterministic content identity includes the profile semantic
hash plus sorted object IDs and normalized object hashes.

The primary inert artifact has schema
`phase10k2.dataset_materials_explorer.v1`. It is one bounded `table_json`
product bundle with dataset identity/resource bindings, overview, composition,
structures, properties, quality, comparison, linked samples, warnings, and
explicit truncation/cap metadata. Companion outputs are
`dataset_quality.json`, `summary.md`, and `recipe.json`. All sample links use
Profile 2.0 stable sample references rather than display-array position.

Composition occurrence, stoichiometric sum, and fractional sum are distinct.
Property statistics use finite values only and preserve missing/non-finite
counts and declared units. Structure duplicates require identical canonical
normalized object hashes; reduced formulas are formula duplicates only, and
near-duplicate or chemical-validity claims are absent. Comparison requires two
explicit resources or one explicit group column and two values; row order never
defines a split, and unlike units are not converted or compared.

Hard execution limits are 100,000 rows, 512 columns, 64 properties, 256
categories, 200 linked rows, 100 histogram bins, 256 structures, 5,000 atoms
per structure, 128 warnings, and 8,000,000 bytes per artifact. Bounded display
lists disclose truncation without changing denominators. Artifacts contain no
JavaScript, HTML authority, callback, URL, executable content, external asset,
ML evaluation, embedding, clustering, or Agent interpretation.

## Phase 10J-1 volumetric source integration

`VolumetricData` is the normalized source object accepted by the strict public parser tool `structure.volumetric_data`. It is not a second artifact contract: the adapter converts it into the existing `phase10j.volumetric_grid.v1`, payload, field, dataset, and manifest schemas. Allowed source formats are `vasp_volumetric` and `gaussian_cube`; the parser cap is 2,097,152 voxels while the larger Phase 10J contract cap remains the trusted canonical upper boundary.

VASP source values are x-fastest and convert to canonical `ijkc_component_fastest`; CUBE already uses i-outer/j-middle/k-fastest order. CUBE spatial units and density volume units are explicitly converted. Outputs are deterministic little-endian float32/float64 raw or gzip binary plus inert JSON metadata. Multi-orbital CUBE, URLs, executable metadata, and renderers are excluded.

## Phase 10I Brillouin-zone contract family

Phase 10I adds five inert schema identities:

- `phase10i.reciprocal_lattice.v1`
- `phase10i.brillouin_zone.v1`
- `phase10i.kpath.v1`
- `phase10i.brillouin_zone_manifest.v1`
- `phase10i.tolerance_policy.v1`

Real and reciprocal lattice vectors are rows. The canonical formulas are
`r_cart=r_frac*A`, `B=2*pi*(A^-1)^T`, `A*B^T=2*pi*I`, and
`k_cart=k_frac*B`; `A` uses angstrom and `B` uses `angstrom^-1`. The BZ is the
origin-centered Wigner-Seitz cell of the standardized primitive reciprocal
lattice. Vertices, undirected edges, and outward counter-clockwise faces have
canonical stable order and exact incidence; a valid polyhedron is closed,
convex, manifold, centrally symmetric, has Euler characteristic 2, and volume
`(2*pi)^3/|det(A)|`.

The optional k-path is provider-bound and geometry-independent. It stores safe
point labels/aliases, reciprocal-fractional and Cartesian coordinates, explicit
path variants, segments, discontinuities, cumulative Cartesian reciprocal
distance, time-reversal policy, and provider tolerances. Phase 10H's
`radian_per_angstrom` path-distance spelling is explicitly compatible with
Phase 10I `angstrom^-1` under the shared `physics_2pi` convention; structure,
primitive lattice hash, and selected endpoints must still match.

Every artifact uses exact fields, versioned independent tolerances, hard caps,
canonical JSON/content hashes, and the same closed inert security declaration.
There is no JavaScript, HTML, CSS, URL, shader, executable asset, renderer, or
WebGL artifact.

Phase 10I-1 registers `structure.brillouin_zone` as the canonical data producer
for exactly one ordered, non-magnetic, 3D periodic `Structure`. Its exact output
types are `reciprocal_lattice_json`, `brillouin_zone_json`, `kpath_json`,
`brillouin_zone_manifest_json`, `summary_md`, and `recipe_json`. The first four
map one-to-one to the schema identities above. This registration grants only
validated asynchronous artifact generation. Artifacts allocate no canvas or
WebGL context and carry no renderer capability.

Phase 10I-2 adds an application-owned consumer without changing these schemas.
The frontend independently validates the reciprocal/BZ/k-path/manifest bundle,
then maps canonical reciprocal Cartesian `angstrom^-1` coordinates exactly once
into a uniformly scaled local Three.js scene. Faces are bounded-triangulated
from canonical outward-CCW loops; canonical edges, points, segments,
discontinuities, IDs, and provider semantics are preserved. Camera, visibility,
opacity, selection, projection, labels, and PNG export are renderer-local state
and are not written into canonical artifacts. Artifact `renderer_included=false`
continues to mean that no executable renderer is packaged, not that the
application lacks a validated consumer.

Phase 10I-3 adds the frontend-only typed model
`phase10i3.reciprocal_band_bz_link.v1`. It binds independently validated Phase
10H phonon-band and Phase 10I reciprocal/BZ/k-path artifacts by content hashes,
structure identity, standardized primitive real lattice, `physics_2pi`
convention, units, selected path variant, ordered segments, discontinuities,
and exact sampled q-point geometry. It stores no new band or BZ scientific data
and is not a persisted artifact schema or public tool output.

Point occurrence identity is distinct from geometric point identity. Segment
mappings retain order and direction; sample mappings retain source q-point
index, segment, normalized `t`, path distance, and residual. Labels are display
metadata only. Reciprocal q-point selection never implies a phonon branch or
mode; exact branch/mode identity is preserved only from band-originated state
or an exact H4/H5 binding. Discontinuities are never interpolated. Shared
selection is bounded, ephemeral frontend state and cannot mutate source
artifacts or grant execution authority.

## Phase 10G-2 trajectory viewer internal display contract

The persisted schema remains `phase10g.trajectory.v1`. The frontend derives immutable per-frame display scenes with stable `atomIndex` and renderer-local `imageOffset`; these are not artifacts and do not modify the canonical contract. Current/requested frame, playback, cache, supercell, clipping, camera, selection, and measurements are application-owned local state. Dynamic bond inference and artifact-controlled execution remain forbidden.

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
  | "dataset"
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
    | "volumetric"
    | "table"
    | "unknown";
  files: FileProfile[];
  objects: ObjectProfile[];
  structureSummary?: StructureSummary;
  tableSummary?: TableSummary;
  phononSummary?: Record<string, unknown>;
  trajectorySummary?: Record<string, unknown>;
  qualityIssues: QualityIssue[];
  recommendedTasks: RecommendedTask[];
  profileContractVersion?: "2.0";
  semanticRulesVersion?: string;
  semanticHash?: string;
  semanticColumns?: DataProfileSemanticColumn[];
  semanticGroups?: DataProfileSemanticGroup[];
  resourceSemantics?: DataProfileResourceSemantic[];
  analysisReadiness?: DataProfileAnalysisReadiness[];
  sampleIdentity?: DataProfileSampleIdentity;
  profileCoverage?: DataProfileCoverage;
  createdAt: string;
};

type DataProfileSemanticRole = {
  role:
    | "material_formula"
    | "material_property"
    | "sample_identity"
    | "regression_target"
    | "regression_prediction"
    | "regression_uncertainty"
    | "classification_target"
    | "classification_prediction"
    | "class_probability";
  authority:
    | "explicit_metadata"
    | "user_declared"
    | "canonical_name"
    | "alias_match"
    | "bounded_pattern";
  groupId?: string;
  details: Record<string, unknown>;
};

type DataProfileSemanticColumn = {
  objectId: string;
  column: string;
  dtype: string;
  roles: DataProfileSemanticRole[];
  missingCount: number;
  uniqueCount: number;
  finiteCount?: number;
  nonFiniteCount?: number;
  rowsInspected: number;
  totalRows: number;
  unit?: string;
  ambiguities: string[];
};

type DataProfileSemanticGroup = {
  groupId: string;
  kind: "regression" | "classification" | "class_probability";
  targetColumns: string[];
  predictionColumns: string[];
  uncertaintyColumns: string[];
  probabilityColumns: string[];
  classes: string[];
  seriesBindings: DataProfileSemanticSeriesBinding[];
  status: "COMPLETE" | "INCOMPLETE" | "AMBIGUOUS";
  reasons: string[];
};

type DataProfileSemanticSeriesBinding = {
  seriesId: string;
  predictionColumn?: string;
  uncertaintyColumns: string[];
};

type DataProfileAnalysisReadiness = {
  capability: string;
  dataStatus: "READY" | "MISSING_REQUIRED_DATA" | "AMBIGUOUS" | "UNSUPPORTED_DATA_KIND";
  platformStatus: "AVAILABLE" | "NOT_IMPLEMENTED" | "NOT_EVALUATED";
  reasons: string[];
  requiredSemantics: string[];
  matchingGroups: string[];
};

type DataProfileResourceSemantic = {
  objectId: string;
  objectType: string;
  objectHash: string;
  kind: string;
  facts: Record<string, unknown>;
  capabilities: string[];
  warnings: string[];
};

type DataProfileSampleIdentity = {
  policy: "explicit_column" | "object_hash_row_index";
  explicitColumn?: string;
  fallbackPolicy: "dataset_version_object_hash_row_index";
  datasetVersion: string;
  objectIds: string[];
};

type DataProfileCoverage = {
  policy: "complete" | "deterministic_bounded_sample";
  rowsInspected: number;
  totalRows: number;
  columnsInspected: number;
  totalColumns: number;
  limits: Record<string, number>;
  warnings: string[];
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
  objectHash?: string;
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

## Phase 10G-3 Addendum: formal trajectory viewer product metadata

Phase 10G-3 does not change the trajectory, frame, summary, parse-report, or
manifest contracts. `structure.trajectory_viewer` is the unique formal product
identity and emits the same four inert JSON artifacts as the internal import
adapter. Persisted Artifact metadata may additionally carry application-owned
viewer launch options, exact capability truth, and desktop/mobile resource
budgets; runtime-owned tool/plan identity overrides any colliding adapter key.

Frontend launch mapping accepts only the strict registered speed, loop,
1-through-3 supercell, cell, clipping, `performanceMode=auto`, and
`bondMode=none` values. Performance tier, fps, cache, pending-request limits,
WebGL capability, and renderer implementation remain client-owned and are not
canonical trajectory fields. Dynamic bonds, analytics, editing, video, remote
frames, and executable assets remain unsupported.

## Phase 10H Addendum: phonon contract family

The inert phonon family is `phase10h.phonon_band.v1`,
`phase10h.phonon_dos.v1`, `phase10h.phonon_summary.v1`, and
`phase10h.phonon_manifest.v1`. Shared semantics are named by
`phase10h.qpoint_path.v1`, `phase10h.frequency_axis.v1`, and
`phase10h.phonon_source.v1`; `phase10h.phonon_mode_ref.v1` is reserved for a
later eigenvector phase and defines no payload here.

Real-space lattice vectors are rows. The canonical reciprocal lattice is the
physics convention `B = 2*pi*(A^-1)^T`, so reciprocal-fractional q-points map
through `q_cart = q*B` and path distance has unit `radian_per_angstrom`.
Segments retain source order and explicit discontinuities. Duplicated segment
endpoints are stored as distinct q-points; global distance excludes a declared
discontinuity gap and never resets.

Canonical frequency is cyclic `terahertz`. Approved source-boundary conversion
units are `inverse_centimeter` and `millielectronvolt`, using exact SI defining
constants. Negative real values encode imaginary modes. Zero tolerance only
classifies values and the validator performs no acoustic-sum-rule correction.
Branch identity is source-stable contiguous index, version 1 requires full
`3N`, and degeneracy is source-declared metadata without branch merging.

DOS frequencies are strictly increasing THz sample grid points and may include
negative values. Total density is `modes_per_terahertz`, normalized by a
trapezoidal integral approximately equal to `3N`. Projected series use exact
atom or species identity in canonical atom order. Band/DOS compatibility checks
structure/order, unit, imaginary encoding, tolerance, calculation lineage, cell
relation, input hash, and NAC metadata.

All objects use exact fields, finite numbers, deterministic order and
serialization, hard atom/q-point/branch/DOS/projection/value/metadata/byte caps,
and explicit no-executable/no-external security flags. This schema family does
not register a phonon tool, parser, adapter, plot, renderer, eigenvector,
animation, notebook/script, external API, or real LLM execution path.

## Phase 10H-1 Addendum: phonon band product artifacts

The canonical Phase 10H schemas and scientific semantics are unchanged.
`phonon.band` now produces `phonon_band_json`, `phonon_summary_json`,
`phonon_report_json`, `phonon_manifest_json`, `plotly_json`, `table_json`, and
`recipe_json`. The canonical manifest still hashes exactly band and summary;
report, plot, table, manifest, and recipe are additional persisted artifacts,
not new canonical phonon scientific fields.

`phase10h1.phonon_band_parse_report.v1`,
`phase10h1.phonon_band_plot.v1`, and
`phase10h1.phonon_band_table.v1` are inert product/audit contracts. They grant
no solver, script, URL, HTML, JavaScript, renderer, DOS, eigenvector, or
animation authority. Frontend Plotly mapping occurs only after independent
validation of `phase10h.phonon_band.v1`.

## Phase 10H-2 Addendum: phonon DOS product artifacts

The canonical `phase10h.phonon_dos.v1` fields and semantics remain unchanged.
`phonon.dos` adds `phonon_dos_json` plus inert report, plot, table, and recipe
products. DOS-only execution uses additive
`phase10h2.phonon_dos_summary.v1` and
`phase10h2.phonon_dos_manifest.v1`; stable band-rooted family contracts are not
relaxed or populated with a synthetic band.

At approved text boundaries, `f_target = c*f_source` requires
`D_target = D_source/c`. Unit-area sources scale total and all projections by
`3N/integral`; total-mode sources are validation-only. Negative frequencies
are preserved, completeness is explicit, broadening is metadata only, and no
backend or frontend resampling/smoothing is permitted.

## Phase 10H-3 Addendum: combined phonon band and DOS product

`phonon.band_dos` consumes one independently validated band artifact and one
independently validated DOS artifact. It adds the inert schemas
`phase10h.phonon_band_dos.v1`, `phonon_band_dos_summary.v1`,
`phonon_band_dos_compatibility_report.v1`, `phonon_band_dos_plot.v1`,
`phonon_band_dos_table.v1`, and `phonon_band_dos_manifest.v1`. Stable Phase 10H
band and DOS schemas are unchanged.

The combined contract references source artifact IDs, schemas, byte sizes, and
SHA-256 values. Compatibility checks structure identity, canonical atom order,
cell/calculation/force-constant lineage, approved frequency conversion, DOS
density Jacobian and integral invariance, imaginary encoding, zero tolerance,
NAC, normalization, projections, caps, and shared-domain policy in deterministic
order. Incompatible inputs produce no success artifacts.

Display uses band q-path distance and DOS density on separate x domains with
one shared THz frequency y-axis. Plot data is inert and mapped only by
application-owned frontend code after independent validation. No eigenvector,
animation, solver, HTML, JavaScript, external asset, or network authority is
added.

## Phase 10H-4 Addendum: phonon eigenvector contract

The inert eigenvector family is `phase10h.phonon_mode_ref.v1`,
`phonon_eigenvector.v1`, `phonon_eigenvector_set.v1`,
`phonon_eigenvector_summary.v1`, and `phonon_eigenvector_manifest.v1`, with
shared `phase10h.complex_scalar.v1` and `complex_vector3.v1` representations.

A mode reference binds the canonical band artifact SHA-256, structure and
calculation identity, reciprocal-fractional q-point and segment, source-stable
branch, THz frequency, and optional Gamma NAC direction. Stored vectors are
Cartesian dimensionless mass-weighted eigenvectors with global Euclidean unit
norm. Canonical global phase makes the first nonzero atom-major xyz component
real and positive; scientific equivalence ignores one common phase.

Real-space display direction is `u_i=e_i/sqrt(m_i)`. Non-Gamma image phase is
`2*pi*q_fractional.cell_image`; display amplitude is a separate bounded
angstrom maximum-atom scale with no thermal or trajectory meaning. Source
degeneracy is preserved without cross-source individual-mode matching.

This contract adds no parser, adapter, tool, planner route, UI, animation,
solver, external asset, notebook/script, network, or real LLM authority.
# Phase 10H-5 Phonon Animation Schemas

The current dynamic phonon visualization family is `phase10h5.phonon_animation.v1`, `phase10h5.phonon_animation_summary.v1`, `phase10h5.phonon_animation_manifest.v1`, and `phase10h5.phonon_animation_recipe.v1`. The package binds one exact H4 mode, canonical structure, source band/eigenvector hashes, bounded renderer-local diagonal supercell, display/playback metadata, caps, warnings, inert security, and provenance. It stores no frames or executable/remote resources. Shared artifact types add `phonon_animation_json`, `phonon_animation_summary_json`, and `phonon_animation_manifest_json`; material object types add `PhononEigenvector` for strict role binding.

Animation reconstruction uses mass-unweighted Cartesian vectors, fixed mode-envelope display scaling, canonical phase, and `2*pi*q_fractional.cell_image`. Display scale is angstrom-valued visualization state, not a physical amplitude.

## Phase 10J Addendum: inert real-space volumetric data

The canonical family is `phase10j.volumetric_grid.v1`,
`phase10j.volumetric_payload.v1`, `phase10j.volumetric_field.v1`,
`phase10j.volumetric_dataset.v1`, and `phase10j.volumetric_manifest.v1`.

Real-space lattices and affine steps are row vectors. Structure coordinates use
`r_cart = r_frac*A`; grid samples use
`origin + (i+s)step_0 + (j+s)step_1 + (k+s)step_2`, where `s=0` for nodes and
`s=0.5` for cell centers. Periodic grids are three-dimensional, structure-bound,
and endpoint-excluded. Mixed periodicity is not accepted. Logical storage is
`(i,j,k,c)` with component fastest.

The contract supports finite real scalar, Cartesian real vector, and interleaved
real/imaginary complex scalar fields. Binary storage is little-endian float32 or
float64 with raw, deterministic gzip, or bounded whole-i-slab chunk encoding;
small fixtures may use inline JSON. Logical and storage SHA-256 identities are
separate. Exact byte lengths, caps, chunk coverage, gzip ratio/member bounds,
quantity/unit compatibility, normalization, spin, potential gauge, statistics,
structure/lattice binding, and inert security metadata are validated.

This family grants no parser, adapter, tool, planner, runtime, renderer,
isosurface, slice, script, URL, HTML, JavaScript, CSS, shader, object
deserialization, or external-resource authority.

## Phase 10J-3 charge and spin product addendum

The volumetric field contract remains source-native. The product layer may
consume explicit `electron_density`, explicitly signed `charge_density`, and
collinear `spin_difference` fields. It may emit only the allowlisted derived
spin channels with formula IDs `COLLINEAR_SPIN_UP_V1` and
`COLLINEAR_SPIN_DOWN_V1`, source provenance, and validated zero-residual
relationships. Electron density is not signed electric charge density.
Full-cell integrals are not atomic partition results, and augmentation
contributions must remain visible as source warnings when unavailable.

## Phase 10J-4 potential product addendum

Potential products accept only validated real scalar `local_potential` or
explicit `electrostatic_potential` fields with exact unit and reference
metadata. Source fields remain immutable. Source-native, cell-average-zero,
and selected-point-zero are product-local constant gauges. Surface layers bind
source-native and displayed isovalues so gauge changes preserve source contour
identity. Trilinear samples, point differences, and three unsmoothed canonical
lattice-axis planar profiles bind to the source field hash; they provide no vacuum, Fermi, work-function,
cross-calculation alignment, electric-field, or arbitrary slicing authority.
# Phase 10J-2 Volumetric Structure Overlay

`phase10j2.volumetric_structure_overlay.v1` is an additive, inert, renderer-consumer artifact. It binds exactly to one validated `phase10j.volumetric_grid.v1` by `grid_id` and `grid_content_hash`. Fully periodic sources may embed one independently validated canonical viewer scene; fully non-periodic sources may carry bounded `{atomic_number, cartesian_angstrom}` records. The artifact is not part of `phase10j.volumetric_manifest.v1` schema identity and does not modify the canonical grid, field, payload, dataset, or manifest contracts.

The overlay security object is the canonical Phase 10J inert security declaration. It cannot contain executable content, HTML/CSS, JavaScript, shaders, renderer code, URLs, external assets, callbacks, or arbitrary appearance data. Missing overlay context is a supported renderer state and never changes backend job success.
## Phase 10J-5 Application-Owned ELF / Orbital Product Model

Phase 10J-5 does not change the canonical Phase 10J grid, payload, field,
dataset, or manifest schemas. The frontend may derive an immutable bounded
`phase10j5.elf_orbital_product.v1` view model only after canonical validation.
It binds the dataset/manifest/source-field hashes, exact quantity/unit,
normalization and integral semantics, full-cell integral, dtype-aware range
status, source identity completeness, exact contour presets, warnings, and the
fixed no-execution security policy. This view model is not persisted as a
canonical scientific artifact and does not authorize new tool execution.

ELF compatibility is exactly real scalar `electron_localization_function` in
`dimensionless`. Orbital compatibility is exactly real scalar
`orbital_density` in `electron/angstrom^3` or `angstrom^-3`. Missing
band/k-point/orbital/occupancy identity remains missing; filenames cannot fill
it. A renderer-local periodic structure overlay may be derived at `1x1x1` or
`2x2x2` within eight replicas, 4096 atoms, and 8192 bonds, while the scalar
field remains the source cell.

## Phase 10J-6 Application-Owned Slice / Direct Volume Models

Phase 10J-6 does not change the canonical Phase 10J grid, payload, field,
dataset, or manifest schemas. A validated frontend may derive an ephemeral,
immutable `phase10j6.volumetric_slice.v1` model for exactly one canonical
lattice-axis plane. It binds source dataset/field hashes, axis, fractional and
physical position, exact-grid or one-axis linear interpolation metadata,
affine plane origin/bases/normal, output shape, float64 sampled values, unit,
statistics, deterministic SHA-256, and `sourceMutated=false` provenance.

Direct Volume is renderer state rather than a scientific artifact. Canonical
`ijkc` storage maps without transpose to a 3D texture with
`width=nz`, `height=ny`, `depth=nx`; shader sampling uses `(q2,q1,q0)`.
Float64 inputs are copied to a bounded float32 display buffer with explicit
error/hash metadata. Transfer function, palette, quality, clipping, camera,
structure depth target, and WebGL capability are application-owned display
state and never modify or extend the canonical source artifact.

Only finite real scalar one-component node data is supported. No artifact may
supply shader, Worker/WASM, transfer code, plane expression, URL, texture,
module, callback, HTML, CSS, or execution authority. Cell-centered,
vector/complex, arbitrary oblique/curved slices, resampling, downsampling,
segmentation, feature detection, and 4D volume remain outside this model.
