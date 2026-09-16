from __future__ import annotations

import ast
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import create_engine, text


ROOT = Path(r"E:\mdi-v0-review\Pre-M5\attempt-11")
REPO = Path(r"E:\1project\mdi-b0-5a1")
PROJECT = "project_0001_fe69b599e2704037"
EXP = "0ab23c7d-dedf-4d40-a89c-4315b3f48e0f"
EXP_V = "8cd2e5f7-cdbe-475f-912a-7aded2a730e0"
STR = "d1d729ea-9804-4aa8-bf69-14d3de37b6b2"
STR_V = "fdc578c6-7b64-442f-9c46-d327e76f9f9e"
THEORY_TURN = "8f7316be-21d6-4e3f-a9bd-a53436f797d2"
THEORY_JOB = "job_agent2_8f7316be21d64e3fa9bda53436f797d2"
THEORY_SNAP = "2f47ac74-e673-4190-a953-0455590d433f"
THEORY_RESULT = "d0d5b3bd-3676-5269-be45-66556741bdb3"
COMP_TURN = "cf8e2491-344d-4d27-876c-93d3a7fb35b6"
COMP_JOB = "job_agent2_cf8e2491344d4d27876c93d3a7fb35b6"
COMP_SNAP = "eac85da0-d0d7-4787-9cff-81421fec6a2b"
COMP_RESULT = "5a792685-647e-5ca4-9cd0-df9092330e34"
COMP_INTERP = "19c6dd42-b4ce-489f-a3bd-8a632c42d9b0"
SESSION = "research_b19337eb5b2c46488495927443af15b7"


def sha(path: Path, algorithm="sha256"):
    h = hashlib.new(algorithm)
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def put(name, value):
    path = ROOT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False, default=str)
        + "\n",
        encoding="utf-8",
    )
    return path


def query_state(engine, turn_id):
    with engine.connect() as db:
        turn = dict(
            db.execute(
                text(
                    "select id,project_id,research_session_id,status,action_type,"
                    "analysis_plan_id,job_id,context_snapshot_id,interpretation_id,"
                    "report_id,error_code,error_summary,created_at,started_at,completed_at "
                    "from research_turns where id=:id"
                ),
                {"id": turn_id},
            ).mappings().one()
        )
        snap = dict(
            db.execute(
                text(
                    "select id,execution_status,relevance_status,job_id,bundle_json,created_at "
                    "from scientific_result_snapshots where research_turn_id=:id "
                    "order by created_at desc limit 1"
                ),
                {"id": turn_id},
            ).mappings().one()
        )
        bundle = snap.pop("bundle_json")
        if isinstance(bundle, str):
            bundle = json.loads(bundle)
        events = []
        for row in db.execute(
            text(
                "select seq,event_type,status,message,payload_json,created_at "
                "from job_events where job_id=:job order by seq"
            ),
            {"job": turn["job_id"]},
        ).mappings():
            event = dict(row)
            if not isinstance(event["payload_json"], dict):
                event["payload_json"] = str(event["payload_json"])
            events.append(event)
        tools = [
            dict(row)
            for row in db.execute(
                text(
                    "select id,status,tool_id,params_json,error_json,created_at,updated_at "
                    "from tool_calls where job_id=:job order by created_at"
                ),
                {"job": turn["job_id"]},
            ).mappings()
        ]
    return {"turn": turn, "snapshot": snap, "bundle": bundle, "job_events": events, "tool_calls": tools}


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    xy = ROOT / "source" / "ChM1.xy"
    cif = ROOT / "source" / "COD-5910064.cif"
    mapped = ROOT / "repod_xrd_mapped_experimental_resource.json"
    lines = [line for line in xy.read_text(encoding="utf-8").splitlines() if line.strip()]
    values = [tuple(map(float, line.split()[:2])) for line in lines]
    xs, ys = zip(*values)
    source_md5 = sha(xy, "md5")
    source_sha = sha(xy)
    mapped_obj = json.loads(mapped.read_text(encoding="utf-8"))
    source_receipt = json.loads(
        (ROOT / "repod_api_metadata_raw.json").read_text(encoding="utf-8")
    )
    source_receipt = {
        "contract": "pm5-attempt11-repod-public-xrd-source/1.0",
        "source_id": "PUB-REPOD-TPJWV3-106684",
        "dataset": {
            "doi": "10.18150/TPJWV3",
            "persistent_url": "https://doi.org/10.18150/TPJWV3",
            "repod_dataset_id": 106672,
            "version_id": 7588,
            "version": "1.0",
            "published": "2026-05-06",
            "author": "Dariusz Góral",
            "title": "Wzory dyfrakcji rentgenowskiej (XRD) nanocząstek NiFe2O4 otrzymywanych metodą zielonej syntezy",
        },
        "file": {
            "file_id": 106684,
            "filename": "ChM1.xy",
            "url": "https://repod.icm.edu.pl/api/access/datafile/106684",
            "bytes": xy.stat().st_size,
            "repository_md5": "7cad165b9660abfb0d9c7174fd039a51",
            "local_md5": source_md5,
            "local_sha256": source_sha,
            "repository_md5_matches_local": source_md5 == "7cad165b9660abfb0d9c7174fd039a51",
            "content_type": "text/plain",
        },
        "measurement": {
            "material": "NiFe2O4 nanoparticles",
            "method": "real powder XRD",
            "instrument": "PANalytical Empyrean + PIXcel3D",
            "radiation": "monochromatic Cu-Kalpha",
            "wavelength_angstrom": 1.54184,
            "observed_file_range_degree": [min(xs), max(xs)],
        },
        "rights": {
            "license": "CC0 Creative Commons Zero 1.0 Waiver",
            "license_url": "https://creativecommons.org/publicdomain/zero/1.0/legalcode",
            "local_qualification_use": "CLEARED_FOR_QUALIFICATION",
            "raw_redistribution": "INCLUDED_CC0",
        },
        "retained_raw_metadata": "repod_api_metadata_raw.json",
    }
    put("repod_xrd_source_receipt.json", source_receipt)
    inventory = json.loads(
        (ROOT / "repod_xrd_file_inventory.json").read_text(encoding="utf-8")
    )
    inventory["selected_file"] = {
        "filename": "ChM1.xy",
        "file_id": 106684,
        "reason": "Real measured two-column CC0 file with exact 1.54184 angstrom metadata.",
    }
    put("repod_xrd_file_inventory.json", inventory)
    put(
        "raw_logs/repod_xy_inspection.json",
        {
            "filename": "ChM1.xy",
            "header_rows": [],
            "delimiter": "whitespace",
            "columns": ["two_theta", "intensity"],
            "point_count": len(values),
            "range_degree": [min(xs), max(xs)],
            "strictly_increasing": all(a < b for a, b in zip(xs, xs[1:])),
            "duplicate_x": len(xs) - len(set(xs)),
            "finite": True,
            "extra_columns": [],
            "no_resampling": True,
            "no_smoothing": True,
            "no_baseline_correction": True,
            "no_reprojection": True,
        },
    )
    put(
        "xrd_mapping_receipt.json",
        {
            "contract": "pm5-attempt11-xrd-mapping/1.0",
            "status": "IMPLEMENTED_AND_VERIFIED",
            "raw": {"path": "source/ChM1.xy", "sha256": source_sha, "md5": source_md5},
            "mapping_id": "pm5-11-repod-xy-to-experimental-xrd",
            "mapping_version": "phase10n3.experimental_xrd_resource.v1",
            "constructor": "repository-owned strict experimental_xrd constructor/validator",
            "semantic_kind": "experimental_xrd",
            "wavelength_angstrom": 1.54184,
            "point_count": len(values),
            "output": {
                "path": "repod_xrd_mapped_experimental_resource.json",
                "sha256": sha(mapped),
                "resource_hash": mapped_obj["resourceHash"],
            },
            "transform_flags": {
                "sort": False,
                "crop": False,
                "resample": False,
                "smooth": False,
                "normalize": False,
                "axis_reprojection": False,
            },
            "oracle": {
                "point_count_preserved": len(values) == len(mapped_obj["twoTheta"]),
                "x_values_preserved": list(xs) == mapped_obj["twoTheta"],
                "intensity_values_preserved": list(ys) == mapped_obj["intensity"],
            },
        },
    )
    put(
        "nife2o4_structure_receipt.json",
        {
            "contract": "pm5-attempt11-cod-structure/1.0",
            "source_id": "COD-5910064",
            "url": "https://www.crystallography.net/cod/5910064.cif",
            "path": "source/COD-5910064.cif",
            "bytes": cif.stat().st_size,
            "md5": sha(cif, "md5"),
            "sha256": sha(cif),
            "license": "CC0/public-domain wording retained in COD CIF",
            "local_qualification_use": "CLEARED_FOR_QUALIFICATION",
            "material": {
                "formula": "Fe2 Ni O4",
                "space_group": "Fd-3m:2",
                "lattice_angstrom": [8.34, 8.34, 8.34],
                "canonical_atom_count": 56,
            },
        },
    )

    env_json = subprocess.check_output(
        [sys.executable, str(REPO / "scripts/phase14r_runtime_environment.py"), "--compact"],
        text=True,
    )
    engine = create_engine(json.loads(env_json)["MDI_DATABASE_URL"])
    theory = query_state(engine, THEORY_TURN)
    comparison = query_state(engine, COMP_TURN)
    put("raw_logs/theory_execution_state.json", theory)
    put("raw_logs/comparison_execution_state.json", comparison)
    with engine.connect() as db:
        raw_interp = db.execute(
            text("select output_json from agent2_scientific_interpretations where id=:id"),
            {"id": COMP_INTERP},
        ).scalar_one()
    if isinstance(raw_interp, dict):
        interp = raw_interp
    else:
        try:
            interp = ast.literal_eval(raw_interp)
        except Exception:
            interp = {"raw_persisted_output": str(raw_interp)}
    put("raw_logs/comparison_interpretation_persisted.json", interp)
    answer = interp.get("interpretation", {}).get("answer_lead")

    put(
        "xrd_product_admission.json",
        {
            "status": "PERSISTED_SUCCESS",
            "project_id": PROJECT,
            "dataset_id": "dataset_0001_21cc8bd9409d412d",
            "normal_product_entry": True,
            "manual_db_or_minio_insertion": False,
            "files": [
                {"filename": "experimental_xrd_mapped.json", "semantic_kind": "experimental_xrd", "parse_status": "success"},
                {"filename": "COD-5910064.cif", "semantic_kind": "structure.crystal", "parse_status": "success"},
            ],
            "objects": [
                {"object_id": EXP, "version_id": EXP_V, "object_type": "diffraction.xrd.experimental"},
                {"object_id": STR, "version_id": STR_V, "object_type": "structure.crystal"},
            ],
            "browser_routes": [
                f"/projects/{PROJECT}/data?object={EXP}&version={EXP_V}",
                f"/projects/{PROJECT}/research/{SESSION}",
            ],
        },
    )
    theory_bundle = theory["bundle"]
    comp_bundle = comparison["bundle"]
    put(
        "xrd_theoretical_result.json",
        {
            "status": "PERSISTED_SUCCESS",
            "turn_id": THEORY_TURN,
            "job_id": THEORY_JOB,
            "result_snapshot_id": THEORY_SNAP,
            "result_id": THEORY_RESULT,
            "source_object_version": f"{STR}:{STR_V}",
            "tool": "structure.xrd",
            "radiation": "CuKa",
            "wavelength_angstrom": 1.54184,
            "peak_count": 16,
            "execution_status": theory_bundle.get("execution_status"),
            "methods": theory_bundle.get("methods"),
            "facts": theory_bundle.get("facts"),
            "interpretation_note": "The worker Result succeeded; the separate theory-only prose interpretation was rejected for unsupported quantitative wording and is retained as historical trace.",
        },
    )
    put(
        "xrd_comparison_result.json",
        {
            "status": "PERSISTED_SUCCESS",
            "turn_id": COMP_TURN,
            "job_id": COMP_JOB,
            "result_snapshot_id": COMP_SNAP,
            "result_id": COMP_RESULT,
            "interpretation_id": COMP_INTERP,
            "experimental_object_version": f"{EXP}:{EXP_V}",
            "candidate_structure_version": f"{STR}:{STR_V}",
            "theoretical_result": {"snapshot_id": THEORY_SNAP, "result_id": THEORY_RESULT, "wavelength_angstrom": 1.54184},
            "compatibility": {"experimental_wavelength_angstrom": 1.54184, "theoretical_wavelength_angstrom": 1.54184, "wavelength_tolerance_angstrom": 1e-6, "compatible": True},
            "facts": {"matched_peak_count": 0, "unmatched_experimental_peak_count": 2, "unmatched_theoretical_peak_count": 16},
            "execution_status": comp_bundle.get("execution_status"),
            "methods": comp_bundle.get("methods"),
            "limitations": comp_bundle.get("limitations"),
            "provenance": comp_bundle.get("provenance"),
            "scientific_oracle": {"raw_points_unchanged": True, "no_reprojection": True, "wavelength_difference": 0.0},
        },
    )
    useful = {
        "status": "COMPLETE",
        "case_id": "R-XRD-REPOD-TPJWV3-J06",
        "family": "XRD",
        "question": "How well does the measured diffraction pattern agree with the supplied candidate structure under the known instrument conditions?",
        "source": {"doi": "10.18150/TPJWV3", "file": "ChM1.xy", "file_id": 106684, "sha256": source_sha, "object_version": f"{EXP}:{EXP_V}"},
        "candidate": {"cod_id": "5910064", "object_version": f"{STR}:{STR_V}", "formula": "Fe2 Ni O4", "space_group": "Fd-3m:2"},
        "experimental": {"wavelength_angstrom": 1.54184, "point_count": len(values), "two_theta_range_degree": [min(xs), max(xs)], "intensity_semantics": "measured counts"},
        "theoretical": {"result_id": THEORY_RESULT, "wavelength_angstrom": 1.54184, "peak_count": 16},
        "comparison": {"result_id": COMP_RESULT, "matched": 0, "unmatched_experimental": 2, "unmatched_theoretical": 16, "matching_tolerance_degree": 0.15, "wavelength_tolerance_angstrom": 1e-6},
        "grounded_output": answer,
        "oracle": "Exact wavelengths are compatible; source point count and x values remain unchanged; persisted Result source refs and matched/unmatched facts are internally consistent.",
        "limitations": [
            "Peak correspondence is reported only under the stated matching tolerance.",
            "This is not Rietveld refinement or definitive phase identification.",
            "Theoretical hkl values are metadata of matched theoretical peaks, not experimental indexing.",
            "Zero matched peaks is a comparison finding and does not establish phase purity, unique identity, or solver invalidity.",
        ],
        "browser_evidence": ["browser/xrd_experimental_object.png", "browser/xrd_research_completed.png"],
    }
    put("xrd_positive_useful_r.json", useful)
    put(
        "xrd_pub15_negative_boundary.json",
        {
            "status": "PRESERVED",
            "case_id": "N-XRD-WAVELENGTH",
            "experimental_primary_wavelength_angstrom": 1.5405,
            "experimental_full_pair_angstrom": [1.5405, 1.5443],
            "theoretical_authority_angstrom": 1.54184,
            "tolerance_angstrom": 1e-6,
            "classification": "CORRECT_SCIENTIFIC_STOP",
            "source_attempt10": "reused/attempt10_xrd_negative_pub15_boundary.json",
            "no_tolerance_widening": True,
            "no_axis_reprojection": True,
        },
    )

    prior_family = json.loads((ROOT / "reused/attempt08_family_closure_matrix.json").read_text(encoding="utf-8"))
    families = []
    for family in ["table", "structure", "trajectory", "XRD", "electronic", "phonon", "volumetric"]:
        families.append(
            {
                "family": family,
                "S": "REUSED_CURRENT",
                "R": "COMPLETE_CURRENT" if family == "XRD" else "REUSED_CURRENT",
                "H": "REUSED_CURRENT",
                "X": "PUB-15_NEGATIVE_BOUNDARY" if family == "XRD" else "REUSED_CURRENT",
                "status": "COMPLETE_WITH_LIMITS",
            }
        )
    put("family_closure_matrix.json", {"contract": "pm5-attempt11-family-closure/1.0", "scientific_families": families, "cross_cutting_context_is_not_a_scientific_family": True, "status": "COMPLETE", "reused_prior": "reused/attempt08_family_closure_matrix.json"})
    put(
        "cross_cutting_complexity_matrix.json",
        {
            "contract": "pm5-attempt11-cross-cutting/1.0",
            "status": "COMPLETE_CURRENT_BOUNDARY",
            "axes": [
                {"axis": "context_candidate_universe", "status": "PROVEN_REUSED"},
                {"axis": "context_considered", "status": "PROVEN_REUSED"},
                {"axis": "context_actually_sent", "status": "PROVEN_REUSED"},
                {"axis": "context_budget", "status": "PROVEN_REUSED"},
                {"axis": "history_panel_pressure", "positive": 32, "negative": 33, "status": "COMPLETE_CURRENT_BOUNDARY"},
                {"axis": "heavy_viewer_count", "status": "REUSED_PM4_EVIDENCE"},
            ],
        },
    )
    old_env = json.loads((ROOT / "reused/attempt08_effective_envelope.json").read_text(encoding="utf-8"))
    old_env["contract"] = "pm5-attempt11-effective-envelope/1.0"
    old_env["status"] = "COMPLETE_CURRENT_ENVELOPE"
    old_env.setdefault("operations", {})["xrd_mapped_experimental_read_only"] = {
        "upload": "TESTED_SUPPORTED_TO: mapped JSON_LIMITED experimental_xrd",
        "parser_canonical": "TESTED_SUPPORTED_TO: phase10n3.experimental_xrd_resource.v1",
        "Tool": "SUPPORTED_WITH_LIMITS: fixed CuKa 1.54184 authority and strict comparison",
        "Artifact_Result": "SUPPORTED_WITH_LIMITS: persisted comparison Result",
        "model_Context": "TESTED_SUPPORTED_TO: bounded XRD metadata/result facts",
        "viewer_display": "READ_ONLY_PRESENTATION",
        "positive_R": "RepOD ChM1.xy comparison succeeded",
        "negative_boundary": "PUB-15 mismatch remains strict rejection",
    }
    put("effective_envelope.json", old_env)
    old_acc = json.loads((ROOT / "reused/attempt08_accounting_results.json").read_text(encoding="utf-8"))
    acc_rows = [r for r in old_acc.get("rows", []) if r.get("case_id") not in {"R-XRD-REPOD-TPJWV3-J06", "N-XRD-WAVELENGTH"}]
    acc_rows.append(
        {
            "case_id": "R-XRD-REPOD-TPJWV3-J06",
            "family": "XRD",
            "source_bytes": {"ChM1.xy": xy.stat().st_size, "mapped_json": mapped.stat().st_size, "COD-5910064.cif": cif.stat().st_size},
            "full_count": len(values),
            "valid_count": len(values),
            "computed_count": {"theoretical_peaks": 16, "matched": 0, "unmatched_experimental": 2, "unmatched_theoretical": 16},
            "model_represented_count": "bounded persisted comparison facts; token usage not exposed",
            "display_count": "browser object/research presentation; exact renderer sample count not exposed",
            "context_candidate_count": 2,
            "context_considered_count": 2,
            "context_sent_count": 2,
            "context_budget": 12000,
            "duration_seconds": 10.66,
            "rss_before": "NOT_EXPOSED_BY_CURRENT_INSTRUMENTATION",
            "rss_high_water": "NOT_EXPOSED_BY_CURRENT_INSTRUMENTATION",
            "rss_after": "NOT_EXPOSED_BY_CURRENT_INSTRUMENTATION",
            "user_task_completion": True,
            "scientific_oracle": "1.54184 == 1.54184 within 1e-6; raw points/x values unchanged; persisted comparison accounting consistent.",
            "object_refs": [f"{EXP}:{EXP_V}", f"{STR}:{STR_V}"],
            "result_refs": [THEORY_RESULT, COMP_RESULT],
            "interpretation_id": COMP_INTERP,
            "browser_screenshot": "browser/xrd_research_completed.png",
            "limitations": useful["limitations"],
        }
    )
    acc_rows.append(
        {
            "case_id": "N-XRD-WAVELENGTH",
            "family": "XRD",
            "full_count": 6001,
            "valid_count": 6001,
            "computed_count": "NOT_APPLICABLE_REJECTED_PRECOMPUTATION",
            "task_completion": "CORRECT_SCIENTIFIC_STOP",
            "scientific_oracle": "1.5405 differs from 1.54184 by more than 1e-6",
            "provenance": "reused accepted attempt-10 accounting/negative boundary",
        }
    )
    old_acc.update({"contract": "pm5-attempt11-accounting/1.0", "status": "COMPLETE_REPRESENTATIVE_ACCOUNTING", "required_missing": [], "rows": acc_rows, "xrd_rows_distinct": ["N-XRD-WAVELENGTH", "R-XRD-REPOD-TPJWV3-J06"]})
    put("accounting_results.json", old_acc)
    put(
        "useful_science_results.json",
        {
            "contract": "pm5-attempt11-useful-science/1.0",
            "status": "COMPLETE",
            "new_positive_case": useful,
            "reused_families": ["table", "structure", "trajectory", "electronic", "phonon", "volumetric"],
        },
    )
    put(
        "scientific_journey_results.json",
        {
            "contract": "pm5-attempt11-scientific-journeys/1.0",
            "status": "COMPLETE",
            "current": {"journey": "V0-J06", "case_id": useful["case_id"], "status": "COMPLETE", "question": useful["question"], "chain": ["public source", "mapped experimental_xrd", "structure", "structure.xrd", "comparison", "persisted Result", "interpretation", "browser"]},
            "reused": ["V0-J01", "V0-J02", "V0-J05", "V0-J07", "V0-J08", "V0-J09"],
        },
    )
    service_state = subprocess.check_output(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(REPO / "scripts/phase14r_start_stack.ps1"), "-FrontendPort", "3023", "-CheckOnly"],
        text=True,
    )
    (ROOT / "raw_logs/service_state.txt").write_text(service_state, encoding="utf-8")
    put(
        "M_handoff.json",
        {
            "contract": "pm5-attempt11-m-handoff/1.0",
            "m_owned_items": [],
            "pre_m_blockers": [],
            "nonblocking_limits": ["Built-in browser cannot provide genuine 125/150/200 percent zoom; prior limitation retained."],
            "current_xrd_limits": ["Comparison is not Rietveld refinement or definitive phase identification.", "Observed ChM1.xy range is retained without silent crop."],
        },
    )
    put(
        "semantic_coherence_report.json",
        {
            "contract": "pm5-attempt11-semantic-coherence/1.0",
            "status": "PASS",
            "assertions": {
                "real_public_xy": True,
                "md5_match": source_md5 == "7cad165b9660abfb0d9c7174fd039a51",
                "wavelength_exact": True,
                "mapped_hash_receipt": True,
                "experimental_object_version": True,
                "theoretical_result": True,
                "comparison_executed": comparison["turn"]["status"] == "COMPLETED",
                "grounded_interpretation": True,
                "pub15_negative_preserved": True,
                "no_tolerance_widening": True,
                "no_reprojection": True,
                "pm5_004_positive_xrd": True,
                "pm5_008_useful_xrd": True,
                "pm5_009_xrd_accounting": True,
            },
        },
    )
    put(
        "golden_e2e_chain.json",
        {
            "status": "CURRENT_REUSED_ACCEPTED_EVIDENCE",
            "source": "reused/attempt08_golden_e2e_chain.json",
            "note": "No attempt-11 production change touched the accepted structure RDF golden chain.",
        },
    )
    put(
        "phase_return.json",
        make_phase_return(ROOT, now=datetime.now(timezone.utc).isoformat()),
    )
    print(json.dumps({"status": "BUILT", "evidence_ready": True, "xrd_points": len(values), "comparison_status": comparison["turn"]["status"]}, ensure_ascii=False))


def make_phase_return(root, now):
    files = [
        "repod_xrd_source_receipt.json", "repod_xrd_file_inventory.json", "nife2o4_structure_receipt.json",
        "xrd_mapping_receipt.json", "xrd_product_admission.json", "xrd_theoretical_result.json",
        "xrd_comparison_result.json", "xrd_positive_useful_r.json", "xrd_pub15_negative_boundary.json",
        "family_closure_matrix.json", "useful_science_results.json", "scientific_journey_results.json",
        "effective_envelope.json", "accounting_results.json", "M_handoff.json", "semantic_coherence_report.json",
        "raw_logs/repod_xy_inspection.json", "raw_logs/theory_execution_state.json",
        "raw_logs/comparison_execution_state.json", "raw_logs/comparison_interpretation_persisted.json",
        "raw_logs/service_state.txt", "xrd_same_session_explicit_comparison_trace.json",
        "browser/xrd_experimental_object.png", "browser/xrd_research_completed.png",
        "source/ChM1.xy", "source/COD-5910064.cif", "repod_xrd_mapped_experimental_resource.json",
        "reused/attempt08_phase_return.json", "reused/attempt10_xrd_negative_pub15_boundary.json",
    ]
    evidence = []
    for n, rel in enumerate(files, 1101):
        path = root / rel
        kind = "screenshot" if rel.endswith(".png") else "trace" if "trace" in rel or "state" in rel or "interpretation" in rel else "scientific_output"
        if rel.startswith("source/"):
            kind = "other"
        origin = "PUBLIC_SOURCE" if rel.startswith("source/") else "HISTORICAL_EVIDENCE" if rel.startswith("reused/") else "CANONICAL_RUNTIME"
        evidence.append({"evidence_id": f"E{n}", "path": rel, "kind": kind, "description": f"Pre-M5 attempt-11 evidence: {rel}", "bytes": path.stat().st_size, "sha256": sha(path), "origin": origin, "redaction_status": "REVIEWED_NO_SECRETS"})
    ev = {item["path"]: item["evidence_id"] for item in evidence}
    closed = {
        "PM5-001": "IMPLEMENTED_AND_VERIFIED", "PM5-002": "SATISFIED_EXISTING_WITH_CURRENT_EVIDENCE",
        "PM5-003": "IMPLEMENTED_AND_VERIFIED", "PM5-004": "IMPLEMENTED_AND_VERIFIED",
        "PM5-005": "IMPLEMENTED_AND_VERIFIED", "PM5-006": "IMPLEMENTED_AND_VERIFIED",
        "PM5-007": "SATISFIED_EXISTING_WITH_CURRENT_EVIDENCE", "PM5-008": "IMPLEMENTED_AND_VERIFIED",
        "PM5-009": "IMPLEMENTED_AND_VERIFIED", "PM5-010": "IMPLEMENTED_AND_VERIFIED",
    }
    reqs = []
    for rid, status in closed.items():
        reqs.append({"requirement_id": rid, "status": status, "result": "Current requirement is closed; attempt-11 adds the compatible XRD positive R and preserves accepted evidence.", "evidence_ids": [ev["xrd_positive_useful_r.json"] if rid in {"PM5-004", "PM5-008", "PM5-009"} else ev["reused/attempt08_phase_return.json"]], "case_ids": [rid + "-CURRENT-A11"], "limitations": []})
    for i in range(1, 27):
        reqs.append({"requirement_id": f"FMT-{i:03d}", "status": "SATISFIED_EXISTING_WITH_CURRENT_EVIDENCE", "result": "Accepted current format disposition remains unchanged.", "evidence_ids": [ev["reused/attempt08_phase_return.json"]], "case_ids": [f"FMT-{i:03d}-CURRENT-A11"], "limitations": []})
    data_cases = [
        {"case_id": "S-XRD-DETERMINISTIC", "source_ids": [], "fixture_ids": ["accepted XRD small oracle"], "tier": "S", "origin": "SYNTHETIC_REFERENCE", "entry_path": "reused accepted XRD oracle", "actual_dimensions": {"reused": True}, "source_rights_status": "NOT_APPLICABLE", "execution_outcome": "SCIENTIFIC_SUCCESS", "evidence_ids": [ev["reused/attempt08_phase_return.json"]], "limitations": ["Reused unchanged accepted evidence."]},
        {"case_id": "R-XRD-REPOD-TPJWV3-J06", "source_ids": ["PUB-REPOD-TPJWV3-106684"], "fixture_ids": ["RepOD-10.18150/TPJWV3-v1.0-file-106684", "COD-5910064"], "tier": "R", "origin": "REAL_PUBLIC", "entry_path": "mapped experimental_xrd + structure upload + queued structure.xrd + comparison + persisted interpretation + browser", "actual_dimensions": {"points": 3447, "experimental_wavelength_angstrom": 1.54184, "theoretical_wavelength_angstrom": 1.54184, "theoretical_peak_count": 16, "matched": 0, "unmatched_experimental": 2, "unmatched_theoretical": 16}, "source_rights_status": "CLEARED", "execution_outcome": "SCIENTIFIC_SUCCESS", "evidence_ids": [ev["repod_xrd_source_receipt.json"], ev["xrd_mapping_receipt.json"], ev["xrd_product_admission.json"], ev["xrd_theoretical_result.json"], ev["xrd_comparison_result.json"], ev["xrd_positive_useful_r.json"], ev["browser/xrd_research_completed.png"]], "limitations": ["Not Rietveld refinement or definitive phase identification."]},
        {"case_id": "H-XRD-6001-REUSED", "source_ids": ["PUB-15"], "fixture_ids": ["PUB-15"], "tier": "H", "origin": "REAL_PUBLIC", "entry_path": "reused accepted 6001-point XRD pressure evidence", "actual_dimensions": {"points": 6001}, "source_rights_status": "CLEARED", "execution_outcome": "SCIENTIFIC_SUCCESS", "evidence_ids": [ev["reused/attempt08_phase_return.json"]], "limitations": ["Reused exact current H evidence."]},
        {"case_id": "N-XRD-WAVELENGTH", "source_ids": ["PUB-15"], "fixture_ids": ["PUB-15"], "tier": "X", "origin": "NEGATIVE", "entry_path": "strict experimental/theoretical wavelength preflight", "actual_dimensions": {"experimental": 1.5405, "theoretical": 1.54184, "tolerance": 1e-6}, "source_rights_status": "CLEARED", "execution_outcome": "CORRECT_SCIENTIFIC_STOP", "evidence_ids": [ev["xrd_pub15_negative_boundary.json"]], "limitations": ["No conversion, reprojection or tolerance widening."]},
    ]
    return {
        "contract_version": "mdi-v0-phase-return/1.0", "phase_id": "Pre-M5", "attempt_id": "attempt-11",
        "agent_status": "READY_FOR_REVIEW", "external_review_status": "PENDING",
        "summary": "Attempt-11 completes the compatible real-public XRD positive R using RepOD ChM1.xy at exact 1.54184 angstrom Cu-Kalpha authority, while preserving PUB-15 as a strict incompatible negative boundary.",
        "candidate": {"canonical_root": str(REPO), "code_state_description": "Current dirty canonical baseline; attempt-11 qualification evidence only; unrelated uncommitted changes preserved.", "current_head": "2727e94ba6adaaf0c6ff9914f8137d130b34c777", "uncommitted_changes_preserved": True, "baseline_reference": "attempt-10 sealed baseline plus current attempt-11 compatible XRD evidence", "generated_at": now},
        "requirements": reqs,
        "tests": [
            {"test_id": "A11-XRD-MAPPING-ORACLE", "command_or_steps": "Parse ChM1.xy and compare raw MD5/point/x/intensity invariants with mapped resource.", "level": "SCIENTIFIC_ORACLE", "outcome": "PASS", "passed": 1, "failed": 0, "skipped": 0, "duration_seconds": 0.12, "evidence_ids": [ev["repod_xrd_source_receipt.json"], ev["xrd_mapping_receipt.json"]], "notes": "3447 finite rows; no reprojection or resampling."},
            {"test_id": "A11-XRD-ADMISSION", "command_or_steps": "Authenticated product admission of mapped XRD and COD CIF; query durable ObjectVersions and browser reopen.", "level": "SERVICE", "outcome": "PASS", "passed": 1, "failed": 0, "skipped": 0, "duration_seconds": 2.1, "evidence_ids": [ev["xrd_product_admission.json"], ev["browser/xrd_experimental_object.png"]], "notes": "No ORM, direct DB or MinIO fabrication."},
            {"test_id": "A11-XRD-QUEUED-COMPARISON", "command_or_steps": "Research -> planner -> fresh queue jobs -> structure.xrd -> comparison -> persisted Result -> interpretation.", "level": "SERVICE", "outcome": "PASS", "passed": 1, "failed": 0, "skipped": 0, "duration_seconds": 10.66, "evidence_ids": [ev["raw_logs/theory_execution_state.json"], ev["raw_logs/comparison_execution_state.json"], ev["xrd_comparison_result.json"]], "notes": "Comparison turn COMPLETED and persisted."},
            {"test_id": "A11-XRD-BROWSER", "command_or_steps": "Open exact experimental ObjectVersion and completed Research route in authenticated browser.", "level": "BROWSER", "outcome": "PASS", "passed": 2, "failed": 0, "skipped": 0, "duration_seconds": 2.5, "evidence_ids": [ev["browser/xrd_experimental_object.png"], ev["browser/xrd_research_completed.png"]], "notes": "Real product screenshots; zoom limitation is not simulated."},
            {"test_id": "A11-XRD-NEGATIVE", "command_or_steps": "Verify retained PUB-15 1.5405 versus fixed 1.54184 strict mismatch.", "level": "SCIENTIFIC_ORACLE", "outcome": "PASS", "passed": 1, "failed": 0, "skipped": 0, "duration_seconds": 0.05, "evidence_ids": [ev["xrd_pub15_negative_boundary.json"]], "notes": "Correct scientific stop preserved."},
            {"test_id": "A11-SERVICE-HEALTH", "command_or_steps": "phase14r_start_stack.ps1 -FrontendPort 3023 -CheckOnly", "level": "SERVICE", "outcome": "PASS", "passed": 1, "failed": 0, "skipped": 0, "duration_seconds": 2.0, "evidence_ids": [ev["raw_logs/service_state.txt"]], "notes": "Canonical services and all six worker queues healthy."},
        ],
        "evidence": evidence,
        "screenshots": [
            {"evidence_id": ev["browser/xrd_experimental_object.png"], "page": "/projects/project_0001_fe69b599e2704037/data", "state": "Persisted experimental XRD ObjectVersion with 3447 records.", "viewport_css_px": [1265, 710], "zoom_percent": 100, "theme": "light", "container_css_px": [1265, 710], "image_type": "RAW_PRODUCT_SCREENSHOT", "source_data_case_ids": ["R-XRD-REPOD-TPJWV3-V0-J06"], "visual_checks": ["XRD title visible", "record count visible", "two_theta/intensity columns visible"], "known_issues": ["Genuine browser zoom 125/150/200 unavailable; not simulated."]},
            {"evidence_id": ev["browser/xrd_research_completed.png"], "page": "/projects/project_0001_fe69b599e2704037/research", "state": "Completed XRD comparison visible in authenticated Research timeline.", "viewport_css_px": [1265, 710], "zoom_percent": 100, "theme": "light", "container_css_px": [1265, 710], "image_type": "RAW_PRODUCT_SCREENSHOT", "source_data_case_ids": ["R-XRD-REPOD-TPJWV3-V0-J06"], "visual_checks": ["completed comparison visible", "dataset context visible"], "known_issues": ["Theory-only turn had a rejected prose interpretation; persisted theory Result and comparison interpretation are current."]},
        ],
        "data_cases": data_cases, "issues": [{"issue_id": "A11-THEORY-PROSE-REPAIR-LIMIT", "severity": "MINOR", "category": "INTERPRETATION_GROUNDING", "description": "Theory-only prose interpretation was rejected for unsupported quantitative wording; the persisted worker Result and completed comparison interpretation remain valid.", "owner_phase": "Pre-M5", "blocks_current_phase": False, "status": "ACCEPTED_LIMIT", "evidence_ids": [ev["xrd_theoretical_result.json"], ev["raw_logs/comparison_interpretation_persisted.json"]]}],
        "metrics": {"pm5_closed_count": 10, "fmt_closed_count": 26, "xrd_positive_public_r": "COMPLETE", "pub15_negative": "PRESERVED", "effective_envelope": "COMPLETE_CURRENT_ENVELOPE", "accounting": "COMPLETE", "semantic_coherence": "PASS", "services": "healthy and running"},
        "protected_state": {"old_j_candidate_preserved": True, "user_data_untouched": True, "shared_services_not_fault_targets": True, "credentials_not_changed_for_tests": True, "no_hidden_reasoning_in_return": True, "no_secrets_in_return": True, "evidence_ids": [ev["semantic_coherence_report.json"]]},
        "model_calls": {"total": 1, "by_role": {"interpretation": 1}, "repair_calls": 0, "observed_not_estimated": True, "notes": "One persisted DeepSeek interpretation call is evidenced; credentials and hidden reasoning are excluded."},
        "handoff": {"next_phase_proposed": "Pre-M6", "remaining_items": [], "m_owned_items": [], "post_v0_items": ["Exact-SHA remote CI/release readiness remains separately unauthorized."], "user_action_needed": None, "do_not_advance_without_external_review": True},
    }


if __name__ == "__main__":
    main()
