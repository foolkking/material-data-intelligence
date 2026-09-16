from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "scientist_evaluation", ROOT / "scripts" / "scientist_evaluation.py"
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_j_case_manifest_is_held_out_and_balanced() -> None:
    payload = MODULE.build_cases()
    cases = payload["cases"]

    assert len(cases) == 24
    assert len(payload["calibration"]) == 4
    assert len(payload["shadow_cases"]) == 6
    assert sum(case["anchor"] for case in cases) == 8
    assert sum(case["class"] == "single_domain" for case in cases) == 12
    assert sum(case["class"] == "cross_evidence" for case in cases) == 8
    assert sum(case["class"] == "insufficient_evidence" for case in cases) == 4
    assert all(case["held_out_from_workstream_i"] for case in cases)
    assert all(case["independent_contributor"] is None for case in cases)


def test_j_assignments_are_balanced_and_reviewer_blinded() -> None:
    assignments = MODULE.build_assignments(MODULE.build_cases())
    rows = assignments["assignments"]
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["reviewer_id"]] = counts.get(row["reviewer_id"], 0) + 1
        assert row["case_id"] not in row["reviewer_visible_case_id"]
        assert row["reviewer_case_author_conflict"] is False

    assert len(rows) == 56
    assert counts == {
        "reviewer_A": 14,
        "reviewer_B": 14,
        "reviewer_C": 14,
        "reviewer_D": 14,
    }


def test_frozen_formal_responses_and_empty_human_ledger_are_integral() -> None:
    generated = ROOT / "docs" / "scientist-evaluation" / "generated"
    responses = json.loads(
        (generated / "formal_responses.json").read_text(encoding="utf-8")
    )
    ledger = json.loads(
        (generated / "reviewer_scores.json").read_text(encoding="utf-8")
    )
    summary = json.loads(
        (generated / "scientist_validation_summary.json").read_text(
            encoding="utf-8"
        )
    )

    assert responses["freeze_status"] == "FROZEN"
    assert len(responses["responses"]) == 24
    for row in responses["responses"]:
        assert hashlib.sha256(row["response_content"].encode()).hexdigest() == row[
            "response_content_sha256"
        ]
    assert ledger["review_records"] == []
    assert ledger["must_not_be_populated_by_model"] is True
    assert summary["j_status"] == "REVIEW_READY"
    assert summary["independent_human_expert_validation"] == "PENDING"
    assert summary["scientist_validation_maturity"] == "NOT_YET_ASSESSED"


def test_reviewer_packets_do_not_expose_provider_or_gold_labels() -> None:
    packets = (
        ROOT
        / "docs"
        / "scientist-evaluation"
        / "generated"
        / "reviewer_packets"
    )
    for reviewer in ("reviewer_A", "reviewer_B", "reviewer_C", "reviewer_D"):
        assigned = (packets / reviewer / "assigned_cases.json").read_text(
            encoding="utf-8"
        )
        pass1 = (
            packets / reviewer / "pass1_submission_template.json"
        ).read_text(encoding="utf-8")
        combined = (assigned + pass1).lower()
        assert "deepseek" not in combined
        assert "expected" not in combined
        assert "anchor" not in combined
        assert "repair_attempted" not in combined
        assert "result_1" not in assigned.lower()
        assert "literature_1" not in assigned.lower()
        forms = json.loads(pass1)["records"]
        assert all(record["locked"] is False for record in forms)
        assert all(record["pass1"]["scientific_acceptability"] is None for record in forms)


def test_ordinal_alpha_is_only_computed_from_supplied_human_values() -> None:
    assert MODULE._ordinal_alpha({}) is None
    assert MODULE._ordinal_alpha({"case": [4.0]}) is None
    assert MODULE._ordinal_alpha({"case_a": [4.0, 4.0], "case_b": [2.0, 2.0]}) == 1.0


def _structural_response_set() -> tuple[dict, dict, dict]:
    cases = MODULE.build_cases()
    baseline = MODULE.build_baseline(cases)
    rows = []
    for case in cases["cases"]:
        result_refs = sorted(
            item["ref"]
            for item in case["authorized_evidence"]
            if item["origin"] != "LITERATURE"
        )
        literature_refs = sorted(
            item["ref"]
            for item in case["authorized_evidence"]
            if item["origin"] == "LITERATURE"
        )
        content = f"offline structural response for {case['case_id']}"
        rows.append(
            {
                "case_id": case["case_id"],
                "baseline_id": baseline["baseline_id"],
                "baseline_fingerprint": baseline["baseline_fingerprint"],
                "response_content": content,
                "response_content_sha256": hashlib.sha256(content.encode()).hexdigest(),
                "generated_at": "2026-09-12T00:00:00+00:00",
                "claims": [],
                "summary": "bounded response",
                "contradictions": [],
                "limitations": ["structural fixture"],
                "authorized_result_refs": result_refs,
                "authorized_literature_refs": literature_refs,
                "evidence_manifest_hash": MODULE._hash_json(case["authorized_evidence"]),
                "status": "FROZEN",
                "generation_outcome": "VALIDATED_PROVIDER_RESPONSE",
            }
        )
    responses = {
        "contract_version": MODULE.FORMAL_RESPONSE_CONTRACT,
        "baseline_id": baseline["baseline_id"],
        "baseline_fingerprint": baseline["baseline_fingerprint"],
        "freeze_status": "FROZEN",
        "responses": rows,
    }
    responses["formal_responses_hash"] = MODULE._hash_json(rows)
    return cases, baseline, responses


def _write_candidate(directory: Path) -> tuple[dict, dict, dict, dict]:
    cases, baseline, responses = _structural_response_set()
    assignments = MODULE.build_assignments(cases, baseline_id=baseline["baseline_id"])
    MODULE._write(directory / "evaluation_baseline.json", baseline)
    MODULE._write(directory / "human_review_cases.json", cases)
    MODULE._write(directory / "formal_responses.json", responses)
    MODULE._write(directory / "reviewer_assignments.json", assignments)
    MODULE._write(directory / "reviewer_scores.json", MODULE._empty_review_ledger())
    MODULE._write(
        directory / "disagreement_ledger.json",
        {"status": "AWAITING_HUMAN_REVIEWS", "items": []},
    )
    MODULE._write(
        directory / "scientist_validation_summary.json",
        MODULE._preparation_summary(responses, baseline_id=baseline["baseline_id"]),
    )
    MODULE.build_packets(
        cases,
        responses,
        assignments,
        packets_dir=directory / "reviewer_packets",
        baseline_id=baseline["baseline_id"],
    )
    return cases, baseline, responses, assignments


def _valid_review_payloads(
    directory: Path, responses: dict, assignments: dict
) -> tuple[dict, dict]:
    assignment = assignments["assignments"][0]
    response = next(
        row
        for row in responses["responses"]
        if row["case_id"] == assignment["case_id"]
    )
    common = {
        "review_contract_version": MODULE.REVIEW_VERSION,
        "baseline_id": responses["baseline_id"],
        "reviewer_visible_case_id": assignment["reviewer_visible_case_id"],
        "case_id": assignment["case_id"],
        "reviewer_id": assignment["reviewer_id"],
        "response_content_sha256": response["response_content_sha256"],
        "locked": True,
        "submitted_at": "2026-09-12T00:00:00+00:00",
        "correction_of_sha256": None,
        "reviewer_expertise_for_case": "COMPETENT",
        "conflict_check": "NO_CONFLICT",
    }
    pass1 = {
        **common,
        "evidence_packet_sha256": None,
        "pass": "PASS1",
        "pass1": {
            "scientific_acceptability": "YES",
            "misleading_issue": "NO",
            "usefulness": "YES_WITH_MINOR_REVIEW",
            "research_decision_value": "YES_WITH_MINOR_REVIEW",
        },
        "pass2": None,
    }
    reveal = json.loads(
        (
            directory
            / "reviewer_packets"
            / assignment["reviewer_id"]
            / "pass2_reveal_DO_NOT_SEND_BEFORE_PASS1_LOCK.json"
        ).read_text(encoding="utf-8")
    )
    evidence_hash = next(
        row["evidence_packet_sha256"]
        for row in reveal["evidence_records"]
        if row["reviewer_visible_case_id"] == assignment["reviewer_visible_case_id"]
    )
    pass2 = {
        **common,
        "evidence_packet_sha256": evidence_hash,
        "pass": "PASS2",
        "pass1": None,
        "pass2": {
            "rubric_scores": {
                "scientific_correctness": 4,
                "evidence_claim_support": 4,
                "method_scope_conditions": 4,
                "epistemic_calibration": 4,
                "contradiction_alternatives": 4,
                "limitations_uncertainty": 4,
                "research_usefulness": 4,
                "auditability_traceability": 4,
            },
            "overall_verdict": "MINOR_REVISION",
            "research_decision": "YES_WITH_MINOR_REVIEW",
            "critical_failure": False,
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
    return pass1, pass2


def _rehash_record(record: dict) -> None:
    record["record_sha256"] = MODULE._hash_json(
        {key: value for key, value in record.items() if key != "record_sha256"}
    )


def _remove_required_rubric(record: dict) -> None:
    record["pass2"]["rubric_scores"].pop("scientific_correctness")
    _rehash_record(record)


def test_case_wide_evidence_labels_follow_opaque_refs(tmp_path: Path) -> None:
    cases = MODULE.build_cases()
    case = next(item for item in cases["cases"] if item["case_id"] == "J02")
    baseline = MODULE.build_baseline(cases)
    responses = {
        "responses": [
            {
                "case_id": case["case_id"],
                "response_content": "claim",
                "claims": [
                    {
                        "claim_id": "claim_1",
                        "statement": "bounded claim",
                        "scientific_result_refs": ["result_2", "result_1"],
                        "literature_evidence_refs": [],
                    }
                ],
            }
        ]
    }
    assignments = MODULE.build_assignments(cases, baseline_id=baseline["baseline_id"])
    assignment = next(
        row for row in assignments["assignments"] if row["case_id"] == "J02"
    )
    reviewer = assignment["reviewer_id"]
    MODULE.build_packets(
        cases,
        {
            "responses": [
                {
                    **responses["responses"][0],
                    "response_content_sha256": hashlib.sha256(b"claim").hexdigest(),
                }
            ],
        },
        {
            "assignments": [
                assignment
            ],
            "expertise": {reviewer: assignments["expertise"][reviewer]},
        },
        packets_dir=tmp_path,
        baseline_id=baseline["baseline_id"],
    )
    reveal = json.loads(
        (
            tmp_path
            / reviewer
            / "pass2_reveal_DO_NOT_SEND_BEFORE_PASS1_LOCK.json"
        ).read_text(encoding="utf-8")
    )
    selected = reveal["evidence_records"][0]["selected_critical_claims"][0]
    assert selected["support_refs"] == ["Evidence 2", "Evidence 1"]


@pytest.mark.parametrize(
    "mutation,expected_error",
    [
        (lambda rows: rows.clear(), "FORMAL_RESPONSE_SET_EMPTY"),
        (lambda rows: rows.pop(), "FORMAL_RESPONSE_COUNT_MISMATCH"),
        (
            lambda rows: rows.append(dict(rows[0])),
            "FORMAL_RESPONSE_DUPLICATE_CASE_ID",
        ),
        (
            lambda rows: rows.__setitem__(0, {**rows[0], "case_id": "STALE"}),
            "FORMAL_RESPONSE_CASE_SET_MISMATCH",
        ),
        (
            lambda rows: rows.__setitem__(
                0, {**rows[0], "baseline_id": "stale-baseline"}
            ),
            "RESPONSE_BASELINE_ID_MISMATCH",
        ),
    ],
)
def test_formal_response_set_rejects_coverage_and_stale_candidates(
    mutation, expected_error: str
) -> None:
    cases, baseline, responses = _structural_response_set()
    mutation(responses["responses"])
    errors = MODULE._validate_formal_response_set(cases, responses, baseline)
    assert any(error == expected_error or error.startswith(expected_error + ":") for error in errors)


@pytest.mark.parametrize(
    "claim_mutation,expected_error",
    [
        (
            lambda claim: claim.update(
                {"scientific_result_refs": [], "literature_evidence_refs": []}
            ),
            "CLAIM_EVIDENCE_MISSING",
        ),
        (
            lambda claim: claim.update(
                {
                    "scientific_result_refs": ["result_1", "result_1"],
                    "literature_evidence_refs": [],
                }
            ),
            "CLAIM_EVIDENCE_DUPLICATE",
        ),
        (
            lambda claim: claim.update(
                {
                    "scientific_result_refs": ["foreign_result"],
                    "literature_evidence_refs": [],
                }
            ),
            "CLAIM_EVIDENCE_FOREIGN",
        ),
    ],
)
def test_claim_refs_fail_closed_against_case_wide_mapping(
    claim_mutation, expected_error: str
) -> None:
    case = next(
        item for item in MODULE.build_cases()["cases"] if item["case_id"] == "J02"
    )
    claim = {
        "claim_id": "claim_1",
        "scientific_result_refs": ["result_1"],
        "literature_evidence_refs": [],
    }
    claim_mutation(claim)
    errors = MODULE._validate_claim_refs(case, {"claims": [claim]})
    assert any(error.startswith(expected_error) for error in errors)


def test_prepare_guards_before_writes_and_never_overwrites(tmp_path: Path, monkeypatch) -> None:
    destination = tmp_path / "candidate"
    destination.mkdir()
    sentinel = destination / "sentinel.txt"
    sentinel.write_text("historical", encoding="utf-8")

    def fail_if_called(*args, **kwargs):
        raise AssertionError("provider generation must not run for occupied destination")

    monkeypatch.setattr(MODULE, "generate_formal_responses", fail_if_called)
    with pytest.raises(SystemExit, match="destination must be absent"):
        MODULE.prepare(live=True, output_dir=destination)
    assert sentinel.read_text(encoding="utf-8") == "historical"


def test_prepare_stages_and_publishes_only_valid_exact_candidate(
    tmp_path: Path, monkeypatch
) -> None:
    destination = tmp_path / "candidate"
    cases, baseline, responses = _structural_response_set()

    async def fake_generation(*args, **kwargs):
        return responses

    monkeypatch.setattr(
        MODULE, "build_baseline", lambda ignored, **kwargs: baseline
    )
    monkeypatch.setattr(MODULE, "generate_formal_responses", fake_generation)
    assert MODULE.prepare(live=True, output_dir=destination) == 0
    assert (destination / "formal_responses.json").is_file()
    assert not list(tmp_path.glob(".candidate.staging-*"))
    assert MODULE._verify_preparation_dir(destination) == []


def test_candidate_root_routes_complete_offline_review_workflow(
    tmp_path: Path,
) -> None:
    candidate = tmp_path / "candidate"
    _, _, responses, assignments = _write_candidate(candidate)
    pass1, pass2 = _valid_review_payloads(candidate, responses, assignments)
    assert MODULE.verify(candidate) == 0
    assert MODULE.verify_reviews(candidate) == 0

    pass1_path = tmp_path / "pass1.json"
    MODULE._write(pass1_path, pass1)
    imported = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "scientist_evaluation.py"),
            "import-review",
            str(pass1_path),
            "--candidate-dir",
            str(candidate),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert imported.returncode == 0, imported.stderr
    assert MODULE.verify_reviews(candidate) == 0

    pass2_path = tmp_path / "pass2.json"
    MODULE._write(pass2_path, pass2)
    assert MODULE.import_reviews(pass2_path, candidate) == 0
    assert MODULE.verify_reviews(candidate) == 0
    assert MODULE.report(candidate) == 0
    for args in (
        ["verify", "--directory", str(candidate)],
        ["verify-reviews", "--directory", str(candidate)],
        ["report", "--directory", str(candidate)],
    ):
        completed = subprocess.run(
            ["python", str(ROOT / "scripts" / "scientist_evaluation.py"), *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert completed.returncode == 0, completed.stderr


def test_import_requires_explicit_nonhistorical_candidate(
    tmp_path: Path,
) -> None:
    submission = tmp_path / "submission.json"
    MODULE._write(submission, {})
    missing_candidate = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "scientist_evaluation.py"),
            "import-review",
            str(submission),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert missing_candidate.returncode == 2
    historical_ledger = (
        ROOT
        / "docs"
        / "scientist-evaluation"
        / "generated"
        / "reviewer_scores.json"
    )
    before = historical_ledger.read_bytes()
    with pytest.raises(SystemExit, match="historical pre-correction candidate"):
        MODULE.import_reviews(
            submission,
            ROOT / "docs" / "scientist-evaluation" / "generated",
        )
    assert historical_ledger.read_bytes() == before


def test_review_ledger_tampering_and_lifecycle_fail_closed(tmp_path: Path) -> None:
    candidate = tmp_path / "candidate"
    _, _, responses, assignments = _write_candidate(candidate)
    pass1, pass2 = _valid_review_payloads(candidate, responses, assignments)

    pass2_path = tmp_path / "pass2-first.json"
    MODULE._write(pass2_path, pass2)
    before = (candidate / "reviewer_scores.json").read_bytes()
    with pytest.raises(SystemExit, match="Pass 2 cannot be imported"):
        MODULE.import_reviews(pass2_path, candidate)
    assert (candidate / "reviewer_scores.json").read_bytes() == before

    pass1_path = tmp_path / "pass1.json"
    MODULE._write(pass1_path, pass1)
    MODULE.import_reviews(pass1_path, candidate)
    ledger_path = candidate / "reviewer_scores.json"
    valid_ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert MODULE._verify_review_ledger(candidate) == []

    mutations = [
        lambda row: row.update(record_sha256="record"),
        lambda row: row.update(reviewer_visible_case_id="WRONG"),
    ]
    for mutate in mutations:
        ledger = json.loads(json.dumps(valid_ledger))
        mutate(ledger["review_records"][0])
        assert MODULE._verify_review_ledger(
            candidate, ledger_override=ledger
        )

    pass2_bad_hash = {**pass2, "evidence_packet_sha256": "0" * 64}
    with pytest.raises(SystemExit, match="evidence hash"):
        MODULE._validate_review_payload(pass2_bad_hash, candidate)
    pass2_bad_rubric = json.loads(json.dumps(pass2))
    pass2_bad_rubric["pass2"]["rubric_scores"].pop("scientific_correctness")
    with pytest.raises(SystemExit, match="rubric dimensions"):
        MODULE._validate_review_payload(pass2_bad_rubric, candidate)

    assignment_path = candidate / "reviewer_assignments.json"
    original_assignments = assignment_path.read_bytes()
    altered = json.loads(original_assignments)
    altered["assignments"][0]["reviewer_case_author_conflict"] = True
    MODULE._write(assignment_path, altered)
    with pytest.raises(SystemExit, match="case author"):
        MODULE._validate_review_payload(pass1, candidate)
    assignment_path.write_bytes(original_assignments)


def test_valid_versioned_correction_and_failed_import_is_atomic(
    tmp_path: Path,
) -> None:
    candidate = tmp_path / "candidate"
    _, _, responses, assignments = _write_candidate(candidate)
    pass1, _ = _valid_review_payloads(candidate, responses, assignments)
    submission = tmp_path / "pass1.json"
    MODULE._write(submission, pass1)
    MODULE.import_reviews(submission, candidate)
    ledger_path = candidate / "reviewer_scores.json"
    first = json.loads(ledger_path.read_text(encoding="utf-8"))["review_records"][0]

    correction = {
        **pass1,
        "correction_of_sha256": first["record_sha256"],
        "pass1": {**pass1["pass1"], "usefulness": "YES"},
    }
    correction_path = tmp_path / "correction.json"
    MODULE._write(correction_path, correction)
    MODULE.import_reviews(correction_path, candidate)
    assert MODULE._verify_review_ledger(candidate) == []

    before = ledger_path.read_bytes()
    malformed = json.loads(json.dumps(correction))
    malformed["correction_of_sha256"] = "bad"
    malformed_path = tmp_path / "malformed.json"
    MODULE._write(malformed_path, malformed)
    with pytest.raises(SystemExit):
        MODULE.import_reviews(malformed_path, candidate)
    assert ledger_path.read_bytes() == before


def test_stored_ledger_metadata_and_contiguous_versions_fail_closed(
    tmp_path: Path,
) -> None:
    candidate = tmp_path / "candidate"
    _, _, responses, assignments = _write_candidate(candidate)
    pass1, _ = _valid_review_payloads(candidate, responses, assignments)
    submission = tmp_path / "pass1.json"
    MODULE._write(submission, pass1)
    MODULE.import_reviews(submission, candidate)
    ledger = json.loads(
        (candidate / "reviewer_scores.json").read_text(encoding="utf-8")
    )
    mutations = [
        lambda item: item.update(contract_version="wrong"),
        lambda item: item.update(must_not_be_populated_by_model=False),
        lambda item: item.update(status="AWAITING_INDEPENDENT_HUMAN_SUBMISSIONS"),
        lambda item: item["review_records"][0].update(
            source_submission_sha256="bad"
        ),
        lambda item: item["review_records"][0].update(ingested_at="naive"),
        lambda item: item["review_records"][0].update(record_version=0),
    ]
    for mutate in mutations:
        altered = json.loads(json.dumps(ledger))
        mutate(altered)
        if altered["review_records"]:
            _rehash_record(altered["review_records"][0])
        assert MODULE._verify_review_ledger(
            candidate, ledger_override=altered
        )

    first = ledger["review_records"][0]
    third = {
        **first,
        "record_version": 3,
        "correction_of_sha256": first["record_sha256"],
    }
    _rehash_record(third)
    gap = json.loads(json.dumps(ledger))
    gap["review_records"].append(third)
    assert any(
        error.startswith("REVIEW_VERSION_NOT_CONTIGUOUS")
        for error in MODULE._verify_review_ledger(
            candidate, ledger_override=gap
        )
    )


@pytest.mark.parametrize(
    "mutation",
    [
        lambda record: record.update(record_sha256="0" * 64),
        lambda record: (
            record.update(reviewer_visible_case_id="WRONG"),
            _rehash_record(record),
        ),
        lambda record: (
            record.update(evidence_packet_sha256="0" * 64),
            _rehash_record(record),
        ),
        _remove_required_rubric,
    ],
)
def test_report_rejects_invalid_review_evidence_without_writes(
    tmp_path: Path, mutation
) -> None:
    candidate = tmp_path / "candidate"
    _, _, responses, assignments = _write_candidate(candidate)
    pass1, pass2 = _valid_review_payloads(candidate, responses, assignments)
    pass1_path = tmp_path / "pass1.json"
    pass2_path = tmp_path / "pass2.json"
    MODULE._write(pass1_path, pass1)
    MODULE._write(pass2_path, pass2)
    MODULE.import_reviews(pass1_path, candidate)
    MODULE.import_reviews(pass2_path, candidate)
    ledger_path = candidate / "reviewer_scores.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    pass2_record = next(
        record for record in ledger["review_records"] if record["pass"] == "PASS2"
    )
    mutation(pass2_record)
    MODULE._write(ledger_path, ledger)
    disagreement = candidate / "disagreement_ledger.json"
    summary = candidate / "scientist_validation_summary.json"
    disagreement_before = disagreement.read_bytes()
    summary_before = summary.read_bytes()
    assert MODULE.report(candidate) == 1
    assert disagreement.read_bytes() == disagreement_before
    assert summary.read_bytes() == summary_before


def test_working_tree_fingerprint_includes_untracked_bytes(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "r0@example.invalid"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "R0"], cwd=tmp_path, check=True)
    tracked = tmp_path / "tracked.txt"
    tracked.write_text("baseline", encoding="utf-8")
    subprocess.run(["git", "add", "tracked.txt"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "baseline"], cwd=tmp_path, check=True)
    untracked = tmp_path / "new-contract.py"
    untracked.write_bytes(b"first")
    first = MODULE._working_tree_fingerprint(tmp_path)
    assert MODULE._working_tree_fingerprint(tmp_path) == first
    untracked.write_bytes(b"second")
    assert MODULE._working_tree_fingerprint(tmp_path) != first


def test_new_blinded_packets_do_not_leak_machine_support_or_verdict(
    tmp_path: Path,
) -> None:
    cases, baseline, responses = _structural_response_set()
    assignments = MODULE.build_assignments(cases, baseline_id=baseline["baseline_id"])
    MODULE.build_packets(
        cases,
        responses,
        assignments,
        packets_dir=tmp_path,
        baseline_id=baseline["baseline_id"],
    )
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in tmp_path.rglob("*.json")
    ).lower()
    assert '"support_status"' not in combined
    assert '"overall_verdict": "accept"' not in combined
    assert '"overall_verdict": "reject"' not in combined


def test_legacy_frozen_candidate_is_not_rewritten_by_verify_or_report() -> None:
    generated = ROOT / "docs" / "scientist-evaluation" / "generated"

    def manifest() -> dict[str, str]:
        return {
            str(path.relative_to(generated)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in generated.rglob("*")
            if path.is_file()
        }

    before = manifest()
    assert MODULE.verify() == 0
    assert MODULE.report() == 0
    assert manifest() == before


def test_shadow_slots_and_failed_generation_are_not_human_validation() -> None:
    generated = ROOT / "docs" / "scientist-evaluation" / "generated"
    cases = json.loads(
        (generated / "human_review_cases.json").read_text(encoding="utf-8")
    )
    responses = json.loads(
        (generated / "formal_responses.json").read_text(encoding="utf-8")
    )
    assert all(
        row["status"] == "NOT_GENERATED_OPTIONAL"
        for row in cases["shadow_cases"]
    )
    failures = [
        row
        for row in responses["responses"]
        if row.get("generation_outcome")
        == "VALIDATION_FAILURE_AFTER_DOCUMENTED_RETRY"
    ]
    assert len(failures) == 6
    assert all(row["claims"] == [] for row in failures)
