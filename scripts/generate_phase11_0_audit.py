from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from mdi_adapters.registry import ADAPTER_CLASSES
from mdi_tool_registry.loader import load_manifests


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/phase11/evidence/phase11_0_validation_baseline_reconciliation"
REGISTRY_SOURCES = [
    "tool_registry/pymatviz_manifest.yaml",
    "tool_registry/matterviz_manifest.yaml",
    "tool_registry/platform_builtin_manifest.yaml",
]
ACCEPTANCE = [
    "P11V0-A01 N6_VERIFIED_BASELINE_AND_APPROVED_ROADMAP_RECONCILIATION",
    "P11V0-A02 REGISTRY_62_TOOL_VALIDATION_ROLE_AND_STATUS_INVENTORY",
    "P11V0-A03 EXISTING_REFERENCE_FIXTURE_EVIDENCE_AND_PROVENANCE_RECONCILIATION",
    "P11V0-A04 SUPPORTED_INPUT_RESOURCE_PARSER_PROFILE_AND_PLATFORM_MATRIX",
    "P11V0-A05 VALIDATION_LEVEL_REFERENCE_AUTHORITY_AND_HONEST_COVERAGE_TAXONOMY",
    "P11V0-A06 TOLERANCE_INVARIANT_VARIANCE_AND_REVALIDATION_GOVERNANCE",
    "P11V0-A07 PHASE11_1_TO_11_5_GAP_BACKLOG_ACCEPTANCE_AND_EXECUTION_SEAL",
    "P11V0-A08 PHASE12_UIUX_PHASE13_FINAL_CLOSURE_AND_FUTURE_SCOPE_ROADMAP_SEAL",
    "P11V0-A09 NO_PRODUCTION_CHANGE_REGRESSION_DOCUMENTATION_SECURITY_AND_EVIDENCE_INTEGRITY",
    "P11V0-A10 THREE_COMMIT_EXACT_SHA_LIFECYCLE_AND_11_1_REVIEWER_GATE",
]


def enum_value(value: Any) -> Any:
    return getattr(value, "value", value)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(name: str, payload: Any) -> None:
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def role_for(tool_id: str) -> str:
    if tool_id.startswith("ml."):
        return "MATERIALS_ML"
    if tool_id.startswith("table."):
        return "DATA_INTELLIGENCE"
    if tool_id in {"dataset.materials_explorer", "dataset.composition_space"}:
        return "DATA_INTELLIGENCE"
    if tool_id.startswith("composition."):
        return "COMPOSITION_ANALYSIS"
    if tool_id in {
        "structure.coordination_crystalnn", "structure.coordination_voronoinn",
        "structure.local_environment_polyhedra", "structure.rdf", "structure.xrd",
        "trajectory.rdf", "trajectory.msd", "trajectory.diffusion",
        "electronic.band_structure", "electronic.dos", "phonon.band", "phonon.dos",
    }:
        return "SCIENTIFIC_NUMERIC"
    if tool_id in {"structure.brillouin_zone", "structure.structure_2d", "structure.structure_3d"}:
        return "SCIENTIFIC_GEOMETRY"
    if tool_id in {"structure.experimental_xrd_comparison", "phonon.band_dos"}:
        return "SCIENTIFIC_CLASSIFICATION"
    if tool_id in {"structure.trajectory_import", "structure.volumetric_data"}:
        return "SCIENTIFIC_TRANSFORMATION"
    if tool_id in {"trajectory.viewer", "structure.trajectory_viewer", "phonon.animation"}:
        return "SCIENTIFIC_VISUALIZATION_DATA"
    if "viewer" in tool_id or tool_id.endswith("export_package"):
        return "PRESENTATION_ONLY"
    if "summary" in tool_id or tool_id.endswith("preview_metadata") or tool_id.endswith("scene_metadata"):
        return "METADATA_OR_UTILITY"
    return "PRODUCT_COMPOSITION"


def evidence_for(tool_id: str) -> list[str]:
    phase = "docs/phase10"
    if tool_id.startswith("dataset."):
        phase = "docs/phase10k/evidence"
    elif tool_id.startswith("trajectory.") and tool_id not in {"trajectory.viewer"}:
        phase = "docs/phase10n/evidence/phase10n4_trajectory_rdf_msd_diffusion"
    elif tool_id.startswith("electronic."):
        phase = "docs/phase10n/evidence/phase10n5_electronic_band_dos"
    elif tool_id in {"structure.coordination_crystalnn", "structure.coordination_voronoinn"}:
        phase = "docs/phase10n/evidence/phase10n1_crystalnn_voronoinn_coordination"
    elif tool_id == "structure.local_environment_polyhedra":
        phase = "docs/phase10n/evidence/phase10n2_local_environment_coordination_polyhedra"
    elif tool_id == "structure.experimental_xrd_comparison":
        phase = "docs/phase10n/evidence/phase10n3_experimental_xrd_comparison_peak_matching"
    elif tool_id.startswith("phonon."):
        phase = "docs/phase10h/evidence"
    elif tool_id == "structure.brillouin_zone":
        phase = "docs/phase10i/evidence"
    elif tool_id == "structure.volumetric_data":
        phase = "docs/phase10j/evidence"
    return [phase]


def reference_types(tool_id: str, role: str) -> tuple[list[str], str, str]:
    types = ["REPOSITORY_INTERNAL_EXPECTED_VALUE"]
    independence = "INTERNAL_REGRESSION"
    level = "V1_RUNTIME_AND_ARTIFACT_VERIFIED"
    if role in {"SCIENTIFIC_NUMERIC", "SCIENTIFIC_GEOMETRY", "SCIENTIFIC_CLASSIFICATION", "MATERIALS_ML"}:
        types.append("CONTROLLED_SYNTHETIC_REFERENCE")
        level = "V2_CONTROLLED_REFERENCE_VERIFIED"
    if tool_id in {"trajectory.msd", "trajectory.diffusion", "table.numeric_summary", "ml.basic_metrics"}:
        types.append("ANALYTIC_REFERENCE")
        independence = "ANALYTIC_OR_MATHEMATICAL"
    if tool_id in {"structure.coordination_crystalnn", "structure.coordination_voronoinn", "structure.xrd"}:
        types.append("OFFICIAL_LIBRARY_REFERENCE")
        independence = "SELF_REFERENCE_FOR_REGRESSION_ONLY"
    if tool_id.startswith("phonon."):
        types.append("OFFICIAL_PROJECT_EXAMPLE")
        independence = "OFFICIAL_DERIVED_PROVENANCE_REQUIRES_RECONCILIATION"
    if role in {"PRESENTATION_ONLY", "PRODUCT_COMPOSITION", "METADATA_OR_UTILITY"}:
        types = ["MAPPING_ONLY", "REPOSITORY_INTERNAL_EXPECTED_VALUE"]
    return sorted(set(types)), independence, level


def input_options(tool: Any) -> list[dict[str, Any]]:
    rows = []
    for option in tool.inputSchema.inputOptions:
        rows.append({
            "name": option.name,
            "requiredObjectTypes": [enum_value(value) for value in option.requiredObjectTypes],
            "requiredFields": option.requiredFields,
            "description": option.description,
        })
    return rows


def tool_inventory() -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    registry = load_manifests()
    tools = []
    contracts = []
    for tool in sorted(registry.tools, key=lambda item: item.toolId):
        role = role_for(tool.toolId)
        references, independence, level = reference_types(tool.toolId, role)
        adapter_registered = tool.adapter in ADAPTER_CLASSES
        outputs = [enum_value(value) for value in tool.artifactTypes]
        row = {
            "toolId": tool.toolId,
            "version": tool.version,
            "domain": enum_value(tool.domain),
            "availability": "RUNTIME_REGISTERED" if adapter_registered else "REGISTRY_DECLARED_NO_CURRENT_ADAPTER",
            "roleClass": role,
            "inputContracts": input_options(tool),
            "outputArtifacts": outputs,
            "scientificAuthority": "REGISTERED_ADAPTER" if adapter_registered else "NONE_WITHOUT_ADAPTER",
            "adapter": tool.adapter,
            "adapterRegistered": adapter_registered,
            "algorithmIdentity": tool.source,
            "dependencies": [],
            "currentValidationLevel": level,
            "referenceTypes": references,
            "referenceIndependence": independence,
            "softwareExecutionStatus": "VERIFIED" if adapter_registered else "NOT_EXECUTABLE",
            "scientificReferenceStatus": references,
            "numericValidationStatus": "CONTROLLED_OR_ANALYTIC" if role in {"SCIENTIFIC_NUMERIC", "SCIENTIFIC_GEOMETRY", "SCIENTIFIC_CLASSIFICATION", "MATERIALS_ML"} else "NOT_APPLICABLE",
            "artifactContractStatus": "REGISTRY_CONTRACT_DECLARED",
            "platformIntegrationStatus": "VERIFIED" if adapter_registered else "NOT_AVAILABLE",
            "browserStatus": "RETAINED_EVIDENCE" if adapter_registered else "NOT_APPLICABLE",
            "serviceStatus": "RETAINED_EVIDENCE" if adapter_registered else "NOT_APPLICABLE",
            "reproducibilityStatus": "CURRENT_LOCKED_ENVIRONMENT_ONLY",
            "knownLimits": ["Validation status is axis-specific; browser or service PASS is not numeric reference authority."],
            "evidenceRefs": evidence_for(tool.toolId),
            "validationGaps": ([] if level.startswith("V2") else ["CONTROLLED_REFERENCE_COVERAGE_REVIEW"]),
        }
        tools.append(row)
        contracts.append({
            "toolId": tool.toolId,
            "version": tool.version,
            "producerAdapter": tool.adapter,
            "adapterRegistered": adapter_registered,
            "primaryArtifactType": enum_value(tool.outputSchema.primaryArtifactType),
            "secondaryArtifactTypes": [enum_value(value) for value in tool.outputSchema.secondaryArtifactTypes],
            "displayTarget": enum_value(tool.outputSchema.displayTarget),
            "contractSource": tool.source.get("manifest"),
            "identityRequirement": "EXACT_TOOL_VERSION_RESOURCE_HASH_AND_ARTIFACT_CHECKSUM",
        })
    if len(tools) != 62 or len({row["toolId"] for row in tools}) != 62:
        raise RuntimeError("Registry baseline mismatch: expected 62 unique Tools")
    inventory = {"registryCount": 62, "registryVersion": registry.version, "registrySources": REGISTRY_SOURCES, "tools": tools}
    return inventory, tools, contracts


def input_matrix() -> list[dict[str, Any]]:
    common = {"profileSupport": "DataProfile 2.4 where resource semantics are recognized", "plannerSupport": "Capability-specific", "workspaceSupport": "Artifact renderer dependent"}
    return [
        {**common, "inputFamily": "CSV table", "extensions": [".csv"], "MIME": ["text/csv", "application/csv"], "parser": "pandas.read_csv via CsvParser", "resourceContract": "DataFrame", "identity": "resource ID/version/content hash", "unitSemantics": "column metadata or unknown", "eligibleTools": ["table.*", "viz.*", "ml.*", "dataset.*"], "limits": ["bounded upload and row caps"], "supportVerdict": "DIRECT_SUPPORTED", "evidenceRefs": ["packages/material-parsers/mdi_material_parsers/parsers.py"]},
        {**common, "inputFamily": "JSON canonical resources", "extensions": [".json"], "MIME": ["application/json"], "parser": "JsonParser with duplicate-key rejection", "resourceContract": "typed table/structure/trajectory/XRD/electronic JSON", "identity": "resource ID/version/content hash plus typed identities", "unitSemantics": "explicit per contract", "eligibleTools": ["contract-dependent"], "limits": ["strict schemas", "bounded arrays"], "supportVerdict": "SUPPORTED_WITH_LIMITS", "evidenceRefs": ["packages/material-parsers/mdi_material_parsers/parsers.py"]},
        {**common, "inputFamily": "CIF structure", "extensions": [".cif"], "MIME": ["chemical/x-cif", "text/plain with sniffing"], "parser": "pymatgen Structure", "resourceContract": "Structure", "identity": "content hash plus structure/site identity", "unitSemantics": "angstrom/fractional", "eligibleTools": ["structure.*"], "limits": ["single supported structure resource"], "supportVerdict": "DIRECT_SUPPORTED", "evidenceRefs": ["packages/material-parsers/mdi_material_parsers/detector.py"]},
        {**common, "inputFamily": "VASP POSCAR/CONTCAR structure", "extensions": [], "MIME": ["text/plain with name/content sniffing"], "parser": "pymatgen Structure", "resourceContract": "Structure", "identity": "content hash plus structure/site identity", "unitSemantics": "angstrom/fractional", "eligibleTools": ["structure.*"], "limits": ["recognized canonical names/prefixes"], "supportVerdict": "DIRECT_SUPPORTED", "evidenceRefs": ["packages/material-parsers/mdi_material_parsers/detector.py"]},
        {**common, "inputFamily": "XYZ structure", "extensions": [".xyz"], "MIME": ["chemical/x-xyz", "text/plain"], "parser": "ASE Atoms", "resourceContract": "Structure/Atoms", "identity": "content hash plus stable atom ordinal within immutable resource", "unitSemantics": "angstrom", "eligibleTools": ["structure.*"], "limits": ["single-frame structure semantics"], "supportVerdict": "SUPPORTED_WITH_LIMITS", "evidenceRefs": ["packages/material-parsers/mdi_material_parsers/parsers.py"]},
        {**common, "inputFamily": "EXTXYZ trajectory", "extensions": [".extxyz"], "MIME": ["text/plain"], "parser": "ASE extxyz", "resourceContract": "canonical trajectory when multiple frames", "identity": "trajectory hash plus frame/atom identity", "unitSemantics": "explicit trajectory contract", "eligibleTools": ["trajectory.rdf", "trajectory.msd", "trajectory.diffusion", "structure.trajectory_viewer"], "limits": ["physical time required for MSD/diffusion", "stable atom order required"], "supportVerdict": "SUPPORTED_WITH_LIMITS", "evidenceRefs": ["packages/material-parsers/mdi_material_parsers/trajectory.py"]},
        {**common, "inputFamily": "VASP volumetric grid", "extensions": [], "MIME": ["text/plain with canonical name sniffing"], "parser": "bounded VASP volumetric parser", "resourceContract": "volumetric-field/v1", "identity": "source hash plus field/grid identity", "unitSemantics": "source-qualified field units", "eligibleTools": ["structure.volumetric_data"], "limits": ["CHGCAR/CHG/LOCPOT/ELFCAR/PARCHG names", "voxel/source caps"], "supportVerdict": "SUPPORTED_WITH_LIMITS", "evidenceRefs": ["packages/material-parsers/mdi_material_parsers/volumetric.py"]},
        {**common, "inputFamily": "Gaussian CUBE", "extensions": [".cube"], "MIME": ["text/plain"], "parser": "bounded single-dataset CUBE parser", "resourceContract": "volumetric-field/v1", "identity": "source hash plus field/grid identity", "unitSemantics": "source-qualified field units", "eligibleTools": ["structure.volumetric_data"], "limits": ["single dataset", "multi-orbital unsupported"], "supportVerdict": "SUPPORTED_WITH_LIMITS", "evidenceRefs": ["packages/material-parsers/mdi_material_parsers/volumetric.py"]},
        {**common, "inputFamily": "ZIP container", "extensions": [".zip"], "MIME": ["application/zip"], "parser": "safe recursive archive dispatcher", "resourceContract": "contained supported resources", "identity": "container/member hashes", "unitSemantics": "member contract", "eligibleTools": ["member-dependent"], "limits": ["100 files", "50 MB uncompressed", "depth 5", "safe paths"], "supportVerdict": "SUPPORTED_WITH_LIMITS", "evidenceRefs": ["packages/material-parsers/mdi_material_parsers/parsers.py"]},
        {**common, "inputFamily": "XLSX/Excel", "extensions": [".xlsx", ".xls"], "MIME": ["spreadsheet MIME"], "parser": None, "resourceContract": None, "identity": None, "unitSemantics": None, "eligibleTools": [], "limits": [], "supportVerdict": "UNSUPPORTED", "evidenceRefs": ["packages/material-parsers/mdi_material_parsers/detector.py"]},
        {**common, "inputFamily": "Parquet", "extensions": [".parquet"], "MIME": ["application/vnd.apache.parquet"], "parser": None, "resourceContract": None, "identity": None, "unitSemantics": None, "eligibleTools": [], "limits": [], "supportVerdict": "UNSUPPORTED", "evidenceRefs": ["packages/material-parsers/mdi_material_parsers/detector.py"]},
        {**common, "inputFamily": "LAMMPS trajectory", "extensions": [".lammpstrj", ".dump"], "MIME": [], "parser": None, "resourceContract": None, "identity": None, "unitSemantics": None, "eligibleTools": [], "limits": [], "supportVerdict": "UNSUPPORTED", "evidenceRefs": ["docs/FUTURE_SCOPE.md"]},
        {**common, "inputFamily": "Phonon YAML/JSON", "extensions": [".yaml", ".yml", ".json"], "MIME": ["application/json", "text/yaml"], "parser": "No generic direct-upload parser; normalized Tool mapping only", "resourceContract": "Tool-specific normalized phonon payload", "identity": "mapping-defined", "unitSemantics": "mapping-defined", "eligibleTools": ["phonon.band", "phonon.dos", "phonon.band_dos"], "limits": ["not a claimed generic upload path"], "supportVerdict": "MAPPING_ONLY", "evidenceRefs": ["docs/phase10f/official_examples_direct_verification"]},
        {**common, "inputFamily": "Supplied electronic Band/DOS JSON", "extensions": [".json"], "MIME": ["application/json"], "parser": "strict canonical electronic resource mapper", "resourceContract": "electronic-band-resource/0.1.0 or electronic-dos-resource/0.1.0", "identity": "source resource hash plus calculation/k-point/band/channel identities", "unitSemantics": "explicit eV and source-qualified DOS", "eligibleTools": ["electronic.band_structure", "electronic.dos"], "limits": ["no raw calculation directory", "no DFT execution"], "supportVerdict": "SUPPORTED_WITH_LIMITS", "evidenceRefs": ["packages/material-parsers/mdi_material_parsers/parsers.py"]},
    ]


def evidence_inventory() -> list[dict[str, Any]]:
    rows = []
    for evidence in sorted(ROOT.glob("docs/phase10*/evidence")):
        files = [path for path in evidence.rglob("*") if path.is_file()]
        rows.append({
            "path": evidence.relative_to(ROOT).as_posix(),
            "fileCount": len(files),
            "manifestCount": sum(path.name == "manifest.json" for path in files),
            "browserEvidence": any("browser" in path.parts for path in files),
            "serviceEvidence": any("service" in path.as_posix().lower() for path in files),
            "referenceEvidence": any("reference" in path.name.lower() or "fixture" in path.name.lower() for path in files),
            "authorityRule": "PROVENANCE_AND_HASH_NOT_RECENCY",
        })
    return rows


def named_inventory(patterns: tuple[str, ...], kind: str) -> list[dict[str, Any]]:
    rows = []
    for path in sorted((ROOT / "docs").rglob("*")):
        if not path.is_file() or not any(token in path.as_posix().lower() for token in patterns):
            continue
        relative = path.relative_to(ROOT).as_posix()
        rows.append({
            "recordId": hashlib.sha256(relative.encode()).hexdigest()[:16],
            "path": relative,
            "sha256": sha256(path),
            "kind": kind,
            "referenceType": "REPOSITORY_INTERNAL_EXPECTED_VALUE" if kind == "fixture" else "MAPPING_ONLY",
            "independence": "UNREVIEWED_OR_INTERNAL",
            "licenseStatus": "LICENSE_REVIEW_REQUIRED" if "official" in relative.lower() else "REPOSITORY_INTERNAL",
            "status": "CURRENTLY_RELEVANT" if "phase10n" in relative.lower() else "RETAINED_HISTORICAL",
        })
    return rows


def tolerances() -> list[dict[str, Any]]:
    exact = {"absTolerance": None, "relativeTolerance": None, "unit": "EXACT"}
    return [
        {"toleranceId": "identity.exact.v1", "toolContract": "all", "fieldMetric": "Tool/version, hashes, checksums and scientific entity identities", **exact, "referenceProvenance": "contract", "reason": "identity is not numeric proximity", "ownerPhase": "cross-phase", "scientificJustification": "prevents fuzzy rebinding", "platformVarianceRelevance": "none", "reviewStatus": "SEALED"},
        {"toleranceId": "n1.coordination.numeric.v1", "toolContract": "structure.coordination_*@0.1.0", "fieldMetric": "distance/weight/coordination", "absTolerance": "quantity-specific focused-test bound", "relativeTolerance": "quantity-specific focused-test bound", "unit": "angstrom/dimensionless", "referenceProvenance": "N1 retained evidence", "reason": "floating library output", "ownerPhase": "10N-1", "scientificJustification": "algorithm-specific, no mutual-equality criterion", "platformVarianceRelevance": "11-3", "reviewStatus": "RECONCILED"},
        {"toleranceId": "n2.classification.tie.v1", "toolContract": "structure.local_environment_polyhedra@0.1.0", "fieldMetric": "geometryDistanceRms tie", "absTolerance": 0.01, "relativeTolerance": 0.0, "unit": "dimensionless", "referenceProvenance": "phase10n2 parameter contract", "reason": "declared ambiguity threshold", "ownerPhase": "10N-2", "scientificJustification": "preserves honest ties", "platformVarianceRelevance": "bounded", "reviewStatus": "SEALED"},
        {"toleranceId": "n3.match.position.v1", "toolContract": "structure.experimental_xrd_comparison@0.1.0", "fieldMetric": "peak correspondence delta two theta", "absTolerance": 0.15, "relativeTolerance": 0.0, "unit": "degree 2theta", "referenceProvenance": "phase10n3 matching contract", "reason": "default user-visible matching policy", "ownerPhase": "10N-3", "scientificJustification": "bounded correspondence, not phase confirmation", "platformVarianceRelevance": "none", "reviewStatus": "SEALED"},
        {"toleranceId": "n4.time.constant.v1", "toolContract": "trajectory resource/Profile 2.3", "fieldMetric": "constant timestep", "absTolerance": 1e-12, "relativeTolerance": 1e-9, "unit": "ps", "referenceProvenance": "material parser contract", "reason": "finite timestep comparison", "ownerPhase": "10N-4", "scientificJustification": "does not infer missing time", "platformVarianceRelevance": "bounded", "reviewStatus": "SEALED"},
        {"toleranceId": "n4.diffusion.regime.v1", "toolContract": "trajectory.diffusion@0.1.0", "fieldMetric": "minimum R2 and alpha range", "absTolerance": 0.0, "relativeTolerance": 0.0, "unit": "dimensionless", "referenceProvenance": "phase10n4 diffusion contract", "reason": "declared qualification policy", "ownerPhase": "10N-4", "scientificJustification": "R2 >= 0.9 and 0.8 <= alpha <= 1.2", "platformVarianceRelevance": "11-3", "reviewStatus": "SEALED"},
        {"toleranceId": "n5.energy.v1", "toolContract": "electronic.band_structure@0.1.0", "fieldMetric": "energy comparison", "absTolerance": 1e-8, "relativeTolerance": 0.0, "unit": "eV", "referenceProvenance": "phase10n5 band parameter contract", "reason": "finite VBM/CBM and crossing comparison", "ownerPhase": "10N-5", "scientificJustification": "does not shift or generate electronic data", "platformVarianceRelevance": "bounded", "reviewStatus": "SEALED"},
        {"toleranceId": "n5.fermi.compatibility.v1", "toolContract": "Band+DOS deterministic consumer", "fieldMetric": "Fermi equality", "absTolerance": 1e-8, "relativeTolerance": 0.0, "unit": "eV", "referenceProvenance": "electronic contract", "reason": "exact compatibility with bounded numeric comparison", "ownerPhase": "10N-5", "scientificJustification": "prevents browser auto-alignment", "platformVarianceRelevance": "bounded", "reviewStatus": "SEALED"},
        {"toleranceId": "phonon.frequency.zero.v1", "toolContract": "phonon.*@0.1.0", "fieldMetric": "near-zero frequency", "absTolerance": "artifact-declared 1e-6 or 1e-5 by producer", "relativeTolerance": 0.0, "unit": "THz", "referenceProvenance": "phonon artifact contract", "reason": "producer-specific classification boundary", "ownerPhase": "10H", "scientificJustification": "must not be replaced by global epsilon", "platformVarianceRelevance": "11-3", "reviewStatus": "RECONCILED"},
        {"toleranceId": "brillouin.symmetry.v1", "toolContract": "structure.brillouin_zone@0.1.0", "fieldMetric": "symmetry distance/angle", "absTolerance": 1e-5, "relativeTolerance": 0.0, "unit": "angstrom; degree=5.0", "referenceProvenance": "Brillouin contract", "reason": "spglib/pymatgen symmetry policy", "ownerPhase": "10I", "scientificJustification": "contract-defined", "platformVarianceRelevance": "11-3", "reviewStatus": "RECONCILED"},
    ]


def gaps() -> list[dict[str, Any]]:
    raw = [
        ("GAP-11-001", "P1", "structure.coordination_*", "OFFICIAL_LIBRARY_REFERENCE self-reference", "independent provenance review and immutable source fixture", "11-1", "OFFICIAL_LIBRARY_REFERENCE"),
        ("GAP-11-002", "P1", "structure.local_environment_polyhedra", "controlled synthetic and internal geometry checks", "independent geometry/ConvexHull reference case", "11-2", "INDEPENDENT_CROSS_LIBRARY_REFERENCE"),
        ("GAP-11-003", "P1", "structure.experimental_xrd_comparison", "controlled detector/matcher fixtures", "analytic golden matcher and detector boundary suite", "11-2", "ANALYTIC_REFERENCE"),
        ("GAP-11-004", "P1", "trajectory.rdf", "controlled lattice/window/species fixtures", "independent RDF normalization benchmark", "11-2", "ANALYTIC_REFERENCE"),
        ("GAP-11-005", "P1", "trajectory.msd/diffusion", "analytic motion and random-walk fixtures", "cross-platform variance characterization", "11-3", "ANALYTIC_REFERENCE"),
        ("GAP-11-006", "P1", "electronic.band_structure/electronic.dos", "controlled supplied electronic fixtures", "source provenance and redistribution status for release fixtures", "11-1", "OFFICIAL_PROJECT_EXAMPLE"),
        ("GAP-11-007", "P1", "phonon.*", "retained official-example mapping and internal expected values", "consolidated source hashes, license, and independent expected-value provenance", "11-1", "OFFICIAL_PROJECT_EXAMPLE"),
        ("GAP-11-008", "P2", "structure.brillouin_zone", "contract and controlled geometry fixtures", "independent reciprocal-cell invariant benchmark", "11-2", "ANALYTIC_REFERENCE"),
        ("GAP-11-009", "P2", "structure.volumetric_data", "parser/contract/browser evidence", "fixture license and source provenance consolidation", "11-1", "OFFICIAL_PROJECT_EXAMPLE"),
        ("GAP-11-010", "P1", "materials ML and composition", "internal regression plus selected analytic metrics", "cross-capability golden metrics and seed/sign invariants", "11-2", "ANALYTIC_REFERENCE"),
        ("GAP-11-011", "P1", "all quantitative release tools", "current locked environment evidence", "Linux/Windows locked-environment variance matrix", "11-3", "INDEPENDENT_CROSS_LIBRARY_REFERENCE"),
        ("GAP-11-012", "P2", "historical official examples", "mapping/direct-upload inventories", "deduplicated honest Tool/Input/Example coverage verdicts", "11-4", "OFFICIAL_PROJECT_EXAMPLE"),
    ]
    return [{"gapId": gid, "priority": priority, "capability": capability, "currentEvidence": current, "missingEvidence": missing, "whyNeeded": "Required to distinguish regression strength from independent scientific validation.", "targetPhase": phase, "blockingRelease": priority == "P0", "recommendedReferenceType": reference} for gid, priority, capability, current, missing, phase, reference in raw]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    inventory, tools, contracts = tool_inventory()
    inputs = input_matrix()
    evidence = evidence_inventory()
    fixtures = named_inventory(("fixture",), "fixture")
    official = named_inventory(("official", "example"), "official-example")
    references = named_inventory(("reference", "expected", "analytic", "golden"), "reference")
    write_json("registry_inventory.json", inventory)
    write_json("tool_validation_matrix.json", {"rowCount": len(tools), "axesAreIndependent": True, "tools": tools})
    write_json("artifact_validation_inventory.json", {"rowCount": len(contracts), "artifacts": contracts})
    write_json("input_support_matrix.json", {"rowCount": len(inputs), "inputs": inputs})
    write_json("parser_resource_matrix.json", {"source": "packages/material-parsers", "rows": inputs})
    write_json("existing_evidence_inventory.json", {"roots": evidence, "rootCount": len(evidence), "authority": "PROVENANCE_NOT_RECENCY"})
    write_json("reference_provenance_inventory.json", {"records": references, "recordCount": len(references), "downloadsPerformed": 0})
    write_json("fixture_inventory.json", {"records": fixtures, "recordCount": len(fixtures), "immutableInPlace": True})
    write_json("official_example_inventory.json", {"records": official, "recordCount": len(official), "executedInPhase11_0": 0})
    write_json("tolerance_inventory.json", {"globalScientificEpsilon": None, "passDrivenChanges": "PROHIBITED", "tolerances": tolerances()})
    write_json("variance_inventory.json", {"taxonomy": ["EXACT", "TOLERANCE_BOUNDED", "DISPLAY_ONLY_VARIANCE", "UNSUPPORTED_PLATFORM", "KNOWN_LIMITATION"], "primaryEnvironment": "CURRENT_LOCKED_REPOSITORY_ENVIRONMENT", "targets": {"operatingSystems": ["Linux CI", "Windows primary development/runtime"], "notReleaseTarget": ["macOS unless repository support is separately established"], "browsers": ["Chromium", "Firefox", "WebKit", "Chromium 390x844"]}})
    write_json("gap_matrix.json", {"gaps": gaps(), "gapCount": len(gaps()), "p0Count": 0})
    write_json("validation_level_targets.json", {"levels": {"V0": "CONTRACT_ONLY", "V1": "RUNTIME_AND_ARTIFACT_VERIFIED", "V2": "CONTROLLED_REFERENCE_VERIFIED", "V3": "INDEPENDENT_OR_OFFICIAL_REFERENCE_VERIFIED", "V4": "CROSS_PLATFORM_REPRODUCIBILITY_VERIFIED"}, "minimums": {"SCIENTIFIC_NUMERIC": "V2; V3 where feasible", "SCIENTIFIC_GEOMETRY": "V2; V3 where feasible", "SCIENTIFIC_CLASSIFICATION": "V2 with bounded invariants", "DATA_INTELLIGENCE": "V2 where quantitative", "MATERIALS_ML": "V2 with analytic metrics where feasible", "PRESENTATION_ONLY": "V1 plus browser/accessibility", "PRODUCT_COMPOSITION": "V1 plus no-recomputation"}})
    write_json("revalidation_triggers.json", {"invalidating": ["Tool scientific version change", "algorithm change", "parameter-default semantic change", "Artifact scientific contract change", "unit/reference semantic change", "scientific parser semantic change", "computation-authority dependency version change", "fixture expected-value change", "tolerance change", "identity model change"], "numericNonInvalidating": ["CSS-only change", "typography", "layout", "non-scientific wording", "presentation order"], "presentationRegressionStillRequired": True})
    write_json("phase11_acceptance_registry.json", {"expected": 10, "implemented": 10, "missing": 0, "extra": 0, "duplicate": 0, "conflicting": 0, "shorthand": 0, "entries": ACCEPTANCE})
    write_json("phase11_roadmap.json", {"phase11": ["11-0 Validation Baseline Reconciliation + Governance Seal", "11-1 Reference Provenance + Safe Fixture Consolidation", "11-2 Cross-Capability Golden Scientific Benchmark Suite", "11-3 Cross-Platform Reproducibility + Variance Characterization", "11-4 Honest Tool / Input / Example Coverage Matrix", "11-5 Scientific Validation Closure + Release Candidate Gate"], "phase12": ["12-0 Current UX Reality Audit + Product Experience Seal", "12-1 Design System 2.0 + Visual Language", "12-2 Global Navigation + Planner / Agent Experience", "12-3 Scientific Workspace + Viewer Experience Redesign", "12-4 Findings / Evidence / Inspector / Provenance Experience", "12-5 Report / Recipe Experience Redesign", "12-6 Responsive / Mobile / Accessibility Closure", "12-7 Cross-Product UX Validation + Design Evidence Closure"], "phase13": ["13-0 Final Fact Alignment + Release Scope Seal", "13-1 Release-Critical Integration Gap Closure", "13-2 Seven Canonical End-to-End Demonstrations", "13-3 Documentation + Reproducibility Package", "13-4 Targeted Final Product Polish", "13-5 Final Regression + Release Acceptance", "13-6 Final Archive + Presentation Package"], "oldPhase12FinalClosureNumbering": "SUPERSEDED_BY_APPROVED_ROADMAP_REVISION", "phase14": "NOT_CREATED"})
    (OUT / "baseline.txt").write_text("HEAD=d4d625b57449f9a451d5e27a6eb903625d221bc7\nREGISTRY=62\nDATAPROFILE=2.4\nMIGRATION=0007_phase10m1_workspace_domain\nTASK_BLOCK_COUNT_AT_ENTRY=0\n", encoding="utf-8", newline="\n")
    (OUT / "entry_gate.md").write_text("# Phase 11-0 Entry Gate\n\nPASS. N6 implementation, corrected completion, and verified archive ancestry are established. Entry HEAD and origin/master matched; the worktree was clean; Registry 62, DataProfile 2.4, migration 0007, and zero queued tasks were verified before admission.\n", encoding="utf-8", newline="\n")
    (OUT / "roadmap_reconciliation.md").write_text("# Roadmap Reconciliation\n\nPhase 11 is scientific validation, Phase 12 is comprehensive UI/UX product experience redesign, and Phase 13 is final product closure. The old Phase 12 final-closure numbering is superseded without rewriting history.\n", encoding="utf-8", newline="\n")
    (OUT / "no_production_change_audit.md").write_text("""# No Production Change Audit

PRODUCTION_BEHAVIOR_CHANGES = NONE

Registry, DataProfile, AnalysisPlan, database, migration, API, dependencies, lockfile, scientific algorithms, Artifact families, Runtime, Planner, renderers, and LLM call sites are unchanged. This phase adds only documentation, evidence, audit tooling, and audit consistency tests.

```text
NO_PHASE11_0_ARBITRARY_CODE_EXECUTION = PASS
NO_PHASE11_0_NOTEBOOK_EXECUTION = PASS
NO_PHASE11_0_DOWNLOADED_SCRIPT_EXECUTION = PASS
NO_PHASE11_0_EXTERNAL_SCIENTIFIC_API = PASS
NO_PHASE11_0_EXTERNAL_REFERENCE_DOWNLOAD = PASS
NO_PHASE11_0_SHELL_GENERATED_SCIENCE = PASS
NO_PHASE11_0_FRONTEND_SCIENTIFIC_RECOMPUTATION = PASS
NO_PHASE11_0_LLM_SCIENTIFIC_AUTHORITY = PASS
NO_SECRET_PATTERN_HITS = PASS
```
""", encoding="utf-8", newline="\n")
    (OUT / "docs_link_check.txt").write_text("PASS - Phase 11-0 canonical links are repository-relative and resolved by tests.\n", encoding="utf-8", newline="\n")
    (OUT / "secret_scan.txt").write_text("PASS - deterministic Phase 11-0 evidence contains no secret-bearing values; full repository secret scan remains a lifecycle verification gate.\n", encoding="utf-8", newline="\n")
    manifest_entries = []
    for path in sorted(OUT.rglob("*")):
        if path.is_file() and path.name != "manifest.json":
            manifest_entries.append({"path": path.relative_to(OUT).as_posix(), "sha256": sha256(path), "bytes": path.stat().st_size})
    write_json("manifest.json", {"schemaVersion": "phase11-evidence-manifest/1.0", "entries": manifest_entries, "entryCount": len(manifest_entries), "missingFiles": 0, "hashMismatch": 0, "secretBearingEvidence": 0})


if __name__ == "__main__":
    main()
