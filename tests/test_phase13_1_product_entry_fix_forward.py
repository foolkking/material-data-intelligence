from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from mdi_material_parsers import map_normalized_phonon_resource, parse_file
from mdi_schemas import (
    CURRENT_DATAPROFILE_CONTRACT_VERSION,
    SUPPORTED_DATAPROFILE_CONTRACT_VERSIONS,
    is_supported_data_profile_contract_version,
)
from scripts.generate_phase13_1_product_entry_fix_forward import (
    OLD_FACT_HASH,
    OLD_SCOPE_HASH,
    OUT,
    _alternate_prompt_result,
    run_entry_slices,
    run_negative_slices,
)


ROOT = Path(__file__).resolve().parents[1]


def data(name: str):
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def stable_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


@pytest.fixture(scope="module")
def entry_records() -> list[dict[str, object]]:
    return run_entry_slices()


def test_profile_compatibility_is_explicit_and_current(entry_records: list[dict[str, object]]) -> None:
    assert CURRENT_DATAPROFILE_CONTRACT_VERSION == "2.4"
    assert SUPPORTED_DATAPROFILE_CONTRACT_VERSIONS == {"2.0", "2.1", "2.2", "2.3", "2.4"}
    assert all(is_supported_data_profile_contract_version(version) for version in SUPPORTED_DATAPROFILE_CONTRACT_VERSIONS)
    assert not is_supported_data_profile_contract_version("2.5")
    by_id = {item["demoId"]: item for item in entry_records}
    assert by_id["P13-DEMO-04"]["profileContractVersion"] == "2.3"
    assert by_id["P13-DEMO-07"]["profileContractVersion"] == "2.4"
    assert by_id["P13-DEMO-04"]["planningOutcome"] == "PLAN_READY"
    assert by_id["P13-DEMO-07"]["planningOutcome"] == "PLAN_READY"
    web = (ROOT / "apps/web/app/lib/planner-api.ts").read_text(encoding="utf-8")
    assert '["2.0", "2.1", "2.2", "2.3", "2.4"]' in web
    assert '"2.5"' not in web


def test_xrd_uses_existing_strict_user_input_without_support_promotion() -> None:
    historical = parse_file(
        ROOT / "docs/phase10n/evidence/phase10n3_experimental_xrd_comparison_peak_matching/perfect_match.json",
        dataset_id="historical_xrd",
        file_id="historical",
    )
    corrected = parse_file(
        ROOT / "tests/fixtures/experimental_xrd/phase13_demo3_xrd.json",
        dataset_id="corrected_xrd",
        file_id="corrected",
    )
    assert historical.parse_status == "unsupported"
    assert corrected.parse_status == "success"
    decision = data("xrd_input_authority_decision.json")
    assert decision["selectedBranch"] == "B1"
    assert decision["inputSupportPromotion"] == 0
    support = data("xrd_input_support_matrix_reconciliation.json")
    assert support["strictContract"] == "phase10n3.experimental_xrd_resource.v1"
    assert support["genericJsonPromoted"] is False

    phonon_path = ROOT / "docs/phase10h/fixtures/phonon_contract/stable_band.json"
    assert parse_file(phonon_path, dataset_id="generic_phonon", file_id="generic").parse_status == "unsupported"
    assert map_normalized_phonon_resource(
        phonon_path,
        dataset_id="mapped_phonon",
        file_id="mapped",
    ).parse_status == "success"


def test_all_seven_entry_slices_select_the_exact_capability_and_validate(
    entry_records: list[dict[str, object]],
) -> None:
    assert len(entry_records) == 7
    assert all(item["ready"] is True for item in entry_records)
    assert all(item["intentOutcome"] == "READY" for item in entry_records)
    assert all(item["planningOutcome"] == "PLAN_READY" for item in entry_records)
    assert all(item["planValidated"] is True for item in entry_records)
    assert all(sorted(item["selectedTools"]) == sorted(item["expectedTools"]) for item in entry_records)
    aggregate = data("entry_slice_aggregate.json")
    assert aggregate["expected"] == aggregate["ready"] == aggregate["planValidated"] == 7
    assert aggregate["blocked"] == aggregate["wrongCapability"] == aggregate["fullE2eExecuted"] == 0
    assert all(value == 0 for value in aggregate["sideEffects"].values())


def test_phonon_and_volumetric_authority_decisions_are_bounded() -> None:
    phonon = data("rf003_before_after.json")
    assert phonon["after"]["canonical"]["planningOutcome"] == "PLAN_READY"
    assert phonon["after"]["alternate"]["intentOutcome"] != "UNSUPPORTED"
    assert set(phonon["after"]["canonical"]["selectedTools"]) == {
        "phonon.band",
        "phonon.band_dos",
        "phonon.dos",
        "structure.brillouin_zone",
    }
    volumetric = data("volumetric_prompt_authority_decision.json")
    assert volumetric["selectedBranch"] == "B"
    assert volumetric["scopeBroadened"] is False
    assert data("rf004_before_after.json")["after"]["selectedTools"] == ["structure.volumetric_data"]
    generated = _alternate_prompt_result("P13-DEMO-05", "Run DFT to generate new phonons for this structure.")
    unrelated = _alternate_prompt_result("P13-DEMO-07", "Review the husband labels in this dataset.")
    advanced_volume = _alternate_prompt_result("P13-DEMO-06", "Perform Bader topology on this volume.")
    assert generated["intentOutcome"] == "UNSUPPORTED"
    assert unrelated["intentOutcome"] == "UNSUPPORTED"
    assert advanced_volume["intentOutcome"] == "UNSUPPORTED"


def test_negative_entry_slices_retain_current_boundaries() -> None:
    records = run_negative_slices()
    assert records["futureScope"]["intentOutcome"] == "UNSUPPORTED"
    assert records["unsupportedInput"]["parseStatus"] == "unsupported"
    assert records["clarification"]["parentOutcome"] == "NEEDS_CLARIFICATION"
    assert records["clarification"]["firstRoundOutcome"] == "READY"
    assert records["clarification"]["secondRoundCode"] == "CLARIFICATION_NOT_ALLOWED"
    assert records["clarification"]["staleProfileHashCode"] == "STALE_PROFILE"
    assert "RESOURCE_NOT_FOUND" in records["invalidCrossResourceBinding"]["codes"]
    assert not any(item["planCreated"] for item in records.values())


def test_no_fixture_prompt_or_tool_injection_shortcut_exists() -> None:
    production_paths = [
        ROOT / "apps/api/mdi_api/routers/planner.py",
        ROOT / "packages/material-parsers/mdi_material_parsers/mapped_resources.py",
        ROOT / "packages/material-parsers/mdi_material_parsers/semantic_profile.py",
        ROOT / "services/llm/mdi_llm/analysis_intent.py",
        ROOT / "services/llm/mdi_llm/capability_planner.py",
    ]
    source = "\n".join(path.read_text(encoding="utf-8") for path in production_paths)
    assert "P13-DEMO" not in source
    assert "phase13_demo3" not in source
    assert "bc36695e447f50c7c0ad51a3b1ab59e4cbfcf68fa9589c4e62c0319f7eadbc28" not in source
    assert "version.startswith(\"2\")" not in source
    injection = data("no_injection_audit.json")
    assert all(injection[key] == 0 for key in (
        "handcraftedIntent",
        "handcraftedEligibility",
        "handcraftedPlan",
        "handcraftedToolSelection",
        "fixtureSpecificProductionRouting",
        "exactPromptProductionRouting",
    ))


def test_historical_findings_are_retained_with_append_only_closures() -> None:
    historical = json.loads(
        (ROOT / "docs/phase13/evidence/phase13_2_seven_real_user_e2e/release_finding_registry.json").read_text(encoding="utf-8")
    )
    assert historical["releaseCriticalIntegrationDefects"] == 3
    assert all(item["fixed"] is False for item in historical["findings"])
    closure = data("finding_closure_registry.json")
    assert [item["findingId"] for item in closure["findings"]] == [f"P13-RF-{index:03d}" for index in range(1, 5)]
    assert all(item["status"] == "CLOSED" and item["fixed"] is True for item in closure["findings"])
    gaps = data("release_gap_reconciliation.json")
    assert gaps["before"] == {"releaseCriticalIntegrationGaps": 3, "documentationDefects": 1}
    assert all(value == 0 for value in gaps["after"].values())


def test_fact_and_scope_hash_impacts_are_deterministic() -> None:
    fact = data("fact_model_hash_impact.json")
    scope = data("scope_baseline_hash_impact.json")
    baseline = data("initial_release_scope_baseline.json")
    assert fact["impact"] == "NO" and fact["old"] == fact["current"] == OLD_FACT_HASH
    assert scope["impact"] == "YES" and scope["old"] == OLD_SCOPE_HASH
    assert scope["current"] == baseline["semanticHash"] != OLD_SCOPE_HASH
    payload = {key: value for key, value in baseline.items() if key != "semanticHash"}
    regenerated = hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    assert regenerated == baseline["semanticHash"]
    determinism = data("baseline_determinism.json")
    assert determinism["run1"] == determinism["run2"] == regenerated
    assert determinism["status"] == "PASS"


def test_manifest_is_complete_and_cross_platform_stable() -> None:
    manifest = data("manifest.json")
    assert manifest["missing"] == manifest["hashMismatch"] == manifest["unclassified"] == 0
    assert manifest["expectedFiles"] == len(manifest["entries"])
    assert manifest["entrySliceReady"] == 7 and manifest["fullE2eExecuted"] == 0
    for item in manifest["entries"]:
        content = stable_bytes(OUT / item["path"])
        assert len(content) == item["bytes"]
        assert hashlib.sha256(content).hexdigest() == item["sha256"]


def test_current_docs_and_ci_use_the_fix_forward_authority() -> None:
    generator = (ROOT / "scripts/generate_phase13_1_product_entry_fix_forward.py").read_text(encoding="utf-8")
    for name in (
        "phase13_initial_release_scope.md",
        "phase13_initial_release_fact_model.md",
        "phase13_release_critical_gap_registry.md",
        "phase13_seven_canonical_e2e_demo_contract.md",
        "phase13_2_rerun_handoff.md",
    ):
        assert f'"{name}"' in generator
    assert "current superseding Scope Baseline is `{scope_hash}`" in generator
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "generate_phase13_1_product_entry_fix_forward.py" in workflow
    assert "verify_phase13_1_fix_forward_hash.py" in workflow
    assert "generate_phase13_2_blocker_evidence.py" not in workflow
    assert "tests/test_phase13_2_blocker_evidence.py" in workflow


def test_phase13_2_remains_failed_unexecuted_and_reviewer_gated() -> None:
    handoff = data("phase13_2_rerun_handoff.json")
    assert handoff["historicalFailureSha"] == "456b698948d286d4e60dc8d6807748a97df9fb96"
    assert handoff["entrySlice"] == "7/7 PASS"
    assert handoff["p13x2Acceptance"] == "0/8"
    assert handoff["failedTaskBlockRetained"] is True
    assert handoff["rerunExecutableTaskCreated"] is False
