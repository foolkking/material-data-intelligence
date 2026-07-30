from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError

from mdi_schemas import AnalysisPlan, DependencyCompositionProposal
from mdi_schemas.dependency_planning import (
    AnalysisPlanV02,
    ArtifactLineageRecord,
    DependencyBinding,
    DependencyExecutionRecord,
    ResolvedArtifactInputRef,
    ToolArtifactPortMetadata,
    compute_analysis_plan_02_hash,
    compute_dependency_graph_hash,
    make_dependency_binding,
    topological_order,
)
from mdi_schemas.models import AnalysisStep
from mdi_llm.dependency_planner import compose_analysis_plan_with_provider
from mdi_llm.providers import OpenAICompatibleProvider
from mdi_tool_registry import build_artifact_compatibility_matrix, load_manifests, validate_dependency_plan


def _step(step_id: str, tool_id: str = "phonon.band") -> AnalysisStep:
    return AnalysisStep.model_validate(
        {
            "stepId": step_id,
            "toolId": tool_id,
            "purpose": f"Execute {tool_id}",
            "reason": "Validated dependency fixture",
            "inputRefs": [
                {
                    "refType": "normalized_object",
                    "ref": f"resource_{step_id}",
                    "objectType": "PhononBand",
                }
            ],
            "params": {},
            "output": {"artifactTypes": ["phonon_band_json"], "displayTarget": "phonon"},
        }
    )


def _binding(
    producer: str,
    consumer: str,
    *,
    output_port: str = "canonical-band",
    input_port: str = "band",
) -> DependencyBinding:
    return make_dependency_binding(
        producerStepId=producer,
        producerOutputPort=output_port,
        consumerStepId=consumer,
        consumerInputPort=input_port,
        artifactKind="phonon_band_json",
        artifactContractVersion="phase10h.phonon_band.v1",
        mediaType="application/json",
        cardinality="EXACTLY_ONE",
    )


def _plan(*, steps: list[AnalysisStep] | None = None, bindings: list[DependencyBinding] | None = None) -> AnalysisPlanV02:
    actual_steps = steps or [_step("band"), _step("combined", "phonon.band_dos")]
    actual_bindings = bindings if bindings is not None else [_binding("band", "combined")]
    return AnalysisPlanV02.model_validate(
        {
            "schemaVersion": "0.2",
            "goal": "Compose typed phonon artifacts.",
            "datasetId": "dataset_1",
            "profileId": "profile_1",
            "toolRegistryVersion": "1.0",
            "graphHash": compute_dependency_graph_hash(actual_bindings),
            "assumptions": [],
            "warnings": [],
            "steps": [item.model_dump(mode="json") for item in actual_steps],
            "dependencyBindings": [item.model_dump(mode="json") for item in actual_bindings],
            "expectedArtifacts": [],
        }
    )


def test_analysis_plan_02_is_strict_and_keeps_analysis_plan_01_unchanged() -> None:
    plan = _plan()
    assert plan.schemaVersion == "0.2"
    assert topological_order(plan.steps, plan.dependencyBindings) == ["band", "combined"]

    payload = plan.model_dump(mode="json")
    payload["unexpected"] = True
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        AnalysisPlanV02.model_validate(payload)

    legacy = AnalysisPlan.model_validate(
        {
            "schemaVersion": "0.1",
            "goal": "Legacy plan",
            "datasetId": "dataset_1",
            "profileId": "profile_1",
            "toolRegistryVersion": "1.0",
            "steps": [_step("legacy").model_dump(mode="json")],
        }
    )
    assert legacy.schemaVersion == "0.1"
    assert "dependencyBindings" not in legacy.model_dump(mode="json")
    with pytest.raises(ValidationError):
        AnalysisPlan.model_validate({**legacy.model_dump(mode="json"), "schemaVersion": "0.2"})


def test_binding_graph_and_plan_hashes_are_deterministic() -> None:
    first = _binding("band", "combined")
    second = _binding("band", "combined")
    dos = _binding("dos", "combined", output_port="canonical-dos", input_port="dos")
    assert first.bindingId == second.bindingId
    assert compute_dependency_graph_hash([first, dos]) == compute_dependency_graph_hash([dos, first])

    plan = _plan(
        steps=[_step("band"), _step("dos", "phonon.dos"), _step("combined", "phonon.band_dos")],
        bindings=[first, dos],
    )
    assert compute_analysis_plan_02_hash(plan) == compute_analysis_plan_02_hash(plan.model_dump(mode="json"))
    assert len(compute_analysis_plan_02_hash(plan)) == 64


def test_cycle_and_duplicate_consumer_port_are_rejected() -> None:
    steps = [_step("a"), _step("b")]
    with pytest.raises(ValidationError, match="cycle"):
        _plan(steps=steps, bindings=[_binding("a", "b"), _binding("b", "a")])

    duplicate_port = [
        _binding("a", "c", input_port="band"),
        _binding("b", "c", output_port="other-band", input_port="band"),
    ]
    with pytest.raises(ValidationError, match="input port may be bound only once"):
        _plan(steps=[_step("a"), _step("b"), _step("c")], bindings=duplicate_port)


def test_step_binding_and_depth_caps_are_enforced() -> None:
    with pytest.raises(ValidationError):
        _plan(steps=[_step(f"s{i}") for i in range(5)], bindings=[])

    depth_steps = [_step(f"s{i}") for i in range(5)]
    depth_bindings = [_binding(f"s{i}", f"s{i + 1}") for i in range(4)]
    with pytest.raises(ValueError, match="depth cap exceeded"):
        topological_order(depth_steps, depth_bindings)

    six = [_binding("a", "b", output_port=f"out-{i}", input_port=f"in-{i}") for i in range(6)]
    with pytest.raises(ValidationError):
        _plan(steps=[_step("a"), _step("b")], bindings=six + [_binding("a", "b", output_port="overflow", input_port="overflow")])


@pytest.mark.parametrize(
    ("payload_mutator", "expected_code"),
    [
        (
            lambda payload: payload["dependencyBindings"][0].update({"producerStepId": "missing"}),
            "UNKNOWN_STEP",
        ),
        (
            lambda payload: payload["dependencyBindings"][0].update({"producerOutputPort": "invented"}),
            "DEPENDENCY_COMPOSITION_NOT_ALLOWED",
        ),
        (
            lambda payload: payload.update({"graphHash": "f" * 64}),
            "GRAPH_IDENTITY_INVALID",
        ),
    ],
)
def test_dependency_validator_returns_typed_diagnostics(payload_mutator, expected_code: str) -> None:
    payload = _plan().model_dump(mode="json")
    payload_mutator(payload)
    if expected_code != "GRAPH_IDENTITY_INVALID":
        binding = payload["dependencyBindings"][0]
        binding["bindingId"] = make_dependency_binding(
            producerStepId=binding["producerStepId"],
            producerOutputPort=binding["producerOutputPort"],
            consumerStepId=binding["consumerStepId"],
            consumerInputPort=binding["consumerInputPort"],
            artifactKind=binding["artifactKind"],
            artifactContractVersion=binding["artifactContractVersion"],
            mediaType=binding["mediaType"],
            cardinality=binding["cardinality"],
        ).bindingId
        payload["graphHash"] = compute_dependency_graph_hash([DependencyBinding.model_validate(binding)])
    result = validate_dependency_plan(payload, registry=load_manifests())
    assert result.ok is False
    assert result.errors[0].code.value == expected_code


def test_checked_in_json_schema_matches_python_contracts_and_validates_plan() -> None:
    checked_in = json.loads(Path("packages/schemas/json/dependency-planning-v1.schema.json").read_text(encoding="utf-8"))
    assert checked_in == {
        "analysisPlanV02": AnalysisPlanV02.model_json_schema(),
        "dependencyBinding": DependencyBinding.model_json_schema(),
        "dependencyCompositionProposal": DependencyCompositionProposal.model_json_schema(),
        "toolArtifactPortMetadata": ToolArtifactPortMetadata.model_json_schema(),
        "dependencyExecutionRecord": DependencyExecutionRecord.model_json_schema(),
        "resolvedArtifactInputRef": ResolvedArtifactInputRef.model_json_schema(),
        "artifactLineageRecord": ArtifactLineageRecord.model_json_schema(),
    }
    Draft202012Validator(checked_in["analysisPlanV02"]).validate(_plan().model_dump(mode="json"))


def test_typescript_contract_tokens_match_python_contract() -> None:
    source = Path("packages/schemas/src/index.ts").read_text(encoding="utf-8")
    required_types = (
        "AnalysisPlanV02",
        "DependencyBinding",
        "DependencyCompositionProposal",
        "ArtifactOutputPort",
        "ArtifactInputPort",
        "ToolArtifactPortMetadata",
        "DependencyExecutionRecord",
        "ResolvedArtifactInputRef",
        "ArtifactLineageRecord",
    )
    for type_name in required_types:
        assert f"export type {type_name} =" in source
    for field in AnalysisPlanV02.model_fields:
        assert f"{field}:" in source
    for field in DependencyBinding.model_fields:
        assert f"{field}:" in source
    for token in (
        'schemaVersion: "0.1"',
        'schemaVersion: "0.2"',
        'schemaVersion: "1.1"',
        '"EXACTLY_ONE"',
        '"BLOCKED_DEPENDENCY"',
        '"PARTIAL_RESULTS"',
        '"CHECKSUM_MISMATCH"',
    ):
        assert token in source


def _phonon_base_plan() -> AnalysisPlan:
    return AnalysisPlan.model_validate(
        {
            "schemaVersion": "0.1",
            "goal": "Create a combined phonon band and DOS product.",
            "datasetId": "dataset_1",
            "profileId": "profile_1",
            "toolRegistryVersion": load_manifests().version,
            "steps": [
                _step("band", "phonon.band").model_dump(mode="json"),
                _step("dos", "phonon.dos").model_dump(mode="json"),
                _step("combined", "phonon.band_dos").model_dump(mode="json"),
            ],
        }
    )


def test_llm_composer_sees_only_compatible_pair_ids_and_uses_one_shared_repair() -> None:
    registry = load_manifests()
    selected = ["phonon.band", "phonon.band_dos", "phonon.dos"]
    matrix = build_artifact_compatibility_matrix(registry, selected_tool_ids=selected)
    compatible_ids = sorted(item.pairId for item in matrix.pairs if item.compatible)
    assert len(compatible_ids) == 2
    assert len(set(compatible_ids)) == 2
    calls: list[dict[str, object]] = []

    def transport(**kwargs: object) -> dict[str, object]:
        calls.append(kwargs)
        context = json.loads(kwargs["messages"][-1]["content"])
        assert sorted(item["pairId"] for item in context["compatiblePairs"]) == compatible_ids
        assert "artifactPayload" not in json.dumps(context)
        selected_pair_ids = [] if len(calls) == 1 else compatible_ids
        payload = {
            "schemaVersion": "1.0",
            "matrixId": context["matrixId"],
            "selectedPairIds": selected_pair_ids,
        }
        return {"choices": [{"message": {"content": json.dumps(payload)}, "finish_reason": "stop"}]}

    plan, repairs, initial_hash, diagnostics = compose_analysis_plan_with_provider(
        _phonon_base_plan(),
        registry=registry,
        decision=SimpleNamespace(selections=[SimpleNamespace(toolId=item) for item in selected]),
        provider=OpenAICompatibleProvider(transport=transport),
        user_config=None,
        repair_budget=1,
    )
    assert isinstance(plan, AnalysisPlanV02)
    assert sorted(item.bindingId for item in plan.dependencyBindings)
    assert repairs == 1
    assert initial_hash and len(initial_hash) == 64
    assert diagnostics[0]["code"] == "DEPENDENCY_PAIR_DOMAIN_MISMATCH"
    assert len(calls) == 2


def test_llm_composer_strict_json_failure_is_not_repaired_or_mocked() -> None:
    registry = load_manifests()
    selected = ["phonon.band", "phonon.band_dos", "phonon.dos"]
    calls = 0

    def transport(**_kwargs: object) -> dict[str, object]:
        nonlocal calls
        calls += 1
        return {"choices": [{"message": {"content": "```json\n{}\n```"}, "finish_reason": "stop"}]}

    from mdi_llm.dependency_planner import DependencyCompositionError

    with pytest.raises(DependencyCompositionError, match="bare JSON"):
        compose_analysis_plan_with_provider(
            _phonon_base_plan(),
            registry=registry,
            decision=SimpleNamespace(selections=[SimpleNamespace(toolId=item) for item in selected]),
            provider=OpenAICompatibleProvider(transport=transport),
            user_config=None,
            repair_budget=1,
        )
    assert calls == 1
