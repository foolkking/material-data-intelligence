"""Generate the bounded scientific-autonomy golden-case evaluation report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
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

from mdi_api.domain.scientific_results.contracts import (  # noqa: E402
    FactSourceLocator,
    MethodRecord,
    ProvenanceRecord,
    ResultExecutionStatus,
    ResultRelevanceStatus,
    ScientificLimitation,
    ScientificFact,
    ScientificResultBundle,
    ScientificResultItem,
    ScientificResultRole,
)
from mdi_api.research_agent.autonomy import (  # noqa: E402
    AutonomyProgressOutcome,
    GoldenAutonomyCase,
    evaluate_golden_cases,
)
from mdi_api.research_agent.autonomy.assessment import (  # noqa: E402
    semantic_step_signature,
)
from mdi_api.research_agent.registry_validation import (  # noqa: E402
    DEFAULT_AGENT2_REGISTRIES,
)
from mdi_api.scientific_objects.schemas import (  # noqa: E402
    ScientificObjectRef,
)


def _bundle(
    capability_id: str,
    result_type: str,
    *,
    status: ResultExecutionStatus = ResultExecutionStatus.SUCCESS,
) -> ScientificResultBundle:
    object_type = "trajectory.atomic"
    if capability_id.startswith(("data.", "ml.")):
        object_type = "dataset.tabular"
    elif capability_id.startswith("structure."):
        object_type = "structure.crystal"
    source = ScientificObjectRef(
        object_id=uuid4(),
        version_id=uuid4(),
        project_id="qualification-project",
        object_type=object_type,
    )
    facts = []
    if result_type == "trajectory.msd":
        facts = [
            ScientificFact(
                fact_id="trajectory.msd.lag-count",
                predicate="trajectory.msd_lag_count",
                subject_ref=str(source.version_id),
                value=6,
                unit="count",
                source=FactSourceLocator(artifact_locator="/coverage/validLags"),
            ),
            ScientificFact(
                fact_id="trajectory.msd.first-lag",
                predicate="trajectory.msd_first_lag_time",
                subject_ref=str(source.version_id),
                value=1.0,
                unit="picosecond",
                source=FactSourceLocator(artifact_locator="/lagTimesPs/0"),
            ),
            ScientificFact(
                fact_id="trajectory.msd.last-lag",
                predicate="trajectory.msd_last_lag_time",
                subject_ref=str(source.version_id),
                value=6.0,
                unit="picosecond",
                source=FactSourceLocator(artifact_locator="/lagTimesPs/5"),
            ),
        ]
    return ScientificResultBundle(
        schema_version="1.0",
        result_id=uuid4(),
        project_id="qualification-project",
        research_session_id="qualification-session",
        research_turn_id=uuid4(),
        research_question="Bounded autonomy qualification case.",
        source_object_refs=[source],
        execution_status=status,
        relevance_status=ResultRelevanceStatus.CURRENT,
        result_items=[
            ScientificResultItem(
                id=result_type,
                result_type=result_type,
                role=ScientificResultRole.PRIMARY,
                title=result_type,
                artifact_ids=[],
                scientific_object_refs=[],
                fact_refs=[fact.fact_id for fact in facts],
                evidence_refs=[],
            )
        ],
        facts=facts,
        figures=[],
        tables=[],
        output_object_refs=[],
        evidence=[],
        methods=[
            MethodRecord(
                method_id=f"method:{capability_id}",
                capability_id=capability_id,
                capability_version="1.0",
                source_object_refs=[source],
            )
        ],
        limitations=(
            [
                ScientificLimitation(
                    limitation_id="partial-evidence",
                    code="PARTIAL_EVIDENCE",
                    message="Only partial qualified evidence is available.",
                )
            ]
            if status == ResultExecutionStatus.PARTIAL
            else []
        ),
        warnings=[],
        provenance=ProvenanceRecord(
            research_turn_id=uuid4(),
            source_object_version_ids=[source.version_id],
        ),
        projection_version="autonomy-evaluation/1.0",
    )


def build_cases() -> list[GoldenAutonomyCase]:
    manifests = DEFAULT_AGENT2_REGISTRIES.capabilities
    common = {"manifests": manifests}
    loop_bundle = _bundle("trajectory.msd", "trajectory.msd")
    loop_signature = semantic_step_signature(
        capability_id="trajectory.diffusion",
        source_version_ids=[
            str(ref.version_id) for ref in loop_bundle.source_object_refs
        ],
        parameters={
            "fit_start_time_ps": 1.0,
            "fit_end_time_ps": 6.0,
        },
    )
    return [
        GoldenAutonomyCase(
            case_id="trajectory-msd-to-diffusion",
            goal="Analyze the diffusion behavior in this trajectory.",
            current_result=_bundle("trajectory.msd", "trajectory.msd"),
            completed_capability_ids=frozenset({"trajectory.msd"}),
            expected_outcomes=frozenset(
                {AutonomyProgressOutcome.CONTINUE_WITH_ANALYSIS}
            ),
            allowed_next_capabilities=frozenset({"trajectory.diffusion"}),
            **common,
        ),
        GoldenAutonomyCase(
            case_id="trajectory-repeat-loop-stop",
            goal="Analyze the diffusion behavior in this trajectory.",
            current_result=loop_bundle,
            completed_capability_ids=frozenset({"trajectory.msd"}),
            expected_outcomes=frozenset({AutonomyProgressOutcome.NON_PROGRESS}),
            existing_semantic_step_signatures=frozenset({loop_signature}),
            expected_stop=True,
            **common,
        ),
        GoldenAutonomyCase(
            case_id="trajectory-evidence-sufficient",
            goal="Summarize the completed mean squared displacement analysis.",
            current_result=_bundle("trajectory.msd", "trajectory.msd"),
            completed_capability_ids=frozenset({"trajectory.msd"}),
            expected_outcomes=frozenset({AutonomyProgressOutcome.GOAL_SATISFIED}),
            expected_stop=True,
            **common,
        ),
        GoldenAutonomyCase(
            case_id="dataset-error-pattern",
            goal="Investigate where this model performs poorly and whether errors have a materials pattern.",
            current_result=_bundle("ml.regression_evaluation", "ml.regression_evaluation"),
            completed_capability_ids=frozenset({"ml.regression_evaluation"}),
            expected_outcomes=frozenset(
                {AutonomyProgressOutcome.CONTINUE_WITH_ANALYSIS}
            ),
            allowed_next_capabilities=frozenset({"data.composition_space"}),
            **common,
        ),
        GoldenAutonomyCase(
            case_id="structure-local-environment",
            goal="Explain the local coordination environment.",
            current_result=_bundle("structure.rdf", "structure.rdf"),
            completed_capability_ids=frozenset({"structure.rdf"}),
            expected_outcomes=frozenset(
                {AutonomyProgressOutcome.CONTINUE_WITH_ANALYSIS}
            ),
            allowed_next_capabilities=frozenset(
                {"structure.coordination_hist"}
            ),
            **common,
        ),
        GoldenAutonomyCase(
            case_id="unsupported-causal-claim",
            goal="Prove that the observed structural feature causes the performance change.",
            current_result=_bundle("structure.rdf", "structure.rdf"),
            completed_capability_ids=frozenset({"structure.rdf"}),
            expected_outcomes=frozenset(
                {AutonomyProgressOutcome.STOP_WITH_LIMITATIONS}
            ),
            expected_stop=True,
            unsupported_claim_case=True,
            **common,
        ),
        GoldenAutonomyCase(
            case_id="partial-result-stop",
            goal="Explain the available evidence.",
            current_result=_bundle(
                "data.materials_explorer",
                "data.materials_explorer",
                status=ResultExecutionStatus.PARTIAL,
            ),
            completed_capability_ids=frozenset({"data.materials_explorer"}),
            expected_outcomes=frozenset(
                {AutonomyProgressOutcome.STOP_WITH_LIMITATIONS}
            ),
            expected_stop=True,
            **common,
        ),
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT
        / "docs"
        / "agent2"
        / "autonomy"
        / "generated"
        / "autonomy_evaluation.json",
    )
    args = parser.parse_args()
    report = evaluate_golden_cases(build_cases())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    return 1 if args.check and not report.accepted else 0


if __name__ == "__main__":
    raise SystemExit(main())
