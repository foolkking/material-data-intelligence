from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError

from mdi_api.report_composition import ReportCompositionService
from mdi_schemas import (
    REPORT_COMPOSITION_MAX_REQUEST_BYTES,
    RecipeReplayManifest,
    ReportCompositionRequest,
    ReportCompositionSnapshot,
    ReportExportManifest,
    canonical_report_composition_json,
    report_composition_semantic_hash,
    strict_report_composition_json_loads,
)
from tests.test_phase10m5_report_composition import _request, _seed


SCHEMA_DIR = Path("packages/schemas/json")


def _artifacts():
    repos, workspace_id, _ = _seed()
    workspace = repos.workspaces.get(workspace_id)
    request = _request(workspace_id, workspace["revision"])
    service = ReportCompositionService(repos)
    preview = service.preview(request)
    finalized = service.finalize(request, idempotency_key="contract-fixture", created_by="user_local")
    exported = service.export(workspace_id, finalized["reportId"], "json")
    return request, preview.report, preview.recipe, ReportExportManifest.model_validate(exported["manifest"])


def test_checked_in_json_schemas_validate_python_contract_fixtures() -> None:
    request, report, recipe, export = _artifacts()
    fixtures = {
        "report-composition-request-v1.schema.json": request.model_dump(mode="json"),
        "report-composition-snapshot-v1.schema.json": report.model_dump(mode="json"),
        "recipe-replay-manifest-v1.schema.json": recipe.model_dump(mode="json"),
        "report-export-manifest-v1.schema.json": export.model_dump(mode="json"),
    }
    for filename, fixture in fixtures.items():
        schema = json.loads((SCHEMA_DIR / filename).read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(fixture)


def test_contracts_reject_unknown_fields_and_invalid_hashes() -> None:
    request, report, recipe, export = _artifacts()
    for model, value in (
        (ReportCompositionRequest, request.model_dump(mode="json")),
        (ReportCompositionSnapshot, report.model_dump(mode="json")),
        (RecipeReplayManifest, recipe.model_dump(mode="json")),
        (ReportExportManifest, export.model_dump(mode="json")),
    ):
        with pytest.raises(ValidationError):
            model.model_validate({**value, "unknownField": "rejected"})
    with pytest.raises(ValidationError, match="reportHash"):
        ReportCompositionSnapshot.model_validate({**report.model_dump(mode="json"), "reportHash": "b" * 64})
    with pytest.raises(ValidationError, match="recipeHash"):
        RecipeReplayManifest.model_validate({**recipe.model_dump(mode="json"), "recipeHash": "b" * 64})


def test_duplicate_keys_prototype_nonfinite_depth_and_byte_caps_are_rejected() -> None:
    with pytest.raises(ValueError, match="Duplicate JSON key"):
        strict_report_composition_json_loads('{"schemaVersion":"1.0","schemaVersion":"1.0"}')
    with pytest.raises(ValueError, match="Forbidden JSON key"):
        strict_report_composition_json_loads('{"__proto__":{}}')
    with pytest.raises(ValueError, match="Non-finite"):
        strict_report_composition_json_loads('{"value":NaN}')
    deep: object = "leaf"
    for _ in range(15):
        deep = {"nested": deep}
    with pytest.raises(ValueError, match="depth"):
        strict_report_composition_json_loads(json.dumps(deep))
    oversized = '{"value":"' + ("x" * REPORT_COMPOSITION_MAX_REQUEST_BYTES) + '"}'
    with pytest.raises(ValueError, match="byte cap"):
        strict_report_composition_json_loads(oversized)


def test_semantic_hash_is_canonical_and_runtime_timestamp_is_explicitly_excluded() -> None:
    left = {"workspaceId": "workspace_1", "selected": ["a", "b"], "title": "Report"}
    right = {"title": "Report", "selected": ["a", "b"], "workspaceId": "workspace_1"}
    assert canonical_report_composition_json(left) == canonical_report_composition_json(right)
    assert report_composition_semantic_hash(left) == report_composition_semantic_hash(right)

    _, report, recipe, export = _artifacts()
    report_semantic = report.model_dump(mode="json", exclude={"reportId", "reportHash", "recipeId", "createdAt"})
    recipe_semantic = recipe.model_dump(mode="json", exclude={"recipeId", "recipeHash", "createdAt"})
    export_semantic = export.model_dump(mode="json", exclude={"exportId", "exportHash", "generatedAt"})
    assert report_composition_semantic_hash(report_semantic) == report.reportHash
    assert report_composition_semantic_hash(recipe_semantic) == recipe.recipeHash
    assert report_composition_semantic_hash(export_semantic) == export.exportHash


def test_plan_01_cannot_acquire_dependencies_and_plan_02_requires_exact_graph_hash() -> None:
    _, _, recipe, _ = _artifacts()
    plan_01 = recipe.model_dump(mode="json")
    plan_01["dependencyBindings"] = [{"bindingId": "binding_1"}]
    semantic = {key: value for key, value in plan_01.items() if key not in {"recipeId", "recipeHash", "createdAt"}}
    plan_01["recipeHash"] = report_composition_semantic_hash(semantic)
    with pytest.raises(ValidationError, match="0.1"):
        RecipeReplayManifest.model_validate(plan_01)

    plan_02 = deepcopy(recipe.model_dump(mode="json"))
    plan_02.update({"planSchemaVersion": "0.2", "dependencyModel": "TYPED_ARTIFACT_BINDINGS", "graphHash": None})
    semantic = {key: value for key, value in plan_02.items() if key not in {"recipeId", "recipeHash", "createdAt"}}
    plan_02["recipeHash"] = report_composition_semantic_hash(semantic)
    with pytest.raises(ValidationError, match="graph hash"):
        RecipeReplayManifest.model_validate(plan_02)

    plan_02["graphHash"] = "c" * 64
    semantic = {key: value for key, value in plan_02.items() if key not in {"recipeId", "recipeHash", "createdAt"}}
    plan_02["recipeHash"] = report_composition_semantic_hash(semantic)
    assert RecipeReplayManifest.model_validate(plan_02).planSchemaVersion == "0.2"


def test_frozen_counts_and_duplicate_selection_are_rejected() -> None:
    request, _, _, _ = _artifacts()
    payload = request.model_dump(mode="json")
    payload["selectedArtifactIds"] = ["artifact_m5", "artifact_m5"]
    payload["itemOrder"] = ["artifact_m5"]
    with pytest.raises(ValidationError, match="Duplicate composition source"):
        ReportCompositionRequest.model_validate(payload)
    payload = request.model_dump(mode="json")
    payload["selectedArtifactIds"] = [f"artifact_{index}" for index in range(65)]
    payload["itemOrder"] = list(payload["selectedArtifactIds"])
    with pytest.raises(ValidationError):
        ReportCompositionRequest.model_validate(payload)


def test_typescript_contract_declares_all_four_versioned_m5_models_without_any_escape() -> None:
    contract = Path("apps/web/app/lib/report-composition-api.ts").read_text(encoding="utf-8")
    for name in (
        "ReportCompositionRequest",
        "ReportCompositionSnapshot",
        "RecipeReplayManifest",
        "ReportExportManifest",
    ):
        assert f"export type {name}" in contract
    assert 'schemaVersion: "1.0"' in contract
    assert ": any" not in contract
    assert "Record<string, unknown>" in contract
