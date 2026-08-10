import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/phase12/evidence/phase12_5_report_recipe_experience"


def load(name: str):
    return json.loads((OUT / name).read_text(encoding="utf-8"))


def test_phase12_5_evidence_is_complete_and_exact():
    subprocess.run([sys.executable, "scripts/generate_phase12_5_report_recipe_evidence.py"], cwd=ROOT, check=True)
    manifest = load("manifest.json")
    assert manifest["phase"] == "12-5"
    assert manifest["missing"] == manifest["extra"] == manifest["hashMismatch"] == 0
    assert len(manifest["entries"]) >= 40
    acceptance = load("acceptance_registry.json")
    assert acceptance["expected"] == acceptance["implemented"] == 8
    assert acceptance["missing"] == acceptance["extra"] == acceptance["duplicate"] == acceptance["conflicting"] == acceptance["shorthand"] == 0


def test_human_recipe_and_finalize_are_non_executable():
    recipe = load("human_recipe_matrix.json")
    raw = load("raw_recipe_matrix.json")
    boundary = load("recipe_nonexecution_matrix.json")
    finalization = load("finalization_matrix.json")
    assert recipe["meaningFirst"] and recipe["stepsVisible"]
    assert raw["exactDeclarationAvailable"] and raw["inertText"] and not raw["executionAction"]
    assert all(value is False for value in boundary.values())
    assert finalization["explicitConfirmation"] and finalization["atomicPair"] and finalization["immutable"]


def test_phase12_5_closes_only_owned_problem_and_preserves_authority():
    closure = load("phase12_5_problem_closure.json")
    deferred = load("deferred_problem_matrix.json")
    science = load("scientific_nonchange_matrix.json")
    assert [item["problemId"] for item in closure["closed"]] == ["UX-005"]
    assert closure["open"] == [] and closure["newP0"] == closure["newP1"] == 0
    assert deferred == {"12-6": ["UX-006", "UX-009"], "12-7": ["UX-010"]}
    assert all(value == 0 for value in science.values())
