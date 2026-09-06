from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any
import xml.etree.ElementTree as ET

try:
    from scripts.pytest_junit_summary import parse_pytest_junit
    from scripts.phase14r_runtime_environment import build_same_stack_environment
except ModuleNotFoundError:
    from pytest_junit_summary import parse_pytest_junit
    from phase14r_runtime_environment import build_same_stack_environment


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "config" / "mandatory-service-qualification.json"
SCHEMA_VERSION = "mdi.mandatory-service-qualification/1.0"
REQUIRED_SERVICES = ("postgresql", "redis", "minio")


def _write_console(text: str) -> None:
    """Forward subprocess output without crashing on a legacy Windows code page."""
    try:
        sys.stdout.write(text)
    except UnicodeEncodeError:
        stream = getattr(sys.stdout, "buffer", None)
        if stream is not None:
            stream.write(text.encode(sys.stdout.encoding or "utf-8", errors="replace"))
            stream.flush()
        else:
            sys.stdout.write(text.encode("utf-8", errors="replace").decode("utf-8"))


def load_manifest(path: Path = DEFAULT_MANIFEST) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schemaVersion") != SCHEMA_VERSION:
        raise ValueError("Unsupported mandatory-service manifest schema.")
    if tuple(payload.get("services", ())) != REQUIRED_SERVICES:
        raise ValueError("Mandatory services must be PostgreSQL, Redis, and MinIO.")
    pytest_config = payload.get("pytest")
    if not isinstance(pytest_config, dict):
        raise ValueError("Manifest pytest configuration is required.")
    paths = pytest_config.get("paths")
    required_tests = pytest_config.get("requiredTests")
    if not isinstance(paths, list) or not paths or len(paths) != len(set(paths)):
        raise ValueError("Manifest pytest paths must be a non-empty unique list.")
    if (
        not isinstance(required_tests, list)
        or not required_tests
        or len(required_tests) != len(set(required_tests))
    ):
        raise ValueError("Manifest required tests must be a non-empty unique list.")
    missing_paths = [item for item in paths if not (ROOT / item).is_file()]
    if missing_paths:
        raise ValueError(f"Manifest references missing tests: {missing_paths}")
    if not isinstance(pytest_config.get("minimumPassed"), int):
        raise ValueError("Manifest minimumPassed must be an integer.")
    return payload


def pytest_arguments(
    manifest: dict[str, Any],
    *,
    junit: Path,
) -> list[str]:
    config = manifest["pytest"]
    return [
        *config["paths"],
        "-vv",
        "-m",
        config["marker"],
        "--tb=long",
        "--color=yes",
        f"--junitxml={junit}",
    ]


def _testcase_names(report: Path) -> set[str]:
    root = ET.parse(report).getroot()
    return {
        testcase.attrib["name"]
        for testcase in root.iter()
        if testcase.tag.rsplit("}", 1)[-1] == "testcase"
        and testcase.attrib.get("name")
    }


def validate_report(
    manifest: dict[str, Any],
    report: Path,
) -> tuple[bool, list[str]]:
    config = manifest["pytest"]
    summary = parse_pytest_junit(report)
    failures: list[str] = []
    if config["requireZeroSkips"] and summary.skipped:
        failures.append(f"{summary.skipped} mandatory service test(s) skipped")
    if config["requireZeroFailures"] and (summary.failed or summary.errors):
        failures.append(
            f"{summary.failed} failed and {summary.errors} errored mandatory service test(s)"
        )
    if summary.passed < config["minimumPassed"]:
        failures.append(
            f"only {summary.passed}/{config['minimumPassed']} minimum tests passed"
        )
    observed = _testcase_names(report)
    missing = sorted(set(config["requiredTests"]) - observed)
    if missing:
        failures.append(f"required tests absent from JUnit report: {', '.join(missing)}")
    return not failures, failures


def run_qualification(
    manifest: dict[str, Any],
    *,
    junit: Path,
    log: Path,
    exit_file: Path | None,
) -> int:
    environment = os.environ.copy()
    canonical = build_same_stack_environment(environ=environment)
    # Qualification must run against one coherent topology.  Inherited shell
    # aliases can describe an older SQLite/local runtime and would otherwise
    # make the same-stack validator reject the campaign or mix authorities.
    environment.update(canonical)
    # Individual integration tests intentionally spawn workers with temporary
    # queue names.  Keep the real PostgreSQL/Redis/MinIO backends, but do not
    # impose the production same-stack queue-manifest guard on those fixtures.
    environment["MDI_RUNTIME_PROFILE"] = "local"
    environment.update(manifest.get("enableEnvironment", {}))
    command = [
        sys.executable,
        "-m",
        "pytest",
        *pytest_arguments(manifest, junit=junit),
    ]
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("w", encoding="utf-8", newline="\n") as stream:
        process = subprocess.Popen(
            command,
            cwd=ROOT,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert process.stdout is not None
        for line in process.stdout:
            _write_console(line)
            stream.write(line)
        return_code = process.wait()
    if exit_file is not None:
        exit_file.write_text(f"{return_code}\n", encoding="utf-8")
    return return_code


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run or validate the checked-in mandatory service qualification."
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--junit", type=Path, default=Path("integration.junit.xml"))
    run_parser.add_argument("--log", type=Path, default=Path("integration.log"))
    run_parser.add_argument("--exit-file", type=Path)
    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument(
        "--junit", type=Path, default=Path("integration.junit.xml")
    )
    subparsers.add_parser("show")
    args = parser.parse_args()

    try:
        manifest = load_manifest(args.manifest.resolve())
        if args.command == "run":
            return run_qualification(
                manifest,
                junit=args.junit.resolve(),
                log=args.log.resolve(),
                exit_file=(
                    args.exit_file.resolve() if args.exit_file is not None else None
                ),
            )
        if args.command == "validate":
            valid, failures = validate_report(manifest, args.junit.resolve())
            summary = parse_pytest_junit(args.junit.resolve())
            print(
                "Mandatory service qualification: "
                f"selected={summary.selected} passed={summary.passed} "
                f"failed={summary.failed} errors={summary.errors} "
                f"skipped={summary.skipped}"
            )
            for failure in failures:
                print(f"ERROR: {failure}.")
            return 0 if valid else 1
        print(json.dumps(manifest, ensure_ascii=True, indent=2, sort_keys=True))
        return 0
    except (ET.ParseError, OSError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR: mandatory service qualification manifest/report invalid: {error}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
