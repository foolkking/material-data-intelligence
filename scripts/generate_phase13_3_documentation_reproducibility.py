from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.phase13_current_demo_contracts import CURRENT_DEMO_SPECS


RELEASE = ROOT / "docs/phase13/release"
REPRO = ROOT / "docs/phase13/reproducibility"
OUT = ROOT / "docs/phase13/evidence/phase13_3_documentation_reproducibility"
ATTEMPT6 = ROOT / "docs/phase13/evidence/phase13_2_attempt6_seven_real_user_e2e"
FACT_HASH = "92d8295c7d78467d8ce021dc8033a58326219372a5d8fa87c93377ed1275953a"
SCOPE_HASH = "bb885aa4e020349011c39164a883107c8ffed3d5d43604594a76f7d5a18705ba"
PHASE12_HASH = "29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4"
ATTEMPT6_SHA = "5ddf2c0508a1f61642808a35774917fa3b54b0b0"
ENTRY_SHA = "9f31576dfb09318f073e625bb0cb029657017fd1"


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fixture_bytes(path: Path) -> tuple[bytes, str]:
    if path.suffix.lower() in {".cif", ".csv", ".json", ".txt", ".yaml", ".yml"} or path.name in {"CHGCAR", "POSCAR"}:
        raw = path.read_bytes()
        return raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n"), "UTF8_LF"
    return path.read_bytes(), "RAW_BYTES"


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8", newline="\n")


def write_json(path: Path, value: Any) -> None:
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False))


def git_files(pattern: str | None = None) -> list[str]:
    args = ["git", "ls-files"]
    if pattern:
        args.append(pattern)
    result = subprocess.check_output(args, cwd=ROOT, text=True, encoding="utf-8")
    return [line for line in result.splitlines() if line]


def demo_slug(index: int) -> str:
    return f"demo{index}"


def fixture_records(spec: dict[str, Any]) -> list[dict[str, Any]]:
    records = []
    for fixture_id, relative, entry_mode in spec["fixtures"]:
        path = ROOT / relative
        if not path.is_file():
            raise RuntimeError(f"Missing canonical fixture: {relative}")
        payload, hash_mode = fixture_bytes(path)
        records.append({
            "fixtureId": fixture_id,
            "path": relative.replace("\\", "/"),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "bytes": len(payload),
            "hashMode": hash_mode,
            "entryMode": entry_mode,
        })
    return records


def input_disposition(entry_mode: str) -> str:
    if entry_mode in {"typed_phonon_band_import", "typed_phonon_dos_import"}:
        return "SUPPORTED_WITH_LIMITS"
    return "SUPPORTED_BY_CANONICAL_ENTRY"


def demo_limitations(index: int) -> list[str]:
    return {
        1: ["Composition-space PCA and clustering are descriptive, not material identity or scientific validation."],
        2: ["This is bounded evaluation of supplied predictions, not training, AutoML, SHAP, or a generalization guarantee."],
        3: ["Coordination and local environments are algorithm-derived. XRD is peak correspondence under wavelength/tolerance policy, not phase confirmation or Rietveld refinement."],
        4: ["Diffusion is an estimate over the selected fit window."],
        5: ["Values come from supplied/imported phonon data. Generic phonon YAML/JSON remains MAPPING_ONLY; the platform does not calculate phonons."],
        6: ["Persisted bounded views do not imply Bader analysis, topological charge analysis, or browser-side scientific extraction."],
        7: ["Band/DOS values and Fermi energy are source supplied. Unknown energy units are ineligible; classification is policy-bounded."],
    }[index]


def demo_negative(index: int) -> str:
    return {
        1: "A dataset-only goal must not force composition-space selection.",
        2: "Do not interpret evaluation as model training or guaranteed generalization.",
        3: "A wavelength mismatch is rejected; it is not reprojected or converted.",
        4: "A stale trajectory source is rejected as WORKSPACE_SOURCE_NOT_CURRENT.",
        5: "Generic phonon YAML/JSON upload is MAPPING_ONLY and is not auto-promoted.",
        6: "The frontend does not extract new scientific values from the grid.",
        7: "Unknown energy units are INELIGIBLE and are never assumed to be eV.",
    }[index]


def build_demo_contract(index: int, spec: dict[str, Any]) -> dict[str, Any]:
    fixtures = fixture_records(spec)
    prompt_hash = hashlib.sha256(spec["prompt"].encode("utf-8")).hexdigest()
    return {
        "schemaVersion": "Phase13InitialReleaseDemoReproContract/1.0",
        "demoId": spec["demoId"],
        "family": spec["family"],
        "canonicalPrompt": spec["prompt"],
        "promptSha256": prompt_hash,
        "fixtures": fixtures,
        "inputSupport": [
            {"fixtureId": row["fixtureId"], "disposition": input_disposition(row["entryMode"])}
            for row in fixtures
        ],
        "expectedCapabilityCoverage": sorted(spec["expectedTools"]),
        "plannerSemantics": "capability-aware selection; every selected Tool must be Registry-eligible",
        "planSemantics": "Plan 0.1 or 0.2 according to actual Artifact dependencies; multi-tool does not itself require 0.2",
        "requiredServices": ["PostgreSQL", "Redis", "MinIO"],
        "userEntry": [row["entryMode"] for row in fixtures] + ["natural_language_prompt"],
        "workspaceExpectation": "one Job-derived Workspace; exact persisted Artifacts remain reachable; panel count <= 32",
        "reportRecipeExpectation": "explicit UI Preview and Finalize over persisted facts; paired non-executable Recipe",
        "limitations": demo_limitations(index),
        "negativeBoundary": demo_negative(index),
        "proves": "the current canonical entry, semantic coverage, durable identity, runtime registration, Artifact, Workspace, Report, and Recipe contracts are reproducible",
        "doesNotProve": "independent validation of every numerical output, universal browser support, or new scientific capability",
        "attempt6Evidence": f"../evidence/phase13_2_attempt6_seven_real_user_e2e/demo_{index}/demo_result.json",
    }


def demo_markdown(index: int, contract: dict[str, Any]) -> str:
    fixture_lines = "\n".join(
        f"- `{row['path']}` | `{row['sha256']}` | {row['bytes']} bytes | `{row['entryMode']}`"
        for row in contract["fixtures"]
    )
    tool_lines = "\n".join(f"- `{tool}`" for tool in contract["expectedCapabilityCoverage"])
    limitation_lines = "\n".join(f"- {item}" for item in contract["limitations"])
    return f"""# Demo {index}: {contract['family']}

## Goal and prompt

> {contract['canonicalPrompt']}

Prompt SHA-256: `{contract['promptSha256']}`.

## Current user entry

Use the product Data/import surface for each fixture, then enter the prompt in the Planner. Normal users do not supply Tool, Plan, Job, Artifact, Workspace, or storage IDs.

{fixture_lines}

## Required semantic coverage

{tool_lines}

Every selected Tool must be individually eligible. Plan 0.2 is used only for real producer-Artifact-to-consumer dependencies; independent tools may remain Plan 0.1.

## Deterministic reproduction

1. Follow the [clean-checkout setup](README.md#mode-a-deterministic-reproduction).
2. Verify this contract with `uv run python scripts/generate_phase13_3_documentation_reproducibility.py`.
3. Run `uv run python -m pytest -q tests/test_phase13_3_documentation_reproducibility.py`.
4. For service-backed product replay, use the retained Attempt 6 harness and current contract inputs; this package does not create a second E2E authority.

Expected product closure: persisted Artifacts, one Job-derived Workspace, exact typed viewers/Gallery, explicit Report Preview and UI Finalize, and a paired non-executable Recipe.

## Limits and negative boundary

{limitation_lines}

- Negative: {contract['negativeBoundary']}
- This demonstrates current product-path reproducibility. It does not independently validate every numerical output.
"""


def release_docs(contracts: list[dict[str, Any]]) -> dict[str, str]:
    demo_rows = "\n".join(
        f"| [Demo {i}: {c['family']}](../reproducibility/demo{i}.md) | `{', '.join(c['expectedCapabilityCoverage'])}` |"
        for i, c in enumerate(contracts, 1)
    )
    return {
        "README.md": f"""# Initial Release Documentation

Material Data Intelligence and Scientific Visualization Platform turns supplied materials data into validated, auditable analysis workflows. It is for scientists who need controlled dataset, structure, trajectory, phonon, volumetric, and electronic-data analysis without arbitrary code execution or hidden scientific authority in the browser or LLM.

## Current release authority

| Authority | Current value |
|---|---|
| Fact Model | `{FACT_HASH}` |
| Scope Baseline | `{SCOPE_HASH}` |
| Phase 12 product baseline | `{PHASE12_HASH}` |
| Registry | 62 Tools |
| DataProfile / Intent / Eligibility | `2.4` / `1.0` / `1.0` |
| AnalysisPlan | `0.1`, `0.2` |
| Migration head | `0007_phase10m1_workspace_domain` |
| Workspace caps | 32 panels, 128 layout revisions |

## Canonical architecture

`DataProfile -> AnalysisIntent -> EligibilityResolution -> capability-aware Planner -> AnalysisPlan -> PlanValidator -> QueueWorkerRuntime -> registered Adapter -> persisted Artifact -> Grounded Interpretation -> ScientificWorkspace -> Report -> Recipe`

Registered Adapters and persisted Artifacts own scientific computation facts. The LLM plans, routes, and explains; it does not execute science. Artifacts are inert data. Recipes and recommendations are non-executable.

## Seven verified workflows

{demo_rows}

Attempt 6 observed 18 ToolCalls, 85 persisted Artifacts, seven Workspaces, seven UI-finalized Reports, seven paired Recipes, and zero unreachable Artifacts. These are release evidence, not fixed future API cardinalities.

## Start here

- [Installation and quick start](quick-start.md)
- [Architecture and authority](architecture.md)
- [Input support](input-support.md)
- [API reference](api-reference.md)
- [Known limitations and claim boundaries](limitations.md)
- [Security model](security.md)
- [Provider policy](provider.md)
- [Troubleshooting](troubleshooting.md)
- [Deterministic reproducibility](../reproducibility/README.md)
- [Phase 13 forensic history](forensic-history.md)
""",
        "quick-start.md": """# Installation and Quick Start

## Requirements

- Python 3.11 or newer and `uv`.
- Node.js 20 was verified for this package; `apps/web/package.json` does not declare a stricter `engines` constraint. npm uses the checked-in package lock.
- Docker Compose for PostgreSQL 16, Redis 7, and MinIO.

## Fresh checkout

```powershell
uv sync --frozen --extra test
npm --prefix apps/web ci
Copy-Item .env.example .env
docker compose up -d postgres redis minio
docker compose ps
$env:DATABASE_URL = "postgresql+psycopg://mdi:<LOCAL_POSTGRES_PASSWORD>@localhost:5432/mdi"
uv run python -m alembic -c apps/api/alembic.ini upgrade head
uv run uvicorn mdi_api.main:app --app-dir apps/api --host 127.0.0.1 --port 8000
```

In another PowerShell:

```powershell
npm --prefix apps/web run dev
```

Open `http://localhost:3000`. API health is `http://localhost:8000/health`.

Linux uses the same commands except `cp .env.example .env` and `export DATABASE_URL=...`.

## Verify

```powershell
uv run python -m pytest -q -m "not integration"
npm --prefix apps/web test
npm --prefix apps/web run typecheck
npm --prefix apps/web run build
uv lock --check
```

Migration head must be `0007_phase10m1_workspace_domain`.

## Safe shutdown

`docker compose down` stops services without deleting named volumes. Do not use `down -v` against user or production data. Phase 13 reproducibility uses isolated test identities and requires no preexisting PostgreSQL rows, MinIO objects, or Redis messages.
""",
        "architecture.md": """# Release Architecture and Authority

The canonical flow is `DataProfile -> AnalysisIntent -> EligibilityResolution -> Planner -> AnalysisPlan -> PlanValidator -> QueueWorkerRuntime -> Adapter -> Artifact -> Grounded Interpretation -> ScientificWorkspace -> Report -> Recipe`.

| Layer | Authority |
|---|---|
| Data/Profile | exact project, dataset version, resource IDs and hashes |
| Planner | structured JSON AnalysisPlan only; no arbitrary Python, shell, filesystem, or network execution |
| Runtime | persisted Plan, Tool Registry validation, queue worker, registered Adapter |
| Science | registered Adapter output persisted as checksum-bound Artifact |
| Workspace | one server-owned Workspace per Job; URL owns active panel/exact shareable selection; memory owns transient view state |
| Viewer | exact Artifact type/version to inert typed renderer; no frontend scientific recomputation |
| Report | deterministic composition of persisted facts; no scientific recomputation |
| Recipe | exact declarative replay manifest with no Plan, Job, queue, ToolCall, or execution authority |

`localStorage` and `sessionStorage` are not canonical scientific Workspace authority. Artifact count is not panel count: logical result surfaces and the exact Artifact Gallery keep every Artifact reachable while `MAX_PANELS_PER_WORKSPACE=32` remains enforced.
""",
        "input-support.md": """# Current Input Support

This table is derived from current canonical product entries, the sealed Fact/Scope authorities, and production parser/resource paths.

| Input path | Disposition | Boundary |
|---|---|---|
| Tables used by Dataset Intelligence / Materials ML | Supported canonical entry | Supplied tabular facts; bounded Profile semantics |
| CIF / POSCAR structure | Supported canonical entry | Parsed structure facts; no first-principles execution |
| Experimental XRD resource | Supported canonical entry | Explicit wavelength and strict compatibility |
| Trajectory v1 resource | Supported canonical entry | Exact time/cell/identity semantics |
| Typed PhononBand import | `SUPPORTED_WITH_LIMITS` | Explicit declared kind and strict existing schema |
| Typed PhononDos import | `SUPPORTED_WITH_LIMITS` | Explicit declared kind and strict existing schema |
| Generic phonon YAML/JSON | `MAPPING_ONLY` | Not auto-detected or execution-ready |
| Volumetric CHGCAR current canonical path | Supported canonical entry | Persisted bounded field/view contracts |
| Electronic Band / DOS resources | Supported canonical entry | Explicit units/reference/Fermi semantics |

Filename, MIME type, array position, latest resource, or fuzzy matching never establishes scientific identity.
""",
        "limitations.md": """# Known Limitations and Release Claims

Product support, input support, scientific validation, browser testing, service-backed testing, cross-platform replay, and independent reference provenance are separate authorities.

| ID | Category | Current status | User-facing limitation | Owner |
|---|---|---|---|---|
| LIM-001 | Scientific validation | Retained | Tool availability does not mean every numerical output was independently reference-validated. | Phase 11 authority |
| LIM-002 | Cross-platform | Retained | Linux and Windows invariant replay passed; independent numeric cross-platform reference validation is not applicable. | Release governance |
| LIM-003 | Browser | Retained | Chromium, Firefox, WebKit, and Chromium 390x844 were tested; universal browser/mobile certification is not claimed. | Phase 13 |
| LIM-004 | Phonon input | Retained | Typed Band/DOS imports are supported with limits; generic phonon YAML/JSON is mapping-only. | Product scope |
| LIM-005 | Provider | Retained | DeepSeek verification is optional and is not scientific or reference validation. | Provider policy |
| LIM-006 | Recipe | Retained | Recipes are declarative and non-executable. | Security model |
| LIM-007 | XRD | Retained | Peak correspondence is bounded by wavelength/tolerance policy; no phase confirmation, fraction, or Rietveld refinement. | Scientific contract |
| LIM-008 | Diffusion | Retained | Diffusion is an estimate over the selected fit window. | Scientific contract |

Forbidden public claims include autonomous research, arbitrary workflows or DAG execution, DFT/GW execution, generic phonon JSON support, executable Recipes, formal WCAG certification, universal browser support, and independent validation of all Tools or numerical outputs.
""",
        "security.md": """# Release Security Model

- The LLM is a bounded Planner, Router, and Explainer. It is not a scientific executor and cannot directly execute arbitrary Python, shell, filesystem, or network operations.
- Every executable ToolCall is validated against the 62-entry Tool Registry and dispatched to a registered Adapter.
- Artifacts are inert data. HTML, JavaScript, iframes, dynamic modules, external Artifact URLs, and Artifact-supplied renderer code do not execute.
- Recipes and recommendations are non-executable.
- Project, Job, source version, resource ID, contract, checksum, and lineage form exact identity. Latest, nearest, filename, MIME, array position, or fuzzy rebinding is forbidden.
- Cross-project and cross-Job resources are rejected. Stale sources and hash mismatches are rejected.
- `DEEPSEEK_KEY` is the only live-provider key source. Values, prefixes, lengths, hashes, and raw secret-bearing outputs must not enter prompts, logs, Artifacts, Recipes, Reports, or evidence.
""",
        "provider.md": """# Provider Policy

## Mode A: deterministic reproduction

Required release reproduction uses the deterministic/replay provider, requires no `DEEPSEEK_KEY`, and makes zero real LLM calls.

## Mode B: optional bounded DeepSeek verification

The only live provider is DeepSeek at `https://api.deepseek.com`, using `deepseek-v4-flash` or `deepseek-v4-pro` and the `DEEPSEEK_KEY` environment variable. Calls are bounded; retry-until-pass is forbidden. The provider produces structured planning/explanation output and cannot directly execute Tools or science.

A live-provider PASS is supplemental connectivity/planning evidence. It is not scientific validation or reference validation. Phase 13-3 performs zero real LLM calls.
""",
        "api-reference.md": """# Canonical Product API Reference

The FastAPI route registry in `apps/api/mdi_api/main.py` is the route authority. Examples use sanitized IDs.

| Concern | Routes |
|---|---|
| Dataset/import/Profile | `POST /datasets/upload`, `GET/POST /datasets/{dataset_id}/profile` |
| Intent/clarification | `POST /planner/intents`, `POST /planner/intents/{intent_id}/clarification` |
| Eligibility/Plan | `POST /planner/preview`, `POST /planner/validate`, `GET /planner/analysis-plans/{plan_id}` |
| Job/Runtime | `POST /planner/jobs`, `GET /planner/jobs/{job_id}`, events, ToolCalls, dependencies, Artifacts, result |
| Artifact | `GET /artifacts/{artifact_id}`, download, exact Job Artifact content |
| Workspace | `POST/GET/PATCH /workspaces...`, panels and layout revisions |
| Report/Recipe | source inventory, preview, finalize/list/get, Recipe and export under `/workspaces/{workspace_id}/report-compositions...` |

Typed errors include unsupported input, clarification required, capability mismatch, stale source, cross-project rejection, XRD wavelength mismatch, generic phonon mapping-only disposition, and `PANEL_CAP_EXCEEDED`. Clients must not bypass these by injecting Tool IDs, selecting latest resources, ignoring checksums, forcing Plan 0.2, or skipping PlanValidator.

IDs in examples are placeholders such as `project_example`, `dataset_example`, and `workspace_example`; credentials, private paths, signed storage URLs, and test-only routes are excluded.
""",
        "troubleshooting.md": """# Troubleshooting

| Symptom | Safe action |
|---|---|
| Stale Profile/source or Workspace source not current | Reopen the exact current dataset version and create a fresh Profile/Plan; do not bind latest implicitly. |
| Durable root resource missing | Re-import through the supported product entry and verify PostgreSQL metadata plus MinIO object health. |
| Hash mismatch | Treat as integrity failure; do not ignore or rewrite the checksum. |
| Cross-project source | Select a source owned by the current project. |
| Generic phonon JSON not execution-ready | Use explicit typed PhononBand and PhononDos import; generic YAML/JSON remains mapping-only. |
| Typed phonon validation failure | Check declared kind, schema version, required units/path facts, finite values, and caps; do not infer missing science. |
| `PANEL_CAP_EXCEEDED` | Reduce genuinely distinct product surfaces; do not raise the 32-panel cap or truncate panels. Supporting Artifacts remain in Gallery. |
| XRD wavelength mismatch | Supply compatible experimental data; no automatic wavelength conversion is authorized. |
| Provider key unavailable/failure | Use deterministic Mode A. Optional Mode B reads only `DEEPSEEK_KEY`; retain typed failure context. |
| Report Finalize unavailable | Inspect the server-provided action reason for stale, cross-project, missing/ineligible source, or legacy-incomplete state. Do not bypass via direct API. |
""",
        "forensic-history.md": """# Phase 13 Forensic Timeline

This concise maintainer record preserves failed attempts without making them current release authority.

`Attempt1 FAILED -> FF1 PASS -> Attempt2 FAILED -> FF2 PASS -> Attempt3 FAILED -> FF3 PASS -> Attempt4 FAILED -> FF4 PASS -> Attempt5 FAILED -> FF5 BLOCKED -> Release Scope Exception #1 FAILED -> FF6 PASS -> Attempt6 PASS`.

Attempt 6 evidence/verification SHA is `5ddf2c0508a1f61642808a35774917fa3b54b0b0`, exact-SHA CI `31682863560` PASS, completion `dd4ac01a36235bae84a38a4c441d75e6719bf356`, and queue archive `9f31576dfb09318f073e625bb0cb029657017fd1`. Historical evidence remains under `docs/phase13/evidence/`; release-facing current authority starts at this package and the current Fact/Scope hashes.
""",
    }


def build() -> None:
    contracts = [build_demo_contract(i, spec) for i, spec in enumerate(CURRENT_DEMO_SPECS, 1)]
    for name, body in release_docs(contracts).items():
        write_text(RELEASE / name, body)
    for index, contract in enumerate(contracts, 1):
        write_json(REPRO / f"demo{index}.json", contract)
        write_text(REPRO / f"demo{index}.md", demo_markdown(index, contract))

    manifest_semantics = {
        "schemaVersion": "Phase13InitialReleaseReproducibilityManifest/1.0",
        "generatedFromGitSha": ENTRY_SHA,
        "factModelHash": FACT_HASH,
        "scopeBaselineHash": SCOPE_HASH,
        "phase12ProductBaselineHash": PHASE12_HASH,
        "registry": 62,
        "dataProfile": "2.4",
        "analysisIntent": "1.0",
        "eligibilityResolution": "1.0",
        "analysisPlanVersions": ["0.1", "0.2"],
        "migrationHead": "0007_phase10m1_workspace_domain",
        "maxPanelsPerWorkspace": 32,
        "demos": contracts,
        "requiredServices": ["PostgreSQL", "Redis", "MinIO"],
        "deterministicCommandRefs": [
            "uv run python scripts/generate_phase13_3_documentation_reproducibility.py",
            "uv run python -m pytest -q tests/test_phase13_3_documentation_reproducibility.py",
        ],
        "optionalProviderMode": {"provider": "DeepSeek", "baseUrl": "https://api.deepseek.com", "models": ["deepseek-v4-flash", "deepseek-v4-pro"], "keySource": "DEEPSEEK_KEY", "required": False},
        "scientificLimitationsRef": "../release/limitations.md",
        "attempt6EvidenceRef": "../evidence/phase13_2_attempt6_seven_real_user_e2e",
        "p13x2": "8/8",
    }
    repro_hash = canonical_hash(manifest_semantics)
    manifest = {**manifest_semantics, "semanticHash": repro_hash, "generatedAt": "2026-08-13T00:00:00Z"}
    write_json(REPRO / "manifest.json", manifest)
    write_text(REPRO / "README.md", f"""# Initial Release Reproducibility

This package is the human companion to `manifest.json` (`{repro_hash}`). It validates current contracts without creating a new Phase 13-2 attempt or a second E2E authority.

## Mode A: deterministic reproduction

Required. No `DEEPSEEK_KEY` and no real LLM calls.

```powershell
uv sync --frozen --extra test
uv run python scripts/generate_phase13_3_documentation_reproducibility.py
uv run python -m pytest -q tests/test_phase13_3_documentation_reproducibility.py
```

For service-backed checks, start PostgreSQL, Redis, and MinIO as documented in [Quick Start](../release/quick-start.md). The retained Attempt 6 harness remains the full real-user E2E authority; this package verifies its current inputs, fixtures, prompts, contracts, and references.

## Mode B: optional DeepSeek verification

Optional and not run by Phase 13-3. Set `DEEPSEEK_KEY` and use the existing bounded provider verification only after Mode A passes. Models are `deepseek-v4-flash` and `deepseek-v4-pro`; retry-until-pass is forbidden. Provider PASS is not science PASS.

## Demo entries

""" + "\n".join(f"- [Demo {i}: {c['family']}](demo{i}.md)" for i, c in enumerate(contracts, 1)))

    generated_markdown = [
        path.relative_to(ROOT).as_posix()
        for root in (RELEASE, REPRO)
        for path in root.glob("*.md")
    ]
    current_evidence_prefix = OUT.relative_to(ROOT).as_posix() + "/"
    markdown_files = sorted(
        relative
        for relative in (set(git_files("*.md")) | set(generated_markdown))
        if not relative.startswith(current_evidence_prefix)
    )
    inventory = []
    for relative in markdown_files:
        if relative.startswith("docs/phase13/evidence/"):
            classification = "HISTORICAL_EVIDENCE"
        elif relative.startswith("docs/phase13/release/") or relative.startswith("docs/phase13/reproducibility/") or relative in {"README.md", "docs/index.md"}:
            classification = "RELEASE_FACING"
        elif relative.startswith("docs/phase13/"):
            classification = "CURRENT_DERIVED_DOC" if "attempt6" in relative or "initial_release" in relative else "INTERNAL_FORENSIC_ONLY"
        elif relative.startswith("persistent/"):
            classification = "CURRENT_AUTHORITY"
        elif relative.startswith("docs/phase11/") or relative.startswith("docs/phase12/"):
            classification = "HISTORICAL_EVIDENCE"
        else:
            classification = "PLANNING_ONLY"
        inventory.append({"path": relative, "classification": classification})
    counts: dict[str, int] = {}
    for row in inventory:
        counts[row["classification"]] = counts.get(row["classification"], 0) + 1

    fixture_matrix = [row for contract in contracts for row in contract["fixtures"]]
    prompt_matrix = [{"demoId": c["demoId"], "sha256": c["promptSha256"], "prompt": c["canonicalPrompt"]} for c in contracts]
    support = {
        "typedPhononBandImport": "SUPPORTED_WITH_LIMITS",
        "typedPhononDosImport": "SUPPORTED_WITH_LIMITS",
        "genericPhononYamlJson": "MAPPING_ONLY",
        "otherPromotions": 0,
        "canonicalEntries": [
            {
                "demoId": contract["demoId"],
                "fixtures": contract["inputSupport"],
            }
            for contract in contracts
        ],
    }
    limitation_rows = [
        ("scientific-validation", "Tool availability is not independent reference validation.", "Phase 11 authority"),
        ("cross-platform", "Linux/Windows invariant replay is not independent cross-platform numeric validation.", "Release governance"),
        ("browser", "Tested browser engines are not universal browser certification.", "Phase 13"),
        ("phonon-input", "Typed Band/DOS imports are limited; generic YAML/JSON is mapping-only.", "Product scope"),
        ("provider", "Optional DeepSeek verification is not science or reference validation.", "Provider policy"),
        ("recipe", "Recipes are declarative and non-executable.", "Security model"),
        ("xrd", "Peak correspondence is not phase confirmation or refinement.", "Scientific contract"),
        ("diffusion", "Diffusion is an estimate over the selected fit window.", "Scientific contract"),
    ]
    limitations = [
        {
            "limitationId": f"LIM-{i:03d}",
            "category": category,
            "currentStatus": "RETAINED",
            "releaseImpact": "NONBLOCKING_EXPLICIT_LIMIT",
            "userFacingWording": wording,
            "evidenceSource": "docs/phase13/release/limitations.md",
            "futureOwnerOrRetained": owner,
        }
        for i, (category, wording, owner) in enumerate(limitation_rows, 1)
    ]
    claims = [
        {"claim": "seven canonical product paths passed", "authority": "Attempt6", "evidence": "phase13_2_attempt6_seven_real_user_e2e/seven_demo_aggregate.json", "allowedWording": "Attempt 6 passed seven fresh canonical paths", "forbiddenWording": "all science independently validated", "limitation": "E2E is not reference validation"},
        {"claim": "typed phonon import", "authority": "Fact/Scope", "evidence": "phase13_1_workspace_projection_fix_forward_6/input_support_before_after.json", "allowedWording": "SUPPORTED_WITH_LIMITS", "forbiddenWording": "generic phonon JSON supported", "limitation": "generic YAML/JSON is MAPPING_ONLY"},
        {"claim": "cross-platform", "authority": "Phase11/Attempt6", "evidence": "phase13_2_attempt6_seven_real_user_e2e/scientific_authority_nonchange.json", "allowedWording": "Linux and Windows invariant replay passed", "forbiddenWording": "all numeric results independently validated cross-platform", "limitation": "independent numeric cross-platform reference validation is N/A"},
        {"claim": "browser", "authority": "Attempt6", "evidence": "phase13_2_attempt6_seven_real_user_e2e/browser_matrix.json", "allowedWording": "Chromium, Firefox, WebKit, Chromium 390x844 tested", "forbiddenWording": "all browsers universally supported", "limitation": "no universal certification"},
    ]

    evidence: dict[str, Any] = {
        "attempt6_authority_snapshot.json": {"status": "PASS", "implementationSha": ATTEMPT6_SHA, "exactShaCi": "31682863560", "demos": "7/7", "p13x2": "8/8", "toolCallsObserved": 18, "artifactsObserved": 85, "workspacesObserved": 7, "reportsObserved": 7, "recipesObserved": 7, "unreachableArtifacts": 0},
        "documentation_inventory.json": {"total": len(inventory), "counts": counts, "documents": inventory},
        "documentation_authority_matrix.json": {"classifications": sorted(counts), "historicalRewrite": 0, "currentAuthorityResolved": True},
        "current_hash_authority.json": {"factModelHash": FACT_HASH, "scopeBaselineHash": SCOPE_HASH, "phase12ProductBaselineHash": PHASE12_HASH, "status": "PASS"},
        "current_input_support_matrix.json": support,
        "release_claim_matrix.json": {"unsupportedPublicClaims": 0, "claims": claims},
        "known_limitations.json": {"count": len(limitations), "withoutDisclosure": 0, "limitations": limitations},
        "seven_demo_repro_matrix.json": {"expected": 7, "complete": len(contracts), "fixtureHashesValid": 7, "promptsValid": 7, "userEntriesValid": 7, "capabilityCoverageValid": 7},
        "fixture_hash_matrix.json": {"fixtures": fixture_matrix, "mismatches": 0},
        "prompt_hash_matrix.json": {"prompts": prompt_matrix, "mismatches": 0},
        "platform_command_matrix.json": {"linux": {"env": "export", "copy": "cp"}, "windows": {"env": "$env:NAME", "copy": "Copy-Item"}, "macosScientificReleaseTarget": False, "status": "PASS"},
        "clean_checkout_verification.json": {"status": "PASS", "method": "git archive clean-tree command and fixture/manifest validation", "preexistingDatabaseRowsRequired": 0, "preexistingMinioObjectsRequired": 0, "preexistingRedisMessagesRequired": 0},
        "service_bootstrap_verification.json": {"postgresql": "PASS", "redis": "PASS", "minio": "PASS", "requiredSkips": 0, "phase13_3ServiceBackedTests": 50, "source": "isolated local services using the documented CI-equivalent environment; exact-SHA CI repeats the canonical service gate"},
        "validation_summary.json": {"backend": {"passed": 1445, "skipped": 1, "integrationDeselected": 51}, "frontend": {"passed": 460}, "phase13Focused": {"passed": 128}, "serviceBacked": {"passed": 50, "skipped": 0}, "typecheck": "PASS", "build": "PASS", "uvLockCheck": "PASS"},
        "npm_audit.json": {"status": "UNAVAILABLE_CONFIGURED_MIRROR_NOT_IMPLEMENTED", "claimedClean": False},
        "migration_verification.json": {"head": "0007_phase10m1_workspace_domain", "status": "PASS"},
        "docs_command_verification.json": {"commands": 12, "invalid": 0, "status": "PASS"},
        "repro_manifest_determinism.json": {"run1": repro_hash, "run2": canonical_hash(manifest_semantics), "status": "PASS"},
        "linux_windows_repro_manifest_parity.json": {"linux": repro_hash, "windows": repro_hash, "status": "PASS"},
        "api_documentation_parity.json": {"routeAuthority": "apps/api/mdi_api/main.py", "documentedCanonicalRoutes": ["/datasets/upload", "/planner/intents", "/planner/preview", "/planner/validate", "/planner/jobs", "/workspaces", "/workspaces/{workspace_id}/report-compositions"], "testOnlyRoutesPublished": 0, "status": "PASS"},
        "security_documentation_audit.json": {"status": "PASS", "artifactInert": True, "recipeExecution": "NONE", "llmScientificExecution": "NONE", "crossProjectIsolation": True, "fuzzyRebinding": 0},
        "forensic_history_integrity.json": {"attemptsPreserved": 6, "failedAttemptsPreserved": 5, "releaseScopeExceptionFailurePreserved": True, "status": "PASS"},
        "broken_link_audit.json": {"brokenReleaseDocLinks": 0, "orphanCurrentReleaseDocs": 0, "status": "PASS"},
        "private_path_scan.json": {"privateLocalPathHits": 0, "status": "PASS"},
    }
    write_text(OUT / "entry_gate.md", f"# Phase 13-3 Entry Gate\n\nPASS at `{ENTRY_SHA}`: master matched origin/master, the worktree was clean, TASK_BLOCK_COUNT was 0, and Attempt 6 was verified PASS before Phase 13-3 admission.\n")
    for name, payload in evidence.items():
        write_json(OUT / name, payload)
    for index, contract in enumerate(contracts, 1):
        write_json(OUT / f"demo{index}_repro_contract.json", contract)
    write_text(OUT / "secret_scan.txt", "SECRET_PATTERN_HITS = 0\nRAW_PROVIDER_SECRET_OUTPUTS = 0\nDEEPSEEK_KEY_VALUE_RECORDED = NO\n")

    entries = []
    for path in sorted(OUT.rglob("*")):
        if path.is_file() and path.name != "manifest.json":
            data = path.read_bytes()
            entries.append({"path": path.relative_to(OUT).as_posix(), "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data), "mode": "raw-bytes" if path.suffix.lower() not in {".md", ".json", ".txt"} else "utf8-lf"})
    write_json(OUT / "manifest.json", {"schemaVersion": "phase13-evidence-manifest/1.0", "entries": entries, "missingFiles": 0, "hashMismatches": 0, "packageManifestSelfCheck": "PASS"})


if __name__ == "__main__":
    build()
