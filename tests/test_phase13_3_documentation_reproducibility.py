from __future__ import annotations

import json
import re
from pathlib import Path

from scripts.phase13_current_demo_contracts import CURRENT_DEMO_SPECS
from tests.evidence_inventory_contract import assert_readable_evidence_inventory
from tests.task_queue_contract import assert_current_task_queue


ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "docs/phase13/release"
REPRO = ROOT / "docs/phase13/reproducibility"
OUT = ROOT / "docs/phase13/evidence/phase13_3_documentation_reproducibility"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_current_authorities_and_support_are_declared() -> None:
    authority = load(OUT / "current_hash_authority.json")
    assert authority["status"] == "PASS"
    support = load(OUT / "current_input_support_matrix.json")
    assert support["typedPhononBandImport"] == support["typedPhononDosImport"] == "SUPPORTED_WITH_LIMITS"
    assert support["genericPhononYamlJson"] == "MAPPING_ONLY" and support["otherPromotions"] == 0


def test_seven_demo_contracts_match_current_registry_and_fixtures() -> None:
    for index, spec in enumerate(CURRENT_DEMO_SPECS, 1):
        contract = load(REPRO / f"demo{index}.json")
        assert contract["canonicalPrompt"] == spec["prompt"]
        assert contract["expectedCapabilityCoverage"] == sorted(spec["expectedTools"])
        assert len(contract["fixtures"]) == len(spec["fixtures"])
        for row in contract["fixtures"]:
            fixture = ROOT / row["path"]
            assert fixture.is_file() and fixture.stat().st_size > 0
            assert row["hashMode"] in {"UTF8_LF", "RAW_BYTES"}


def test_repro_manifest_is_semantically_deterministic() -> None:
    manifest = load(REPRO / "manifest.json")
    assert manifest["schemaVersion"] == "Phase13InitialReleaseReproducibilityManifest/1.0"
    assert len(manifest["demos"]) == 7
    evidence = load(OUT / "repro_manifest_determinism.json")
    assert evidence["status"] == "PASS"
    parity = load(OUT / "linux_windows_repro_manifest_parity.json")
    assert parity["status"] == "PASS"


def test_release_docs_have_no_broken_relative_markdown_links() -> None:
    files = list(RELEASE.glob("*.md")) + list(REPRO.glob("*.md")) + [ROOT / "README.md", ROOT / "docs/index.md"]
    broken = []
    for source in files:
        text = source.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", text):
            if target.startswith(("http://", "https://", "#")):
                continue
            relative = target.split("#", 1)[0]
            if relative and not (source.parent / relative).resolve().exists():
                broken.append((source, target))
    assert not broken


def test_claims_limitations_security_and_api_docs_are_bounded() -> None:
    claims = load(OUT / "release_claim_matrix.json")
    limitations = load(OUT / "known_limitations.json")
    security = load(OUT / "security_documentation_audit.json")
    api = load(OUT / "api_documentation_parity.json")
    assert claims["unsupportedPublicClaims"] == 0
    assert all({"claim", "authority", "evidence", "allowedWording", "forbiddenWording", "limitation"} <= set(row) for row in claims["claims"])
    assert limitations["count"] >= 8 and limitations["withoutDisclosure"] == 0
    assert all({"category", "releaseImpact", "userFacingWording", "evidenceSource", "futureOwnerOrRetained"} <= set(row) for row in limitations["limitations"])
    assert security["status"] == api["status"] == "PASS"
    assert "/datasets/upload" in api["documentedCanonicalRoutes"]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in RELEASE.glob("*.md"))
    assert "Recipe = exact declarative replay manifest" not in combined or "non-executable" in combined
    assert "generic phonon YAML/JSON" in combined and "MAPPING_ONLY" in combined


def test_evidence_manifest_inventory_is_complete_and_readable() -> None:
    manifest = load(OUT / "manifest.json")
    paths = assert_readable_evidence_inventory(OUT, manifest)
    assert {"release_claim_matrix.json", "known_limitations.json", "api_documentation_parity.json"}.issubset(paths)


def test_attempt6_is_authority_and_phase13_4_is_not_queued() -> None:
    attempt6 = load(OUT / "attempt6_authority_snapshot.json")
    assert attempt6["status"] == "PASS" and attempt6["demos"] == "7/7" and attempt6["p13x2"] == "8/8"
    tasks = (ROOT / "TASKS.md").read_text(encoding="utf-8")
    assert "Task: Phase 13-3 Documentation + Reproducibility Package\nStatus: processing" not in tasks
    assert_current_task_queue(ROOT)
