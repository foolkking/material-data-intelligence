from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "apps" / "web"
RUNNER = ROOT / "scripts" / "workspace_cache_runner.mjs"


def _runner(environment: dict[str, str] | None = None):
    script = (
        "console.log(JSON.stringify({"
        "npm:process.env.NPM_CONFIG_CACHE,"
        "playwright:process.env.PLAYWRIGHT_BROWSERS_PATH,"
        "next:process.env.MDI_NEXT_DIST_DIR,"
        "temp:process.env.TEMP"
        "}))"
    )
    return subprocess.run(
        ["node", str(RUNNER), "node", "-e", script],
        cwd=WEB,
        env={**os.environ, **(environment or {})},
        capture_output=True,
        text=True,
        check=False,
    )


def test_tool_caches_default_to_workspace_local_paths() -> None:
    completed = _runner()

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    for key in ("npm", "playwright", "temp"):
        Path(payload[key]).resolve().relative_to(ROOT)
    assert payload["next"] == str(Path(".cache") / "next")


def test_workspace_cache_override_must_remain_inside_repository() -> None:
    completed = _runner(
        {"MDI_WORKSPACE_CACHE_DIR": str(ROOT.parent / "outside-cache")}
    )

    assert completed.returncode == 64
    payload = json.loads(completed.stderr)
    assert payload["code"] == "MDI_WORKSPACE_CACHE_OUTSIDE_REPOSITORY"


def test_npm_next_playwright_and_pytest_configs_use_bounded_cache_contract(
    pytestconfig,
) -> None:
    package = json.loads((WEB / "package.json").read_text(encoding="utf-8"))
    npmrc = (WEB / ".npmrc").read_text(encoding="utf-8")
    next_config = (WEB / "next.config.mjs").read_text(encoding="utf-8")
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(
        encoding="utf-8"
    )

    assert "cache=../../.cache/tooling/npm" in npmrc
    assert '|| ".cache/next"' in next_config
    assert "workspace_cache_runner.mjs" in package["scripts"]["build"]
    assert "workspace_cache_runner.mjs" in package["scripts"]["test"]
    assert "workspace_cache_runner.mjs" in package["scripts"][
        "playwright:install"
    ]
    assert "PLAYWRIGHT_BROWSERS_PATH:" in workflow
    pytest_cache = Path(pytestconfig.option.basetemp).resolve()
    pytest_cache.relative_to(ROOT)
    configured_pytest_cache = os.getenv(
        "MDI_PYTEST_CACHE_DIR", ".cache/tooling/pytest"
    )
    expected_pytest_cache = Path(configured_pytest_cache)
    if not expected_pytest_cache.is_absolute():
        expected_pytest_cache = ROOT / expected_pytest_cache
    assert pytest_cache == expected_pytest_cache.resolve()
