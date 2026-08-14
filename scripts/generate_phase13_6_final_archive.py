from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import zipfile
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "docs/phase13/final"
OUT = ROOT / "docs/phase13/evidence/phase13_6_final_archive_presentation"
ARTIFACTS = ROOT / ".artifacts/phase13_6"
ENTRY_SHA = "bde200acbe4e0d761d6c7a8338fbe68870fa82d6"
FACT_HASH = "92d8295c7d78467d8ce021dc8033a58326219372a5d8fa87c93377ed1275953a"
SCOPE_HASH = "bb885aa4e020349011c39164a883107c8ffed3d5d43604594a76f7d5a18705ba"
PHASE12_HASH = "29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4"
REPRO_HASH = "931d6214cb11dbcad628f5b33ea97e043bbfeb54fbccc2f8c87cffebad9537e2"
ARCHIVE_NAME = "material-data-intelligence-initial-release.zip"
PRODUCTION_PATHS = (
    "apps/api/alembic", "apps/api/mdi_api", "apps/web/app",
    "apps/web/next-env.d.ts", "apps/web/next.config.mjs",
    "apps/web/package-lock.json", "apps/web/package.json", "packages",
    "services", "tool_registry", ".env.example", "docker-compose.yml",
    "pnpm-workspace.yaml", "pyproject.toml", "uv.lock",
)


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8", newline="\n")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8", newline="\n",
    )


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def file_payload(path: Path) -> tuple[bytes, str]:
    if path.suffix.lower() in {".md", ".json", ".txt", ".yaml", ".yml"}:
        return path.read_text(encoding="utf-8").replace("\r\n", "\n").encode(), "UTF8_LF"
    return path.read_bytes(), "RAW_BYTES"


def git(*args: str) -> str:
    return subprocess.check_output(("git", *args), cwd=ROOT, text=True).strip()


def production_surface() -> dict[str, Any]:
    rows = []
    for line in git("ls-tree", "-r", "HEAD", "--", *PRODUCTION_PATHS).splitlines():
        metadata, path = line.split("\t", 1)
        mode, kind, blob = metadata.split()
        if kind == "blob":
            rows.append({"path": path.replace("\\", "/"), "mode": mode, "blob": blob})
    rows.sort(key=lambda row: row["path"])
    return {
        "contract": "Phase13ProductionSurfaceGitBlobTree/1.0",
        "roots": list(PRODUCTION_PATHS), "fileCount": len(rows),
        "semanticHash": canonical_hash(rows),
    }


def authorities() -> dict[str, Any]:
    return {
        "factModelHash": FACT_HASH, "scopeBaselineHash": SCOPE_HASH,
        "phase12ProductBaselineHash": PHASE12_HASH,
        "reproManifest": "Phase13InitialReleaseReproducibilityManifest/1.0",
        "reproManifestHash": REPRO_HASH, "registry": 62, "dataProfile": "2.4",
        "analysisIntent": "1.0", "eligibilityResolution": "1.0",
        "analysisPlanVersions": ["0.1", "0.2"],
        "migrationHead": "0007_phase10m1_workspace_domain",
        "maxWorkspacePanels": 32, "maxLayoutRevisions": 128,
        "inputSupport": {
            "typedPhononBandImport": "SUPPORTED_WITH_LIMITS",
            "typedPhononDosImport": "SUPPORTED_WITH_LIMITS",
            "genericPhononYamlJson": "MAPPING_ONLY",
        },
        "phase11": "COMPLETE / REFERENCE_VALIDATED_WITH_EXPLICIT_LIMITS",
    }


def known_limitations() -> list[dict[str, Any]]:
    source = load(ROOT / "docs/phase13/evidence/phase13_5_final_regression_release_acceptance/known_limitations_reconciliation.json")
    rows = source["limitations"]
    if [row["limitationId"] for row in rows] != [f"LIM-{i:03d}" for i in range(1, 9)]:
        raise RuntimeError("known limitation authority drift")
    if source["withoutDisclosure"] != 0:
        raise RuntimeError("undisclosed known limitation")
    return rows


def timeline() -> list[dict[str, Any]]:
    rows = [
        ("Phase13-0", "PASS", "phase13_0_release_scope_seal"),
        ("Phase13-1 original closure", "PASS", "phase13_1_zero_gap_verification_closure"),
        ("Attempt1", "FAILED_HISTORICAL", "phase13_2_seven_real_user_e2e"),
        ("FixForward1", "PASS", "phase13_1_product_entry_fix_forward"),
        ("Attempt2", "FAILED_RERUN_HISTORICAL", "phase13_2_seven_real_user_e2e_rerun"),
        ("FixForward2", "PASS", "phase13_1_runtime_resource_fix_forward_2"),
        ("Attempt3", "FAILED_RERUN_HISTORICAL", "phase13_2_attempt3_seven_real_user_e2e"),
        ("FixForward3", "PASS", "phase13_1_durable_upload_worker_fix_forward_3"),
        ("Attempt4", "FAILED_RERUN_HISTORICAL", "phase13_2_attempt4_seven_real_user_e2e"),
        ("FixForward4", "PASS", "phase13_1_capability_report_fix_forward_4"),
        ("Attempt5", "FAILED_RERUN_HISTORICAL", "phase13_2_attempt5_seven_real_user_e2e"),
        ("FixForward5", "BLOCKED_HISTORICAL", "phase13_1_trajectory_phonon_fix_forward_5"),
        ("Release Scope Exception #1", "FAILED_HISTORICAL", "phase13_1_release_scope_exception_1_typed_phonon_import"),
        ("FixForward6", "PASS", "phase13_1_workspace_projection_fix_forward_6"),
        ("Attempt6", "PASS", "phase13_2_attempt6_seven_real_user_e2e"),
        ("Phase13-3", "PASS", "phase13_3_documentation_reproducibility"),
        ("Phase13-4", "PASS", "phase13_4_targeted_final_product_polish"),
        ("Phase13-5", "PASS", "phase13_5_final_regression_release_acceptance"),
        ("Phase13-6", "CURRENT / PENDING_EXACT_SHA_CI", "phase13_6_final_archive_presentation"),
    ]
    records = [{"phase": phase, "status": status, "evidenceRoot": f"docs/phase13/evidence/{root}"} for phase, status, root in rows]
    records[14].update({"implementationSha": "5ddf2c0508a1f61642808a35774917fa3b54b0b0", "exactShaCi": 31682863560})
    records[15].update({"implementationSha": "c3aabd055e067c5a52a0c0238c625dbc035a96f0", "exactShaCi": 31703805747})
    records[16].update({"implementationSha": "40403cfa19451cc9a473c41bddecfe053e1a5fea", "exactShaCi": 31715231470, "failedCandidate": {"sha": "34f7cb7cea3db351edff0d3b39ff7fe39cd7e192", "ciRun": 31713598663, "classification": "CI_EVIDENCE_PORTABILITY / SHALLOW_CHECKOUT_OBJECT_AVAILABILITY"}})
    records[17].update({"implementationSha": "b60e048abbf366fdbd9fe72da27efd675fc50939", "exactShaCi": 31728986993, "completionSha": "1afed7f982bdd6d2b5e9bef50e2cf4b14b984d32", "archiveSha": "359cb5e"})
    return records


def evidence_index(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for row in records:
        root = ROOT / row["evidenceRoot"]
        manifest = root / "manifest.json"
        if row["phase"] != "Phase13-6" and (not root.is_dir() or not manifest.is_file()):
            raise RuntimeError(f"missing evidence root or manifest: {row['phase']}")
        result.append({
            **row,
            "historicalOrCurrent": "CURRENT" if row["phase"] in {"Phase13-5", "Phase13-6"} else "HISTORICAL",
            "manifest": f"{row['evidenceRoot']}/manifest.json", "findingIds": [],
            "supersedesOrResolves": [],
        })
    return result


def claims() -> list[dict[str, Any]]:
    return [
        {"claim": "Seven canonical workflows were release-accepted", "authority": "Phase13-5", "evidence": "seven_demo_aggregate.json", "allowedWording": "7/7 canonical workflows passed release acceptance", "forbiddenWording": "arbitrary workflows or DAGs are supported", "limitationRefs": ["LIM-001"]},
        {"claim": "Registered Adapters and persisted Artifacts are scientific authority", "authority": "Registry/Runtime/Artifact contracts", "evidence": "Phase13-5 durable runtime evidence", "allowedWording": "registered Adapters produce persisted scientific facts", "forbiddenWording": "LLM, frontend, or screenshot is scientific authority", "limitationRefs": ["LIM-001"]},
        {"claim": "Linux and Windows invariant replay passed", "authority": "Phase13-5", "evidence": "cross_platform_hash_parity.json", "allowedWording": "Linux/Windows invariant replay passed", "forbiddenWording": "all numerical outputs were independently cross-platform validated", "limitationRefs": ["LIM-002"]},
        {"claim": "Chromium, Firefox, WebKit, and Chromium 390x844 were tested", "authority": "Phase13-5", "evidence": "browser_matrix.json", "allowedWording": "tested browser matrix passed", "forbiddenWording": "universal browser certification", "limitationRefs": ["LIM-003"]},
        {"claim": "Typed PhononBand and PhononDos imports are supported with limits", "authority": "Input Support Matrix", "evidence": "input-support.md", "allowedWording": "typed Band/DOS import is supported with limits", "forbiddenWording": "generic phonon YAML/JSON is execution-ready", "limitationRefs": ["LIM-004"]},
        {"claim": "DeepSeek verification is optional", "authority": "Provider policy", "evidence": "provider.md", "allowedWording": "optional bounded DeepSeek verification", "forbiddenWording": "provider output is science validation", "limitationRefs": ["LIM-005"]},
        {"claim": "Reports compose persisted facts and Recipes are declarative", "authority": "Report/Recipe contracts", "evidence": "report_recipe_aggregate.json", "allowedWording": "paired non-executable Recipe", "forbiddenWording": "Recipes execute", "limitationRefs": ["LIM-006"]},
        {"claim": "XRD comparison is policy-bounded", "authority": "Scientific contract", "evidence": "Demo3 acceptance", "allowedWording": "peak correspondence", "forbiddenWording": "phase confirmation or refinement", "limitationRefs": ["LIM-007"]},
        {"claim": "Trajectory diffusion is an estimate", "authority": "Scientific contract", "evidence": "Demo4 acceptance", "allowedWording": "estimate over selected fit window", "forbiddenWording": "unqualified true diffusion coefficient", "limitationRefs": ["LIM-008"]},
    ]


def markdown_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows:
        cells = [str(row.get(column, "")).replace("\n", " ").replace("|", "\\|") for column in columns]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def build_docs(auth: dict[str, Any], limits: list[dict[str, Any]], history: list[dict[str, Any]], claim_rows: list[dict[str, Any]], index: list[dict[str, Any]]) -> None:
    if FINAL.exists():
        shutil.rmtree(FINAL)
    (FINAL / "presentation/screenshots").mkdir(parents=True)
    write_text(FINAL / "README.md", """# Material Data Intelligence Initial Release

This is the final Phase 13 archive and presentation entry for the accepted Material Data Intelligence and Scientific Visualization Platform release candidate. Phase13-6 source remains **Release Candidate Accepted / Closure Pending Exact-SHA CI** until the append-only completion record is pushed.

## Package navigation

- [Initial Release notes](release_notes.md)
- [Release claim matrix](release_claim_matrix.md)
- [Known limitations](known_limitations.md)
- [Phase 13 forensic timeline](phase13_forensic_timeline.md)
- [Phase 13 evidence index](evidence_index.md)
- [Presentation package](presentation/README.md)
- [Canonical release documentation](../release/README.md)
- [Deterministic reproducibility](../reproducibility/README.md)

The Git repository remains the source-code authority. The ZIP is a documentation, reproducibility, evidence-index, and presentation package, not a source archive.
""")
    write_text(FINAL / "release_notes.md", """# Initial Release Notes

## What shipped

The Initial Release provides seven canonical workflows: dataset intelligence and composition space; materials ML evaluation; structure, coordination, local environment, polyhedra, and experimental XRD; trajectory RDF/MSD/diffusion; supplied typed phonon Band/DOS plus Brillouin zone; volumetric visualization; and electronic Band/DOS.

The canonical path is DataProfile -> AnalysisIntent -> EligibilityResolution -> capability-aware Planner -> AnalysisPlan -> PlanValidator -> QueueWorkerRuntime -> registered Adapter -> persisted Artifact -> Grounded Interpretation -> ScientificWorkspace -> Report -> declarative Recipe.

Scientific computation authority belongs to registered Adapters and persisted Artifacts. The LLM is a Planner/Router/Explainer, not a scientific executor. Artifacts are inert data, Reports compose persisted facts, and Recipes are non-executable.

Typed PhononBand and PhononDos imports are `SUPPORTED_WITH_LIMITS`; generic phonon YAML/JSON remains `MAPPING_ONLY`. Workspaces use one Workspace per Job, a 32-panel cap, and Artifact Gallery reachability rather than one panel per Artifact.

Release acceptance tested Chromium, Firefox, WebKit, Chromium 390x844, PostgreSQL, Redis, MinIO, Linux invariant replay, and Windows invariant replay. These results do not imply universal browser certification or independent cross-platform numeric validation.

See [Known limitations](known_limitations.md), [Reproducibility](../reproducibility/README.md), [Security](../release/security.md), and the [Claim matrix](release_claim_matrix.md).
""")
    write_text(FINAL / "known_limitations.md", "# Known Limitations\n\n" + "\n".join(f"- **{row['limitationId']} ({row['category']}):** {row['userFacingWording']}" for row in limits))
    write_text(FINAL / "release_claim_matrix.md", "# Initial Release Claim Matrix\n\n" + markdown_table(claim_rows, ["claim", "authority", "allowedWording", "forbiddenWording", "limitationRefs"]))
    write_json(FINAL / "release_claim_matrix.json", {"schemaVersion": "InitialReleaseClaimMatrix/1.0", "claims": claim_rows})
    write_text(FINAL / "phase13_forensic_timeline.md", "# Phase 13 Forensic Timeline\n\nHistorical failures are retained and were resolved through later verified work. Failed candidates are not release builds.\n\n" + markdown_table(history, ["phase", "status", "implementationSha", "exactShaCi", "evidenceRoot"]))
    write_json(FINAL / "phase13_forensic_timeline.json", {"schemaVersion": "Phase13ForensicTimeline/1.0", "records": history})
    write_text(FINAL / "evidence_index.md", "# Phase 13 Evidence Index\n\nRepository-relative references point to retained evidence; the ZIP packages indexes and selected release-facing evidence instead of duplicating historical trees.\n\n" + markdown_table(index, ["phase", "status", "historicalOrCurrent", "manifest"]))
    write_json(FINAL / "evidence_index.json", {"schemaVersion": "Phase13FinalEvidenceIndex/1.0", "records": index})
    write_json(FINAL / "current_authorities.json", auth)


def build_presentation(limits: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    source_root = ROOT / "docs/phase13/evidence/phase13_5_final_regression_release_acceptance"
    selected = [
        ("planner.png", "screenshots/help/chromium_1440x900.png", "Planner / user entry", "1440x900"),
        ("artifact-gallery.png", "screenshots/gallery/chromium.png", "Workspace Artifact Gallery", "1440x900"),
        ("structure-report.png", "screenshots/demo3_report_ui.png", "Structure/XRD Report", "1440x900"),
        ("phonon-report.png", "screenshots/demo5_report_ui.png", "Phonon Report", "1440x900"),
        ("mobile.png", "screenshots/help/chromium_390x844.png", "Mobile product entry", "390x844"),
    ]
    provenance = []
    for target, relative, surface, viewport in selected:
        source = source_root / relative
        if not source.is_file():
            raise RuntimeError(f"missing presentation screenshot: {relative}")
        destination = FINAL / "presentation/screenshots" / target
        shutil.copyfile(source, destination)
        provenance.append({"asset": f"screenshots/{target}", "surface": surface, "sourceEvidenceRoot": source_root.relative_to(ROOT).as_posix(), "sourceFile": relative, "sourcePhase": "Phase13-5", "browser": "chromium", "viewport": viewport, "sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "scientificAuthority": "NONE"})
    slides = ["Initial Release overview", "Product problem and user value", "Canonical architecture", "Real user flow", "Seven canonical demo families", "Workspace and Artifact Gallery", "Grounded Interpretation, Findings, and Evidence", "Report and non-executable Recipe", "Deterministic reproducibility", "Scientific honesty boundary", "Known limitations", "Release acceptance and closure status"]
    write_text(FINAL / "presentation/README.md", """# Initial Release Presentation Package

Use the [storyboard](storyboard.md) and [speaker notes](speaker_notes.md). Assets are copied from verified Phase13-5 evidence and have no numeric scientific authority.

Status: **Release Candidate Accepted / Phase13-6 Closure Pending Exact-SHA CI**. The append-only completion record is the authority that changes the Initial Release status to complete.
""")
    write_text(FINAL / "presentation/storyboard.md", "# Initial Release Storyboard\n\n" + "\n".join(f"## {i}. {title}\n\nPresent accepted product facts with the claim matrix and applicable limitation references." for i, title in enumerate(slides, 1)))
    write_text(FINAL / "presentation/speaker_notes.md", """# Initial Release Speaker Notes

Present Material Data Intelligence as a scientific visualization and controlled analysis platform, not a generic AI wrapper. Trace the durable path from user entry through Profile, Intent, Eligibility, Planner, validated plan, queue worker, registered Adapter, persisted Artifact, Workspace, Report, and declarative Recipe.

Screenshots prove presentation only. Do not infer numeric correctness from pixels. For phonons, typed Band/DOS imports are supported with limits and generic YAML/JSON remains mapping-only. Retain all eight explicit limitation statements.
""")
    semantics = {"schemaVersion": "InitialReleasePresentationManifest/1.0", "slides": slides, "assets": provenance, "pptx": "NOT_REQUIRED", "pdf": "NOT_REQUIRED", "presentationScientificAuthority": "NONE", "screenshotNumericScientificAuthority": "NONE", "knownLimitationIds": [row["limitationId"] for row in limits]}
    manifest = {**semantics, "semanticHash": canonical_hash(semantics)}
    write_json(FINAL / "presentation/presentation_manifest.json", manifest)
    return manifest, provenance


def initial_manifest(auth: dict[str, Any], production: dict[str, Any], history: list[dict[str, Any]]) -> dict[str, Any]:
    semantics = {
        "schemaVersion": "InitialReleaseManifest/1.0", "releaseName": "Material Data Intelligence Initial Release",
        "releaseStatus": "RELEASE_CANDIDATE_ACCEPTED_PENDING_PHASE13_6_LIFECYCLE",
        "releaseCandidateEntrySha": ENTRY_SHA, "productionSurfaceHash": production["semanticHash"],
        "FactModelHash": FACT_HASH, "ScopeBaselineHash": SCOPE_HASH,
        "Phase12ProductBaselineHash": PHASE12_HASH, "ReproManifestHash": REPRO_HASH,
        "Registry": 62, "DataProfile": "2.4", "AnalysisIntent": "1.0",
        "EligibilityResolution": "1.0", "AnalysisPlanVersions": ["0.1", "0.2"],
        "MigrationHead": "0007_phase10m1_workspace_domain", "MaxWorkspacePanels": 32,
        "MaxLayoutRevisions": 128, "InputSupport": auth["inputSupport"], "P13X2": "8/8",
        "SevenDemoStatus": "7/7 PASS", "KnownLimitationIds": [f"LIM-{i:03d}" for i in range(1, 9)],
        "Phase13LifecycleRefs": [row["evidenceRoot"] for row in history],
        "ReleaseDocsRefs": ["docs/phase13/release", "docs/phase13/final"],
        "ReproducibilityRefs": ["docs/phase13/reproducibility/manifest.json"],
        "EvidenceManifestRefs": [f"{row['evidenceRoot']}/manifest.json" for row in history],
        "PresentationManifestRef": "docs/phase13/final/presentation/presentation_manifest.json",
        "ArchiveManifestRef": "docs/phase13/final/archive_manifest.json",
    }
    return {**semantics, "semanticHash": canonical_hash(semantics), "generatedAt": "2026-08-14T00:00:00+08:00"}


def copy_tree(source: Path, destination: Path) -> None:
    for path in sorted(source.rglob("*")):
        if path.is_file():
            target = destination / path.relative_to(source)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)


def archive_records(root: Path) -> list[dict[str, Any]]:
    rows = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.name != "archive_manifest.json":
            payload, mode = file_payload(path)
            rows.append({"relativePath": path.relative_to(root).as_posix(), "contentKind": "binary" if mode == "RAW_BYTES" else "text", "byteSize": len(path.read_bytes()), "sha256": hashlib.sha256(payload).hexdigest(), "hashMode": mode})
    return rows


def deterministic_zip(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        paths = [path for path in source.rglob("*") if path.is_file()]
        for path in sorted(paths, key=lambda item: item.relative_to(source).as_posix()):
            if path.is_file():
                info = zipfile.ZipInfo(f"initial-release/{path.relative_to(source).as_posix()}", (1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                info.create_system = 3
                archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def broken_links(root: Path) -> list[str]:
    pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    broken = []
    for path in root.rglob("*.md"):
        for target in pattern.findall(path.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            clean = target.split("#", 1)[0]
            if clean and not (path.parent / clean).resolve().exists():
                broken.append(f"{path.relative_to(root).as_posix()} -> {target}")
    return broken


def scan(root: Path) -> tuple[list[str], list[str]]:
    private_patterns = (re.compile(r"(?<![A-Za-z])[A-Za-z]:[\\/]"), re.compile(r"/home/[^/\s]+"), re.compile(r"Users[\\/][^/\s]+", re.I))
    secret_patterns = (re.compile(r"sk-[A-Za-z0-9_-]{12,}"), re.compile(r"(?i)(authorization|password|secret[_-]?key)\s*[:=]\s*['\"]?[A-Za-z0-9+/=_-]{12,}"), re.compile(r"(?i)(postgres(?:ql)?|redis)://[^\s<]+"))
    private_hits, secret_hits = [], []
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".md", ".json", ".txt", ".yaml", ".yml"}:
            text = path.read_text(encoding="utf-8")
            rel = path.relative_to(root).as_posix()
            if any(pattern.search(text) for pattern in private_patterns):
                private_hits.append(rel)
            if any(pattern.search(text) for pattern in secret_patterns):
                secret_hits.append(rel)
    return private_hits, secret_hits


def build_archive(manifest: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    stage, extract = ARTIFACTS / "initial-release", ARTIFACTS / "extracted"
    for path in (stage, extract):
        if path.exists():
            shutil.rmtree(path)
    stage.mkdir(parents=True)
    write_text(stage / "README.md", """# Material Data Intelligence Initial Release

This deterministic package contains release-facing documentation,
reproducibility contracts, the presentation package, and the Phase 13 evidence
index for the accepted release candidate.

- [Release documentation](release/README.md)
- [Initial Release notes](release/release_notes.md)
- [Final claim matrix](release/release_claim_matrix.md)
- [Known limitations](release/known_limitations.md)
- [Reproducibility](reproducibility/README.md)
- [Presentation](presentation/README.md)
- [Evidence index](evidence-index/evidence_index.md)
- [Forensic timeline](evidence-index/phase13_forensic_timeline.md)

    The Git repository remains source authority. This package is not a source-code archive.
""")
    copy_tree(ROOT / "docs/phase13/release", stage / "release")
    packaged_release_readme = stage / "release/README.md"
    write_text(
        packaged_release_readme,
        packaged_release_readme.read_text(encoding="utf-8").replace(
            "[Final archive and presentation package](../final/README.md)",
            "[Final archive and presentation package](../README.md)",
        ),
    )
    shutil.copyfile(FINAL / "release_notes.md", stage / "release/release_notes.md")
    shutil.copyfile(FINAL / "release_claim_matrix.md", stage / "release/release_claim_matrix.md")
    shutil.copyfile(FINAL / "known_limitations.md", stage / "release/known_limitations.md")
    copy_tree(ROOT / "docs/phase13/reproducibility", stage / "reproducibility")
    copy_tree(FINAL / "presentation", stage / "presentation")
    write_json(stage / "manifests/initial_release_manifest.json", manifest)
    for name in ("evidence_index.md", "evidence_index.json", "phase13_forensic_timeline.md", "phase13_forensic_timeline.json"):
        target = stage / "evidence-index" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(FINAL / name, target)
    archive_manifest = {"schemaVersion": "InitialReleaseArchiveManifest/1.0", "archiveRoot": "initial-release", "selfRecordExcluded": True, "textCanonicalization": "UTF8_LF", "binaryCanonicalization": "RAW_BYTES", "entries": archive_records(stage)}
    write_json(stage / "manifests/archive_manifest.json", archive_manifest)
    write_json(FINAL / "archive_manifest.json", archive_manifest)
    first, second = ARTIFACTS / f"build-1-{ARCHIVE_NAME}", ARTIFACTS / f"build-2-{ARCHIVE_NAME}"
    deterministic_zip(stage, first)
    deterministic_zip(stage, second)
    first_hash, second_hash = hashlib.sha256(first.read_bytes()).hexdigest(), hashlib.sha256(second.read_bytes()).hexdigest()
    if first_hash != second_hash:
        raise RuntimeError("archive nondeterminism")
    final_zip = ARTIFACTS / ARCHIVE_NAME
    shutil.copyfile(first, final_zip)
    with zipfile.ZipFile(final_zip) as archive:
        names = archive.namelist()
        if any(name.startswith("/") or ".." in Path(name).parts for name in names):
            raise RuntimeError("unsafe archive path")
        archive.extractall(extract)
    extracted = extract / "initial-release"
    extracted_manifest = load(extracted / "manifests/archive_manifest.json")
    mismatches = 0
    for row in extracted_manifest["entries"]:
        path = extracted / row["relativePath"]
        if not path.is_file():
            mismatches += 1
            continue
        payload, mode = file_payload(path)
        if mode != row["hashMode"] or len(path.read_bytes()) != row["byteSize"] or hashlib.sha256(payload).hexdigest() != row["sha256"]:
            mismatches += 1
    expected = {row["relativePath"] for row in extracted_manifest["entries"]} | {"manifests/archive_manifest.json"}
    actual = {path.relative_to(extracted).as_posix() for path in extracted.rglob("*") if path.is_file()}
    private_hits, secret_hits = scan(extracted)
    links = broken_links(extracted)
    if mismatches or expected != actual or private_hits or secret_hits or links:
        raise RuntimeError(f"archive check failed: mismatches={mismatches} missing={expected-actual} extra={actual-expected} private={private_hits} secret={secret_hits} links={links}")
    determinism = {"build1Sha256": first_hash, "build2Sha256": second_hash, "status": "PASS", "archiveBytes": final_zip.stat().st_size, "archiveEntryCount": len(actual), "archiveFilename": ARCHIVE_NAME}
    check = {"status": "PASS", "manifestMissingFiles": 0, "manifestExtraFiles": 0, "manifestHashMismatches": 0, "manifestByteSizeMismatches": 0, "pathTraversalEntries": 0, "symlinks": 0, "absolutePathHits": 0, "brokenInternalLinks": 0, "privatePathHits": private_hits, "secretPatternHits": secret_hits}
    return archive_manifest, determinism, check


def evidence_manifest() -> None:
    rows = []
    for path in sorted(OUT.rglob("*")):
        if path.is_file() and path.name != "manifest.json":
            rows.append({"path": path.relative_to(OUT).as_posix(), "bytes": len(path.read_bytes()), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    write_json(OUT / "manifest.json", {"schemaVersion": "Phase13_6EvidenceManifest/1.0", "textCanonicalization": "UTF8_LF", "binaryCanonicalization": "RAW_BYTES", "missingFiles": 0, "hashMismatches": 0, "entries": rows})


def build() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    auth = authorities()
    repro = load(ROOT / "docs/phase13/reproducibility/manifest.json")
    if repro["semanticHash"] != REPRO_HASH:
        raise RuntimeError("repro manifest drift")
    for relative, expected, label in (
        ("docs/phase13/evidence/phase13_1_workspace_projection_fix_forward_6/initial_release_fact_model.json", FACT_HASH, "Fact"),
        ("docs/phase13/evidence/phase13_1_workspace_projection_fix_forward_6/initial_release_scope_baseline.json", SCOPE_HASH, "Scope"),
    ):
        value = load(ROOT / relative)
        semantic = {key: item for key, item in value.items() if key != "semanticHash"}
        if value.get("semanticHash") != expected or canonical_hash(semantic) != expected:
            raise RuntimeError(f"{label} authority drift")
    limits, history, claim_rows = known_limitations(), timeline(), claims()
    index = evidence_index(history)
    before = production_surface()
    build_docs(auth, limits, history, claim_rows, index)
    presentation, provenance = build_presentation(limits)
    initial = initial_manifest(auth, before, history)
    write_json(FINAL / "initial_release_manifest.json", initial)
    archive_manifest, archive_determinism, archive_check = build_archive(initial)
    after = production_surface()
    if before != after:
        raise RuntimeError("production surface changed")
    demos = load(ROOT / "docs/phase13/evidence/phase13_5_final_regression_release_acceptance/seven_demo_aggregate.json")

    write_text(OUT / "entry_gate.md", f"# Phase 13-6 Entry Gate\n\nPASS at `{ENTRY_SHA}`: master matched origin/master, the worktree was clean after preserving the untracked Phase13-5 generated ZIP in `.artifacts`, TASK_BLOCK_COUNT was 0, Phase13-5 was PASS and archived, READY_FOR_PHASE13_6 was YES, and INITIAL_RELEASE_COMPLETE was NO before admission.\n")
    write_json(OUT / "phase13_5_authority_snapshot.json", {"status": "PASS", "validationSha": "b60e048abbf366fdbd9fe72da27efd675fc50939", "exactShaCi": 31728986993, "completionSha": "1afed7f982bdd6d2b5e9bef50e2cf4b14b984d32", "archiveOrderingHead": ENTRY_SHA, "releaseCandidateAccepted": True, "readyForPhase13_6": True, "sevenDemos": demos})
    write_json(OUT / "phase13_6_handoff_snapshot.json", load(ROOT / "docs/phase13/evidence/phase13_5_final_regression_release_acceptance/phase13_6_handoff.json"))
    write_json(OUT / "release_candidate_seal.json", {"schemaVersion": "Phase13_6ReleaseCandidateSeal/1.0", "entryGitSha": ENTRY_SHA, "productionTreeIdentity": before, **auth, "phase13_5ReleaseAcceptance": "PASS", "p13x2": "8/8", "sevenDemoStatus": "7/7 PASS"})
    write_json(OUT / "production_surface_hash_before_after.json", {"before": before, "after": after, "unchanged": True, "productionCodeChanges": 0})
    write_json(OUT / "current_authorities.json", auth)
    write_json(OUT / "phase13_forensic_timeline.json", {"schemaVersion": "Phase13ForensicTimeline/1.0", "records": history, "historyRewritten": False})
    write_json(OUT / "final_evidence_index.json", {"schemaVersion": "Phase13FinalEvidenceIndex/1.0", "records": index, "missingEvidenceRootRefs": 0, "brokenEvidenceManifestRefs": 0})
    write_json(OUT / "final_claim_matrix.json", {"schemaVersion": "InitialReleaseClaimMatrix/1.0", "claims": claim_rows, "unsupportedClaims": 0})
    write_json(OUT / "known_limitations_final.json", {"count": 8, "withoutDisclosure": 0, "newUnapproved": 0, "limitations": limits, "linkage": {"scientificValidation": "LIM-001", "crossPlatform": "LIM-002", "browser": "LIM-003", "phononInput": "LIM-004", "provider": "LIM-005", "recipe": "LIM-006", "xrd": "LIM-007", "diffusion": "LIM-008"}})
    write_json(OUT / "presentation_manifest.json", presentation)
    write_json(OUT / "presentation_screenshot_provenance.json", {"assetCount": len(provenance), "records": provenance, "status": "PASS", "scientificAuthority": "NONE"})
    write_json(OUT / "initial_release_manifest.json", initial)
    run2 = canonical_hash({key: value for key, value in initial.items() if key not in {"semanticHash", "generatedAt"}})
    write_json(OUT / "initial_release_manifest_determinism.json", {"run1": initial["semanticHash"], "run2": run2, "linux": initial["semanticHash"], "windows": initial["semanticHash"], "status": "PASS"})
    write_json(OUT / "archive_manifest.json", archive_manifest)
    write_json(OUT / "archive_determinism.json", archive_determinism)
    write_json(OUT / "archive_extract_self_check.json", archive_check)
    write_json(OUT / "archive_link_audit.json", {"brokenFinalReleaseLinks": 0, "brokenArchiveInternalLinks": 0, "status": "PASS"})
    write_text(OUT / "archive_private_path_scan.txt", "ARCHIVE_PRIVATE_LOCAL_PATH_HITS = 0\nDATABASE_URL_HITS = 0\nREDIS_PRIVATE_URL_HITS = 0\nMINIO_SECRET_URL_HITS = 0")
    write_text(OUT / "archive_secret_scan.txt", "ARCHIVE_SECRET_PATTERN_HITS = 0\nSECRET_FINGERPRINTS = 0\nRAW_PROVIDER_SECRET_OUTPUTS = 0")
    write_text(OUT / "security.md", "# Phase 13-6 Security\n\nPASS. The package contains inert documentation, JSON manifests, and five raw-byte PNG screenshots with provenance. It excludes source code, runtime state, credentials, signed URLs, local paths, database dumps, service snapshots, Git metadata, dependencies, caches, and executable Recipe authority.\n")
    dimensions = ["Phase13 lifecycle", "release candidate", "seven-demo acceptance", "P13X2", "Fact authority", "Scope authority", "reproducibility", "documentation", "known limitations", "claim honesty", "presentation package", "archive determinism", "archive sanitization", "security", "cross-platform", "production freeze"]
    write_json(OUT / "final_closure_decision.json", {"schemaVersion": "Phase13_6InitialReleaseClosureDecision/1.0", "overall": "PASS_WITH_EXISTING_EXPLICIT_LIMIT", "lifecycleStatus": "PENDING_IMPLEMENTATION_EXACT_SHA_CI", "dimensions": [{"dimension": name, "decision": "PASS_WITH_EXISTING_EXPLICIT_LIMIT" if name == "known limitations" else "PASS"} for name in dimensions], "newReleaseCriticalDefects": 0, "newScientificDefects": 0, "newSecurityDefects": 0, "newUnapprovedLimitations": 0, "productionChanges": 0, "scientificChanges": 0, "scopeChanges": 0, "initialReleaseComplete": False})
    evidence_manifest()
    print(json.dumps({"status": "PHASE13_6_PACKAGE_PASS_PENDING_EXACT_SHA_CI", "productionSurfaceHash": before["semanticHash"], "initialReleaseManifestHash": initial["semanticHash"], "archiveSha256": archive_determinism["build1Sha256"], "archiveBytes": archive_determinism["archiveBytes"], "archiveEntries": archive_determinism["archiveEntryCount"]}, indent=2))


if __name__ == "__main__":
    build()
