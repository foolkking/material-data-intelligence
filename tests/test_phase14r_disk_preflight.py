from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "phase14r_disk_preflight.ps1"
PYTHON_SCRIPT = ROOT / "scripts" / "phase14r_disk_preflight.py"
START_SCRIPTS = (
    ROOT / "scripts" / "phase14r_start_stack.ps1",
    ROOT / "scripts" / "phase14r_start_api.ps1",
    ROOT / "scripts" / "phase14r_start_workers.ps1",
)


def _run(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(SCRIPT),
            "-CheckPath",
            str(ROOT),
            *arguments,
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_disk_preflight_is_read_only_and_reports_volume_capacity() -> None:
    before = {path.name for path in ROOT.iterdir()}

    completed = _run("-MinimumFreeBytes", "1", "-WarningFreeBytes", "1")

    after = {path.name for path in ROOT.iterdir()}
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["schemaVersion"] == "phase14r-disk-preflight/1.0"
    assert payload["status"] == "ok"
    assert payload["code"] == "MDI_DISK_PREFLIGHT_OK"
    assert payload["readOnly"] is True
    assert payload["volumes"][0]["availableFreeBytes"] > 0
    assert before == after


def test_disk_preflight_fails_with_typed_critical_capacity_error() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            str(PYTHON_SCRIPT),
            "--check-path",
            str(ROOT),
            "--minimum-free-bytes",
            str(2**63 - 1),
            "--warning-free-bytes",
            str(2**63 - 1),
            "--fallback-path",
            str(ROOT),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 78
    payload = json.loads(completed.stdout)
    assert payload["status"] == "error"
    assert payload["code"] == "MDI_DISK_SPACE_CRITICAL"
    assert payload["readOnly"] is True
    assert payload["volumes"][0]["state"] == "critical"
    assert payload["configuredFallback"]["configured"] is True
    assert payload["configuredFallback"]["path"] == str(ROOT)


def test_disk_preflight_rejects_invalid_threshold_contract() -> None:
    completed = _run(
        "-MinimumFreeBytes", "1024", "-WarningFreeBytes", "512"
    )

    assert completed.returncode == 64
    payload = json.loads(completed.stdout)
    assert payload == {
        "schemaVersion": "phase14r-disk-preflight/1.0",
        "status": "error",
        "code": "MDI_DISK_PREFLIGHT_CONFIGURATION_INVALID",
        "readOnly": True,
        "minimumFreeBytes": 0,
        "warningFreeBytes": 0,
        "volumes": [],
        "configuredFallback": None,
    }


def test_same_stack_launchers_fail_fast_before_starting_processes() -> None:
    for script in START_SCRIPTS:
        source = script.read_text(encoding="utf-8")
        preflight_index = source.index("phase14r_disk_preflight.ps1")
        assert "MDI_DISK_PREFLIGHT_FAILED" in source
        if script.name == "phase14r_start_stack.ps1":
            invocation_index = source.index(
                "$diskPreflight = Assert-DiskPreflight"
            )
            launch_gate_index = source.index("if (-not $CheckOnly)")
            assert preflight_index < invocation_index < launch_gate_index
        else:
            first_start_index = source.index("Start-Process")
            assert preflight_index < first_start_index


def test_build_test_browser_and_evidence_entrypoints_use_the_preflight() -> None:
    package = json.loads((ROOT / "apps" / "web" / "package.json").read_text())
    for name in (
        "build",
        "test",
        "typecheck",
        "test:phase10-browser-evidence",
        "test:product-navigation-spa",
    ):
        assert "preflight:disk" in package["scripts"][name]

    conftest = (ROOT / "tests" / "conftest.py").read_text(encoding="utf-8")
    assert "phase14r_disk_preflight.py" in conftest
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(
        encoding="utf-8"
    )
    assert workflow.count("Disk space preflight") >= 2
    assert "python scripts/phase14r_disk_preflight.py --check-path ." in workflow


def test_python_preflight_accepts_environment_fallback_without_writing(
    tmp_path: Path,
) -> None:
    before = set(tmp_path.iterdir())
    environment = {
        **os.environ,
        "MDI_DISK_FALLBACK_PATH": str(tmp_path),
    }
    completed = subprocess.run(
        [
            sys.executable,
            str(PYTHON_SCRIPT),
            "--check-path",
            str(ROOT),
            "--minimum-free-bytes",
            "1",
            "--warning-free-bytes",
            "1",
        ],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert payload["configuredFallback"]["path"] == str(tmp_path)
    assert payload["readOnly"] is True
    assert set(tmp_path.iterdir()) == before
