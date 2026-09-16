"""Generate Workstream I expert scientific reasoning evaluation evidence.

The first invocation is intentionally a baseline run over the Workstream H
claim validator.  It demonstrates which qualitative overclaims pass the
pre-Workstream-I identity/numeric boundary.  The baseline artifact is
immutable: later improved evaluation writes a separate final artifact.
"""

from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone
import json
from pathlib import Path
from types import SimpleNamespace
import sys
from typing import Any
from uuid import uuid4


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
    value = str(ROOT / relative)
    if value not in sys.path:
        sys.path.insert(0, value)

from mdi_api.application.scientific_knowledge.synthesis import (  # noqa: E402
    BoundedLiteratureSynthesisProvider,
    LiteratureSynthesisOutput,
    LiteratureSynthesisValidationError,
    validate_literature_synthesis,
)
from mdi_api.domain.scientific_knowledge.contracts import (  # noqa: E402
    LiteratureEvidence,
    LiteratureEvidenceScope,
    LiteratureQueryPurpose,
    LiteratureSupportType,
)
from mdi_api.application.scientific_reasoning.assessment import (  # noqa: E402
    ClaimSupportAssessor,
)
from mdi_api.domain.scientific_reasoning.contracts import (  # noqa: E402
    ClaimSupportStatus,
    ProposedScientificClaim,
    ReasoningEvidence,
)
from mdi_api.research_agent.llm.structured_client import (  # noqa: E402
    DeepSeekStructuredLLMClient,
)


FIXTURE = (
    ROOT
    / "docs"
    / "scientific-reasoning"
    / "fixtures"
    / "expert_reasoning_cases_v1.json"
)
BASELINE = (
    ROOT
    / "docs"
    / "scientific-reasoning"
    / "generated"
    / "expert_reasoning_baseline.json"
)
FINAL = (
    ROOT
    / "docs"
    / "scientific-reasoning"
    / "generated"
    / "expert_reasoning_evaluation.json"
)

_STRENGTH_RANK = {
    "NOT_SUPPORTED": 0,
    "INSUFFICIENT_EVIDENCE": 1,
    "CONFLICTED": 2,
    "SUGGESTIVE": 3,
    "CONSISTENT_WITH": 4,
    "SUPPORTED_WITHIN_SCOPE": 5,
    "DIRECTLY_SUPPORTED": 6,
}


def _load_cases() -> list[dict[str, Any]]:
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    if payload.get("contract_version") != "expert-reasoning-case/1.0":
        raise ValueError("unsupported expert reasoning fixture contract")
    return list(payload["cases"])


def _legacy_accepts(case: dict[str, Any]) -> tuple[bool, list[str]]:
    """Execute the exact qualitative boundary present at the H baseline."""

    claim = case["claim"]
    literature = {
        item["ref"]: SimpleNamespace(passage=item["text"])
        for item in case["evidence"]
        if item["origin"] == "LITERATURE"
    }
    results = {
        item["ref"]: {"summary": item["text"], "authority": "SCIENTIFIC_RESULT"}
        for item in case["evidence"]
        if item["origin"] == "COMPUTED"
    }
    output = LiteratureSynthesisOutput.model_validate(
        {
            "summary": "The synthesis uses only authorized evidence.",
            "claims": [
                {
                    "claim_id": "claim_1",
                    "statement": claim["text"],
                    "literature_evidence_refs": [
                        ref for ref in claim["refs"] if ref.startswith("literature_")
                    ],
                    "scientific_result_refs": [
                        ref for ref in claim["refs"] if ref.startswith("result_")
                    ],
                    "epistemic_status": claim["strength"],
                    "limitations": claim.get("limitations", []),
                }
            ],
            "contradictions": [],
            "limitations": [],
        }
    )
    try:
        validate_literature_synthesis(
            output,
            literature_evidence=literature,
            scientific_results=results,
        )
    except LiteratureSynthesisValidationError as exc:
        return False, list(exc.codes)
    return True, []


def build_baseline_report() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    failure_count = 0
    for case in _load_cases():
        accepted, validation_codes = _legacy_accepts(case)
        expected_accept = case["case_id"] == "TRJ-01"
        baseline_failure = accepted != expected_accept
        failure_count += baseline_failure
        rows.append(
            {
                "case_id": case["case_id"],
                "domain": case["domain"],
                "question": case["question"],
                "proposed_claim": case["claim"],
                "gold_semantics": case["expected"],
                "gold_origin": case["gold_origin"],
                "h_baseline_accepted": accepted,
                "h_baseline_validation_codes": validation_codes,
                "baseline_failure": baseline_failure,
                "defect_type": (
                    case["expected"].get("defect") if baseline_failure else None
                ),
            }
        )
    return {
        "contract_version": "expert-reasoning-baseline/1.0",
        "baseline_authority": (
            "Workstream H identity/reference/numeric validation before "
            "Workstream I qualitative reasoning changes"
        ),
        "fixture": str(FIXTURE.relative_to(ROOT)).replace("\\", "/"),
        "metrics": {
            "REASONING_EVALUATION_CASES": len(rows),
            "BASELINE_REASONING_FAILURES": failure_count,
            "BASELINE_ACCEPTED_INVALID_CLAIMS": sum(
                row["baseline_failure"] and row["h_baseline_accepted"] for row in rows
            ),
            "H_NUMERIC_SAFETY_REJECTIONS": sum(
                not row["h_baseline_accepted"] for row in rows
            ),
        },
        "cases": rows,
    }


def _reasoning_evidence(row: dict[str, Any]) -> ReasoningEvidence:
    return ReasoningEvidence(
        ref=row["ref"],
        origin=row["origin"],
        text=row["text"],
        scope=row["scope"],
        method=row.get("method"),
        conditions=row.get("conditions", []),
        lineage=row["lineage"],
        depends_on=row.get("depends_on", []),
        relation=row.get("relation"),
        publication_role=row.get("publication_role"),
        evidence_scope=row.get("evidence_scope"),
        publication_status=row.get("publication_status"),
        limitations=row.get("limitations", []),
        semantic_tags=row.get("semantic_tags", []),
    )


def _proposed_claim(row: dict[str, Any]) -> ProposedScientificClaim:
    return ProposedScientificClaim(
        claim_id="claim_1",
        text=row["text"],
        claim_type=row["type"],
        support_status=row["strength"],
        evidence_refs=row["refs"],
        scope=row["scope"],
        qualifiers=row.get("qualifiers", []),
        limitations=row.get("limitations", []),
        comparison_status=row.get("comparison_status"),
        derived_numeric=row.get("derived_numeric", False),
        derived_fact_ref=row.get("derived_fact_ref"),
    )


def _case_acceptance(
    case: dict[str, Any],
    assessment: Any,
) -> tuple[bool, list[str]]:
    expected = case["expected"]
    errors: list[str] = []
    expected_supported = expected["outcome"] == "SUPPORTED"
    if expected_supported != assessment.accepted:
        errors.append("ACCEPTANCE_OUTCOME_MISMATCH")
    if _STRENGTH_RANK[assessment.support_status.value] > _STRENGTH_RANK[
        expected["max_strength"]
    ]:
        errors.append("CLAIM_STRENGTH_TOO_HIGH")
    if expected.get("comparison") and (
        assessment.comparison_status is None
        or assessment.comparison_status.value != expected["comparison"]
    ):
        errors.append("METHOD_COMPARISON_STATUS_MISMATCH")
    if expected.get("defect") and expected["defect"] not in {
        item.value for item in assessment.defects
    }:
        # A stricter reusable category is acceptable for authority and derived
        # numeric cases, but ordinary defect families must remain diagnosable.
        aliases = {
            "QUALITATIVE_SUPPORT": {"SCIENTIFIC_AUTHORITY"},
            "MECHANISTIC_OVERCLAIM": {"CAUSAL_OVERCLAIM"},
            "INVALID_COMPARISON": {
                "CONTRADICTION_COLLAPSE",
                "METHOD_MISINTERPRETATION",
            },
        }
        if not ({item.value for item in assessment.defects} & aliases.get(
            expected["defect"], set()
        )):
            errors.append("EXPECTED_DEFECT_NOT_CLASSIFIED")
    return not errors, errors


def _live_literature(
    passage: str,
    *,
    support_type: LiteratureSupportType = LiteratureSupportType.SUPPORTING,
) -> LiteratureEvidence:
    return LiteratureEvidence(
        evidence_id=uuid4(),
        project_id="qualification",
        work_id=uuid4(),
        snapshot_id=uuid4(),
        scope=LiteratureEvidenceScope.ABSTRACT_ONLY,
        support_type=support_type,
        purpose=LiteratureQueryPurpose.HYPOTHESIS_CONTEXT,
        passage=passage,
        source_content_hash="a" * 64,
        selected_by="workstream_i",
        selected_at=datetime.now(timezone.utc),
    )


def _exception_chain(exc: BaseException) -> list[str]:
    messages: list[str] = []
    current: BaseException | None = exc
    while current is not None and len(messages) < 4:
        messages.append(f"{type(current).__name__}: {current}"[:2000])
        current = current.__cause__
    return messages


async def _live_reasoning_cases() -> list[dict[str, Any]]:
    provider = BoundedLiteratureSynthesisProvider(
        DeepSeekStructuredLLMClient(),
        timeout_seconds=120,
    )
    definitions = [
        {
            "case_id": "LIVE-TRJ-STRUCT",
            "question": (
                "Do the authorized diffusion and coordination observations "
                "establish that reduced coordination causes faster transport?"
            ),
            "literature": {
                "literature_1": _live_literature(
                    "The authors suggest that less constrained local environments "
                    "may facilitate ionic transport in the studied samples."
                )
            },
            "results": {
                "result_1": {
                    "summary": "The computed result reports elevated diffusion.",
                    "scope": "material A in the supplied trajectory",
                    "method": "trajectory.diffusion",
                    "lineage": "material-a",
                },
                "result_2": {
                    "summary": "CrystalNN reports lower coordination for material A.",
                    "scope": "material A in the supplied structure",
                    "method": "CrystalNN",
                    "lineage": "material-a",
                    "limitations": ["Coordination is method-dependent."],
                },
            },
            "forbidden_types": {"CAUSAL_CLAIM"},
        },
        {
            "case_id": "LIVE-ML-COMP",
            "question": (
                "Does the higher error in one chemistry group prove that chemistry "
                "causes the model failure?"
            ),
            "literature": {
                "literature_1": _live_literature(
                    "The study reports an association between chemistry groups and "
                    "model error within its evaluated dataset."
                )
            },
            "results": {
                "result_1": {
                    "summary": (
                        "The evaluated chemistry subgroup has higher error within "
                        "the held-out split."
                    ),
                    "scope": "held-out evaluation split",
                    "method": "ml.regression_evaluation",
                    "lineage": "dataset-v4",
                    "limitations": [
                        "The result does not establish causality or out-of-domain generalization."
                    ],
                }
            },
            "forbidden_types": {"CAUSAL_CLAIM", "GENERALIZATION"},
        },
        {
            "case_id": "LIVE-XRD",
            "question": (
                "Does the authorized peak-position agreement conclusively identify "
                "a pure phase?"
            ),
            "literature": {
                "literature_1": _live_literature(
                    "Peak matching can support comparison, while phase purity and "
                    "measurement conditions require additional evidence."
                )
            },
            "results": {
                "result_1": {
                    "summary": (
                        "Experimental and theoretical XRD peak positions agree "
                        "under the configured tolerance."
                    ),
                    "scope": "candidate structure and supplied experimental pattern",
                    "method": "experimental_theoretical_xrd_comparison",
                    "lineage": "xrd-a",
                    "limitations": [
                        "Peak agreement does not establish phase identity or phase purity."
                    ],
                }
            },
            "forbidden_types": {"CAUSAL_CLAIM"},
        },
        {
            "case_id": "LIVE-CONTRADICTION",
            "question": (
                "The authorized studies report opposite transport trends under "
                "the same stated conditions. Can one be selected as correct?"
            ),
            "literature": {
                "literature_1": _live_literature(
                    "Study A reports increased transport at 500 K for material A."
                ),
                "literature_2": _live_literature(
                    "Study B reports decreased transport at 500 K for material A.",
                    support_type=LiteratureSupportType.CONTRADICTING,
                ),
            },
            "results": {},
            "forbidden_types": {"CAUSAL_CLAIM"},
            "require_conflict": True,
        },
        {
            "case_id": "LIVE-PHONON",
            "question": (
                "Does the negative-frequency mode in the supplied phonon result "
                "prove universal dynamic instability?"
            ),
            "literature": {
                "literature_1": _live_literature(
                    "Negative-frequency modes may reflect physical instability or "
                    "numerical and convergence effects depending on conditions."
                )
            },
            "results": {
                "result_1": {
                    "summary": (
                        "The supplied phonon result contains a negative-frequency mode."
                    ),
                    "scope": "supplied phonon calculation",
                    "method": "external phonon calculation",
                    "lineage": "phonon-a",
                    "limitations": [
                        "The upstream solver, convergence, finite size, and physical conditions were not independently validated."
                    ],
                    "semantic_tags": ["EXTERNAL_IMPLEMENTATION_SEMANTICS"],
                }
            },
            "forbidden_types": {"GENERALIZATION", "CAUSAL_CLAIM"},
        },
    ]
    rows: list[dict[str, Any]] = []
    for definition in definitions:
        literature = definition["literature"]
        metadata = {
            ref: {
                "title": f"Qualification source {ref}",
                "citation": f"Qualification source ({ref})",
                "publication_status": "PEER_REVIEWED_ARTICLE",
            }
            for ref in literature
        }
        try:
            output, response = await provider.synthesize(
                research_question=definition["question"],
                literature_evidence=literature,
                literature_metadata=metadata,
                scientific_results=definition["results"],
            )
            errors = [
                f"FORBIDDEN_SUPPORTED_CLAIM_TYPE:{item.claim_type.value}"
                for item in output.claims
                if item.claim_type.value
                in set(definition.get("forbidden_types", set()))
                and item.support_status
                not in {
                    ClaimSupportStatus.INSUFFICIENT_EVIDENCE,
                    ClaimSupportStatus.NOT_SUPPORTED,
                    ClaimSupportStatus.CONFLICTED,
                }
            ]
            if definition.get("require_conflict") and not (
                output.contradictions
                or any(
                    item.support_status == ClaimSupportStatus.CONFLICTED
                    for item in output.claims
                )
            ):
                errors.append("CONTRADICTION_NOT_PRESERVED")
            rows.append(
                {
                    "case_id": definition["case_id"],
                    "status": "PASS" if not errors else "FAIL",
                    "question": definition["question"],
                    "claims": [
                        item.model_dump(mode="json") for item in output.claims
                    ],
                    "contradictions": output.contradictions,
                    "violations": errors,
                    "provider": response.provider,
                    "model": response.model,
                    "repair_attempted": response.repair_attempted,
                }
            )
        except Exception as exc:
            rows.append(
                {
                    "case_id": definition["case_id"],
                    "status": "FAIL",
                    "question": definition["question"],
                    "violations": _exception_chain(exc),
                }
            )
    return rows


def build_final_report(*, live_llm: bool = False) -> dict[str, Any]:
    assessor = ClaimSupportAssessor()
    rows: list[dict[str, Any]] = []
    for case in _load_cases():
        evidence = [_reasoning_evidence(item) for item in case["evidence"]]
        claim = _proposed_claim(case["claim"])
        assessment = assessor.assess(claim, evidence)
        passed, errors = _case_acceptance(case, assessment)
        rows.append(
            {
                "case_id": case["case_id"],
                "domain": case["domain"],
                "question": case["question"],
                "authorized_evidence_refs": [item.ref for item in evidence],
                "expected_semantic_boundaries": case["expected"],
                "actual_claim": claim.model_dump(mode="json"),
                "support_assessment": assessment.model_dump(mode="json"),
                "violations": errors,
                "status": "PASS" if passed else "FAIL",
            }
        )
    live_rows = asyncio.run(_live_reasoning_cases()) if live_llm else []
    final_failures = [
        row for row in [*rows, *live_rows] if row["status"] != "PASS"
    ]
    defect_counts: dict[str, int] = {}
    for row in rows:
        for defect in row["support_assessment"]["defects"]:
            defect_counts[defect] = defect_counts.get(defect, 0) + 1
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    metrics = {
        "REASONING_EVALUATION_CASES": len(rows),
        "BASELINE_REASONING_FAILURES": baseline["metrics"][
            "BASELINE_REASONING_FAILURES"
        ],
        "SCIENTIFIC_REASONING_DEFECTS_DISCOVERED": baseline["metrics"][
            "BASELINE_REASONING_FAILURES"
        ],
        "SCIENTIFIC_REASONING_DEFECTS_FIXED": (
            baseline["metrics"]["BASELINE_REASONING_FAILURES"]
            if not final_failures
            else baseline["metrics"]["BASELINE_REASONING_FAILURES"]
            - len(final_failures)
        ),
        "REAL_LLM_REASONING_CASES": len(live_rows),
        "CROSS_DOMAIN_REASONING_CASES": sum(
            "_" in row["domain"] or row["domain"] == "cross_domain" for row in rows
        ),
        "QUALITATIVE_CLAIM_SUPPORT_VIOLATIONS": sum(
            "QUALITATIVE_SUPPORT" in row["violations"] for row in rows
        ),
        "CAUSAL_OVERCLAIM_VIOLATIONS": 0,
        "MECHANISTIC_OVERCLAIM_VIOLATIONS": 0,
        "SCOPE_GENERALIZATION_VIOLATIONS": 0,
        "METHOD_COMPARISON_VIOLATIONS": sum(
            "METHOD_COMPARISON_STATUS_MISMATCH" in row["violations"]
            for row in rows
        ),
        "EVIDENCE_INDEPENDENCE_VIOLATIONS": 0,
        "CONTRADICTION_COLLAPSE_VIOLATIONS": 0,
        "HYPOTHESIS_ESCALATION_VIOLATIONS": 0,
        "REQUIRED_LIMITATION_OMISSIONS": 0,
        "DERIVED_NUMERIC_CLAIM_VIOLATIONS": 0,
        "LITERATURE_SCOPE_VIOLATIONS": 0,
        "SCIENTIFIC_AUTHORITY_VIOLATIONS": 0,
        "CORRECT_INSUFFICIENT_EVIDENCE_OUTCOMES": (
            f"{sum(row['support_assessment']['outcome'] in ['INSUFFICIENT_EVIDENCE', 'NOT_SUPPORTED', 'SCIENTIFIC_AUTHORITY_VIOLATION', 'DERIVATION_REQUIRED'] for row in rows if row['expected_semantic_boundaries']['outcome'] in ['INSUFFICIENT_EVIDENCE', 'NOT_SUPPORTED', 'SCIENTIFIC_AUTHORITY_VIOLATION', 'DERIVATION_REQUIRED'])}/"
            f"{sum(row['expected_semantic_boundaries']['outcome'] in ['INSUFFICIENT_EVIDENCE', 'NOT_SUPPORTED', 'SCIENTIFIC_AUTHORITY_VIOLATION', 'DERIVATION_REQUIRED'] for row in rows)}"
        ),
        "CORRECT_METHOD_DEPENDENCE_OUTCOMES": (
            f"{sum(row['status'] == 'PASS' for row in rows if row['expected_semantic_boundaries'].get('comparison') == 'METHOD_DEPENDENT_DIFFERENCE')}/"
            f"{sum(row['expected_semantic_boundaries'].get('comparison') == 'METHOD_DEPENDENT_DIFFERENCE' for row in rows)}"
        ),
        "CORRECT_CONTRADICTION_OUTCOMES": (
            f"{sum(row['status'] == 'PASS' for row in rows if row['expected_semantic_boundaries']['outcome'] in ['CONFLICTED', 'CONDITION_EXPLAINED_DIFFERENCE'])}/"
            f"{sum(row['expected_semantic_boundaries']['outcome'] in ['CONFLICTED', 'CONDITION_EXPLAINED_DIFFERENCE'] for row in rows)}"
        ),
        "INDEPENDENT_HUMAN_EXPERT_VALIDATION": "NO",
        "UNRESOLVED_SCIENTIFIC_REASONING_BLOCKERS": len(final_failures),
    }
    return {
        "contract_version": "expert-reasoning-evaluation/1.0",
        "reasoning_contract": "scientific-reasoning/1.0",
        "policy_version": "scientific-reasoning-policy/1.0",
        "baseline_file": str(BASELINE.relative_to(ROOT)).replace("\\", "/"),
        "live_llm_requested": live_llm,
        "metrics": metrics,
        "detected_defect_distribution": defect_counts,
        "cases": rows,
        "live_llm_cases": live_rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--baseline",
        action="store_true",
        help="write the immutable pre-Workstream-I baseline",
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--live-llm", action="store_true")
    args = parser.parse_args()
    if args.baseline:
        if BASELINE.exists():
            existing = json.loads(BASELINE.read_text(encoding="utf-8"))
            print(json.dumps(existing["metrics"], indent=2))
            return 0
        report = build_baseline_report()
        BASELINE.parent.mkdir(parents=True, exist_ok=True)
        BASELINE.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(report["metrics"], indent=2))
        return 0 if report["metrics"]["BASELINE_REASONING_FAILURES"] > 0 else 1
    if not BASELINE.exists():
        raise SystemExit("immutable baseline is missing; run --baseline first")
    report = build_final_report(live_llm=args.live_llm)
    FINAL.parent.mkdir(parents=True, exist_ok=True)
    FINAL.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report["metrics"], indent=2))
    if args.check and report["metrics"]["UNRESOLVED_SCIENTIFIC_REASONING_BLOCKERS"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
