"""Prepare and verify Workstream J independent-scientist review assets.

This tool never creates human scores.  It creates blank review forms, imports
locked human submissions, and reports ``REVIEW_READY`` until real records exist.
Formal responses are generated through the existing bounded DeepSeek synthesis
path and are immutable after preparation.
"""

from __future__ import annotations

import argparse
import asyncio
from collections import Counter, defaultdict
import hashlib
import json
import os
import random
import shutil
from statistics import median
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, uuid5

ROOT = Path(__file__).resolve().parents[1]
for relative in (
    "apps/api",
    "packages/schemas",
    "packages/tool-registry",
    "packages/adapters",
    "packages/artifact-core",
    "packages/material-parsers",
    "services/workers",
    "services/llm",
):
    sys.path.insert(0, str(ROOT / relative))

from mdi_api.application.scientific_knowledge.synthesis import (  # noqa: E402
    BoundedLiteratureSynthesisProvider,
)
from mdi_api.domain.scientific_knowledge.contracts import (  # noqa: E402
    LiteratureEvidence,
    LiteratureEvidenceScope,
    LiteratureQueryPurpose,
    LiteratureSupportType,
)
from mdi_api.research_agent.llm.structured_client import (  # noqa: E402
    DeepSeekStructuredLLMClient,
)

OUT = ROOT / "docs" / "scientist-evaluation" / "generated"
PACKETS = OUT / "reviewer_packets"
MANIFEST_VERSION = "scientist-evaluation-case/1.0"
REVIEW_VERSION = "scientist-review-record/1.0"
BASELINE_ID = "j-baseline-20260911"
FORMAL_RESPONSE_CONTRACT = "scientist-evaluation-formal-responses/1.0"
EXPECTED_FORMAL_RESPONSE_COUNT = 24


def _hash_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _hash_json(value: Any) -> str:
    return _hash_bytes(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    )


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _current_git_value(*args: str, default: str) -> str:
    try:
        return subprocess.run(
            ["git", *args],
            cwd=ROOT,
            check=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
        ).stdout.strip() or default
    except (OSError, subprocess.CalledProcessError):
        return default


_UNTRACKED_FINGERPRINT_EXCLUDES = {
    ".cache",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
}


def _git_paths(repo_root: Path, *args: str) -> list[str]:
    try:
        raw = subprocess.run(
            ["git", *args, "-z"],
            cwd=repo_root,
            check=True,
            capture_output=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return []
    return sorted(
        item.decode("utf-8", errors="surrogateescape")
        for item in raw.split(b"\0")
        if item
    )


def _working_tree_fingerprint(
    repo_root: Path = ROOT, *, excluded_paths: tuple[Path, ...] = ()
) -> str:
    """Hash current changed/untracked bytes relative to HEAD, not status text."""

    excluded = [
        (path if path.is_absolute() else repo_root / path).resolve()
        for path in excluded_paths
    ]
    historical = (repo_root / "docs/scientist-evaluation/generated").resolve()

    def relevant(path_text: str, *, untracked: bool) -> bool:
        path = (repo_root / path_text).resolve()
        if path == historical or historical in path.parents:
            return False
        if any(path == root or root in path.parents for root in excluded):
            return False
        if untracked and any(part in _UNTRACKED_FINGERPRINT_EXCLUDES for part in Path(path_text).parts):
            return False
        return True

    tracked = _git_paths(repo_root, "diff", "--name-only", "HEAD")
    untracked = _git_paths(repo_root, "ls-files", "--others", "--exclude-standard")
    entries = [
        ("TRACKED", path) for path in tracked if relevant(path, untracked=False)
    ] + [
        ("UNTRACKED", path) for path in untracked if relevant(path, untracked=True)
    ]
    digest = hashlib.sha256()
    head = _current_git_value_at(repo_root, "rev-parse", "HEAD", default="UNAVAILABLE")
    digest.update(f"HEAD\0{head}\0".encode())
    for origin, path_text in sorted(entries):
        path = repo_root / path_text
        digest.update(f"{origin}\0{path_text.replace(os.sep, '/')}\0".encode())
        if path.is_symlink():
            digest.update(b"SYMLINK\0" + os.readlink(path).encode("utf-8", errors="surrogateescape"))
        elif path.is_file():
            digest.update(b"FILE\0")
            with path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    digest.update(chunk)
        else:
            digest.update(b"MISSING\0")
        digest.update(b"\0")
    return digest.hexdigest()


def _current_git_value_at(
    repo_root: Path, *args: str, default: str
) -> str:
    try:
        return subprocess.run(
            ["git", *args],
            cwd=repo_root,
            check=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
        ).stdout.strip() or default
    except (OSError, subprocess.CalledProcessError):
        return default


def _current_baseline_metadata(
    *, repo_root: Path = ROOT, excluded_paths: tuple[Path, ...] = ()
) -> dict[str, str]:
    head = _current_git_value_at(repo_root, "rev-parse", "HEAD", default="UNAVAILABLE")
    return {
        "head": head,
        "working_tree_state": "DIRTY_EXPECTED_UNCOMMITTED_H_I_J_PRE_M_BASELINE",
        "working_tree_fingerprint_sha256": _working_tree_fingerprint(
            repo_root, excluded_paths=excluded_paths
        ),
    }


def _formal_case_ids(cases: dict[str, Any]) -> list[str]:
    return [str(item.get("case_id") or "") for item in cases.get("cases", [])]


def _case_map(cases: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(item["case_id"]): item for item in cases.get("cases", [])}


def _evidence_label_map(case: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Build the one case-wide opaque-ref → displayed-label mapping."""

    mapping: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(case.get("authorized_evidence", []), start=1):
        ref = str(item.get("ref") or "")
        if not ref:
            raise ValueError(f"{case.get('case_id')}: evidence reference is empty")
        if ref in mapping:
            raise ValueError(f"{case.get('case_id')}: duplicate evidence reference {ref}")
        mapping[ref] = {
            "label": f"Evidence {index}",
            "origin": item.get("origin"),
            "item": item,
        }
    if not mapping:
        raise ValueError(f"{case.get('case_id')}: authorized evidence is empty")
    return mapping


def _validate_claim_refs(case: dict[str, Any], response: dict[str, Any]) -> list[str]:
    """Validate claims against the case-wide source map, never array positions."""

    mapping = _evidence_label_map(case)
    result_refs = {
        str(item["ref"])
        for item in case.get("authorized_evidence", [])
        if item.get("origin") != "LITERATURE"
    }
    literature_refs = {
        str(item["ref"])
        for item in case.get("authorized_evidence", [])
        if item.get("origin") == "LITERATURE"
    }
    errors: list[str] = []
    claim_ids: set[str] = set()
    for index, claim in enumerate(response.get("claims") or [], start=1):
        claim_id = str(claim.get("claim_id") or "")
        if not claim_id:
            errors.append(f"CLAIM_ID_MISSING:{index}")
        elif claim_id in claim_ids:
            errors.append(f"CLAIM_ID_DUPLICATE:{claim_id}")
        else:
            claim_ids.add(claim_id)
        result_claim_refs = [str(ref) for ref in claim.get("scientific_result_refs") or []]
        literature_claim_refs = [
            str(ref) for ref in claim.get("literature_evidence_refs") or []
        ]
        refs = result_claim_refs + literature_claim_refs
        if not refs:
            errors.append(f"CLAIM_EVIDENCE_MISSING:{claim_id or index}")
        if len(refs) != len(set(refs)):
            errors.append(f"CLAIM_EVIDENCE_DUPLICATE:{claim_id or index}")
        for ref in refs:
            if ref not in mapping:
                errors.append(f"CLAIM_EVIDENCE_FOREIGN:{claim_id or index}:{ref}")
        if any(ref not in result_refs for ref in result_claim_refs):
            errors.append(f"CLAIM_RESULT_REF_TYPE_MISMATCH:{claim_id or index}")
        if any(ref not in literature_refs for ref in literature_claim_refs):
            errors.append(f"CLAIM_LITERATURE_REF_TYPE_MISMATCH:{claim_id or index}")
    return errors


def _validate_formal_response_set(
    cases: dict[str, Any],
    responses: dict[str, Any],
    baseline: dict[str, Any],
) -> list[str]:
    """Fail closed on case coverage, candidate identity and response completeness."""

    expected_ids = _formal_case_ids(cases)
    errors: list[str] = []
    if len(expected_ids) != EXPECTED_FORMAL_RESPONSE_COUNT or len(set(expected_ids)) != len(expected_ids):
        errors.append("EXPECTED_CASE_SET_INVALID")
    if not expected_ids:
        errors.append("EXPECTED_CASE_SET_EMPTY")
    rows = responses.get("responses")
    if not isinstance(rows, list) or not rows:
        return [*errors, "FORMAL_RESPONSE_SET_EMPTY"]
    actual_ids = [str(row.get("case_id") or "") for row in rows]
    if len(actual_ids) != len(set(actual_ids)):
        errors.append("FORMAL_RESPONSE_DUPLICATE_CASE_ID")
    if set(actual_ids) != set(expected_ids):
        errors.append("FORMAL_RESPONSE_CASE_SET_MISMATCH")
    if len(actual_ids) != len(expected_ids):
        errors.append("FORMAL_RESPONSE_COUNT_MISMATCH")
    if responses.get("contract_version") != FORMAL_RESPONSE_CONTRACT:
        errors.append("FORMAL_RESPONSE_CONTRACT_MISMATCH")
    if responses.get("baseline_id") != baseline.get("baseline_id"):
        errors.append("FORMAL_RESPONSE_BASELINE_ID_MISMATCH")
    if responses.get("baseline_fingerprint") != baseline.get("baseline_fingerprint"):
        errors.append("FORMAL_RESPONSE_BASELINE_FINGERPRINT_MISMATCH")
    if responses.get("formal_responses_hash") != _hash_json(rows):
        errors.append("FORMAL_RESPONSE_MANIFEST_HASH_MISMATCH")
    case_by_id = _case_map(cases)
    seen: set[str] = set()
    for row in rows:
        case_id = str(row.get("case_id") or "")
        if case_id in seen or case_id not in case_by_id:
            continue
        seen.add(case_id)
        case = case_by_id[case_id]
        required = (
            "response_content",
            "response_content_sha256",
            "generated_at",
            "claims",
            "summary",
            "contradictions",
            "limitations",
            "authorized_result_refs",
            "authorized_literature_refs",
            "evidence_manifest_hash",
        )
        for field in required:
            value = row.get(field)
            if value is None or value == "":
                if field not in {"claims", "contradictions"}:
                    errors.append(f"RESPONSE_FIELD_MISSING:{case_id}:{field}")
        if row.get("status") != "FROZEN":
            errors.append(f"RESPONSE_NOT_FROZEN:{case_id}")
        if row.get("baseline_id") != baseline.get("baseline_id"):
            errors.append(f"RESPONSE_BASELINE_ID_MISMATCH:{case_id}")
        if row.get("baseline_fingerprint") != baseline.get("baseline_fingerprint"):
            errors.append(f"RESPONSE_BASELINE_FINGERPRINT_MISMATCH:{case_id}")
        content = row.get("response_content")
        content_hash = row.get("response_content_sha256")
        if not isinstance(content, str) or not content.strip():
            errors.append(f"RESPONSE_CONTENT_EMPTY:{case_id}")
        elif content_hash != _hash_bytes(content.encode()):
            errors.append(f"RESPONSE_HASH_MISMATCH:{case_id}")
        if row.get("evidence_manifest_hash") != _hash_json(case["authorized_evidence"]):
            errors.append(f"EVIDENCE_HASH_MISMATCH:{case_id}")
        expected_results = sorted(
            item["ref"]
            for item in case["authorized_evidence"]
            if item.get("origin") != "LITERATURE"
        )
        expected_literature = sorted(
            item["ref"]
            for item in case["authorized_evidence"]
            if item.get("origin") == "LITERATURE"
        )
        if sorted(row.get("authorized_result_refs") or []) != expected_results:
            errors.append(f"AUTHORIZED_RESULT_SET_MISMATCH:{case_id}")
        if sorted(row.get("authorized_literature_refs") or []) != expected_literature:
            errors.append(f"AUTHORIZED_LITERATURE_SET_MISMATCH:{case_id}")
        errors.extend(f"{case_id}:{error}" for error in _validate_claim_refs(case, row))
        if row.get("generation_outcome") == "VALIDATION_FAILURE_AFTER_DOCUMENTED_RETRY" and row.get("claims"):
            errors.append(f"FAILED_GENERATION_HAS_CLAIMS:{case_id}")
    return errors


def _e(
    ref: str,
    origin: str,
    text: str,
    *,
    scope: str,
    method: str,
    lineage: str,
    conditions: list[str] | None = None,
    limitations: list[str] | None = None,
    evidence_scope: str | None = None,
    relation: str | None = None,
    publication_role: str | None = None,
) -> dict[str, Any]:
    return {
        "ref": ref,
        "origin": origin,
        "text": text,
        "scope": scope,
        "method": method,
        "lineage": lineage,
        "conditions": conditions or [],
        "limitations": limitations or [],
        "evidence_scope": evidence_scope,
        "relation": relation,
        "publication_role": publication_role,
    }


def _case(
    case_id: str,
    domain: str,
    title: str,
    question: str,
    evidence: list[dict[str, Any]],
    required: list[str],
    forbidden: list[str],
    qualifiers: list[str],
    limitations: list[str],
    *,
    class_name: str = "single_domain",
    anchor: bool = False,
    valid_stop: list[str] | None = None,
    method_expectations: list[str] | None = None,
    response_mode: str = "DEEPSEEK_BOUNDED_SYNTHESIS",
) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "scientific_domain": domain,
        "class": class_name,
        "title": title,
        "research_question": question,
        "held_out_from_workstream_i": True,
        "held_out_basis": [
            "new scenario and source configuration",
            "not a renamed Workstream I fixture",
            "internal regression corpus excluded from formal J scoring",
        ],
        "source_origin": "INTERNALLY_AUTHORED_HELD_OUT_SANITIZED_FIXTURE",
        "independent_contributor": None,
        "anchor": anchor,
        "authorized_evidence": evidence,
        "required_claims": required,
        "allowed_claims": required
        + ["bounded interpretation", "explicit uncertainty", "future evidence recommendation"],
        "forbidden_claims": forbidden,
        "required_qualifiers": qualifiers,
        "required_limitations": limitations,
        "comparison_expectations": [],
        "method_expectations": method_expectations or [],
        "response_mode": response_mode,
        "hypothesis_expectations": ["hypothesis must remain non-authoritative"],
        "valid_stop_outcomes": valid_stop
        or ["SYNTHESIZE", "STOP_WITH_LIMITATIONS", "INSUFFICIENT_EVIDENCE"],
        "reviewer_author_conflict": "NO_FORMAL_CASE_AUTHOR_AVAILABLE; no reviewer may score a case they contributed later",
    }


def build_cases() -> dict[str, Any]:
    c: list[dict[str, Any]] = [
        _case("J01", "trajectory_transport", "Transport estimate",
              "What does the supplied trajectory establish about long-time transport?",
              [_e("result_1", "COMPUTED", "The trajectory analysis reports a diffusion coefficient from a linear MSD fit over 20–80 ps.", scope="Li-containing trajectory V4; 5000 frames; 800 K", method="trajectory.diffusion from MSD", lineage="trajectory-v4", conditions=["temperature=800 K", "fit_interval=20-80 ps"], limitations=["finite trajectory length", "fit interval is selected"],)],
              ["the reported diffusion coefficient is the computed result for this trajectory and fit interval"],
              ["universal transport behavior", "causal mechanism", "out-of-domain generalization"],
              ["temperature and fit interval"],
              ["finite trajectory length"]),
        _case("J02", "trajectory_transport", "Finite trajectory comparison",
              "Can the two trajectory transport estimates be treated as directly comparable?",
              [_e("result_1", "COMPUTED", "Material A has D=1.2e-8 m2/s from a 10–40 ps fit.", scope="Material A trajectory V2", method="MSD diffusion fit", lineage="traj-A", conditions=["temperature=700 K", "fit_interval=10-40 ps"], limitations=["short trajectory"]),
               _e("result_2", "COMPUTED", "Material B has D=1.0e-8 m2/s from a 40–100 ps fit.", scope="Material B trajectory V1", method="MSD diffusion fit", lineage="traj-B", conditions=["temperature=900 K", "fit_interval=40-100 ps"], limitations=["different temperature and fit interval"])],
              ["the estimates differ numerically but direct scientific comparison is limited by conditions"],
              ["Material A is intrinsically more mobile", "temperature-independent ranking"],
              ["temperature differs", "fit intervals differ"], ["conditions and fit intervals prevent an unqualified comparison"]),
        _case("J03", "structure_coordination", "Coordination method dependence",
              "What should be concluded when two coordination definitions give different values?",
              [_e("result_1", "COMPUTED", "CrystalNN reports coordination 6 for the selected site.", scope="Structure S7, selected site", method="CrystalNN", lineage="structure-s7", limitations=["algorithm-dependent neighbor perception"]),
               _e("result_2", "COMPUTED", "A fixed cutoff reports coordination 8 for the same site.", scope="Structure S7, selected site", method="cutoff coordination at 3.0 A", lineage="structure-s7", limitations=["cutoff-dependent"])],
              ["the coordination values are method-dependent observations"],
              ["one method is universally correct", "averaged coordination truth"],
              ["name both methods", "state that definitions differ"], ["the methods use different neighbor semantics"],
              anchor=True, method_expectations=["METHOD_DEPENDENT_DIFFERENCE"]),
        _case("J04", "structure_coordination", "Unusual local environment",
              "Is the selected local environment unusual?",
              [_e("result_1", "COMPUTED", "The selected site has a broad neighbor-distance distribution.", scope="Structure S8, selected site", method="RDF/neighbor distribution", lineage="structure-s8", limitations=["no matched reference structure supplied"])],
              ["the distribution is the observed structural feature"],
              ["unusual relative to all materials", "abnormality without a baseline"],
              ["no comparison baseline is available"], ["unusualness cannot be established without a compatible reference"]),
        _case("J05", "xrd", "Pattern agreement",
              "What does agreement between the experimental and theoretical XRD patterns support?",
              [_e("result_1", "COMPUTED", "Peak positions agree within the configured comparison tolerance.", scope="Candidate structure S9 and supplied experimental pattern", method="experimental/theoretical XRD comparison", lineage="xrd-s9", limitations=["peak agreement alone does not establish phase purity"])],
              ["agreement under the comparison method"],
              ["conclusive phase identification", "phase purity established"],
              ["comparison tolerance", "phase purity and measurement conditions"],
              ["peak agreement is not definitive phase identification"],
              method_expectations=["comparison agreement is narrower than identity confirmation"]),
        _case("J06", "xrd", "XRD condition mismatch",
              "Can the two XRD patterns be used to establish a material identity when broadening and measurement conditions differ?",
              [_e("result_1", "COMPUTED", "The theoretical pattern has sharp peaks; the experimental pattern has broadened peaks.", scope="Candidate structure and experiment", method="theoretical vs experimental XRD", lineage="xrd-s10", conditions=["different instrumental broadening"], limitations=["phase mixture not independently excluded"])],
              ["the comparison is limited by broadening and unresolved phase composition"],
              ["broadening proves a different phase", "pure phase confirmed"],
              ["instrumental broadening", "phase mixture not excluded"],
              ["matching must not be overstated"], anchor=True),
        _case("J07", "materials_ml", "Chemistry-conditioned error",
              "What can the chemistry-group error pattern show about model performance?",
              [_e("result_1", "COMPUTED", "The evaluated oxide subgroup has higher absolute error than the remaining held-out samples.", scope="Held-out split of dataset M3; subgroup n=18", method="materials ML group-conditioned evaluation", lineage="dataset-m3", limitations=["small subgroup", "observational grouping"])],
              ["an association between subgroup membership and observed error"],
              ["chemistry causes model failure", "generalization beyond the evaluated split"],
              ["subgroup size", "held-out split scope"],
              ["association does not establish causality"], anchor=True),
        _case("J08", "materials_ml_composition", "Composition projection",
              "What does a composition-space cluster mean in this dataset?",
              [_e("result_1", "COMPUTED", "PCA followed by KMeans separates the evaluated compositions into three clusters.", scope="Dataset M4 composition features", method="PCA + KMeans", lineage="dataset-m4", limitations=["exploratory projection", "cluster stability not tested"])],
              ["an exploratory grouping in the selected feature representation"],
              ["a new physical material family", "chemical mechanism established", "outlier means invalid material"],
              ["feature representation", "cluster stability"], ["clusters are not automatically physical families"]),
        _case("J09", "electronic_structure", "Supplied band structure",
              "What does the supplied band-structure result establish?",
              [_e("result_1", "COMPUTED", "The supplied band structure shows a gap-like separation under its reported energy reference.", scope="Supplied band structure for material E2", method="external electronic-structure calculation parsed by platform", lineage="band-e2", conditions=["energy reference supplied by source"], limitations=["underlying solver was not independently validated"])],
              ["what the supplied result displays within its method and reference"],
              ["platform independently validated the solver", "experimental band gap confirmed"],
              ["energy reference", "external implementation boundary"],
              ["interpretation is limited to the supplied calculation"], anchor=True),
        _case("J10", "electronic_structure", "Electronic comparison",
              "Can the supplied calculated gap be directly compared with a published optical gap?",
              [_e("result_1", "COMPUTED", "The supplied calculation reports a 1.8 eV electronic gap.", scope="Material E3, supplied calculation", method="external electronic-structure calculation", lineage="band-e3", conditions=["calculation energy reference"], limitations=["solver semantics are externally supplied"]),
               _e("literature_1", "LITERATURE", "The paper reports an optical onset near 2.1 eV for a sample of the same nominal composition.", scope="studied sample in abstract", method="optical measurement", lineage="paper-e3", conditions=["sample preparation not fully available"], evidence_scope="ABSTRACT_ONLY", publication_role="PRIMARY")],
              ["the values concern related but method-distinct quantities"],
              ["the 0.3 eV difference proves calculation error", "direct equivalence without method qualifiers"],
              ["electronic versus optical quantity", "abstract-only scope"], ["method and sample differences limit comparison"]),
        _case("J11", "phonon", "Imaginary mode observation",
              "What does the supplied phonon result show?",
              [_e("result_1", "COMPUTED", "The phonon dispersion contains one negative-frequency mode near Gamma.", scope="Supplied phonon calculation for P2", method="external phonon calculation", lineage="phonon-p2", limitations=["convergence and finite-size checks unavailable", "upstream solver not independently validated"])],
              ["the supplied result contains a negative-frequency mode"],
              ["definitive universal dynamic instability", "causal structural explanation"],
              ["convergence", "finite-size effects", "external solver boundary"], ["negative mode requires cautious interpretation"]),
        _case("J12", "phonon", "Phonon stability boundary",
              "Does a small imaginary branch prove that the material is unusable?",
              [_e("result_1", "COMPUTED", "A small negative branch appears only at one sampled q-point.", scope="Supplied phonon calculation for P3", method="external phonon calculation", lineage="phonon-p3", conditions=["one q-path and one convergence setting"], limitations=["numerical and physical origins unresolved"])],
              ["a possible instability signal requiring further validation"],
              ["material is unusable", "universal instability"],
              ["single q-path", "convergence not established"], ["cannot distinguish numerical from physical origin"]),
        _case("J13", "transport_structure", "Transport and local structure",
              "Does lower coordination establish the mechanism for elevated diffusion?",
              [_e("result_1", "COMPUTED", "Diffusion is elevated in the supplied trajectory.", scope="Material T4 trajectory", method="trajectory.diffusion", lineage="t4-trajectory", limitations=["finite trajectory"]),
               _e("result_2", "COMPUTED", "The same material has lower CrystalNN coordination than the comparison structure.", scope="Material T4 structure", method="CrystalNN", lineage="t4-structure", limitations=["method-dependent coordination"]),
               _e("literature_1", "LITERATURE", "The abstract says less constrained environments may facilitate transport in the studied compounds.", scope="studied compounds only", method="literature synthesis", lineage="paper-t4", evidence_scope="ABSTRACT_ONLY", publication_role="PRIMARY")],
              ["the evidence is consistent with a structural hypothesis or association"],
              ["lower coordination causes diffusion", "mechanism established"],
              ["shared material identity", "coordination method", "abstract-only literature"],
              ["causality is not established"], class_name="cross_evidence", anchor=True),
        _case("J14", "ml_composition", "ML error and composition",
              "Does composition explain the observed model error pattern?",
              [_e("result_1", "COMPUTED", "Errors are higher for the sulfide subgroup in the held-out evaluation.", scope="ML dataset M5 held-out split", method="group-conditioned error analysis", lineage="m5-eval", limitations=["subgroup imbalance"]),
               _e("result_2", "COMPUTED", "The sulfide subgroup occupies a separated region in the composition projection.", scope="Dataset M5 composition features", method="PCA projection", lineage="m5-composition", limitations=["projection is exploratory"])],
              ["composition grouping is associated with the observed error pattern"],
              ["composition causes error", "cluster is a physical family", "out-of-domain generalization"],
               ["subgroup coverage", "exploratory projection", "dataset split"],
               ["alternative explanations such as imbalance remain"], class_name="cross_evidence"),
        _case("J15", "xrd_literature", "XRD and published context",
              "Does pattern agreement plus the paper establish phase purity?",
              [_e("result_1", "COMPUTED", "Experimental and theoretical peak positions agree within tolerance.", scope="Candidate structure X4 and experiment", method="XRD comparison", lineage="x4", limitations=["broadening and phase mixture unresolved"]),
               _e("literature_1", "LITERATURE", "The abstract reports a dominant phase assignment but notes that detailed purity analysis is outside the study.", scope="paper abstract", method="experimental diffraction", lineage="paper-x4", conditions=["sample preparation described only in abstract"], evidence_scope="ABSTRACT_ONLY", publication_role="PRIMARY")],
              ["agreement supports consistency with the candidate under the method"],
              ["phase purity definitively established", "paper's phase assignment transfers without qualification"],
               ["abstract-only", "phase mixture", "broadening"],
               ["phase identification remains limited"], class_name="cross_evidence"),
        _case("J16", "electronic_literature", "Electronic result and literature",
              "How should the supplied electronic result be discussed alongside the paper?",
              [_e("result_1", "COMPUTED", "The supplied calculation displays a metallic-looking band crossing.", scope="Material E5 supplied band result", method="external band-structure calculation", lineage="e5-band", limitations=["solver and convergence not independently validated"]),
               _e("literature_1", "LITERATURE", "The paper reports a temperature-dependent resistivity signature for a related sample.", scope="studied sample and conditions", method="transport experiment", lineage="paper-e5", conditions=["temperature-dependent experiment"], evidence_scope="OPEN_FULL_TEXT", publication_role="PRIMARY")],
              ["the calculation and experiment provide complementary method-dependent evidence"],
              ["one source validates the other", "platform executed a new first-principles calculation"],
               ["sample relation", "method difference", "external solver boundary"],
               ["complementary evidence is not identity"], class_name="cross_evidence"),
        _case("J17", "phonon_literature", "Phonon and method limitation",
              "Does the paper resolve whether the supplied imaginary mode is physical?",
              [_e("result_1", "COMPUTED", "The supplied result contains a small imaginary mode.", scope="Phonon result P6", method="external phonon calculation", lineage="p6", limitations=["no convergence series"]),
               _e("literature_1", "LITERATURE", "The paper states that imaginary modes can be sensitive to convergence and structural conditions.", scope="paper discussion", method="phonon calculation", lineage="paper-p6", evidence_scope="OPEN_FULL_TEXT", publication_role="METHOD")],
              ["the paper provides method context but does not resolve this supplied calculation"],
              ["paper proves the current mode is physical", "universal instability"],
               ["paper is method context", "current convergence absent"],
               ["current data remain insufficient"], class_name="cross_evidence"),
        _case("J18", "result_literature_comparison", "Computed value and publication",
              "Is the computed transport value higher than the published value?",
              [_e("result_1", "COMPUTED", "The current trajectory gives D=2.4e-8 m2/s.", scope="Material T7 at 800 K", method="trajectory.diffusion", lineage="t7", conditions=["temperature=800 K"], limitations=["finite trajectory"]),
               _e("literature_1", "LITERATURE", "The paper reports D=1.7e-8 m2/s for a related composition at 600 K.", scope="studied composition", method="experimental transport", lineage="paper-t7", conditions=["temperature=600 K"], evidence_scope="OPEN_FULL_TEXT", publication_role="PRIMARY")],
              ["the numbers are not directly comparable without a temperature/composition qualifier"],
              ["the material intrinsically has higher diffusion", "temperature-independent difference"],
               ["temperature differs", "composition differs", "method differs"],
               ["comparison is limited"], class_name="cross_evidence", anchor=True),
        _case("J19", "contradictory_literature", "Conflicting reports",
              "How should two papers with opposite trends be summarized?",
              [_e("literature_1", "LITERATURE", "Study A reports increased conductivity at 500 K for phase alpha.", scope="phase alpha", method="impedance measurement", lineage="paper-a", conditions=["500 K"], evidence_scope="OPEN_FULL_TEXT", publication_role="PRIMARY"),
               _e("literature_2", "LITERATURE", "Study B reports decreased conductivity at 500 K for phase beta.", scope="phase beta", method="dc transport", lineage="paper-b", conditions=["500 K"], evidence_scope="ABSTRACT_ONLY", relation="different phase", publication_role="PRIMARY")],
              ["the apparent conflict may be condition/method/phase dependent and remains unresolved without further reconciliation"],
              ["one paper is correct solely because it is newer", "majority vote"],
               ["phase differs", "measurement method differs", "abstract-only scope"],
               ["retain conditional disagreement"], class_name="cross_evidence", anchor=True),
        _case("J20", "literature_lineage", "Review and primary lineage",
              "How many independent studies support the reported mechanism?",
              [_e("literature_1", "LITERATURE", "A review summarizes the mechanism and cites the primary study.", scope="review scope", method="review synthesis", lineage="review-r1", relation="summarizes literature_2", publication_role="REVIEW", evidence_scope="OPEN_FULL_TEXT"),
               _e("literature_2", "LITERATURE", "The primary paper reports the mechanism in its studied samples.", scope="primary study samples", method="experiment", lineage="primary-r1", relation="source summarized by literature_1", publication_role="PRIMARY", evidence_scope="OPEN_FULL_TEXT")],
              ["the sources provide different evidence roles but should not be counted as two independent studies"],
              ["two independent confirmations", "field-wide consensus"],
               ["review/primary lineage"], ["avoid double-counting"],
               class_name="cross_evidence"),
        _case("J21", "causal_restraint", "Correlation and causation",
              "Does a correlation between coordination and diffusion establish causation?",
              [_e("result_1", "COMPUTED", "Across six samples, lower coordination coincides with higher diffusion.", scope="Six evaluated samples", method="correlation of computed Results", lineage="shared-sample-set", limitations=["observational association", "confounders not controlled"])],
              ["an association in the evaluated samples"],
              ["causal claim", "mechanism established"],
               ["observational design", "confounders not controlled"],
               ["causal inference is unavailable"], class_name="insufficient_evidence", anchor=True),
        _case("J22", "insufficient_evidence", "No comparison baseline",
              "Can the system conclude that this structure is unusual?",
              [_e("result_1", "COMPUTED", "The coordination distribution for the selected structure is available.", scope="One selected structure", method="coordination analysis", lineage="single-structure", limitations=["no compatible reference population"])],
              ["the structure can be described, but unusualness is not established"],
              ["unusual compared with materials generally", "abnormality"],
               ["reference baseline missing"], ["needs a compatible comparison"],
               class_name="insufficient_evidence"),
        _case("J23", "insufficient_evidence", "Bounded literature absence",
              "Does finding no supporting paper in the bounded search prove that the phenomenon has never been reported?",
              [_e("literature_1", "LITERATURE", "The bounded search returned no relevant supporting source.", scope="three authorized queries and selected providers", method="bounded scholarly search", lineage="search-q1", evidence_scope="METADATA_ONLY", publication_role="DISCOVERY")],
              ["no supporting source was identified in the current bounded search"],
              ["the phenomenon has never been reported", "evidence of absence"],
               ["bounded query/provider scope"],
               ["absence of evidence is not evidence of absence"],
               class_name="insufficient_evidence",
               response_mode="DETERMINISTIC_INSUFFICIENT_EVIDENCE_STOP"),
        _case("J24", "insufficient_evidence", "Cluster generalization",
              "Does a composition cluster prove a new physical material family?",
              [_e("result_1", "COMPUTED", "A clustering projection separates samples using selected composition descriptors.", scope="Dataset M8", method="PCA + KMeans", lineage="m8", limitations=["descriptor-dependent", "no physical validation"])],
              ["an exploratory descriptor-space cluster"],
              ["new physical family", "universal composition rule"],
               ["descriptor dependence", "no physical validation"],
               ["physical interpretation is unsupported"], class_name="insufficient_evidence"),
    ]
    return {
        "contract_version": MANIFEST_VERSION,
        "formal_scored_cases": 24,
        "calibration_cases": 4,
        "optional_shadow_cases": 6,
        "cases": c,
        "calibration": [
            {
                "case_id": "CAL-01",
                "purpose": "clearly strong answer",
                "question": "What does a directly reported computed value establish?",
                "evidence": "The Result directly reports the value for the named source version and conditions.",
                "system_response": "The computed Result reports the value for this source version and these conditions. It does not establish behavior outside that scope.",
                "guidance": "Expected to be acceptable: direct evidence, scope, and limitation are aligned.",
            },
            {
                "case_id": "CAL-02",
                "purpose": "obvious causal overclaim",
                "question": "Does an observed association establish causation?",
                "evidence": "Two variables coincide in an observational sample; no causal design is present.",
                "system_response": "The first variable causes the second.",
                "guidance": "Expected severe penalty: unsupported causal conclusion.",
            },
            {
                "case_id": "CAL-03",
                "purpose": "obvious scope/generalization error",
                "question": "Does one studied material establish behavior for a material class?",
                "evidence": "One material was studied under one method and condition.",
                "system_response": "All materials in this class behave this way.",
                "guidance": "Expected severe penalty: scope expands beyond the studied system.",
            },
            {
                "case_id": "CAL-04",
                "purpose": "genuinely unresolved contradiction",
                "question": "What follows when two compatible studies report opposite results?",
                "evidence": "The studies remain comparable after the provided method and condition checks.",
                "system_response": "The available evidence remains conflicted and does not select one outcome.",
                "guidance": "Expected to be acceptable: genuine disagreement is preserved.",
            },
        ],
        "shadow_cases": [
            {"case_id": f"SHADOW-{i:02d}", "purpose": "diagnostic I baseline/corrected A/B only", "status": "NOT_GENERATED_OPTIONAL"}
            for i in range(1, 7)
        ],
        "expert_contributed_case_slots": [
            {"slot": f"EXPERT-SLOT-{i:02d}", "status": "AVAILABLE_FOR_FUTURE_CONTRIBUTION", "counts_toward_current_24": False}
            for i in range(1, 9)
        ],
    }


def build_baseline(
    cases: dict[str, Any], *, excluded_paths: tuple[Path, ...] = ()
) -> dict[str, Any]:
    inventory_path = ROOT / "docs/scientific-quality/generated/scientific_quality_inventory.json"
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    qualifications = [
        {
            "capability_id": item["capability_id"],
            "qualification_level": item.get("qualification_level"),
            "evidence_fingerprint": item.get("evidence_fingerprint"),
            "scientific_contract_fingerprint": item.get("scientific_contract_fingerprint"),
        }
        for item in inventory["capabilities"]
    ]
    prompt_files = {
        "scientific_interpreter": ROOT / "apps/api/mdi_api/interpretation/prompts/scientific_interpreter_v1.txt",
        "literature_synthesis": ROOT / "apps/api/mdi_api/application/scientific_knowledge/prompts/literature_synthesis_v1.txt",
        "research_strategy": ROOT / "apps/api/mdi_api/research_agent/strategy/prompts/scientific_research_strategy_v1.txt",
    }
    current = _current_baseline_metadata(excluded_paths=excluded_paths)
    capture_at = datetime.now(timezone.utc).isoformat()
    for name, path in prompt_files.items():
        if not path.is_file() or path.is_symlink() or ROOT not in path.resolve().parents:
            raise ValueError(f"non-canonical prompt path: {name}")
    data: dict[str, Any] = {
        "contract_version": "scientist-evaluation-baseline/1.0",
        "baseline_id": "PENDING_BASELINE_ID",
        "repository_root": r"E:\1project\mdi-b0-5a1",
        "canonical_head_at_freeze": current["head"],
        "working_tree_state": current["working_tree_state"],
        "uncommitted_h_i_fingerprint_sha256": current[
            "working_tree_fingerprint_sha256"
        ],
        "baseline_capture_at": capture_at,
        "j_preparation_files_excluded_from_candidate_fingerprint": True,
        "database_schema_head": "0033_scientific_knowledge",
        "capability_registry": {"count": 17, "inventory_fingerprint": inventory["inventory_fingerprint"]},
        "capability_qualification": {
            "counts": inventory["qualification_counts"],
            "entries": qualifications,
            "inventory_file_sha256": _hash_bytes(inventory_path.read_bytes()),
        },
        "contracts": {
            "scientific_reasoning": "scientific-reasoning/1.0",
            "claim_support_policy": "scientific-reasoning-policy/1.0",
            "scientific_knowledge": "1.0",
            "interpretation": ["1.0", "1.1"],
            "report": "2.0",
            "report_composer": "agent2.report-composer/2.0",
            "report_prompt": "scientific-report-composer/2.0",
            "autonomy_policy": "agent2.autonomy-policy/1.0",
            "autonomy_policy_fingerprint": "a1f613a998e9e9c45a5e16d023028b0d059a5acd296c1c07d4c4e1dff5108016",
            "strategy": "agent2.research-strategy-decision/1.0",
        },
        "prompt_and_provider": {
            "provider": "deepseek",
            "model": os.environ.get("DEEPSEEK_MODEL") or "deepseek-v4-flash",
            "reasoning_prompt": "scientific-literature-synthesis/2.0",
            "strategy_prompt": "scientific-research-strategy/1.0",
            "deepseek_timeout_seconds": 120,
            "deepseek_max_output_tokens": 8192,
            "deepseek_max_prompt_bytes": 524288,
            "deepseek_transient_retries": 1,
            "repair_policy": "at_most_one_bounded_validation_guided_repair",
            "prompt_file_sha256": {
                name: _hash_bytes(path.read_bytes()) for name, path in prompt_files.items()
            },
            "prompt_file_paths": {
                name: str(path.relative_to(ROOT)).replace("\\", "/")
                for name, path in prompt_files.items()
            },
            "secret_values_recorded": False,
        },
        "context_policy": {
            "max_context_input_tokens": 12000,
            "literature_candidate_limit": 20,
            "literature_evidence_limit": 24,
        },
        "evaluation_case_manifest_version": cases["contract_version"],
        "formal_response_policy": "immutable_after_generation_and_before_reviewer_reveal",
        "human_boundary": "NO_MODEL_OR_SCRIPT_MAY_CREATE_HUMAN_REVIEW_RECORDS",
    }
    data["baseline_id"] = (
        f"j-baseline-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-"
        f"{_hash_json(data)[:12]}"
    )
    data["baseline_fingerprint"] = _hash_json(data)
    return data


def _literature_model(case_id: str, item: dict[str, Any]) -> tuple[LiteratureEvidence, dict[str, Any]]:
    source_id = uuid5(NAMESPACE_URL, f"https://mdi.local/evaluation/{case_id}/{item['ref']}")
    scope = LiteratureEvidenceScope(item.get("evidence_scope") or "OPEN_FULL_TEXT")
    passage = item["text"] if scope not in {
        LiteratureEvidenceScope.METADATA_ONLY,
        LiteratureEvidenceScope.REFERENCE_ONLY,
    } else None
    evidence = LiteratureEvidence(
        evidence_id=source_id,
        project_id="scientist-evaluation",
        work_id=uuid5(NAMESPACE_URL, f"work:{case_id}:{item['ref']}"),
        snapshot_id=uuid5(NAMESPACE_URL, f"snapshot:{case_id}:{item['ref']}"),
        scope=scope,
        support_type=LiteratureSupportType.CONTRADICTING if item.get("relation") == "contradicting" else LiteratureSupportType.SUPPORTING,
        purpose=LiteratureQueryPurpose.HYPOTHESIS_CONTEXT,
        passage=passage,
        source_content_hash=_hash_bytes(item["text"].encode()),
        selected_by="j-evaluation-preparation",
        selected_at=datetime.now(timezone.utc),
    )
    metadata = {
        "title": f"Sanitized evaluation source {case_id} {item['ref']}",
        "citation": f"Sanitized evaluation source {case_id} ({item.get('publication_role') or 'PRIMARY'})",
        "publication_status": "REVIEW" if item.get("publication_role") == "REVIEW" else "PEER_REVIEWED_ARTICLE",
    }
    return evidence, metadata


def _response_text(output: Any) -> str:
    lines = [output.summary]
    if output.claims:
        lines.append("\nClaims:")
        lines.extend(f"- {claim.statement}" for claim in output.claims)
    if output.contradictions:
        lines.append("\nContradictions:")
        lines.extend(f"- {item}" for item in output.contradictions)
    if output.limitations:
        lines.append("\nLimitations:")
        lines.extend(f"- {item}" for item in output.limitations)
    return "\n".join(lines)


def _reviewer_safe_text(text: str) -> str:
    """Keep provider-facing opaque refs out of the ordinary scientist view."""
    replacements = {
        "literature_1": "the literature source",
        "literature_2": "the second literature source",
        "result_1": "the computed result",
        "result_2": "the second computed result",
        "result_3": "the third computed result",
        "claim_1": "the first claim",
        "claim_2": "the second claim",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return text


async def generate_formal_responses(
    cases: dict[str, Any],
    baseline: dict[str, Any],
    existing: dict[str, Any] | None = None,
) -> dict[str, Any]:
    provider = BoundedLiteratureSynthesisProvider(
        DeepSeekStructuredLLMClient(), timeout_seconds=120
    )
    existing_by_id = {
        row["case_id"]: row
        for row in (existing or {}).get("responses", [])
        if row.get("status") == "FROZEN"
    }
    prior_by_id = {
        row["case_id"]: row for row in (existing or {}).get("responses", [])
    }
    rows: list[dict[str, Any]] = []
    for case in cases["cases"]:
        if case["case_id"] in existing_by_id:
            rows.append(existing_by_id[case["case_id"]])
            continue
        lit: dict[str, LiteratureEvidence] = {}
        meta: dict[str, dict[str, Any]] = {}
        results: dict[str, dict[str, Any]] = {}
        for item in case["authorized_evidence"]:
            if item["origin"] == "LITERATURE":
                evidence, metadata = _literature_model(case["case_id"], item)
                lit[item["ref"]] = evidence
                meta[item["ref"]] = metadata
            else:
                results[item["ref"]] = {
                    "summary": item["text"],
                    "scope": item["scope"],
                    "method": item["method"],
                    "conditions": {x.split("=", 1)[0]: x.split("=", 1)[1] for x in item.get("conditions", []) if "=" in x},
                    "lineage": item["lineage"],
                    "limitations": item.get("limitations", []),
                    "semantic_tags": ["J_HELD_OUT_EVALUATION_FIXTURE"],
                }
        prior_attempts = int(
            prior_by_id.get(case["case_id"], {}).get("generation_attempt")
            or (1 if case["case_id"] in prior_by_id else 0)
        )
        row: dict[str, Any] = {
            "case_id": case["case_id"],
            "baseline_id": baseline["baseline_id"],
            "baseline_fingerprint": baseline["baseline_fingerprint"],
            "evidence_manifest_hash": _hash_json(case["authorized_evidence"]),
            "status": "FAILED_BEFORE_REVIEW",
            "generation_attempt": prior_attempts + 1,
        }
        if case["response_mode"] == "DETERMINISTIC_INSUFFICIENT_EVIDENCE_STOP":
            text = (
                "No supporting source was identified in the current bounded search. "
                "This does not establish that the phenomenon has never been reported, "
                "because the conclusion is limited by the authorized queries and "
                "provider scope."
            )
            row.update(
                {
                    "status": "FROZEN",
                    "response_content": text,
                    "response_content_sha256": _hash_bytes(text.encode()),
                    "provider": "deterministic_strategy_stop",
                    "model": None,
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "repair_attempted": False,
                    "claims": [
                        {
                            "claim_id": "claim_1",
                            "statement": "No supporting source was identified in the current bounded search.",
                            "scientific_result_refs": [],
                            "literature_evidence_refs": ["literature_1"],
                            "support_status": "SUPPORTED_WITHIN_SCOPE",
                            "scope": "authorized bounded scholarly search",
                            "limitations": [
                                "Absence of a source in this search is not evidence that the phenomenon has never been reported."
                            ],
                        }
                    ],
                    "summary": text,
                    "contradictions": [],
                    "limitations": [
                        "The outcome is limited to the authorized query and provider scope."
                    ],
                    "authorized_result_refs": [],
                    "authorized_literature_refs": ["literature_1"],
                    "stop_outcome": "INSUFFICIENT_EVIDENCE",
                }
            )
            rows.append(row)
            continue
        try:
            output, response = await provider.synthesize(
                research_question=case["research_question"],
                literature_evidence=lit,
                literature_metadata=meta,
                scientific_results=results,
            )
            row.update(
                {
                    "status": "FROZEN",
                    "response_content": _response_text(output),
                    "response_content_sha256": _hash_bytes(_response_text(output).encode()),
                    "provider": response.provider,
                    "model": response.model,
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "repair_attempted": response.repair_attempted,
                    "claims": [claim.model_dump(mode="json") for claim in output.claims],
                    "summary": output.summary,
                    "contradictions": output.contradictions,
                    "limitations": output.limitations,
                    "authorized_result_refs": sorted(results),
                    "authorized_literature_refs": sorted(lit),
                }
            )
        except Exception as exc:
            row["failure"] = f"{type(exc).__name__}: {str(exc)[:500]}"
            if row["generation_attempt"] >= 2:
                text = (
                    "A scientifically validated synthesis could not be produced "
                    "from the authorized evidence under the bounded generation and "
                    "repair policy. No scientific conclusion is asserted. The "
                    "evidence remains available for direct expert inspection."
                )
                row.update(
                    {
                        "status": "FROZEN",
                        "generation_outcome": "VALIDATION_FAILURE_AFTER_DOCUMENTED_RETRY",
                        "response_content": text,
                        "response_content_sha256": _hash_bytes(text.encode()),
                        "provider": "deepseek",
                        "model": baseline["prompt_and_provider"]["model"],
                        "generated_at": datetime.now(timezone.utc).isoformat(),
                        "repair_attempted": True,
                        "claims": [],
                        "summary": text,
                        "contradictions": [],
                        "limitations": [
                            "No provider-generated scientific claim survived the current bounded validator."
                        ],
                        "authorized_result_refs": sorted(results),
                        "authorized_literature_refs": sorted(lit),
                    }
                )
        rows.append(row)
    return {
        "contract_version": FORMAL_RESPONSE_CONTRACT,
        "baseline_id": baseline["baseline_id"],
        "baseline_fingerprint": baseline["baseline_fingerprint"],
        "response_freeze": "FORMAL_RESPONSE_IMMUTABLE=YES",
        "provider_calls_are_not_human_reviews": True,
        "responses": rows,
        "formal_responses_hash": _hash_json(rows),
    }


def build_assignments(
    cases: dict[str, Any], *, baseline_id: str = BASELINE_ID
) -> dict[str, Any]:
    experts = {
        "reviewer_A": ["trajectory_transport", "transport_structure"],
        "reviewer_B": ["structure_coordination", "xrd", "xrd_literature"],
        "reviewer_C": ["electronic_structure", "phonon", "electronic_literature", "phonon_literature"],
        "reviewer_D": ["materials_ml", "materials_ml_composition", "ml_composition", "composition_space", "insufficient_evidence"],
    }
    eligible: dict[str, list[str]] = {}
    loads = {reviewer: 0 for reviewer in experts}
    for case in cases["cases"]:
        pool = [r for r, domains in experts.items() if case["scientific_domain"] in domains or case["class"] == "cross_evidence"]
        if len(pool) < 2:
            pool = list(experts)
        pool.sort(key=lambda r: (loads[r], r))
        selected = pool[:3 if case["anchor"] else 2]
        eligible[case["case_id"]] = selected
        for reviewer in selected:
            loads[reviewer] += 1
    assignments = []
    for case in cases["cases"]:
        for index, reviewer in enumerate(eligible[case["case_id"]], start=1):
            opaque = str(
                uuid5(NAMESPACE_URL, f"{baseline_id}:{reviewer}:{case['case_id']}")
            ).split("-")[0].upper()
            assignments.append(
                {
                    "reviewer_id": reviewer,
                    "case_id": case["case_id"],
                    "reviewer_visible_case_id": f"{reviewer[-1]}-{opaque}",
                    "anchor": False,
                    "reviewer_case_author_conflict": False,
                }
            )
    # Anchor status is administrator-only and must not appear in reviewer packets.
    for row in assignments:
        row["anchor"] = next(item["anchor"] for item in cases["cases"] if item["case_id"] == row["case_id"])
    return {
        "contract_version": "scientist-review-assignments/1.0",
        "baseline_id": baseline_id,
        "target_independent_experts": 4,
        "minimum_independent_experts": 3,
        "expertise": experts,
        "assignments": assignments,
        "formal_record_target": 56,
        "assignment_integrity": "CASE_AUTHOR_CANNOT_SCORE_OWN_FORMAL_CASE",
    }


def _blank_review(
    visible_case_id: str,
    case_id: str,
    pass_name: str,
    *,
    reviewer_id: str,
    response_hash: str,
    evidence_hash: str,
    baseline_id: str = BASELINE_ID,
) -> dict[str, Any]:
    return {
        "review_contract_version": REVIEW_VERSION,
        "baseline_id": baseline_id,
        "reviewer_visible_case_id": visible_case_id,
        "case_id": case_id,
        "reviewer_id": reviewer_id,
        "response_content_sha256": response_hash,
        "evidence_packet_sha256": evidence_hash if pass_name == "PASS2" else None,
        "pass": pass_name,
        "locked": False,
        "submitted_at": None,
        "correction_of_sha256": None,
        "reviewer_expertise_for_case": None,
        "conflict_check": None,
        "pass1": {
            "scientific_acceptability": None,
            "misleading_issue": None,
            "usefulness": None,
            "research_decision_value": None,
        } if pass_name == "PASS1" else None,
        "pass2": None if pass_name == "PASS1" else {
            "rubric_scores": {
                "scientific_correctness": None,
                "evidence_claim_support": None,
                "method_scope_conditions": None,
                "epistemic_calibration": None,
                "contradiction_alternatives": None,
                "limitations_uncertainty": None,
                "research_usefulness": None,
                "auditability_traceability": None,
            },
            "overall_verdict": None,
            "research_decision": None,
            "critical_failure": None,
            "critical_failure_types": [],
            "claim_reviews": [],
            "free_text": {
                "most_problematic": None,
                "missing_qualifier": None,
                "too_strong": None,
                "next_action_change": None,
                "experienced_researcher_difference": None,
            },
        },
    }


def build_packets(
    cases: dict[str, Any],
    responses: dict[str, Any],
    assignments: dict[str, Any],
    *,
    packets_dir: Path = PACKETS,
    baseline_id: str = BASELINE_ID,
) -> None:
    response_by_id = {row["case_id"]: row for row in responses["responses"]}
    case_by_id = {row["case_id"]: row for row in cases["cases"]}
    for reviewer in sorted(assignments["expertise"]):
        rows = [row for row in assignments["assignments"] if row["reviewer_id"] == reviewer]
        random.Random(f"{baseline_id}:{reviewer}").shuffle(rows)
        visible = []
        pass1_forms = []
        pass2 = []
        for row in rows:
            case = case_by_id[row["case_id"]]
            response = response_by_id[row["case_id"]]
            evidence_map = _evidence_label_map(case)
            evidence_packet = [
                {
                    "label": evidence_map[str(item["ref"])]["label"],
                    "origin": item["origin"],
                    "text": item["text"],
                    "scope": item["scope"],
                    "method": item["method"],
                    "conditions": item.get("conditions", []),
                    "lineage": item["lineage"],
                    "limitations": item.get("limitations", []),
                    "evidence_scope": item.get("evidence_scope"),
                    "publication_role": item.get("publication_role"),
                }
                for item in case["authorized_evidence"]
            ]
            evidence_hash = _hash_json(evidence_packet)
            visible.append(
                {
                    "reviewer_visible_case_id": row["reviewer_visible_case_id"],
                    "research_question": case["research_question"],
                    "system_response": _reviewer_safe_text(
                        response.get(
                            "response_content",
                            "No response was generated; mark this packet invalid.",
                        )
                    ),
                    "scientist_view_sources": [
                        {"label": evidence_map[str(item["ref"])]["label"], "origin": "Computed from supplied data" if item["origin"] == "COMPUTED" else "Reported in literature", "method": item["method"], "scope": item.get("evidence_scope") or item["scope"], "limitations": item.get("limitations", [])}
                        for item in case["authorized_evidence"]
                    ],
                }
            )
            pass1_forms.append(
                _blank_review(
                    row["reviewer_visible_case_id"],
                    row["case_id"],
                    "PASS1",
                    reviewer_id=reviewer,
                    response_hash=response["response_content_sha256"],
                    evidence_hash=evidence_hash,
                    baseline_id=baseline_id,
                )
            )
            pass2.append(
                {
                    "reviewer_visible_case_id": row["reviewer_visible_case_id"],
                    "evidence_packet": evidence_packet,
                    "evidence_packet_sha256": evidence_hash,
                    "selected_critical_claims": [
                        {
                            "claim_id": claim.get("claim_id"),
                            "claim": _reviewer_safe_text(
                                claim.get("statement", "")
                            ),
                            "support_refs": [
                                evidence_map[str(ref)]["label"]
                                for ref in (
                                    claim.get("scientific_result_refs", [])
                                    + claim.get("literature_evidence_refs", [])
                                )
                            ],
                        }
                        for claim in response.get("claims", [])
                    ],
                    "submission_template": _blank_review(
                        row["reviewer_visible_case_id"],
                        row["case_id"],
                        "PASS2",
                        reviewer_id=reviewer,
                        response_hash=response["response_content_sha256"],
                        evidence_hash=evidence_hash,
                        baseline_id=baseline_id,
                    ),
                }
            )
        directory = packets_dir / reviewer
        directory.mkdir(parents=True, exist_ok=True)
        _write(directory / "assigned_cases.json", {"reviewer_visible_only": True, "cases": visible})
        _write(directory / "pass1_submission_template.json", {"instructions": "Complete independently from the scientist-facing packet.", "records": pass1_forms})
        _write(directory / "pass2_reveal_DO_NOT_SEND_BEFORE_PASS1_LOCK.json", {"evidence_records": pass2})
        _write(
            directory / "calibration_cases.json",
            {
                "instructions": "Score all four independently before viewing calibration guidance.",
                "cases": [
                    {
                        "case_id": item["case_id"],
                        "question": item["question"],
                        "evidence": item["evidence"],
                        "system_response": item["system_response"],
                    }
                    for item in cases["calibration"]
                ],
            },
        )
        _write(
            directory / "calibration_guidance_DO_NOT_REVEAL_BEFORE_CALIBRATION_LOCK.json",
            {
                "guidance": [
                    {"case_id": item["case_id"], "guidance": item["guidance"]}
                    for item in cases["calibration"]
                ]
            },
        )
        packet_manifest = {
            "baseline_id": baseline_id,
            "reviewer_id": reviewer,
            "assigned_case_count": len(rows),
            "assigned_visible_ids": [row["reviewer_visible_case_id"] for row in rows],
            "assigned_cases_sha256": _hash_json(visible),
            "pass1_template_sha256": _hash_json(pass1_forms),
            "pass2_reveal_sha256": _hash_json(pass2),
            "provider_identity_disclosed": False,
            "expected_labels_disclosed": False,
            "hidden_reasoning_disclosed": False,
        }
        packet_manifest["packet_manifest_sha256"] = _hash_json(packet_manifest)
        _write(directory / "packet_integrity.json", packet_manifest)
        (directory / "README.md").write_text(
            f"# Independent Scientist Review Packet — {reviewer}\n\n"
            "This packet is reviewer-blinded. Do not infer provider, model, Workstream, "
            "case quality, expected labels, or repair history. Complete Pass 1 first. "
            "After Pass 1 is locked, an administrator may release the Pass 2 evidence file. "
            "Submit records without changing the response text. Do not score a case you authored.\n",
            encoding="utf-8",
        )


def _empty_review_ledger() -> dict[str, Any]:
    return {
        "contract_version": "scientist-review-ledger/1.0",
        "status": "AWAITING_INDEPENDENT_HUMAN_SUBMISSIONS",
        "review_records": [],
        "must_not_be_populated_by_model": True,
    }


def _preparation_summary(
    responses: dict[str, Any], *, baseline_id: str
) -> dict[str, Any]:
    outcomes = Counter(
        str(row.get("generation_outcome") or "VALIDATED_PROVIDER_RESPONSE")
        for row in responses.get("responses", [])
    )
    return {
        "j_status": "REVIEW_READY",
        "j_review_infrastructure": "READY",
        "j_formal_responses": "FROZEN",
        "independent_human_expert_validation": "PENDING",
        "scientist_validation_maturity": "NOT_YET_ASSESSED",
        "independent_experts_with_submissions": 0,
        "formal_scored_cases": EXPECTED_FORMAL_RESPONSE_COUNT,
        "valid_scored_cases": 0,
        "critical_scientific_failures": 0,
        "generation_outcomes": dict(outcomes),
        "baseline_id": baseline_id,
        "human_boundary": "No human scores or reviewer conclusions exist in this artifact.",
    }


def _verify_preparation_dir(
    directory: Path, *, require_empty_review_ledger: bool = False
) -> list[str]:
    required = [
        "evaluation_baseline.json", "human_review_cases.json", "formal_responses.json",
        "reviewer_assignments.json", "reviewer_scores.json", "disagreement_ledger.json",
        "scientist_validation_summary.json",
    ]
    missing = [name for name in required if not (directory / name).is_file()]
    if missing:
        return [f"PREPARATION_FILE_MISSING:{name}" for name in missing]
    cases = json.loads((directory / "human_review_cases.json").read_text(encoding="utf-8"))
    baseline = json.loads((directory / "evaluation_baseline.json").read_text(encoding="utf-8"))
    responses = json.loads((directory / "formal_responses.json").read_text(encoding="utf-8"))
    assignments = json.loads((directory / "reviewer_assignments.json").read_text(encoding="utf-8"))
    scores = json.loads((directory / "reviewer_scores.json").read_text(encoding="utf-8"))
    errors = _validate_formal_response_set(cases, responses, baseline)
    expected_ids = _formal_case_ids(cases)
    assignment_rows = assignments.get("assignments")
    if not isinstance(assignment_rows, list) or len(assignment_rows) != 56:
        errors.append("ASSIGNMENT_SET_INVALID")
    else:
        keys = [(row.get("reviewer_id"), row.get("case_id"), row.get("reviewer_visible_case_id")) for row in assignment_rows]
        if len(keys) != len(set(keys)):
            errors.append("ASSIGNMENT_DUPLICATE_KEY")
        if set(row.get("case_id") for row in assignment_rows) != set(expected_ids):
            errors.append("ASSIGNMENT_CASE_SET_MISMATCH")
        if assignments.get("baseline_id") != baseline.get("baseline_id"):
            errors.append("ASSIGNMENT_BASELINE_MISMATCH")
    if require_empty_review_ledger and scores.get("review_records"):
        errors.append("PREPARATION_CONTAINS_HUMAN_RECORDS")
    if responses.get("freeze_status") != "FROZEN":
        errors.append("FORMAL_RESPONSES_NOT_FROZEN")
    return sorted(set(errors))


def prepare(*, live: bool, output_dir: Path = OUT) -> int:
    """Build a new candidate atomically; never repair an existing candidate."""

    # All guards happen before the first write. Existing frozen candidates and
    # human records are never preparation input and are never overwritten.
    if output_dir.exists():
        raise SystemExit(
            "destination must be absent; use a new candidate directory"
        )
    if not live:
        raise SystemExit(
            "offline preparation cannot freeze formal responses without an authorized response set"
        )

    cases = build_cases()
    baseline = build_baseline(cases, excluded_paths=(output_dir,))
    assignments = build_assignments(cases, baseline_id=baseline["baseline_id"])
    responses = asyncio.run(generate_formal_responses(cases, baseline))
    responses["freeze_status"] = (
        "FROZEN"
        if all(row.get("status") == "FROZEN" for row in responses.get("responses", []))
        else "INCOMPLETE_PROVIDER_GENERATION"
    )
    errors = _validate_formal_response_set(cases, responses, baseline)
    if responses["freeze_status"] != "FROZEN":
        errors.append("FORMAL_RESPONSES_NOT_FROZEN")
    if errors:
        raise SystemExit("candidate rejected before publish: " + ", ".join(errors))

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(
        tempfile.mkdtemp(prefix=f".{output_dir.name}.staging-", dir=output_dir.parent)
    )
    published = False
    try:
        _write(staging / "evaluation_baseline.json", baseline)
        _write(staging / "human_review_cases.json", cases)
        _write(staging / "formal_responses.json", responses)
        _write(staging / "reviewer_assignments.json", assignments)
        _write(staging / "reviewer_scores.json", _empty_review_ledger())
        _write(
            staging / "disagreement_ledger.json",
            {
                "contract_version": "scientist-disagreement-ledger/1.0",
                "status": "AWAITING_HUMAN_REVIEWS",
                "items": [],
            },
        )
        _write(
            staging / "scientist_validation_summary.json",
            _preparation_summary(responses, baseline_id=baseline["baseline_id"]),
        )
        build_packets(
            cases,
            responses,
            assignments,
            packets_dir=staging / "reviewer_packets",
            baseline_id=baseline["baseline_id"],
        )
        staged_errors = _verify_preparation_dir(
            staging, require_empty_review_ledger=True
        )
        if staged_errors:
            raise SystemExit(
                "staged candidate rejected before publish: " + ", ".join(staged_errors)
            )
        if output_dir.exists():
            raise SystemExit("destination appeared during preparation; nothing published")
        os.replace(staging, output_dir)
        published = True
        staging = Path()
    finally:
        if not published and staging.exists():
            shutil.rmtree(staging, ignore_errors=True)

    print(json.dumps({
        "cases": len(cases["cases"]),
        "calibration": len(cases["calibration"]),
        "shadow": len(cases["shadow_cases"]),
        "formal_response_status": responses["freeze_status"],
        "formal_review_records": 0,
        "published_directory": str(output_dir),
    }, indent=2))
    return 0

def _load_preparation(directory: Path = OUT) -> tuple[dict[str, Any], ...]:
    return tuple(
        json.loads((directory / name).read_text(encoding="utf-8"))
        for name in (
            "evaluation_baseline.json",
            "human_review_cases.json",
            "formal_responses.json",
            "reviewer_assignments.json",
            "reviewer_scores.json",
        )
    )


def _is_historical_candidate(directory: Path) -> bool:
    try:
        baseline = json.loads(
            (directory / "evaluation_baseline.json").read_text(encoding="utf-8")
        )
    except (FileNotFoundError, json.JSONDecodeError):
        return False
    return baseline.get("baseline_id") == BASELINE_ID


def _verify_review_ledger(
    directory: Path = OUT, *, ledger_override: dict[str, Any] | None = None
) -> list[str]:
    """Verify human submissions independently from preparation integrity."""

    try:
        baseline, cases, responses, assignments, loaded_ledger = _load_preparation(directory)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        return [f"REVIEW_LEDGER_INPUT_INVALID:{type(exc).__name__}"]
    ledger = ledger_override if ledger_override is not None else loaded_ledger

    errors: list[str] = []
    if ledger.get("contract_version") != "scientist-review-ledger/1.0":
        errors.append("REVIEW_LEDGER_CONTRACT_MISMATCH")
    if ledger.get("must_not_be_populated_by_model") is not True:
        errors.append("REVIEW_LEDGER_HUMAN_BOUNDARY_MISSING")
    expected_cases = set(_formal_case_ids(cases))
    assignment_keys = {
        (row.get("reviewer_id"), row.get("case_id"), pass_name)
        for row in assignments.get("assignments", [])
        for pass_name in ("PASS1", "PASS2")
    }
    response_by_case = {
        row.get("case_id"): row for row in responses.get("responses", [])
    }
    records = ledger.get("review_records")
    if not isinstance(records, list):
        return ["REVIEW_RECORDS_NOT_LIST"]
    expected_status = (
        "HUMAN_SUBMISSIONS_PRESENT"
        if records
        else "AWAITING_INDEPENDENT_HUMAN_SUBMISSIONS"
    )
    if ledger.get("status") != expected_status:
        errors.append("REVIEW_LEDGER_STATUS_MISMATCH")

    seen_versions: set[tuple[str, str, str, int]] = set()
    latest_by_key: dict[tuple[str, str, str], dict[str, Any]] = {}
    versions_by_key: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    pass1_keys: set[tuple[str, str]] = set()
    ingested_times: dict[int, datetime] = {}
    for record in records:
        reviewer = record.get("reviewer_id")
        case_id = record.get("case_id")
        pass_name = record.get("pass")
        raw_version = record.get("record_version")
        if (
            not isinstance(raw_version, int)
            or isinstance(raw_version, bool)
            or raw_version < 1
        ):
            errors.append(
                f"REVIEW_RECORD_VERSION_INVALID:{case_id}:{reviewer}:{pass_name}"
            )
            version = 0
        else:
            version = raw_version
        key = (reviewer, case_id, pass_name)
        versions_by_key[key].append(record)
        version_key = (*key, version)
        try:
            _validate_review_payload(record, directory)
        except SystemExit as exc:
            errors.append(
                f"REVIEW_PAYLOAD_INVALID:{case_id}:{reviewer}:{pass_name}:{exc}"
            )
        recorded_hash = record.get("record_sha256")
        expected_hash = _hash_json(
            {name: value for name, value in record.items() if name != "record_sha256"}
        )
        if not recorded_hash or recorded_hash != expected_hash:
            errors.append(f"REVIEW_RECORD_HASH_MISMATCH:{case_id}:{reviewer}:{pass_name}")
        source_hash = record.get("source_submission_sha256")
        if (
            not isinstance(source_hash, str)
            or len(source_hash) != 64
            or any(char not in "0123456789abcdef" for char in source_hash)
        ):
            errors.append(
                f"REVIEW_SOURCE_SUBMISSION_HASH_INVALID:{case_id}:{reviewer}:{pass_name}"
            )
        ingested_at = record.get("ingested_at")
        try:
            parsed = datetime.fromisoformat(str(ingested_at))
            if parsed.tzinfo is None or parsed.utcoffset() is None:
                raise ValueError("timezone required")
            ingested_times[id(record)] = parsed
        except (TypeError, ValueError):
            errors.append(
                f"REVIEW_INGESTED_AT_INVALID:{case_id}:{reviewer}:{pass_name}"
            )
        if version_key in seen_versions:
            errors.append(f"REVIEW_RECORD_DUPLICATE_VERSION:{version_key}")
        seen_versions.add(version_key)
        if case_id not in expected_cases:
            errors.append(f"REVIEW_CASE_FOREIGN:{case_id}")
        if record.get("baseline_id") != baseline.get("baseline_id"):
            errors.append(f"REVIEW_BASELINE_MISMATCH:{case_id}:{reviewer}")
        if key not in assignment_keys:
            errors.append(f"REVIEW_ASSIGNMENT_MISMATCH:{case_id}:{reviewer}:{pass_name}")
        if record.get("locked") is not True or not record.get("submitted_at"):
            errors.append(f"REVIEW_NOT_LOCKED:{case_id}:{reviewer}:{pass_name}")
        if record.get("reviewer_expertise_for_case") not in {
            "PRIMARY",
            "COMPETENT",
            "LIMITED",
        }:
            errors.append(f"REVIEW_EXPERTISE_INVALID:{case_id}:{reviewer}")
        if record.get("conflict_check") != "NO_CONFLICT":
            errors.append(f"REVIEW_CONFLICT_NOT_CLEARED:{case_id}:{reviewer}")
        response = response_by_case.get(case_id)
        if response is None or record.get("response_content_sha256") != response.get(
            "response_content_sha256"
        ):
            errors.append(f"REVIEW_RESPONSE_HASH_MISMATCH:{case_id}:{reviewer}")
        if pass_name == "PASS1":
            pass1_keys.add((reviewer, case_id))
        elif pass_name == "PASS2":
            # Records are append-only but may not be sorted; defer the check
            # until all PASS1 records have been collected below.
            pass
        else:
            errors.append(f"REVIEW_PASS_INVALID:{case_id}:{reviewer}:{pass_name}")
        previous = latest_by_key.get(key)
        if previous is not None:
            if version <= int(previous.get("record_version") or 0):
                errors.append(f"REVIEW_VERSION_NOT_INCREASING:{case_id}:{reviewer}:{pass_name}")
            if record.get("correction_of_sha256") != previous.get("record_sha256"):
                errors.append(f"REVIEW_CORRECTION_CHAIN_INVALID:{case_id}:{reviewer}:{pass_name}")
        elif version != 1:
            errors.append(f"REVIEW_INITIAL_VERSION_INVALID:{case_id}:{reviewer}:{pass_name}")
        latest_by_key[key] = record

    for key, version_rows in versions_by_key.items():
        ordered = sorted(
            version_rows, key=lambda item: int(item.get("record_version") or 0)
        )
        for expected_version, record in enumerate(ordered, start=1):
            actual_version = record.get("record_version")
            if actual_version != expected_version:
                errors.append(f"REVIEW_VERSION_NOT_CONTIGUOUS:{key}")
                break
            if expected_version == 1:
                if record.get("correction_of_sha256") is not None:
                    errors.append(f"REVIEW_INITIAL_CORRECTION_POINTER_INVALID:{key}")
            elif record.get("correction_of_sha256") != ordered[
                expected_version - 2
            ].get("record_sha256"):
                errors.append(f"REVIEW_CORRECTION_CHAIN_INVALID:{key}")

    for record in records:
        if record.get("pass") == "PASS2" and (
            record.get("reviewer_id"),
            record.get("case_id"),
        ) not in pass1_keys:
            errors.append(
                f"PASS2_BEFORE_PASS1:{record.get('case_id')}:{record.get('reviewer_id')}"
            )
        elif record.get("pass") == "PASS2":
            pass1_times = [
                ingested_times[id(item)]
                for item in records
                if item.get("pass") == "PASS1"
                and item.get("reviewer_id") == record.get("reviewer_id")
                and item.get("case_id") == record.get("case_id")
                and id(item) in ingested_times
            ]
            pass2_time = ingested_times.get(id(record))
            if pass2_time is not None and (
                not pass1_times or min(pass1_times) > pass2_time
            ):
                errors.append(
                    f"PASS2_BEFORE_PASS1:{record.get('case_id')}:{record.get('reviewer_id')}"
                )
    return sorted(set(errors))


def verify_reviews(directory: Path = OUT) -> int:
    errors = _verify_review_ledger(directory)
    try:
        ledger = json.loads(
            (directory / "reviewer_scores.json").read_text(encoding="utf-8")
        )
        count = len(ledger.get("review_records", []))
    except (FileNotFoundError, json.JSONDecodeError):
        count = None
    payload = {
        "verification": "HUMAN_REVIEW_LEDGER_ONLY",
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "review_records": count,
        "scientist_validation": "NOT_ASSESSED",
    }
    print(json.dumps(payload, indent=2))
    return 0 if not errors else 1


def verify(directory: Path = OUT) -> int:
    """Verify preparation artifacts only; human records are a separate ledger."""

    required = [
        "evaluation_baseline.json",
        "human_review_cases.json",
        "formal_responses.json",
        "reviewer_assignments.json",
        "reviewer_scores.json",
        "disagreement_ledger.json",
        "scientist_validation_summary.json",
    ]
    missing = [name for name in required if not (directory / name).exists()]
    if missing:
        print(json.dumps({"verification": "PREPARATION_ONLY", "status": "FAIL", "missing": missing}, indent=2))
        return 1
    baseline = json.loads((directory / "evaluation_baseline.json").read_text(encoding="utf-8"))
    # The pre-R0 candidate is historical evidence. Preserve it and report it
    # honestly rather than applying the new candidate contract retroactively.
    if baseline.get("baseline_id") == BASELINE_ID:
        print(json.dumps({
            "verification": "PREPARATION_ONLY",
            "status": "HISTORICAL_FROZEN_CANDIDATE",
            "historical_candidate": True,
            "human_review_verification": "RUN verify-reviews SEPARATELY",
            "scientist_validation": "NOT_ASSESSED",
        }, indent=2))
        return 0
    errors = _verify_preparation_dir(directory)
    print(json.dumps({
        "verification": "PREPARATION_ONLY",
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "human_review_verification": "RUN verify-reviews SEPARATELY",
        "scientist_validation": "NOT_ASSESSED",
    }, indent=2))
    return 0 if not errors else 1


def _assignment_for(
    payload: dict[str, Any], directory: Path = OUT
) -> dict[str, Any]:
    assignments = json.loads(
        (directory / "reviewer_assignments.json").read_text(encoding="utf-8")
    )["assignments"]
    matches = [
        row
        for row in assignments
        if row["reviewer_id"] == payload.get("reviewer_id")
        and row["case_id"] == payload.get("case_id")
        and row["reviewer_visible_case_id"]
        == payload.get("reviewer_visible_case_id")
    ]
    if len(matches) != 1:
        raise SystemExit("review submission does not match one frozen assignment")
    if matches[0]["reviewer_case_author_conflict"]:
        raise SystemExit("case author may not score their own formal case")
    return matches[0]


def _validate_review_payload(
    payload: dict[str, Any], directory: Path = OUT
) -> None:
    if payload.get("review_contract_version") != REVIEW_VERSION:
        raise SystemExit("unsupported review contract")
    try:
        baseline = json.loads(
            (directory / "evaluation_baseline.json").read_text(encoding="utf-8")
        )
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise SystemExit("frozen preparation baseline is unavailable") from exc
    if payload.get("baseline_id") != baseline.get("baseline_id"):
        raise SystemExit("review baseline does not match the frozen candidate")
    if payload.get("locked") is not True or not payload.get("submitted_at"):
        raise SystemExit("human review must be explicitly locked with submitted_at")
    if payload.get("reviewer_expertise_for_case") not in {
        "PRIMARY",
        "COMPETENT",
        "LIMITED",
    }:
        raise SystemExit("reviewer expertise must be PRIMARY, COMPETENT, or LIMITED")
    if payload.get("conflict_check") != "NO_CONFLICT":
        raise SystemExit("review cannot be imported until conflicts are cleared")
    _assignment_for(payload, directory)
    responses = json.loads(
        (directory / "formal_responses.json").read_text(encoding="utf-8")
    )["responses"]
    response = next(
        (row for row in responses if row["case_id"] == payload["case_id"]), None
    )
    if response is None:
        raise SystemExit("formal response does not exist")
    if payload.get("response_content_sha256") != response.get(
        "response_content_sha256"
    ):
        raise SystemExit("reviewed response hash does not match the frozen response")
    pass_name = payload.get("pass")
    if pass_name == "PASS1":
        row = payload.get("pass1") or {}
        if set(row) != {
            "scientific_acceptability",
            "misleading_issue",
            "usefulness",
            "research_decision_value",
        }:
            raise SystemExit("Pass 1 payload fields are incomplete or unexpected")
        if row.get("scientific_acceptability") not in {
            "YES",
            "NO",
            "UNCERTAIN",
        }:
            raise SystemExit("invalid Pass 1 scientific_acceptability")
        if row.get("misleading_issue") not in {"YES", "NO", "UNCERTAIN"}:
            raise SystemExit("invalid Pass 1 misleading_issue")
        if row.get("usefulness") not in {"YES", "YES_WITH_MINOR_REVIEW", "NO"}:
            raise SystemExit("invalid Pass 1 usefulness")
        if row.get("research_decision_value") not in {
            "YES",
            "YES_WITH_MINOR_REVIEW",
            "NO",
        }:
            raise SystemExit("invalid Pass 1 research_decision_value")
        if payload.get("pass2") is not None:
            raise SystemExit("Pass 1 submission must not contain Pass 2 ratings")
        return
    if pass_name != "PASS2":
        raise SystemExit("review pass must be PASS1 or PASS2")
    row = payload.get("pass2") or {}
    if payload.get("pass1") is not None:
        raise SystemExit("Pass 2 submission must not contain Pass 1 ratings")
    if set(row) != {
        "rubric_scores",
        "overall_verdict",
        "research_decision",
        "critical_failure",
        "critical_failure_types",
        "claim_reviews",
        "free_text",
    }:
        raise SystemExit("Pass 2 payload fields are incomplete or unexpected")
    expected_scores = {
        "scientific_correctness",
        "evidence_claim_support",
        "method_scope_conditions",
        "epistemic_calibration",
        "contradiction_alternatives",
        "limitations_uncertainty",
        "research_usefulness",
        "auditability_traceability",
    }
    scores = row.get("rubric_scores") or {}
    if set(scores) != expected_scores:
        raise SystemExit("Pass 2 rubric dimensions are incomplete")
    if any(value not in {1, 2, 3, 4, 5, "N/A"} for value in scores.values()):
        raise SystemExit("Pass 2 scores must be 1-5 or N/A")
    if row.get("overall_verdict") not in {
        "ACCEPT",
        "MINOR_REVISION",
        "MAJOR_REVISION",
        "REJECT",
    }:
        raise SystemExit("invalid overall verdict")
    if row.get("research_decision") not in {
        "YES",
        "YES_WITH_MINOR_REVIEW",
        "NO",
    }:
        raise SystemExit("invalid research-decision answer")
    if not isinstance(row.get("critical_failure"), bool):
        raise SystemExit("critical_failure must be true or false")
    if row["critical_failure"] and not row.get("critical_failure_types"):
        raise SystemExit("critical failure requires at least one typed reason")
    if not isinstance(row.get("critical_failure_types"), list) or any(
        not isinstance(item, str) or not item.strip()
        for item in row["critical_failure_types"]
    ):
        raise SystemExit("critical_failure_types must be a list of non-empty strings")
    claim_reviews = row.get("claim_reviews")
    if not isinstance(claim_reviews, list):
        raise SystemExit("claim_reviews must be a list")
    claim_ids: set[str] = set()
    allowed_claim_ids = {
        str(claim.get("claim_id"))
        for claim in response.get("claims", [])
        if claim.get("claim_id")
    }
    for claim_review in claim_reviews:
        claim_id = str(claim_review.get("claim_id") or "")
        if not claim_id or claim_id in claim_ids or claim_id not in allowed_claim_ids:
            raise SystemExit("claim review must reference one unique frozen claim_id")
        claim_ids.add(claim_id)
        if claim_review.get("support") not in {
            "DIRECT",
            "SUPPORTED_WITHIN_SCOPE",
            "SUGGESTIVE",
            "CONFLICTED",
            "INSUFFICIENT",
            "UNSUPPORTED",
        }:
            raise SystemExit("invalid claim support rating")
        if claim_review.get("strength") not in {
            "APPROPRIATE",
            "TOO_STRONG",
            "TOO_WEAK",
        }:
            raise SystemExit("invalid claim strength rating")
        if claim_review.get("scope") not in {"PRESERVED", "EXPANDED", "UNCLEAR"}:
            raise SystemExit("invalid claim scope rating")
        if claim_review.get("method_conditions") not in {
            "PRESERVED",
            "IMPORTANT_INFORMATION_MISSING",
            "NOT_APPLICABLE",
        }:
            raise SystemExit("invalid claim method/conditions rating")
        if claim_review.get("critical_limitation") not in {
            "PRESENT",
            "MISSING",
            "NOT_APPLICABLE",
        }:
            raise SystemExit("invalid claim limitation rating")
    free_text = row.get("free_text")
    expected_free_text = {
        "most_problematic",
        "missing_qualifier",
        "too_strong",
        "next_action_change",
        "experienced_researcher_difference",
    }
    if not isinstance(free_text, dict) or set(free_text) != expected_free_text:
        raise SystemExit("Pass 2 free_text fields are incomplete or unexpected")
    if any(value is not None and not isinstance(value, str) for value in free_text.values()):
        raise SystemExit("Pass 2 free_text values must be strings or null")
    if not payload.get("evidence_packet_sha256"):
        raise SystemExit("Pass 2 evidence packet hash is required")
    reveal_path = (
        directory / "reviewer_packets"
        / payload["reviewer_id"]
        / "pass2_reveal_DO_NOT_SEND_BEFORE_PASS1_LOCK.json"
    )
    reveal = json.loads(reveal_path.read_text(encoding="utf-8"))
    expected = next(
        (
            row["evidence_packet_sha256"]
            for row in reveal["evidence_records"]
            if row["reviewer_visible_case_id"]
            == payload["reviewer_visible_case_id"]
        ),
        None,
    )
    if payload["evidence_packet_sha256"] != expected:
        raise SystemExit("reviewed evidence hash does not match the frozen packet")


def import_reviews(path: Path, candidate_dir: Path = OUT) -> int:
    if _is_historical_candidate(candidate_dir):
        raise SystemExit(
            "historical pre-correction candidate is read-only and cannot accept reviews"
        )
    payload = json.loads(path.read_text(encoding="utf-8"))
    _validate_review_payload(payload, candidate_dir)
    ledger_path = candidate_dir / "reviewer_scores.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    current_errors = _verify_review_ledger(candidate_dir)
    if current_errors:
        raise SystemExit(
            "current review ledger is invalid; import refused: "
            + ", ".join(current_errors)
        )
    matching = [
        row
        for row in ledger["review_records"]
        if row.get("reviewer_id") == payload["reviewer_id"]
        and row.get("case_id") == payload["case_id"]
        and row.get("pass") == payload["pass"]
    ]
    existing = {
        (row.get("reviewer_id"), row.get("case_id"), row.get("pass"))
        for row in ledger["review_records"]
    }
    key = (payload["reviewer_id"], payload["case_id"], payload["pass"])
    if matching:
        latest = sorted(
            matching, key=lambda row: int(row.get("record_version") or 1)
        )[-1]
        if payload.get("correction_of_sha256") != latest.get("record_sha256"):
            raise SystemExit(
                "duplicate review requires correction_of_sha256 matching the latest record"
            )
        payload["record_version"] = int(latest.get("record_version") or 1) + 1
    else:
        payload["record_version"] = 1
    if payload["pass"] == "PASS2" and (
        payload["reviewer_id"], payload["case_id"], "PASS1"
    ) not in existing:
        raise SystemExit("Pass 2 cannot be imported before locked Pass 1")
    payload["source_submission_sha256"] = _hash_bytes(path.read_bytes())
    payload["ingested_at"] = datetime.now(timezone.utc).isoformat()
    payload["record_sha256"] = _hash_json({k: v for k, v in payload.items() if k != "record_sha256"})
    ledger["review_records"].append(payload)
    ledger["review_records"].sort(
        key=lambda row: (
            row.get("case_id", ""),
            row.get("reviewer_id", ""),
            row.get("pass", ""),
            int(row.get("record_version") or 0),
        )
    )
    ledger["status"] = "HUMAN_SUBMISSIONS_PRESENT"
    ledger_errors = _verify_review_ledger(candidate_dir, ledger_override=ledger)
    if ledger_errors:
        raise SystemExit(
            "prospective review ledger rejected before write: "
            + ", ".join(ledger_errors)
        )
    encoded = (
        json.dumps(ledger, ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")
    temporary = ledger_path.with_name(
        f".{ledger_path.name}.{os.getpid()}.tmp"
    )
    try:
        with temporary.open("xb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, ledger_path)
    finally:
        temporary.unlink(missing_ok=True)
    print(json.dumps({"imported": key, "total_records": len(ledger["review_records"])}, indent=2))
    return 0


_VERDICT_RANK = {
    "REJECT": 1,
    "MAJOR_REVISION": 2,
    "MINOR_REVISION": 3,
    "ACCEPT": 4,
}


def _ordinal_alpha(units: dict[str, list[float]]) -> float | None:
    pair_distances: list[float] = []
    all_values: list[float] = []
    for values in units.values():
        all_values.extend(values)
        for index, left in enumerate(values):
            for right in values[index + 1 :]:
                pair_distances.append((left - right) ** 2)
    if not pair_distances or len(all_values) < 2:
        return None
    observed = sum(pair_distances) / len(pair_distances)
    expected_pairs = [
        (left - right) ** 2
        for index, left in enumerate(all_values)
        for right in all_values[index + 1 :]
    ]
    expected = sum(expected_pairs) / len(expected_pairs)
    if expected == 0:
        return 1.0
    return round(1.0 - observed / expected, 4)


def _complete_pass2(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    latest: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in records:
        key = (
            str(row.get("reviewer_id")),
            str(row.get("case_id")),
            str(row.get("pass")),
        )
        if int(row.get("record_version") or 1) >= int(
            latest.get(key, {}).get("record_version") or 0
        ):
            latest[key] = row
    return [row for row in latest.values() if row.get("pass") == "PASS2"]


def _material_disagreements(
    pass2: list[dict[str, Any]], case_meta: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    by_case: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in pass2:
        by_case[row["case_id"]].append(row)
    critical_keys = {
        "scientific_correctness",
        "evidence_claim_support",
        "method_scope_conditions",
        "epistemic_calibration",
        "limitations_uncertainty",
    }
    disagreements: list[dict[str, Any]] = []
    for case_id, rows in by_case.items():
        if len(rows) < 2:
            continue
        reasons: set[str] = set()
        verdicts = [
            _VERDICT_RANK[row["pass2"]["overall_verdict"]] for row in rows
        ]
        if max(verdicts) - min(verdicts) >= 2:
            reasons.add("OVERALL_VERDICT_DIFFERS_BY_TWO_LEVELS")
        for key in critical_keys:
            values = [
                row["pass2"]["rubric_scores"][key]
                for row in rows
                if isinstance(row["pass2"]["rubric_scores"][key], int)
            ]
            if values and max(values) - min(values) >= 2:
                reasons.add(f"CRITICAL_DIMENSION_DISAGREEMENT:{key}")
        claim_supports: dict[str, set[str]] = defaultdict(set)
        for row in rows:
            for claim in row["pass2"].get("claim_reviews", []):
                claim_id = str(claim.get("claim_id") or "")
                if claim_id:
                    claim_supports[claim_id].add(str(claim.get("support")))
        for claim_id, values in claim_supports.items():
            if {"DIRECT", "SUPPORTED_WITHIN_SCOPE"} & values and {
                "INSUFFICIENT",
                "UNSUPPORTED",
            } & values:
                reasons.add(f"CLAIM_SUPPORT_DISAGREEMENT:{claim_id}")
        if reasons:
            disagreements.append(
                {
                    "case_id": case_id,
                    "anchor": case_meta[case_id]["anchor"],
                    "reviewers": sorted(row["reviewer_id"] for row in rows),
                    "reasons": sorted(reasons),
                    "next_action": "THIRD_INDEPENDENT_REVIEW"
                    if len(rows) == 2
                    else "STRUCTURED_ADJUDICATION",
                }
            )
    return disagreements


def report(directory: Path = OUT) -> int:
    baseline = json.loads(
        (directory / "evaluation_baseline.json").read_text(encoding="utf-8")
    )
    if baseline.get("baseline_id") == BASELINE_ID:
        payload = {
            "analysis_kind": "HISTORICAL_CANDIDATE_ADVISORY",
            "j_status": "REVIEW_READY",
            "independent_human_expert_validation": "PENDING",
            "scientist_validation_maturity": "NOT_YET_ASSESSED",
            "candidate": "PRE_CORRECTION_SCIENTIFIC_CANDIDATE",
            "note": (
                "The historical frozen candidate is preserved byte-for-byte. "
                "R0 does not rewrite its summary or describe preparation as scientist validation."
            ),
        }
        print(json.dumps(payload, indent=2))
        return 0
    preparation_errors = _verify_preparation_dir(directory)
    review_errors = _verify_review_ledger(directory)
    if preparation_errors or review_errors:
        print(
            json.dumps(
                {
                    "analysis_kind": "DESCRIPTIVE_HUMAN_REVIEW_ANALYSIS_ONLY",
                    "status": "FAIL_CLOSED_INVALID_EVIDENCE",
                    "preparation_errors": preparation_errors,
                    "review_ledger_errors": review_errors,
                    "report_artifacts_written": False,
                    "scientist_validation_maturity": "NOT_ASSESSED",
                },
                indent=2,
            )
        )
        return 1
    scores = json.loads((directory / "reviewer_scores.json").read_text(encoding="utf-8"))
    records = scores.get("review_records", [])
    cases = json.loads(
        (directory / "human_review_cases.json").read_text(encoding="utf-8")
    )["cases"]
    case_meta = {row["case_id"]: row for row in cases}
    pass2 = _complete_pass2(records)
    by_case: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in pass2:
        by_case[row["case_id"]].append(row)
    reviewers = sorted({row["reviewer_id"] for row in records})
    disagreements = _material_disagreements(pass2, case_meta)
    _write(
        directory / "disagreement_ledger.json",
        {
            "contract_version": "scientist-disagreement-ledger/1.0",
            "status": "PENDING_THIRD_REVIEW_OR_ADJUDICATION"
            if disagreements
            else ("NO_MATERIAL_DISAGREEMENT_DETECTED" if pass2 else "AWAITING_HUMAN_REVIEWS"),
            "items": disagreements,
        },
    )
    valid_cases = [
        case_id
        for case_id, rows in by_case.items()
        if len(rows) >= (3 if case_meta[case_id]["anchor"] else 2)
    ]
    dimensions = {
        "scientific_correctness": "SCIENTIFIC_CORRECTNESS_MEDIAN",
        "evidence_claim_support": "EVIDENCE_SUPPORT_MEDIAN",
        "method_scope_conditions": "METHOD_SCOPE_MEDIAN",
        "epistemic_calibration": "EPISTEMIC_CALIBRATION_MEDIAN",
        "limitations_uncertainty": "LIMITATION_MEDIAN",
    }
    medians: dict[str, float | None] = {}
    alphas: dict[str, float | None] = {}
    for key, label in dimensions.items():
        values = [
            row["pass2"]["rubric_scores"][key]
            for row in pass2
            if isinstance(row["pass2"]["rubric_scores"][key], int)
        ]
        medians[label] = median(values) if values else None
        units = {
            case_id: [
                float(row["pass2"]["rubric_scores"][key])
                for row in rows
                if isinstance(row["pass2"]["rubric_scores"][key], int)
            ]
            for case_id, rows in by_case.items()
        }
        alphas[key] = _ordinal_alpha(units)
    verdict_units = {
        case_id: [
            float(_VERDICT_RANK[row["pass2"]["overall_verdict"]]) for row in rows
        ]
        for case_id, rows in by_case.items()
    }
    verdict_counts = Counter(
        row["pass2"]["overall_verdict"] for row in pass2
    )
    formal_integrity_complete = (
        len(reviewers) >= 3
        and len(valid_cases) == 24
        and all(
            len(by_case[case["case_id"]]) >= (3 if case["anchor"] else 2)
            for case in cases
        )
    )
    summary = {
        "analysis_kind": "DESCRIPTIVE_HUMAN_REVIEW_ANALYSIS_ONLY",
        "j_status": (
            "HUMAN_REVIEW_DESCRIPTIVE_ANALYSIS_READY"
            if formal_integrity_complete
            else ("REVIEW_READY" if not records else "HUMAN_REVIEW_INCOMPLETE")
        ),
        "j_review_infrastructure": "READY",
        "j_formal_responses": "FROZEN",
        "independent_human_expert_validation": "PENDING",
        "scientist_validation_maturity": "NOT_YET_ASSESSED",
        "INDEPENDENT_EXPERTS": len(reviewers),
        "SCORED_CASES": 24,
        "VALID_SCORED_CASES": len(valid_cases),
        "CALIBRATION_CASES": 4,
        "SHADOW_CASES": 6,
        "TOTAL_FORMAL_REVIEW_RECORDS": len(pass2),
        "ACCEPT": verdict_counts["ACCEPT"],
        "MINOR_REVISION": verdict_counts["MINOR_REVISION"],
        "MAJOR_REVISION": verdict_counts["MAJOR_REVISION"],
        "REJECT": verdict_counts["REJECT"],
        "CRITICAL_SCIENTIFIC_FAILURES": sum(
            bool(row["pass2"]["critical_failure"]) for row in pass2
        ),
        **medians,
        "RESEARCH_USEFULNESS_ACCEPTABLE_RATE": (
            round(
                sum(
                    row["pass2"]["research_decision"]
                    in {"YES", "YES_WITH_MINOR_REVIEW"}
                    for row in pass2
                )
                / len(pass2),
                4,
            )
            if pass2
            else None
        ),
        "DESCRIPTIVE_ORDINAL_AGREEMENT_OVERALL": _ordinal_alpha(verdict_units),
        "DESCRIPTIVE_ORDINAL_AGREEMENT_SCIENTIFIC_CORRECTNESS": alphas[
            "scientific_correctness"
        ],
        "DESCRIPTIVE_ORDINAL_AGREEMENT_EVIDENCE_SUPPORT": alphas[
            "evidence_claim_support"
        ],
        "DESCRIPTIVE_ORDINAL_AGREEMENT_EPISTEMIC": alphas[
            "epistemic_calibration"
        ],
        "DESCRIPTIVE_ORDINAL_AGREEMENT_METHOD_SCOPE": alphas[
            "method_scope_conditions"
        ],
        "MATERIAL_DISAGREEMENTS": len(disagreements),
        "THIRD_REVIEW_CASES": sum(
            item["next_action"] == "THIRD_INDEPENDENT_REVIEW"
            for item in disagreements
        ),
        "ADJUDICATED_CASES": 0,
        "GENUINE_SCIENTIFIC_DISAGREEMENTS": 0,
        "CASE_SPECIFICATION_PROBLEMS": 0,
        "UNRESOLVED_HIGH_SEVERITY_EXPERT_DISAGREEMENTS": len(disagreements),
        "maturity_decision": "NOT_ASSESSED",
        "note": (
            "Descriptive preparation/ledger analysis only. It is not scientist "
            "validation, adjudication, or a maturity decision."
        ),
    }
    _write(directory / "scientist_validation_summary.json", summary)
    print(json.dumps(summary, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--live", action="store_true", help="generate frozen responses with configured DeepSeek")
    p.add_argument(
        "--output-dir",
        type=Path,
        default=OUT,
        help="new candidate directory; must be absent",
    )
    p = sub.add_parser("verify")
    p.add_argument("--directory", type=Path, default=OUT)
    p = sub.add_parser("verify-reviews")
    p.add_argument("--directory", type=Path, default=OUT)
    p = sub.add_parser("import-review")
    p.add_argument("path", type=Path)
    p.add_argument("--candidate-dir", type=Path, required=True)
    p = sub.add_parser("report")
    p.add_argument("--directory", type=Path, default=OUT)
    args = parser.parse_args()
    if args.command == "prepare":
        return prepare(live=args.live, output_dir=args.output_dir)
    if args.command == "verify":
        return verify(args.directory)
    if args.command == "verify-reviews":
        return verify_reviews(args.directory)
    if args.command == "import-review":
        return import_reviews(args.path, args.candidate_dir)
    return report(args.directory)


if __name__ == "__main__":
    raise SystemExit(main())
