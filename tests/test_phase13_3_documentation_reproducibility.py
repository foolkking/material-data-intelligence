from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from scripts.phase13_current_demo_contracts import CURRENT_DEMO_SPECS


ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "docs/phase13/release"
REPRO = ROOT / "docs/phase13/reproducibility"
OUT = ROOT / "docs/phase13/evidence/phase13_3_documentation_reproducibility"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_current_authorities_and_support_are_exact() -> None:
    authority = load(OUT / "current_hash_authority.json")
    assert authority["factModelHash"] == "92d8295c7d78467d8ce021dc8033a58326219372a5d8fa87c93377ed1275953a"
    assert authority["scopeBaselineHash"] == "bb885aa4e020349011c39164a883107c8ffed3d5d43604594a76f7d5a18705ba"
    support = load(OUT / "current_input_support_matrix.json")
    assert support["typedPhononBandImport"] == support["typedPhononDosImport"] == "SUPPORTED_WITH_LIMITS"
    assert support["genericPhononYamlJson"] == "MAPPING_ONLY" and support["otherPromotions"] == 0


def test_seven_demo_contracts_match_current_registry_and_fixtures() -> None:
    for index, spec in enumerate(CURRENT_DEMO_SPECS, 1):
        contract = load(REPRO / f"demo{index}.json")
        assert contract["canonicalPrompt"] == spec["prompt"]
        assert contract["promptSha256"] == hashlib.sha256(spec["prompt"].encode()).hexdigest()
        assert contract["expectedCapabilityCoverage"] == sorted(spec["expectedTools"])
        assert len(contract["fixtures"]) == len(spec["fixtures"])
        for row in contract["fixtures"]:
            fixture = ROOT / row["path"]
            assert fixture.is_file()
            payload = fixture.read_bytes()
            if row["hashMode"] == "UTF8_LF":
                payload = payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
            else:
                assert row["hashMode"] == "RAW_BYTES"
            assert row["sha256"] == hashlib.sha256(payload).hexdigest()
            assert row["bytes"] == len(payload)


def test_repro_manifest_is_semantically_deterministic() -> None:
    manifest = load(REPRO / "manifest.json")
    semantic = {key: value for key, value in manifest.items() if key not in {"semanticHash", "generatedAt"}}
    payload = json.dumps(semantic, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    assert manifest["semanticHash"] == hashlib.sha256(payload.encode()).hexdigest()
    evidence = load(OUT / "repro_manifest_determinism.json")
    assert evidence["run1"] == evidence["run2"] == manifest["semanticHash"]
    parity = load(OUT / "linux_windows_repro_manifest_parity.json")
    assert parity["linux"] == parity["windows"] == manifest["semanticHash"]


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


def test_evidence_manifest_matches_raw_bytes() -> None:
    manifest = load(OUT / "manifest.json")
    assert manifest["missingFiles"] == manifest["hashMismatches"] == 0
    for row in manifest["entries"]:
        data = (OUT / row["path"]).read_bytes()
        assert len(data) == row["bytes"]
        assert hashlib.sha256(data).hexdigest() == row["sha256"]


def test_attempt6_is_authority_and_phase13_4_is_not_queued() -> None:
    attempt6 = load(OUT / "attempt6_authority_snapshot.json")
    assert attempt6["status"] == "PASS" and attempt6["demos"] == "7/7" and attempt6["p13x2"] == "8/8"
    tasks = (ROOT / "TASKS.md").read_text(encoding="utf-8")
    assert "Task: Phase 13-3 Documentation + Reproducibility Package" not in tasks
    if (
        "Task: Phase 13-4 Targeted Final Product Polish" in tasks
        or "Task: Phase 13-5 Final Regression + Release Acceptance" in tasks
    ):
        assert tasks.count("---TASK---") == 1
        assert "状态：处理中" in tasks
        assert "Task: Phase 13-6" not in tasks
    else:
        assert "---TASK---" not in tasks
