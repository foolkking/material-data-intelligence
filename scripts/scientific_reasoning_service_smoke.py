"""Rollback-only PostgreSQL persistence smoke for Workstream I.

The smoke writes a Result snapshot, Interpretation 1.1 claim assessment, and
Report snapshot through the canonical repositories, reopens them, validates
their contracts, and rolls the transaction back. No scientific or user data is
left behind.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from uuid import uuid4

from sqlalchemy import create_engine, insert


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

from mdi_api.application.scientific_reasoning.assessment import (  # noqa: E402
    ClaimSupportAssessor,
)
from mdi_api.db import (  # noqa: E402
    jobs,
    messages,
    organizations,
    projects,
    reports,
    research_turns,
    sessions,
    users,
)
from mdi_api.domain.interpretation.contracts import (  # noqa: E402
    ScientificInterpretationOutput,
)
from mdi_api.domain.scientific_reasoning.contracts import (  # noqa: E402
    ProposedScientificClaim,
    ReasoningEvidence,
)
from mdi_api.domain.scientific_reports.contracts import (  # noqa: E402
    ScientificReportOutput,
)
from mdi_api.infrastructure.persistence.agent2_bundle import (  # noqa: E402
    Agent2RepositoryBundle,
)


DEFAULT_OUTPUT = (
    ROOT
    / "docs"
    / "scientific-reasoning"
    / "generated"
    / "real_service_reasoning_path.json"
)


def run_smoke(database_url: str) -> dict[str, object]:
    engine = create_engine(database_url, pool_pre_ping=True)
    if engine.dialect.name != "postgresql":
        raise RuntimeError("Workstream I service smoke requires PostgreSQL")

    suffix = uuid4().hex[:12]
    user_id = f"ws_i_user_{suffix}"
    organization_id = f"ws_i_org_{suffix}"
    project_id = f"ws_i_project_{suffix}"
    session_id = f"ws_i_session_{suffix}"
    message_id = f"ws_i_message_{suffix}"
    job_id = f"ws_i_job_{suffix}"
    report_id = f"ws_i_report_{suffix}"
    turn_id = uuid4()
    result_snapshot_id = uuid4()
    interpretation_id = uuid4()
    report_snapshot_id = uuid4()

    assessment = ClaimSupportAssessor().assess(
        ProposedScientificClaim(
            claim_id="finding.service",
            text="The persisted Result reports a bounded observation.",
            claim_type="DIRECT_OBSERVATION",
            support_status="DIRECTLY_SUPPORTED",
            evidence_refs=["result_1"],
            scope="qualification-owned service fixture",
        ),
        [
            ReasoningEvidence(
                ref="result_1",
                origin="COMPUTED",
                text="The persisted Result reports a bounded observation.",
                scope="qualification-owned service fixture",
                method="workstream_i.persistence_smoke",
                lineage="qualification-owned-service-fixture",
            )
        ],
    )
    if not assessment.accepted:
        raise RuntimeError("service-smoke claim assessment was unexpectedly rejected")

    interpretation = ScientificInterpretationOutput.model_validate(
        {
            "contract_version": "1.1",
            "title": "Persisted scientific reasoning",
            "answer_lead": assessment.scope,
            "primary_findings": [
                {
                    "finding_id": "finding.service",
                    "statement": "The persisted Result reports a bounded observation.",
                    "importance": "HIGH",
                    "confidence": "HIGH",
                    "fact_refs": [],
                    "evidence_refs": [],
                    "result_item_refs": [],
                    "claim_type": "DIRECT_OBSERVATION",
                    "support_status": "DIRECTLY_SUPPORTED",
                    "scope": assessment.scope,
                    "reasoning_assessment": assessment.model_dump(mode="json"),
                }
            ],
            "supporting_findings": [],
            "limitations": [],
            "primary_result_refs": [],
            "supporting_result_refs": [],
            "follow_up_suggestions": [],
        }
    )
    report = ScientificReportOutput.model_validate(
        {
            "contract_version": "2.0",
            "title": "Persisted scientific reasoning report",
            "research_question": "Does claim support survive persistence?",
            "summary": "The accepted claim assessment is preserved.",
            "main_findings": [
                {
                    "statement": "The persisted Result reports a bounded observation.",
                    "finding_refs": ["finding.service"],
                    "reasoning_assessment": assessment.model_dump(mode="json"),
                }
            ],
            "method_summary": "Canonical Workstream I repository persistence smoke.",
            "limitations": [],
            "data_sources": [],
            "evidence_refs": [],
            "reproducibility_summary": (
                "The transaction is rollback-only and the assessment fingerprint "
                "is compared after reopening."
            ),
        }
    )

    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            connection.execute(
                insert(users),
                {
                    "id": user_id,
                    "email": f"{user_id}@example.invalid",
                    "display_name": "Workstream I",
                    "is_active": True,
                },
            )
            connection.execute(
                insert(organizations),
                {"id": organization_id, "name": f"Workstream I {suffix}"},
            )
            connection.execute(
                insert(projects),
                {
                    "id": project_id,
                    "organization_id": organization_id,
                    "name": f"Workstream I {suffix}",
                    "created_by": user_id,
                },
            )
            connection.execute(
                insert(sessions),
                {
                    "id": session_id,
                    "project_id": project_id,
                    "mode": "project",
                    "status": "active",
                    "created_by": user_id,
                },
            )
            connection.execute(
                insert(messages),
                {
                    "id": message_id,
                    "session_id": session_id,
                    "role": "user",
                    "content_summary": "Workstream I persistence smoke",
                    "payload_json": {},
                },
            )
            connection.execute(
                insert(research_turns),
                {
                    "id": turn_id,
                    "project_id": project_id,
                    "research_session_id": session_id,
                    "sequence_no": 1,
                    "user_message_id": message_id,
                    "action_type": "INTERPRET_RESULT",
                    "status": "COMPLETED",
                },
            )
            connection.execute(
                insert(jobs),
                {
                    "id": job_id,
                    "project_id": project_id,
                    "kind": "qualification",
                    "status": "completed",
                    "created_by": user_id,
                },
            )

            repositories = Agent2RepositoryBundle.create(connection)
            repositories.scientific_result_snapshots.add(
                {
                    "id": result_snapshot_id,
                    "project_id": project_id,
                    "research_turn_id": turn_id,
                    "job_id": job_id,
                    "schema_version": "1.0",
                    "projection_version": "workstream-i-service/1.0",
                    "execution_status": "SUCCESS",
                    "relevance_status": "CURRENT",
                    "source_fingerprint": "a" * 64,
                    "bundle_json": {"qualification_owned": True},
                }
            )
            repositories.interpretations.add(
                {
                    "id": interpretation_id,
                    "research_turn_id": turn_id,
                    "result_snapshot_id": result_snapshot_id,
                    "project_id": project_id,
                    "contract_version": "1.1",
                    "prompt_version": "scientific-interpreter/1.1",
                    "provider": "deterministic",
                    "model": "claim-support-assessor",
                    "provider_request_id": None,
                    "repair_attempted": False,
                    "input_fingerprint": "b" * 64,
                    "grounding_status": "VALID",
                    "output_json": interpretation.model_dump(mode="json"),
                }
            )
            connection.execute(
                insert(reports),
                {
                    "id": report_id,
                    "project_id": project_id,
                    "job_id": job_id,
                    "title": report.title,
                    "report_json": report.model_dump(mode="json"),
                    "created_by": user_id,
                },
            )
            repositories.scientific_reports.add(
                {
                    "id": report_snapshot_id,
                    "report_id": report_id,
                    "project_id": project_id,
                    "research_session_id": session_id,
                    "research_turn_id": turn_id,
                    "scientific_result_snapshot_id": result_snapshot_id,
                    "scientific_interpretation_id": interpretation_id,
                    "contract_version": "2.0",
                    "composer_version": "agent2.report-composer/2.0",
                    "prompt_version": "scientific-report-composer/2.0",
                    "source_fingerprint": "c" * 64,
                    "relevance_at_generation": "CURRENT",
                    "grounding_status": "VALID",
                    "report_json": report.model_dump(mode="json"),
                    "created_by": user_id,
                }
            )

            reopened_interpretation = ScientificInterpretationOutput.model_validate(
                repositories.interpretations.get(interpretation_id)["output_json"]
            )
            reopened_report = ScientificReportOutput.model_validate(
                repositories.scientific_reports.get(report_snapshot_id)["report_json"]
            )
            reopened_interpretation_assessment = (
                reopened_interpretation.primary_findings[0].reasoning_assessment
            )
            reopened_report_assessment = (
                reopened_report.main_findings[0].reasoning_assessment
            )
            if (
                reopened_interpretation_assessment is None
                or reopened_report_assessment is None
                or reopened_interpretation_assessment.fingerprint
                != assessment.fingerprint
                or reopened_report_assessment.fingerprint != assessment.fingerprint
            ):
                raise RuntimeError("reasoning assessment changed across persistence")
        finally:
            transaction.rollback()
    engine.dispose()
    return {
        "contract_version": "scientific-reasoning-service-smoke/1.0",
        "database_backend": "postgresql",
        "transaction_rolled_back": True,
        "scientific_result_snapshot_persisted": True,
        "interpretation_1_1_reopened": True,
        "report_2_0_reopened": True,
        "claim_assessment_fingerprint_preserved": True,
        "assessment_version": assessment.assessment_version,
        "hidden_reasoning_persisted": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    database_url = os.getenv("MDI_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not database_url:
        raise SystemExit("MDI_DATABASE_URL or DATABASE_URL is required")
    result = run_smoke(database_url)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, sort_keys=True))
    return 0 if not args.check or all(
        result[key]
        for key in (
            "transaction_rolled_back",
            "scientific_result_snapshot_persisted",
            "interpretation_1_1_reopened",
            "report_2_0_reopened",
            "claim_assessment_fingerprint_preserved",
        )
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
