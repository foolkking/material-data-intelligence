from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from pathlib import Path

import pytest

from mdi_llm import AnalysisIntentRequest, DeterministicAnalysisIntentBuilder, MockLLMProvider, plan_capabilities
from mdi_tool_registry import load_manifests
from mdi_tool_registry.plan_validator import validate_plan
from scripts.generate_phase13_1_product_entry_fix_forward import FIXED_CREATED_AT, _entry_record, _parse_demo
from scripts.phase13_current_demo_contracts import CURRENT_DEMO_SPECS, DEMO1_CANONICAL_PROMPT


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/phase13/evidence/phase13_1_capability_report_fix_forward_4"


@pytest.mark.parametrize("spec", CURRENT_DEMO_SPECS, ids=lambda item: item["demoId"])
def test_all_current_canonical_demos_cover_their_required_semantic_capabilities(spec: dict) -> None:
    registry = load_manifests()
    record = _entry_record(spec, registry, {item.toolId for item in registry.tools})

    assert record["intentOutcome"] == "READY"
    assert record["planningOutcome"] == "PLAN_READY"
    assert record["planValidated"] is True
    assert sorted(record["selectedTools"]) == sorted(spec["expectedTools"])
    assert record["ready"] is True


@pytest.mark.parametrize(
    ("goal", "required", "forbidden"),
    [
        ("Explore this materials dataset and summarize its quality.", {"dataset.materials_explorer"}, {"dataset.composition_space"}),
        ("Map these compositions in composition space.", {"dataset.composition_space"}, {"dataset.materials_explorer"}),
        ("Summarize this materials dataset and show its composition-space embedding and bounded clusters.", {"dataset.materials_explorer", "dataset.composition_space"}, set()),
    ],
)
def test_demo1_semantic_coverage_is_bounded_and_paraphrase_stable(goal: str, required: set[str], forbidden: set[str]) -> None:
    registry = load_manifests()
    parsed, profile = _parse_demo(CURRENT_DEMO_SPECS[0], {item.toolId for item in registry.tools})
    selected = tuple(sorted(obj.id for result in parsed for obj in result.objects))
    intent = DeterministicAnalysisIntentBuilder().build(
        AnalysisIntentRequest(
            raw_goal=goal,
            dataset_id=profile.datasetId,
            profile_id=profile.profileId,
            selected_resource_ids=selected,
        ),
        profile=profile,
        created_at=FIXED_CREATED_AT,
    )
    planned = plan_capabilities(intent, profile=profile, registry=registry, provider=MockLLMProvider())
    actual = {item.toolId for item in planned.decision.selections}

    assert required.issubset(actual)
    assert actual.isdisjoint(forbidden)
    assert planned.plan is not None and planned.plan.schemaVersion == "0.1"
    assert validate_plan(planned.plan.model_dump(mode="json"), registry=registry).ok


def test_demo1_contract_correction_is_prompt_authority_not_production_routing() -> None:
    assert DEMO1_CANONICAL_PROMPT == (
        "Explore this materials dataset, summarize its quality, and map its "
        "compositions in composition space."
    )
    assert CURRENT_DEMO_SPECS[0]["expectedTools"] == (
        "dataset.composition_space",
        "dataset.materials_explorer",
    )


def test_registry_order_does_not_change_demo1_semantic_selection() -> None:
    registry = load_manifests()
    reversed_registry = replace(registry, tools=tuple(reversed(registry.tools)))
    tool_ids = {item.toolId for item in registry.tools}
    forward = _entry_record(CURRENT_DEMO_SPECS[0], registry, tool_ids)
    reverse = _entry_record(CURRENT_DEMO_SPECS[0], reversed_registry, tool_ids)

    assert forward["selectedTools"] == reverse["selectedTools"]
    assert forward["selectedTools"] == ["dataset.composition_space", "dataset.materials_explorer"]


def test_fix_forward_4_evidence_manifest_is_complete_and_exact() -> None:
    required = {
        "entry_gate.md",
        "canonical_demo_semantic_coverage_matrix.json",
        "fresh_demo1_closure_smoke.json",
        "fresh_demo1_report_ui.json",
        "fresh_demo1_report.json",
        "fresh_demo1_recipe.json",
        "browser_matrix.json",
        "service_environment.json",
        "platform_replay.json",
        "security.md",
        "secret_scan.txt",
    }
    manifest = json.loads((EVIDENCE / "manifest.json").read_text(encoding="utf-8"))
    records = {item["path"]: item for item in manifest["records"]}

    assert required.issubset(records)
    assert manifest["missing"] == manifest["hashMismatch"] == manifest["unclassified"] == 0
    for relative, record in records.items():
        payload = (EVIDENCE / relative).read_bytes()
        assert hashlib.sha256(payload).hexdigest() == record["sha256"]
        assert len(payload) == record["size"]


def test_fix_forward_4_real_smoke_and_platform_evidence_are_closed() -> None:
    smoke = json.loads((EVIDENCE / "fresh_demo1_closure_smoke.json").read_text(encoding="utf-8"))
    report_ui = json.loads((EVIDENCE / "fresh_demo1_report_ui.json").read_text(encoding="utf-8"))
    platform = json.loads((EVIDENCE / "platform_replay.json").read_text(encoding="utf-8"))

    assert smoke["status"] == "PASS"
    assert smoke["realChromiumFinalize"] is True
    assert report_ui["status"] == "PASS"
    assert report_ui["finalizeEnabled"] is True
    assert platform["status"] == "PASS"
    assert platform["linuxScopeHash"] == platform["windowsScopeHash"]
