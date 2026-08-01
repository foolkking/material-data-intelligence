from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/phase10m/evidence/phase10m1_workspace_domain_persistence"
MANIFEST = EVIDENCE / "file_manifest.json"
TEXT_SUFFIXES = {".json", ".md", ".txt"}
REQUIRED = {
    "baseline.txt",
    "entry_gate.txt",
    "m0_decision_verification.txt",
    "acceptance_id_mapping.json",
    "contract_schema_manifest.json",
    "migration_upgrade.txt",
    "migration_downgrade.txt",
    "migration_reupgrade.txt",
    "sqlite_repository_evidence.json",
    "postgresql_repository_evidence.json",
    "workspace_create_idempotency.json",
    "workspace_patch_concurrency.json",
    "workspace_panel_cap.json",
    "workspace_revision_cap.json",
    "historical_projection_cases.json",
    "api_create.json",
    "api_get.json",
    "api_patch.json",
    "api_project_list.json",
    "api_job_projection.json",
    "api_panels.json",
    "api_layout_history.json",
    "security_cases.json",
    "performance.json",
    "compatibility.txt",
    "service_backed.txt",
    "browser_regression.txt",
    "network_summary.json",
    "console_summary.json",
    "secret_scan.txt",
    "test_summary.txt",
}
FORBIDDEN_PATTERNS = {
    "private_windows_path": re.compile(rb"[A-Za-z]:\\\\Users\\\\[^\\\r\n]+", re.I),
    "authorization_header": re.compile(rb"authorization\s*:\s*(?:bearer|basic)\s+\S+", re.I),
    "openai_key": re.compile(rb"sk-[A-Za-z0-9_-]{20,}"),
    "aws_access_key": re.compile(rb"AKIA[0-9A-Z]{16}"),
    "pem_private_key": re.compile(rb"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY"),
}


def _normalized(path: Path) -> tuple[bytes, str]:
    raw = path.read_bytes()
    if path.suffix.lower() in TEXT_SUFFIXES:
        text = raw.decode("utf-8")
        return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8"), "LF_TEXT"
    return raw, "RAW_BYTES"


def _entries() -> list[dict[str, object]]:
    files = sorted(path for path in EVIDENCE.rglob("*") if path.is_file() and path != MANIFEST)
    relative = {path.relative_to(EVIDENCE).as_posix() for path in files}
    missing = sorted(REQUIRED - relative)
    if missing:
        raise ValueError(f"Missing required evidence files: {missing}")

    entries: list[dict[str, object]] = []
    for path in files:
        data, mode = _normalized(path)
        for label, pattern in FORBIDDEN_PATTERNS.items():
            if pattern.search(data):
                raise ValueError(f"Forbidden {label} in {path.relative_to(EVIDENCE).as_posix()}")
        entries.append(
            {
                "path": path.relative_to(EVIDENCE).as_posix(),
                "sha256": hashlib.sha256(data).hexdigest(),
                "bytes": len(data),
                "hashMode": mode,
            }
        )
    return entries


def build_manifest() -> dict[str, object]:
    entries = _entries()
    return {
        "schemaVersion": "phase10m1.evidence-manifest.v1",
        "algorithm": "sha256",
        "textNormalization": "CRLF and CR normalized to LF before hashing",
        "binaryNormalization": "none",
        "entryCount": len(entries),
        "entries": entries,
    }


def write_manifest() -> None:
    MANIFEST.write_text(
        json.dumps(build_manifest(), indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def verify_manifest() -> None:
    expected = json.loads(MANIFEST.read_text(encoding="utf-8"))
    actual = build_manifest()
    if expected != actual:
        raise ValueError("Phase 10M-1 evidence manifest mismatch")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.write == args.verify:
        parser.error("choose exactly one of --write or --verify")
    write_manifest() if args.write else verify_manifest()


if __name__ == "__main__":
    main()
