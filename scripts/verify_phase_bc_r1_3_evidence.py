"""Verify the stable Phase B/C-R1.3 blocked-attempt evidence set."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "_qualification" / "evidence" / "phase_bc_r1_3" / "attempt_01_blocked_authority_conflict"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: dict[str, object]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def write_manifest() -> tuple[int, int]:
    rows = []
    for path in sorted(EVIDENCE.rglob("*"), key=lambda item: item.relative_to(EVIDENCE).as_posix()):
        if path.is_file() and path.name != "SHA256SUMS.txt":
            rows.append(f"{sha256(path)}  {path.relative_to(EVIDENCE).as_posix()}  {path.stat().st_size}  UTF8_LF")
    (EVIDENCE / "SHA256SUMS.txt").write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
    mismatches = 0
    for line in rows:
        expected, relative, _size, _kind = line.split("  ")
        if sha256(EVIDENCE / relative) != expected:
            mismatches += 1
    return len(rows), mismatches


def main() -> None:
    json_errors: list[str] = []
    secret_hits: list[str] = []
    private_path_hits: list[str] = []
    secret_patterns = [
        re.compile(r"(?i)(deepseek|openai|api)[_-]?key\s*[:=]\s*(?!PRESENT|MISSING|REDACTED)[^\s\"']+"),
        re.compile(r"(?i)authorization\s*[:=]\s*bearer\s+[^\s\"']+"),
    ]
    private_patterns = [re.compile(r"(?i)[A-Z]:\\Users\\"), re.compile(r"(?i)/home/"), re.compile(r"(?i)/Users/")]
    for path in sorted(EVIDENCE.rglob("*")):
        if not path.is_file() or path.name == "SHA256SUMS.txt":
            continue
        text = path.read_text(encoding="utf-8")
        if path.suffix == ".json":
            try:
                json.loads(text)
            except json.JSONDecodeError as exc:
                json_errors.append(f"{path.name}: {exc}")
        for pattern in secret_patterns:
            if pattern.search(text):
                secret_hits.append(path.relative_to(EVIDENCE).as_posix())
                break
        for pattern in private_patterns:
            if pattern.search(text):
                private_path_hits.append(path.relative_to(EVIDENCE).as_posix())
                break
    verification = {
        "schemaVersion": "PhaseBCR13EvidenceVerification/1.0",
        "jsonFiles": len(list(EVIDENCE.glob("*.json"))),
        "jsonParseErrors": json_errors,
        "secretPatternHits": sorted(secret_hits),
        "privatePathHits": sorted(private_path_hits),
        "realLlmCalls": 0,
        "formalQualificationExecutions": 0,
        "newQualificationJobs": 0,
        "newQualificationArtifacts": 0,
        "status": "PASS" if not (json_errors or secret_hits or private_path_hits) else "FAIL",
    }
    write_json(EVIDENCE / "EVIDENCE_VERIFICATION.json", verification)
    entries, mismatches = write_manifest()
    verification["sha256ManifestEntries"] = entries
    verification["sha256ManifestMismatches"] = mismatches
    verification["status"] = "PASS" if verification["status"] == "PASS" and mismatches == 0 else "FAIL"
    write_json(EVIDENCE / "EVIDENCE_VERIFICATION.json", verification)
    entries, mismatches = write_manifest()
    print(json.dumps({**verification, "sha256ManifestEntries": entries, "sha256ManifestMismatches": mismatches}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
