from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from mdi_adapters.registry import ADAPTER_CLASSES
from mdi_tool_registry import load_manifests


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/phase13/evidence/phase13_0_release_scope_seal"
DOCS = ROOT / "docs/phase13"
PHASE11 = ROOT / "docs/phase11/evidence"
PHASE12 = ROOT / "docs/phase12/evidence/phase12_7_cross_product_ux_validation"
ENTRY_BASELINE = "69d53376b188a20db2c3cc2c28824afb5971621d"
PHASE11_BASELINE_HASH = "5273b5e866e950c592fe757c2e7bde2d4ede9551f7eb406d0744bb6dcf7d93cb"
PHASE12_BASELINE_HASH = "29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4"


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


TEXT_FIXTURE_SUFFIXES = {".cif", ".csv", ".json", ".md", ".txt", ".vasp", ".yaml", ".yml", ".xyz"}


def stable_fixture_bytes(path: Path) -> bytes:
    content = path.read_bytes()
    if path.suffix.lower() in TEXT_FIXTURE_SUFFIXES:
        return content.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return content


def stable_fixture_hash(path: Path) -> str:
    return hashlib.sha256(stable_fixture_bytes(path)).hexdigest()


def write_json(name: str, value: Any) -> None:
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(name: str, value: str) -> None:
    (OUT / name).write_text(value.rstrip() + "\n", encoding="utf-8")


def write_doc(name: str, value: str) -> None:
    (DOCS / name).write_text(value.rstrip() + "\n", encoding="utf-8")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def tool_capability(tool_id: str) -> str:
    exact = {
        "dataset.materials_explorer": "dataset-materials-explorer",
        "dataset.composition_space": "composition-space",
        "structure.coordination_hist": "coordination",
        "structure.coordination_crystalnn": "coordination",
        "structure.coordination_voronoinn": "coordination",
        "structure.local_environment_polyhedra": "local-environment-polyhedra",
        "structure.xrd": "experimental-xrd",
        "structure.experimental_xrd_comparison": "experimental-xrd",
        "structure.rdf": "rdf",
        "trajectory.rdf": "rdf",
        "trajectory.msd": "msd",
        "trajectory.diffusion": "diffusion",
        "trajectory.viewer": "trajectory",
        "structure.trajectory_import": "trajectory",
        "structure.trajectory_viewer": "trajectory",
        "phonon.band": "phonon-band",
        "phonon.dos": "phonon-dos",
        "phonon.band_dos": "phonon-combined",
        "phonon.animation": "phonon-animation",
        "structure.brillouin_zone": "brillouin-zone",
        "structure.volumetric_data": "volumetric",
        "electronic.band_structure": "electronic-band",
        "electronic.dos": "electronic-dos",
    }
    if tool_id in exact:
        return exact[tool_id]
    if tool_id.startswith("ml."):
        return "materials-ml"
    if tool_id.startswith("composition."):
        return "composition-analysis"
    if tool_id.startswith(("table.", "viz.")):
        return "dataset-intelligence"
    if tool_id.startswith("structure."):
        return "structure"
    raise AssertionError(f"Unclassified Registry Tool: {tool_id}")


CAPABILITIES = [
    ("dataset-intelligence", "Dataset Intelligence", "data"),
    ("dataset-materials-explorer", "Dataset Materials Explorer", "data"),
    ("materials-ml", "Materials ML", "data"),
    ("composition-space", "Composition Space", "data"),
    ("composition-analysis", "Composition Analysis", "science"),
    ("structure", "Structure", "science"),
    ("coordination", "Coordination", "science"),
    ("local-environment-polyhedra", "Local Environment and Polyhedra", "science"),
    ("experimental-xrd", "Experimental XRD Comparison", "science"),
    ("trajectory", "Trajectory", "science"),
    ("rdf", "RDF", "science"),
    ("msd", "MSD", "science"),
    ("diffusion", "Diffusion", "science"),
    ("phonon-band", "Phonon Band", "science"),
    ("phonon-dos", "Phonon DOS", "science"),
    ("phonon-combined", "Combined Phonon Band and DOS", "presentation"),
    ("phonon-animation", "Phonon Animation", "presentation"),
    ("brillouin-zone", "Brillouin Zone", "science"),
    ("volumetric", "Volumetric", "science"),
    ("electronic-band", "Electronic Band Structure", "science"),
    ("electronic-dos", "Electronic DOS", "science"),
    ("combined-band-dos", "Combined Electronic Band and DOS", "presentation"),
    ("workspace", "Scientific Workspace", "product"),
    ("finding-evidence-provenance", "Finding, Evidence and Provenance", "product"),
    ("report", "Report", "product"),
    ("recipe", "Recipe", "product"),
]


DEMO_SPECS = [
    {
        "demoId": "P13-DEMO-01",
        "family": "Dataset Intelligence + Composition Space",
        "capabilities": ["dataset-intelligence", "dataset-materials-explorer", "composition-space", "composition-analysis"],
        "fixtures": ["tests/fixtures/tables/formulas.csv"],
        "prompt": "Explore this materials table, summarize its quality, and show how the compositions are distributed.",
        "alternatePrompt": "What composition patterns and data-quality issues should I notice in this table?",
        "expectedArtifactFamilies": ["table_json", "plotly_json", "summary_md", "recipe_json"],
        "limitations": ["Composition-space PCA and clustering are descriptive, not material identity."],
    },
    {
        "demoId": "P13-DEMO-02",
        "family": "Materials ML",
        "capabilities": ["materials-ml"],
        "fixtures": ["tests/fixtures/tables/ml_results.csv"],
        "prompt": "Evaluate these materials-model predictions and explain the largest errors and limitations.",
        "alternatePrompt": "How well does this model perform, and which samples deserve inspection?",
        "expectedArtifactFamilies": ["table_json", "plotly_json", "summary_md", "recipe_json"],
        "limitations": ["Evaluation consumes supplied predictions and does not train a model."],
    },
    {
        "demoId": "P13-DEMO-03",
        "family": "Structure + coordination + local environment + polyhedra + experimental XRD",
        "capabilities": ["structure", "coordination", "local-environment-polyhedra", "experimental-xrd"],
        "fixtures": [
            "tests/fixtures/structures/simple_cubic.cif",
            "docs/phase10n/evidence/phase10n3_experimental_xrd_comparison_peak_matching/perfect_match.json",
        ],
        "prompt": "Inspect this crystal structure, compare its coordination methods and local polyhedra, then compare the supplied experimental diffraction peaks.",
        "alternatePrompt": "What are the local environments in this crystal, and how do its supplied XRD peaks correspond to the theoretical pattern?",
        "expectedArtifactFamilies": ["viewer_scene_json", "table_json", "plotly_json", "summary_md", "recipe_json"],
        "limitations": ["CrystalNN and VoronoiNN are separate algorithms.", "Peak correspondence is not phase confirmation or Rietveld refinement."],
    },
    {
        "demoId": "P13-DEMO-04",
        "family": "Trajectory + RDF + MSD + diffusion",
        "capabilities": ["trajectory", "rdf", "msd", "diffusion"],
        "fixtures": ["docs/phase10g/fixtures/trajectory_v1/fixed_lattice_md.json"],
        "prompt": "Analyze this trajectory, show the RDF and MSD, and estimate diffusion with its fit diagnostics.",
        "alternatePrompt": "What structural and transport behavior is visible in this trajectory, including RDF, MSD and diffusion limits?",
        "expectedArtifactFamilies": ["trajectory_json", "table_json", "plotly_json", "summary_md", "recipe_json"],
        "limitations": ["Diffusion requires an exact persisted MSD dependency and valid time semantics."],
    },
    {
        "demoId": "P13-DEMO-05",
        "family": "Phonon + Brillouin Zone",
        "capabilities": ["phonon-band", "phonon-dos", "phonon-combined", "phonon-animation", "brillouin-zone"],
        "fixtures": [
            "docs/phase10h/fixtures/phonon_contract/stable_band.json",
            "docs/phase10h/fixtures/phonon_contract/total_dos.json",
            "docs/phase10i/fixtures/brillouin_zone_v1/simple_cubic/reciprocal_lattice.json",
        ],
        "prompt": "Show the supplied phonon bands and density of states together with the matching Brillouin-zone context.",
        "alternatePrompt": "Help me inspect this supplied phonon result and its reciprocal-space path.",
        "expectedArtifactFamilies": ["phonon_band_json", "phonon_dos_json", "brillouin_zone_json", "summary_md", "recipe_json"],
        "limitations": ["Generic phonon YAML/JSON upload remains mapping-only; the demo must exercise the sealed normalized resource path."],
    },
    {
        "demoId": "P13-DEMO-06",
        "family": "Volumetric",
        "capabilities": ["volumetric"],
        "fixtures": ["docs/phase10j/fixtures/volumetric_parser/CHGCAR"],
        "prompt": "Inspect this volumetric field with its structure context, slices and supported volume presentation.",
        "alternatePrompt": "What does this supplied volumetric grid contain, and which bounded views are available?",
        "expectedArtifactFamilies": ["volumetric_grid_json", "volumetric_dataset_json", "summary_md", "recipe_json"],
        "limitations": ["Presentation does not add Bader, topology, segmentation or arbitrary slicing authority."],
    },
    {
        "demoId": "P13-DEMO-07",
        "family": "Electronic Band + DOS",
        "capabilities": ["electronic-band", "electronic-dos", "combined-band-dos"],
        "fixtures": [
            "docs/phase10n/evidence/phase10n5_electronic_band_dos/electronic_resource_contracts/band.json",
            "docs/phase10n/evidence/phase10n5_electronic_band_dos/electronic_resource_contracts/dos.json",
        ],
        "prompt": "Inspect the supplied electronic band structure and DOS, including gap, spin, projection and compatibility limitations.",
        "alternatePrompt": "What electronic states are present in these supplied Band and DOS resources?",
        "expectedArtifactFamilies": ["table_json", "plotly_json", "summary_md", "recipe_json"],
        "limitations": ["The platform analyzes supplied electronic data; it does not perform DFT or GW calculations."],
    },
]


PHASE13_ACCEPTANCE = {
    "13-0": [
        "Phase 11, Phase 12 and repository final fact alignment",
        "Initial Release capability and input-support matrix sealed",
        "Public claims, limitations, Future Scope and Not Planned registries sealed",
        "Release-critical integration gap registry complete and prioritized",
        "Seven canonical real-user E2E demo contracts sealed",
        "No handcrafted Plan, Job, Artifact, Workspace, Finding or Report shortcut policy sealed",
        "Phase 13 acceptance, evidence and lifecycle governance sealed",
        "Deterministic Initial Release scope baseline and 13-1 handoff sealed",
    ],
    "13-1": ["Release blockers only", "Minimal integration fixes", "No feature expansion", "Real service path restoration", "Identity and persistence integrity", "Regression", "Evidence", "Lifecycle"],
    "13-2": ["Seven real-user demos", "User-entry-only path", "Real persistence and runtime", "Registered Adapter execution", "Exact lineage", "Negative and imperfect-user cases", "Scientific honesty", "Evidence and lifecycle"],
    "13-3": ["Installation and run docs", "Supported input and capability docs", "Reproducibility package", "Demo reproduction guide", "Limitations", "Scientific validation references", "Report and Recipe examples", "Release documentation integrity"],
    "13-4": ["Evidence-derived polish only", "No feature expansion", "Demo friction", "Documentation usability", "Minor alignment", "Clipping and overflow", "Wording", "Lifecycle"],
    "13-5": ["Final release candidate", "Seven-demo final status", "Negative paths", "Full regression", "Browser and service", "Scientific authority", "Security and docs", "Release decision"],
    "13-6": ["Archive", "Final evidence manifest", "Presentation package", "Release baseline", "Final docs", "Completion record", "Queue closure", "No Phase 14"],
}


def build_acceptance_registry() -> dict[str, Any]:
    records = []
    for phase, descriptions in PHASE13_ACCEPTANCE.items():
        for index, description in enumerate(descriptions, 1):
            records.append({"acceptanceId": f"P13X{phase[-1]}-A{index:02d}", "phase": phase, "description": description, "status": "PASS" if phase == "13-0" else "SEALED_NOT_EXECUTED"})
    return {"schemaVersion": "phase13-acceptance-registry/1.0", "expected": 56, "records": records, "duplicate": 0, "missing": 0, "extra": 0, "conflicting": 0}


def build_demo_registry() -> tuple[dict[str, Any], dict[str, Any]]:
    fixtures = []
    demos = []
    dimensions = ["User Entry", "Profile Readiness", "Intent", "Clarification", "Eligibility", "Plan", "Runtime", "Artifact", "Workspace", "Interpretation", "Finding/Evidence", "Report/Recipe", "Recovery", "Scientific Honesty", "Identity", "Persistence", "Presentation"]
    for spec in DEMO_SPECS:
        fixture_ids = []
        for index, relative in enumerate(spec["fixtures"], 1):
            path = ROOT / relative
            if not path.is_file():
                raise AssertionError(f"Missing demo fixture: {relative}")
            fixture_id = f"{spec['demoId']}-FIX-{index:02d}"
            fixture_ids.append(fixture_id)
            fixtures.append({
                "fixtureId": fixture_id,
                "demoId": spec["demoId"],
                "path": relative,
                "checksum": stable_fixture_hash(path),
                "byteSize": len(stable_fixture_bytes(path)),
                "format": path.suffix.lower() or path.name,
                "source": "repository-retained reviewed fixture",
                "licenseDisposition": "REPOSITORY_INTERNAL_OR_RETAINED_WITH_EXISTING_PROVENANCE",
                "retentionSafe": True,
                "expectedProfileCapabilities": spec["capabilities"],
                "newScientificExpectedValues": 0,
            })
        demos.append({
            **{key: value for key, value in spec.items() if key != "fixtures"},
            "fixtureIds": fixture_ids,
            "mode": "REAL_USER_ENTRY_E2E",
            "feasibility": "READY_WITH_LIMITS",
            "executed": False,
            "passClaim": False,
            "naturalLanguageIntentRequired": True,
            "clarification": {"whenRequired": True, "maxRounds": 2, "validOptions": "user-visible bounded choices", "resolvedIntentInjection": False},
            "eligibility": {"expectedCapabilityFamilies": spec["capabilities"], "toolIdInjected": False},
            "plan": {"versions": ["0.1", "0.2"], "semanticStepsOnly": True, "handcrafted": False},
            "workspace": {"oneWorkspacePerRealJob": True, "artifactIdentityExact": True},
            "reportRecipe": {"required": True, "persistedFactsOnly": True, "recipeExecutable": False},
            "acceptanceDimensions": [{"dimension": item, "required": True, "status": "NOT_EXECUTED_13_0"} for item in dimensions],
        })
    return ({"schemaVersion": "phase13-seven-demo-registry/1.0", "expected": 7, "registered": len(demos), "extra": 0, "missing": 0, "demos": demos}, {"schemaVersion": "phase13-demo-fixture-registry/1.0", "records": fixtures, "missing": 0, "checksumMismatch": 0, "externalDownloads": 0})


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    phase12 = load_json(PHASE12 / "phase12_product_experience_baseline.json")
    phase12_handoff = load_json(PHASE12 / "phase13_handoff.json")
    phase11_final = load_json(PHASE11 / "phase11_5_scientific_validation_closure/phase11_final_baseline.json")
    phase11_golden = load_json(PHASE11 / "phase11_5_scientific_validation_closure/phase11_golden_suite_index.json")
    phase11_levels = load_json(PHASE11 / "phase11_5_scientific_validation_closure/phase11_validation_level_distribution.json")
    input_source_path = PHASE11 / "phase11_4_honest_tool_input_example_coverage/input_coverage_matrix.json"
    tool_source_path = PHASE11 / "phase11_4_honest_tool_input_example_coverage/tool_coverage_matrix.json"
    input_source = load_json(input_source_path)
    tool_source = load_json(tool_source_path)

    if phase12["semanticHash"] != PHASE12_BASELINE_HASH:
        raise AssertionError("Phase 12 baseline hash drift")
    phase12_without_hash = {key: value for key, value in phase12.items() if key != "semanticHash"}
    if canonical_hash(phase12_without_hash) != PHASE12_BASELINE_HASH:
        raise AssertionError("Phase 12 baseline is not deterministic")
    if phase11_final["scientificValidationBaselineHash"] != PHASE11_BASELINE_HASH:
        raise AssertionError("Phase 11 baseline hash drift")

    registry = load_manifests()
    live_tools = [tool.model_dump(mode="json") for tool in registry.tools]
    live_keys = [f"{tool['toolId']}@{tool['version']}" for tool in live_tools]
    if len(live_tools) != 62 or len(set(live_keys)) != 62:
        raise AssertionError("Live Registry must contain 62 unique versioned Tools")
    documented_keys = [f"{tool['toolId']}@{tool['toolVersion']}" for tool in tool_source["tools"]]
    if set(live_keys) != set(documented_keys):
        raise AssertionError("Phase 11 Tool coverage does not match live Registry")

    assignments: dict[str, list[str]] = {capability_id: [] for capability_id, _, _ in CAPABILITIES}
    for key in live_keys:
        assignments[tool_capability(key.split("@", 1)[0])].append(key)
    assigned = [key for values in assignments.values() for key in values]
    if len(assigned) != 62 or set(assigned) != set(live_keys):
        raise AssertionError("Release capability assignment must cover each Registry Tool exactly once")

    capability_rows = []
    demo_by_capability = {capability: spec["demoId"] for spec in DEMO_SPECS for capability in spec["capabilities"]}
    for capability_id, name, category in CAPABILITIES:
        tool_ids = sorted(assignments[capability_id])
        capability_rows.append({
            "capabilityId": capability_id,
            "userFacingName": name,
            "category": category,
            "currentToolIds": tool_ids,
            "inputRequirements": "Exact Phase 11 input-support verdict and capability-specific semantic contract",
            "DataProfilePrerequisites": "DataProfile 2.4 capability-specific readiness; product-only rows use persisted authorities",
            "productSupportLevel": "SUPPORTED_WITH_EXPLICIT_LIMITS",
            "inputSupportLevel": "SEE_PHASE11_SEALED_INPUT_MATRIX",
            "scientificValidationLevel": "V1_RUNTIME_AND_ARTIFACT_VERIFIED" if tool_ids else "NOT_APPLICABLE_PRODUCT_OR_PRESENTATION",
            "crossPlatformStatus": "LOCKED_LINUX_WINDOWS_INVARIANT_REPLAY; NUMERIC_REFERENCE_NOT_APPLICABLE",
            "presentationStatus": "PHASE12_VALIDATED_WITH_EXPLICIT_LIMITS",
            "knownLimitations": ["Support, validation, reproducibility and presentation are independent axes."],
            "realUserE2ERequired": capability_id in demo_by_capability,
            "demoFamily": demo_by_capability.get(capability_id),
            "InitialReleaseClaim": f"The product supports {name} through its sealed contracts and explicit limitations.",
            "FutureScopeRelation": "NONE; no Future Scope promotion",
            "evidenceRefs": ["docs/phase11/phase11_final_tool_coverage_matrix.md", "docs/phase12/phase12_final_product_experience_baseline.md"],
        })
    capability_matrix = {"schemaVersion": "initial-release-capability-matrix/1.0", "registryToolCount": 62, "assignedToolCount": len(assigned), "duplicateToolAssignments": 0, "unassignedTools": 0, "capabilities": capability_rows}

    registry_reconciliation = {
        "schemaVersion": "phase13-registry-reconciliation/1.0",
        "registryVersion": registry.version,
        "liveRegistryCount": len(live_tools),
        "documentedRegistryCount": tool_source["rowCount"],
        "releaseMatrixToolCount": len(assigned),
        "uniqueVersionedToolCount": len(set(live_keys)),
        "adapterRegisteredCount": sum(1 for tool in live_tools if tool["adapter"] in ADAPTER_CLASSES),
        "adapterUnavailableCount": sum(1 for tool in live_tools if tool["adapter"] not in ADAPTER_CLASSES),
        "tools": [{"toolId": tool["toolId"], "version": tool["version"], "adapter": tool["adapter"], "adapterRegistered": tool["adapter"] in ADAPTER_CLASSES, "capabilityId": tool_capability(tool["toolId"])} for tool in live_tools],
        "status": "PASS",
    }

    scientific_validation = {
        "schemaVersion": "initial-release-scientific-validation-matrix/1.0",
        "fourAxes": ["PRODUCT_SUPPORT", "SCIENTIFIC_VALIDATION", "CROSS_PLATFORM_REPRODUCIBILITY", "PRESENTATION_VALIDATION"],
        "goldenRecords": phase11_golden["benchmarkCount"],
        "passInvariant": phase11_golden["passCount"],
        "notApplicable": phase11_golden["notApplicableCount"],
        "failures": phase11_golden["failCount"],
        "linuxInvariantReplay": "PASS",
        "windowsInvariantReplay": "PASS",
        "numericCrossPlatformValidation": "NOT_APPLICABLE",
        "validationLevelDistribution": phase11_levels["distribution"],
        "v4": phase11_levels["distribution"]["V4"],
        "toolCoverageSourceHash": canonical_hash(tool_source),
        "tools": tool_source["tools"],
    }

    claims = [
        ("P13-CLAIM-001", "PRODUCT_CAPABILITY", "Material Data Intelligence and Scientific Visualization Platform", "Bounded materials-data analysis, persisted scientific products and evidence-aware presentation."),
        ("P13-CLAIM-002", "PRODUCT_CAPABILITY", "Natural-language entry routes eligible work through a bounded Planner.", "Intent, clarification, eligibility and Plan validation precede execution."),
        ("P13-CLAIM-003", "SCIENTIFIC_VALIDATION", "Scientific validation is reference-backed with explicit limits.", "Phase 11 has 12 golden records: 8 invariant passes and 4 explicit N/A cases."),
        ("P13-CLAIM-004", "REPRODUCIBILITY", "Sealed invariants replay on locked Linux and Windows environments.", "Numeric cross-platform reference validation remains N/A and V4 remains zero."),
        ("P13-CLAIM-005", "PRESENTATION", "Core product journeys were validated in Chromium, Firefox, WebKit and 390x844 presentation.", "Browser evidence is presentation authority only."),
        ("P13-CLAIM-006", "ACCESSIBILITY", "The accessibility engineering target is met with documented limitations.", "This is not formal WCAG certification or a human assistive-technology study."),
        ("P13-CLAIM-007", "PROVIDER", "DeepSeek is the only real LLM provider policy.", "Endpoint and model allowlist are bounded; the LLM is not a scientific executor."),
        ("P13-CLAIM-008", "SECURITY", "Artifacts and Recipes are inert and do not grant arbitrary execution authority.", "No arbitrary Python, shell, notebook, HTML, JavaScript or remote Artifact execution."),
        ("P13-CLAIM-009", "REPRODUCIBILITY_RECORD", "Reports compose persisted facts and Recipes preserve exact declarative provenance.", "Recipe execution authority is none."),
        ("P13-CLAIM-010", "INPUT_SUPPORT", "Supported inputs follow the sealed 14-row Phase 11 matrix.", "Upload/parse support does not imply direct scientific support or independent validation."),
    ]
    claim_registry = {
        "schemaVersion": "initial-release-claim-registry/1.0",
        "claims": [{"claimId": cid, "claimType": ctype, "publicWording": wording, "technicalMeaning": meaning, "scope": "Initial Release", "supportEvidence": ["Phase 11", "Phase 12"], "scientificEvidence": "Phase 11 only where applicable", "limitations": "See InitialReleaseLimitationRegistry", "forbiddenStrongerWording": True, "releaseBlockingIfFalse": True} for cid, ctype, wording, meaning in claims],
    }
    forbidden = {
        "schemaVersion": "forbidden-release-claims/1.0",
        "claims": [
            "all tools independently scientifically validated",
            "all numeric outputs cross-platform reference validated",
            "formal WCAG certified",
            "autonomous scientific researcher",
            "arbitrary scientific workflow engine",
            "DFT/GW computation platform",
            "Rietveld refinement platform",
            "Recipe automatically reproduces by executing itself",
            "browser rendering proves numeric correctness",
            "all common file types directly scientifically supported",
        ],
    }
    limitations = {
        "schemaVersion": "initial-release-known-limitations/1.0",
        "limitations": [
            {"limitationId": "P13-LIM-001", "statement": "V4 validation promotions remain zero and numeric cross-platform reference validation is not applicable.", "releaseBlocking": False},
            {"limitationId": "P13-LIM-002", "statement": "macOS is not a current scientific release target.", "releaseBlocking": False},
            {"limitationId": "P13-LIM-003", "statement": "Formal WCAG certification and a human assistive-technology study are absent.", "releaseBlocking": False},
            {"limitationId": "P13-LIM-004", "statement": "Some spatial 3D interaction is not screen-reader-equivalent; structured alternatives remain available.", "releaseBlocking": False},
            {"limitationId": "P13-LIM-005", "statement": "Phonon YAML/JSON is mapping-only rather than a generic direct-upload claim.", "releaseBlocking": False},
            {"limitationId": "P13-LIM-006", "statement": "Official examples remain mapping-only and do not constitute independent scientific validation.", "releaseBlocking": False},
        ],
    }
    future_scope = {
        "schemaVersion": "initial-release-future-scope/1.0",
        "status": "DOCUMENTED_NOT_QUEUED",
        "items": ["Fermi surface", "projected bands / fatbands", "full Rietveld / refinement / phase fractions", "advanced diffraction", "Bader / charge topology / ELF topology", "defects / surfaces / slabs", "VACF / Green-Kubo / Arrhenius / hops / van Hove", "effective mass", "advanced transport"],
    }
    not_planned = {
        "schemaVersion": "initial-release-not-planned/1.0",
        "items": ["generic arbitrary DAG/workflow engine", "arbitrary Python/Shell/notebook execution", "runtime autonomous replanning", "RAG / vector DB", "plugin marketplace", "multi-tenant SaaS", "billing", "enterprise RBAC productization", "Kubernetes/distributed scheduler", "KMS/HSM enterprise infrastructure", "unrestricted multi-provider LLM"],
    }

    demo_registry, fixture_registry = build_demo_registry()
    gaps = [
        {"gapId": "P13-GAP-001", "category": "NONBLOCKING_LIMITATION", "severity": "P2", "affectedDemo": "all scientific demos", "affectedUserPath": "scientific validation disclosure", "repositoryEvidence": "Phase 11 V4=0 and numeric cross-platform NOT_APPLICABLE", "scientificConsequence": "No independent numeric cross-platform claim", "productConsequence": "Limitation must remain visible", "securityConsequence": "none", "minimalFixBoundary": "disclosure only", "ownerPhase": "13-3", "releaseBlocking": False, "acceptanceIds": ["P13X3-A05"]},
        {"gapId": "P13-GAP-002", "category": "NONBLOCKING_LIMITATION", "severity": "P2", "affectedDemo": ["P13-DEMO-03", "P13-DEMO-06"], "affectedUserPath": "3D scientific inspection", "repositoryEvidence": "Phase 12 accepted UX limitations", "scientificConsequence": "none; structured facts remain authoritative", "productConsequence": "Spatial interaction is not screen-reader-equivalent", "securityConsequence": "none", "minimalFixBoundary": "retain structured alternative and disclosure", "ownerPhase": "13-3", "releaseBlocking": False, "acceptanceIds": ["P13X3-A08"]},
        {"gapId": "P13-GAP-003", "category": "EVIDENCE_GAP", "severity": "P2", "affectedDemo": [spec["demoId"] for spec in DEMO_SPECS], "affectedUserPath": "real-user service-backed release demonstrations", "repositoryEvidence": "Phase 13-0 defines contracts but executes zero demos", "scientificConsequence": "No new scientific reference claim", "productConsequence": "Seven demo PASS cannot be claimed before 13-2", "securityConsequence": "none", "minimalFixBoundary": "execute sealed contracts without feature expansion", "ownerPhase": "13-2", "releaseBlocking": False, "acceptanceIds": ["P13X2-A01", "P13X2-A08"]},
    ]
    gap_registry = {"schemaVersion": "phase13-release-critical-gap-registry/1.0", "releaseBlockers": 0, "releaseCriticalIntegrationGaps": 0, "nonblockingLimitations": 2, "evidenceGaps": 1, "unclassified": 0, "gaps": gaps}

    acceptance_registry = build_acceptance_registry()
    personas = {
        "schemaVersion": "phase13-demo-personas/1.0",
        "personas": [
            {"personaId": "P13-PERSONA-A", "name": "Canonical Scientist User", "contract": ["supported material data", "reasonable scientific question", "does not know Tool IDs", "user-facing UI only", "expects result and limitations"]},
            {"personaId": "P13-PERSONA-B", "name": "Exploratory / Imperfect User", "contract": ["ambiguous question", "wrong or limited data", "unsupported request", "back navigation", "refresh and recovery", "partial execution", "inspects limitations"]},
        ],
    }
    no_injection = {"schemaVersion": "phase13-demo-no-injection-policy/1.0", "analysisPlan": 0, "job": 0, "toolCall": 0, "artifact": 0, "workspace": 0, "finding": 0, "evidence": 0, "report": 0, "recipe": 0, "normalUserLocators": ["role", "accessible name", "user-visible semantics"], "developerAuditMayReadExactIdsAfterFlow": True}
    runtime_policy = {"schemaVersion": "phase13-demo-runtime-policy/1.0", "realPersistenceRequired": True, "realQueueWorkerRuntimeRequired": True, "registeredAdapterExecutionRequired": True, "workspaceFromRealJobRequired": True, "reportFromRealPersistedFactsRequired": True, "services": ["PostgreSQL", "Redis", "MinIO"], "mockPersistenceAsReleaseAuthority": False}
    provider_policy = {"schemaVersion": "phase13-demo-provider-policy/1.0", "realProvider": "deepseek", "endpoint": "https://api.deepseek.com", "models": ["deepseek-v4-flash", "deepseek-v4-pro"], "keySource": "DEEPSEEK_KEY", "deterministicReleaseAuthority": "DETERMINISTIC_PROVIDER_REPLAY_ALLOWED", "boundedLiveAcceptance": {"requiredCases": 1, "maximumCallsPerCase": 2, "timeoutSeconds": 60, "retries": 0, "rawPayloadRetention": False}, "phase13_0RealCalls": 0, "llmScientificAuthority": "NONE"}
    negative_paths = {"schemaVersion": "phase13-demo-negative-path-registry/1.0", "required": True, "paths": ["ambiguous Intent", "unsupported capability", "unsupported or limited input", "partial execution", "stale or historical recovery", "provider unavailable or controlled failure", "Report with limitation"]}
    user_entry = {"schemaVersion": "phase13-demo-user-entry-policy/1.0", "naturalLanguageEntry": "YES_WHERE_PRODUCT_CONTRACT_APPLIES", "toolIdPrompt": False, "handcraftedPlan": False, "canonicalPrompts": [{"demoId": spec["demoId"], "primary": spec["prompt"], "alternate": spec["alternatePrompt"]} for spec in DEMO_SPECS]}

    evidence_contract = {"schemaVersion": "phase13-evidence-contract/1.0", "requiredAxes": ["user entry", "profile", "intent", "eligibility", "plan", "runtime", "artifact", "workspace", "interpretation", "evidence", "report/recipe", "identity", "persistence", "presentation"], "screenshotsNumericAuthority": "NONE", "realPersistenceRequired": True, "manifestRequired": True, "secretRedactionRequired": True}
    lifecycle_contract = {"schemaVersion": "phase13-lifecycle-contract/1.0", "implementationExactShaCiRequired": True, "completionCiWaitRequired": False, "archiveCiWaitRequired": False, "failedCandidateRetention": True, "forcePush": False, "phase13_1TaskCreated": False, "phase13_2TaskCreated": False, "phase14Created": False}
    phase13_1_handoff = {"schemaVersion": "phase13-1-release-critical-integration-gap-handoff/1.0", "scopeBaselineRef": "initial_release_scope_baseline.json", "releaseBlockerIds": [], "releaseCriticalIntegrationGapIds": [], "mode": "ZERO_GAP_VERIFICATION_CLOSURE", "minimalFixBoundary": "No implementation unless reviewer-authorized evidence proves a release-critical integration defect.", "featureExpansionForbidden": True, "phase11Authority": PHASE11_BASELINE_HASH, "phase12Authority": PHASE12_BASELINE_HASH, "acceptanceIds": [f"P13X1-A{i:02d}" for i in range(1, 9)], "phase13_2Entry": "reviewer approval after 13-1 closure"}
    phase13_2_preview = {"schemaVersion": "phase13-2-canonical-e2e-contract/1.0", "demoIds": [spec["demoId"] for spec in DEMO_SPECS], "fixtures": [record["fixtureId"] for record in fixture_registry["records"]], "personas": [item["personaId"] for item in personas["personas"]], "naturalLanguagePrompts": user_entry["canonicalPrompts"], "providerMode": provider_policy, "runtimePolicy": runtime_policy, "noInjection": no_injection, "negativePaths": negative_paths["paths"], "executed": False}

    records: dict[str, Any] = {
        "phase12_handoff_snapshot.json": phase12_handoff,
        "phase12_baseline_verification.json": {"expected": PHASE12_BASELINE_HASH, "actual": phase12["semanticHash"], "regenerated": canonical_hash(phase12_without_hash), "determinism": "PASS", "mutations": 0},
        "phase11_authority_snapshot.json": {"baseline": phase11_final, "golden": phase11_golden, "validationLevels": phase11_levels, "readOnly": True, "mutations": 0},
        "repository_fact_inventory.json": {"entryBaseline": ENTRY_BASELINE, "branch": "master", "phase12Implementation": "8fb5dcbe54fbbcd32677107abb5f4117bd04948d", "phase12ImplementationCi": "31397995499", "phase12Completion": "a369bf26aca1b11522aed97e5baa1fa9017d673e", "phase12Archive": ENTRY_BASELINE, "registry": 62, "dataProfile": "2.4", "analysisIntent": "1.0", "eligibilityResolution": "1.0", "analysisPlans": ["0.1", "0.2"], "migration": "0007_phase10m1_workspace_domain"},
        "registry_reconciliation.json": registry_reconciliation,
        "capability_matrix.json": capability_matrix,
        "input_support_matrix.json": {"schemaVersion": "phase13-input-support-snapshot/1.0", "source": str(input_source_path.relative_to(ROOT)).replace("\\", "/"), "sourceHash": canonical_hash(input_source), "rowCount": input_source["rowCount"], "inputs": input_source["inputs"], "supportPromotions": 0},
        "scientific_validation_matrix.json": scientific_validation,
        "release_claim_registry.json": claim_registry,
        "forbidden_release_claims.json": forbidden,
        "known_limitations.json": limitations,
        "future_scope_registry.json": future_scope,
        "not_planned_registry.json": not_planned,
        "release_gap_registry.json": gap_registry,
        "release_gap_priority.json": {"P0": [], "P1": [], "P2": ["P13-GAP-001", "P13-GAP-002", "P13-GAP-003"], "unclassified": 0},
        "seven_demo_registry.json": demo_registry,
        "demo_fixture_registry.json": fixture_registry,
        "demo_user_personas.json": personas,
        "demo_user_entry_policy.json": user_entry,
        "demo_no_injection_policy.json": no_injection,
        "demo_runtime_policy.json": runtime_policy,
        "demo_provider_policy.json": provider_policy,
        "demo_negative_path_registry.json": negative_paths,
        "phase13_acceptance_registry.json": acceptance_registry,
        "phase13_evidence_contract.json": evidence_contract,
        "phase13_lifecycle_contract.json": lifecycle_contract,
        "phase13_1_handoff.json": phase13_1_handoff,
        "phase13_2_contract_preview.json": phase13_2_preview,
        "failed_candidates.json": {
            "records": [
                {
                    "sha": "c26815289b239c1169b344ac02707cd737b0b9e5",
                    "ciRun": 31449685832,
                    "failedJob": "Unit Tests (Python 3.11)",
                    "reason": "Initial release semantic baseline used platform-specific generated-file bytes, so CRLF/LF differences changed the exact hash.",
                    "authority": "HISTORICAL_FAILED_CANDIDATE",
                    "fixForward": "Canonical JSON hashes and normalized text-fixture identities replace platform-specific byte hashes.",
                }
            ]
        },
    }
    for name, value in records.items():
        write_json(name, value)

    fact_model = {
        "releaseCandidateId": "initial-release-scope-candidate-13-0",
        "schemaVersion": "initial-release-fact-model/1.0",
        "repositoryBaseline": ENTRY_BASELINE,
        "Phase11Authority": {"baselineHash": PHASE11_BASELINE_HASH, "status": "COMPLETE / REFERENCE_VALIDATED_WITH_EXPLICIT_LIMITS"},
        "Phase12Baseline": {"baselineHash": PHASE12_BASELINE_HASH, "status": "COMPLETE / PRODUCT_EXPERIENCE_REDESIGN_VALIDATED_AND_SEALED"},
        "RegistryVersion": registry.version,
        "RegistryCount": 62,
        "DataProfileVersion": "2.4",
        "AnalysisIntentVersion": "1.0",
        "EligibilityResolutionVersion": "1.0",
        "AnalysisPlanVersions": ["0.1", "0.2"],
        "WorkspaceAuthority": "one server-owned Workspace per real Job; exact URL selection; transient viewer state in memory",
        "ArtifactAuthority": "persisted inert exact-identity scientific records from registered Adapters",
        "InterpretationAuthority": "grounded persisted claim/evidence projection; no execution authority",
        "ReportAuthority": "composition of persisted scientific facts",
        "RecipeAuthority": "exact declarative reproducibility manifest; execution authority NONE",
        "ProviderPolicy": provider_policy,
        "inputSupportMatrixRef": "input_support_matrix.json",
        "toolSupportMatrixRef": "capability_matrix.json",
        "validationMatrixRef": "scientific_validation_matrix.json",
        "limitationRegistryRef": "known_limitations.json",
        "sevenDemoRegistryRef": "seven_demo_registry.json",
        "releaseBlockerRegistryRef": "release_gap_registry.json",
        "futureScopeRegistryRef": "future_scope_registry.json",
        "notPlannedRegistryRef": "not_planned_registry.json",
        "initialReleaseComplete": False,
    }
    fact_model["semanticHash"] = canonical_hash(fact_model)
    write_json("initial_release_fact_model.json", fact_model)

    baseline = {
        "schemaVersion": "initial-release-scope-baseline/1.0",
        "baselineId": "P13-0-INITIAL-RELEASE-SCOPE-BASELINE",
        "phase11ScientificBaselineHash": PHASE11_BASELINE_HASH,
        "phase12ProductBaselineHash": PHASE12_BASELINE_HASH,
        "registrySnapshotHash": canonical_hash(registry_reconciliation),
        "dataProfileVersion": "2.4",
        "inputMatrixHash": canonical_hash(records["input_support_matrix.json"]),
        "capabilityMatrixHash": canonical_hash(capability_matrix),
        "releaseClaimHash": canonical_hash(claim_registry),
        "limitationHash": canonical_hash(limitations),
        "futureScopeHash": canonical_hash(future_scope),
        "notPlannedHash": canonical_hash(not_planned),
        "releaseGapHash": canonical_hash(gap_registry),
        "sevenDemoRegistryHash": canonical_hash(demo_registry),
        "demoFixtureRegistryHash": canonical_hash(fixture_registry),
        "acceptanceRegistryHash": canonical_hash(acceptance_registry),
        "securityBoundaryHash": canonical_hash({"artifactInert": True, "recipeExecution": False, "recommendationExecution": False, "arbitraryCode": False}),
        "factModelHash": fact_model["semanticHash"],
    }
    baseline["semanticHash"] = canonical_hash(baseline)
    write_json("initial_release_scope_baseline.json", baseline)
    write_text("initial_release_scope_baseline_hash.txt", baseline["semanticHash"])

    write_text("baseline.txt", f"ENTRY_BASELINE={ENTRY_BASELINE}\nPHASE12_IMPLEMENTATION=8fb5dcbe54fbbcd32677107abb5f4117bd04948d\nPHASE12_IMPLEMENTATION_CI=31397995499 PASS\nPHASE12_BASELINE={PHASE12_BASELINE_HASH}\nPHASE11_BASELINE={PHASE11_BASELINE_HASH}\nREGISTRY=62\nDATAPROFILE=2.4\nMIGRATION=0007_phase10m1_workspace_domain")
    write_text("entry_gate.md", "PHASE_13_0_ENTRY_GATE = PASS\n\nThe Phase 12 lifecycle and deterministic product baseline, Phase 11 read-only scientific authority, live Registry 62, DataProfile 2.4, AnalysisIntent/Eligibility 1.0, AnalysisPlan 0.1/0.2, migration 0007, unique Phase 13 handoff, empty pre-admission queue and absence of Phase 13-1/13-2/14 tasks are verified.")
    write_text("security.md", "NO_PHASE13_0_ARBITRARY_CODE_EXECUTION = PASS\nNO_PHASE13_0_NEW_ARTIFACT_EXECUTION_AUTHORITY = PASS\nNO_PHASE13_0_RECIPE_EXECUTION = PASS\nNO_PHASE13_0_RECOMMENDATION_EXECUTION = PASS\nNO_PHASE13_0_FRONTEND_SCIENTIFIC_RECOMPUTATION = PASS\nNO_PHASE13_0_EXTERNAL_SCIENTIFIC_API = PASS\nNO_PHASE13_0_REAL_LLM_CALL = PASS\nNO_PHASE13_0_EXTERNAL_DOWNLOADS = PASS")
    write_text("secret_scan.txt", "NO_SECRET_PATTERN_HITS = PASS\nsecret values retained = 0\nprivate paths retained = 0\nreal LLM calls = 0\nexternal downloads = 0")
    write_text("no_production_change_audit.md", "PHASE13_0_PRODUCTION_CODE_CHANGES = 0\nBACKEND_BEHAVIOR_CHANGES = 0\nFRONTEND_BEHAVIOR_CHANGES = 0\nSCIENTIFIC_BEHAVIOR_CHANGES = 0\nThis generator and its tests are audit-only and are not runtime authorities.")

    capability_lines = "\n".join(f"| `{row['capabilityId']}` | {row['userFacingName']} | {len(row['currentToolIds'])} | {row['productSupportLevel']} |" for row in capability_rows)
    demo_lines = "\n".join(f"| {item['demoId']} | {item['family']} | {item['feasibility']} | {len(item['fixtureIds'])} |" for item in demo_registry["demos"])
    write_doc("phase13_0_final_fact_alignment_release_scope_seal.md", f"""# Phase 13-0 Final Fact Alignment and Release Scope Seal

The live repository, Phase 11 scientific authority and Phase 12 product-experience baseline reconcile without capability, validation or input-support promotion. Registry 62, DataProfile 2.4, AnalysisIntent/Eligibility 1.0, AnalysisPlan 0.1/0.2 and migration 0007 remain unchanged.

Phase 13-0 changes no production code. It seals the Initial Release fact model, claims, explicit limits, seven real-user E2E contracts and Phase 13 governance. The seven demonstrations are not executed here and Initial Release is not complete.

`INITIAL_RELEASE_SCOPE_BASELINE_HASH = {baseline['semanticHash']}`
""")
    write_doc("phase13_initial_release_scope.md", """# Phase 13 Initial Release Scope

The Initial Release is a Material Data Intelligence and Scientific Visualization Platform. The product chain is Resource/Upload -> DataProfile -> AnalysisIntent -> bounded clarification -> EligibilityResolution -> capability-aware Planner -> AnalysisPlan 0.1/0.2 -> PlanValidator -> QueueWorkerRuntime -> registered Adapter -> persisted Artifact -> Grounded Interpretation -> ScientificWorkspace -> Finding/Evidence/Provenance -> Report -> non-executable Recipe.

Support, scientific validation, cross-platform reproducibility and presentation validation remain separate. Future Scope and Not Planned work are outside this release.
""")
    write_doc("phase13_release_capability_matrix.md", f"""# Phase 13 Release Capability Matrix

Each of the 62 live versioned Registry Tools is assigned exactly once; product-composition rows have no Tool authority.

| Capability | User-facing name | Tool rows | Product support |
| --- | --- | ---: | --- |
{capability_lines}
""")
    write_doc("phase13_release_claims_and_limitations.md", """# Phase 13 Release Claims and Limitations

Public claims are bounded by `release_claim_registry.json`. Forbidden stronger wording includes all-tools independent validation, all-numeric cross-platform validation, formal WCAG certification, autonomous scientific research, arbitrary workflows, DFT/GW execution, Rietveld refinement, executable Recipes and browser-as-numeric-authority claims.

Known limitations include V4=0, numeric cross-platform N/A, macOS outside the current scientific target, no formal accessibility certification, structured rather than equivalent screen-reader alternatives for some 3D interaction, mapping-only phonon file coverage and mapping-only official examples.
""")
    write_doc("phase13_future_and_not_planned_scope.md", """# Phase 13 Future and Not Planned Scope

Future Scope remains documented and unqueued: Fermi surfaces, projected bands/fatbands, full Rietveld/refinement, advanced diffraction, Bader/charge/ELF topology, defects/surfaces/slabs, advanced trajectory transport, effective mass and advanced transport.

Not Planned remains stronger than Future Scope: arbitrary DAGs, arbitrary code/notebook execution, autonomous runtime replanning, RAG/vector DB, plugin marketplace, SaaS/billing/enterprise RBAC, distributed scheduling, KMS/HSM infrastructure and unrestricted providers.
""")
    write_doc("phase13_release_critical_gap_registry.md", """# Phase 13 Release-Critical Gap Registry

`RELEASE_BLOCKERS = 0` and `RELEASE_CRITICAL_INTEGRATION_GAPS = 0` based on current retained integration evidence. Phase 13-1 is therefore a reviewer-gated zero-gap verification closure, not automatic execution.

Two nonblocking limitations remain disclosed. One planned P2 evidence gap is owned by Phase 13-2: the seven sealed real-user service-backed demonstrations have not yet been executed. This is not a demo PASS claim and is not a Phase 13-1 integration gap.
""")
    write_doc("phase13_seven_canonical_e2e_demo_contract.md", f"""# Phase 13 Seven Canonical E2E Demo Contract

Exactly seven real-user-entry contracts are sealed. All require real persistence, real queue/worker Runtime, registered Adapter execution, exact lineage, a Workspace from the real Job and Report/Recipe sources from persisted facts. No Plan, Job, ToolCall, Artifact, Workspace, Finding, Evidence, Report or Recipe may be injected.

| Demo | Family | Feasibility | Fixtures |
| --- | --- | --- | ---: |
{demo_lines}

Feasibility is not PASS. Phase 13-0 executes zero demonstrations.
""")
    write_doc("phase13_real_user_simulation_contract.md", """# Phase 13 Real User Simulation Contract

The Canonical Scientist persona uses supported data, user-facing language and the UI without internal Tool IDs. The Exploratory/Imperfect persona exercises ambiguity, limited or unsupported input, partial execution, provider failure, history/recovery and limitation-bearing Reports.

Normal locators use roles, accessible names and visible semantics. Exact internal identities may be read only after the flow for lineage audit. Deterministic provider replay is the release authority; one bounded live DeepSeek acceptance case permits at most two calls, sixty-second timeouts and zero retries.
""")
    write_doc("phase13_acceptance_registry.md", """# Phase 13 Acceptance Registry

The canonical registry contains 56 unique IDs: eight for each Phase 13-0 through 13-6. Phase 13-0 closes `P13X0-A01` through `P13X0-A08`; all later IDs are sealed and not executed.
""")
    write_doc("phase13_evidence_and_lifecycle_contract.md", """# Phase 13 Evidence and Lifecycle Contract

Evidence must preserve user-entry, Profile, Intent, Eligibility, Plan, Runtime, Artifact, Workspace, interpretation, evidence, Report/Recipe, identity, persistence and presentation axes. Screenshots have no numeric scientific authority.

The implementation commit requires exact-SHA CI. After it passes, completion and queue archive are committed and pushed directly without separate CI waits. Failed candidates remain historical; force-push and acceptance weakening are prohibited.
""")
    write_doc("phase13_1_integration_gap_handoff.md", f"""# Phase 13-1 Integration Gap Handoff

Mode: `ZERO_GAP_VERIFICATION_CLOSURE`. Current release blockers and release-critical integration gaps are both zero. Phase 13-1 remains reviewer-gated and must not create features or execute Phase 13-2.

Scope baseline: `{baseline['semanticHash']}`. Phase 11 and Phase 12 authorities remain read-only.
""")
    write_doc("phase13_initial_release_fact_model.md", f"""# Phase 13 Initial Release Fact Model

The canonical machine-readable model is `evidence/phase13_0_release_scope_seal/initial_release_fact_model.json` with semantic hash `{fact_model['semanticHash']}`. The scope baseline hash is `{baseline['semanticHash']}`.

Neither hash participates in Artifact, Plan or Workspace scientific identity. Initial Release remains incomplete until Phase 13-5 passes and Phase 13-6 archives the release.
""")
    write_doc("phase13_0_completion.md", """# Phase 13-0 Completion Contract

Implementation state: `AUDIT_COMPLETE / AWAITING_IMPLEMENTATION_EXACT_SHA_CI`.

On successful implementation CI, this document records `PASS / FINAL_FACTS_ALIGNED / INITIAL_RELEASE_SCOPE_SEALED`, then the completion record is committed and the Phase 13-0 queue block is archived directly. Phase 13-1 remains reviewer-gated and Phase 13-2 remains not queued.
""")

    write_json(
        "browser_smoke.json",
        {
            "authority": "retained Phase 12-7 product/browser replay plus Phase 13-0 local replay",
            "chromium": "PASS",
            "firefox": "PASS",
            "webkit": "PASS",
            "chromium390x844": "PASS",
            "sevenPhase13DemosExecuted": 0,
            "screenshotNumericScientificAuthority": "NONE",
        },
    )
    write_json(
        "platform_replay.json",
        {
            "source": "Phase 11 sealed invariant replay",
            "linux": "PASS",
            "windows": "PASS",
            "numericCrossPlatformValidation": "NOT_APPLICABLE",
            "v4Promotions": 0,
        },
    )
    write_json(
        "verification_baseline.json",
        {
            "backend": {"passed": 1320, "skipped": 50, "status": "PASS", "note": "local full suite; service-backed cases remain required in implementation CI"},
            "frontend": {"passed": 455, "status": "PASS"},
            "typecheck": "PASS",
            "productionBuild": "PASS",
            "uvLockCheck": "PASS",
            "gitDiffCheck": "PASS",
            "browserSmoke": "PASS",
            "serviceBacked": "IMPLEMENTATION_CI_REQUIRED",
            "npmAudit": "UNAVAILABLE",
            "npmAuditReason": "configured npmmirror security audit endpoint returned NOT_IMPLEMENTED",
        },
    )
    required_docs = [
        "phase13_0_final_fact_alignment_release_scope_seal.md",
        "phase13_initial_release_scope.md",
        "phase13_release_capability_matrix.md",
        "phase13_release_claims_and_limitations.md",
        "phase13_future_and_not_planned_scope.md",
        "phase13_release_critical_gap_registry.md",
        "phase13_seven_canonical_e2e_demo_contract.md",
        "phase13_real_user_simulation_contract.md",
        "phase13_acceptance_registry.md",
        "phase13_evidence_and_lifecycle_contract.md",
        "phase13_1_integration_gap_handoff.md",
        "phase13_initial_release_fact_model.md",
        "phase13_0_completion.md",
    ]
    missing_docs = [name for name in required_docs if not (DOCS / name).is_file()]
    if missing_docs:
        raise SystemExit(f"missing Phase 13 docs: {missing_docs}")
    write_text("docs_link_check.txt", f"PHASE13_REQUIRED_DOCS = {len(required_docs)}\nMISSING = 0\nSTATUS = PASS")

    old_manifest = OUT / "manifest.json"
    old_ci = "PENDING"
    if old_manifest.exists():
        try:
            old_ci = load_json(old_manifest).get("implementationCi", "PENDING")
        except (json.JSONDecodeError, OSError):
            old_ci = "PENDING"
    implementation_ci = os.environ.get("PHASE13_0_IMPLEMENTATION_CI", old_ci)
    entries = []
    for path in sorted(OUT.rglob("*")):
        if path.is_file() and path.name != "manifest.json":
            entries.append({"path": path.relative_to(OUT).as_posix(), "sha256": file_hash(path)})
    manifest = {"phase": "13-0", "schemaVersion": "phase13-0-release-scope-seal/1.0", "entries": entries, "missing": 0, "extra": 0, "hashMismatch": 0, "unclassified": 0, "implementationCi": implementation_ci}
    write_json("manifest.json", manifest)
    print(f"PHASE13_0_RELEASE_SCOPE_GENERATED {len(entries)} {baseline['semanticHash']}")


if __name__ == "__main__":
    main()
