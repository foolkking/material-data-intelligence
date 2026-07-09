# RDF API Transcript

Generated at: 2026-07-09T01:24:33.987133+00:00

- service mode: FastAPI local service, deterministic Mock Planner, persisted AnalysisPlan, QueueWorkerRuntime, Tool Registry validation, and local worker.
- backend URL: http://127.0.0.1:8128
- real LLM: not used.

## Successful RDF jobs

### simple_cubic_cif
- request: POST /planner/jobs
- prompt: 计算 RDF
- response status: 200
- job id: `job_cccfebd4cdf641e580538e01`
- plan id: `plan_1096d3645cb6455cbad7df5b`
- selected tool: `structure.rdf`
- artifacts: rdf.json, rdf_plot.json, summary.md, recipe.json

### nacl_poscar
- request: POST /planner/jobs
- prompt: Generate radial distribution function
- response status: 200
- job id: `job_9cbcb0cdd8404f878302e7d7`
- plan id: `plan_705c73bfcd914dae995fa462`
- selected tool: `structure.rdf`
- artifacts: rdf.json, rdf_plot.json, summary.md, recipe.json

## Negative routing

| Prompt | Routed tool | Routes to RDF |
|---|---|---:|
| 生成 XRD 图谱 | `structure.xrd` | false |
| Generate XRD pattern | `structure.xrd` | false |
| 生成这个结构的 coordination histogram | `structure.coordination_hist` | false |
| 计算配位数直方图 | `structure.coordination_hist` | false |
| 打开交互式 3D viewer | `structure.preview_metadata` | false |
| 用 WebGL 显示这个晶体 | `None` | false |
| 生成 Brillouin zone 3D | `structure.preview_metadata` | false |
| 画 phonon bands | `None` | false |
| 画 phonon DOS | `None` | false |
| experimental PDF fitting | `None` | false |
| neutron scattering refinement | `None` | false |
| Rietveld refinement | `None` | false |
| 做 Voronoi local environment analysis | `None` | false |
| 做 CrystalNN chemical environment classification | `structure.summary` | false |
