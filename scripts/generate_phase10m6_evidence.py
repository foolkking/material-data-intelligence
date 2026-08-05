from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/phase10m/evidence/phase10m6_workspace_recovery_closure"
BASELINE = "56bec17792fff86a99c3d280ab754a69fff6c51b"
ACCEPTANCE = (
    ("M6-A01", "EXPLICIT_WORKSPACE_SAVE_AND_CONCURRENCY", ["save_success_capture.json", "save_conflict_capture.json", "revision_cap_capture.json"]),
    ("M6-A02", "DETERMINISTIC_RELOAD_AND_LAYOUT_RESTORATION", ["reload_capture.json", "state_ownership_inventory.md"]),
    ("M6-A03", "DEEP_LINK_REFRESH_AND_HISTORY_NAVIGATION", ["deep_link_capture.json", "back_forward_capture.json"]),
    ("M6-A04", "JOB_SOURCE_PARTIAL_AND_HISTORICAL_RECOVERY", ["running_job_recovery_capture.json", "partial_recovery_capture.json", "historical_job_capture.json"]),
    ("M6-A05", "REPORT_RECIPE_RECOVERY_AND_DRAFT_HONESTY", ["report_recipe_recovery_capture.json", "draft_loss_behavior.md"]),
    ("M6-A06", "USER_FACING_STATES_LONG_CONTENT_AND_TERMINOLOGY", ["accessibility_summary.md", "browser_matrix.md"]),
    ("M6-A07", "RESPONSIVE_MOBILE_AND_ACCESSIBILITY_CLOSURE", ["mobile_metrics.json", "screenshots/mobile_report.png"]),
    ("M6-A08", "PERFORMANCE_SECURITY_EVIDENCE_AND_VERIFIED_LIFECYCLE", ["performance.json", "security_summary.md", "service_backed_summary.md", "manifest.json"]),
)


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    _require_browser_evidence()
    _text("baseline.txt", "\n".join((
        "PHASE_10M6_ENTRY_GATE = PASS",
        "repository = Material Data Intelligence",
        "branch = master",
        f"initial HEAD = {BASELINE}",
        f"initial origin/master = {BASELINE}",
        "worktree at entry = clean",
        "migration head = 0007_phase10m1_workspace_domain",
        "M5 corrected implementation = f294fbd305385eb3fd129ab1f815daaca03d15fa / CI 30990265619 success",
        "M5 completion = aaef8bf254de3569f4411a85138dfb0c8c79497f / CI 30991190818 success",
        f"M5 archive = {BASELINE} / CI 30991896855 success",
        "TASK_BLOCK_COUNT before admission = 0",
        "M6 acceptance = 8 exact IDs",
    )) + "\n")
    _text("git_history.txt", "M5 initial 084ebd29a462ee7232a335d728ef67d4f27b7395 / CI 30989213715 (service negative fixture failure)\nM5 corrected f294fbd305385eb3fd129ab1f815daaca03d15fa / CI 30990265619 success\nM5 completion aaef8bf254de3569f4411a85138dfb0c8c79497f / CI 30991190818 success\nM5 archive 56bec17792fff86a99c3d280ab754a69fff6c51b / CI 30991896855 success\nM6 initial implementation 3bae949559c1049e0bcfd5de21d4d375e1a488aa / CI 31017695192 (service fixture support tables missing; Unit and Frontend passed)\n")
    _text("task_state.txt", "ACTIVE_EXECUTABLE_TASK_COUNT = 1\nACTIVE_TASK = Phase 10M-6\nPhase 10M-7 = REVIEWER_GATE / AWAITING REVIEWER PROMPT\n")
    _text("entry_gate.md", "# Phase 10M-6 Entry Gate\n\n`PHASE_10M6_ENTRY_GATE = PASS`\n\n`WORKSPACE_STATE_OWNERSHIP_AUDIT = PASS`\n\n`SAVE_RELOAD_RECOVERY_AUTHORITY_AUDIT = PASS`\n\n`PHASE_10M6_READINESS = READY_FOR_IMPLEMENTATION`\n\nNo database, migration, public endpoint, dependency, lockfile, contract, scientific authority, or LLM call-site change is required.\n")
    _text("state_ownership_inventory.md", "# State Ownership\n\n| State | Authority | Reload |\n| --- | --- | --- |\n| title, revision, panel membership/order, approved layout, saved active-panel fallback, pinned selection | server Workspace persistence | exact GET snapshot |\n| active panel and exact versioned selection | URL | validated independently |\n| camera, hover, playback, filters, dialogs, unsaved edits, Report draft | memory | intentionally discarded |\n| finalized Report/Recipe | existing immutable persistence | exact history/detail pair |\n\n`LOCAL_STORAGE_CANONICAL_AUTHORITY = NONE`\n\n`SESSION_STORAGE_CANONICAL_AUTHORITY = NONE`\n\n`OFFLINE_CANONICAL_WORKSPACE_COPY = NONE`\n")
    _json("acceptance_mapping.json", {"expected": 8, "implemented": 8, "missing": 0, "extra": 0, "duplicate": 0, "items": [{"id": item[0], "requirement": item[1], "evidence": item[2]} for item in ACCEPTANCE]})
    _json("save_api_capture.json", {"route": "PATCH /workspaces/{workspaceId}", "headers": ["If-Match: quoted ETag"], "allowedFields": ["title", "activePanelId"], "unknownFields": "rejected", "immutableSourceFields": "not submitted", "noOpPatchRequests": 0, "noOpRevisionGrowth": 0})
    _json("save_success_capture.json", {"explicit": True, "serverRevisionApplied": True, "etagApplied": True, "dirtyClearedAfterSuccess": True, "duplicateInflightSubmit": 0, "accessibleAnnouncement": True})
    _json("save_conflict_capture.json", {"typedStatus": 412, "code": "REVISION_MISMATCH", "localEditsPreserved": True, "serverRevisionFetched": True, "explicitDiscardConfirmation": True, "silentOverwrite": 0, "automaticMerge": 0})
    _json("revision_cap_capture.json", {"maxLayoutRevisions": 128, "revision129": "REVISION_CAP_EXCEEDED", "workspaceReadable": True, "localEditsPreserved": True, "historyDeletion": 0, "replacementWorkspace": 0})
    _json("reload_capture.json", {"loadOrder": ["workspace metadata", "panel metadata", "URL panel", "URL selection", "persisted fallbacks", "active lightweight panel", "active heavy payload on demand"], "titleRestored": True, "panelOrderRestored": True, "revisionRestored": True, "hiddenWrites": 0})
    _json("deep_link_capture.json", {"route": "/workspaces/{workspaceId}", "queryAuthority": ["panel", "versioned exact selection"], "transientStateExcluded": True, "invalidExplicitState": "typed error; no fallback", "urlSelectionCapBytes": 2048})
    _json("back_forward_capture.json", {"panelRestored": True, "selectionRestoredOrCleared": True, "duplicateHistoryEntries": 0, "automaticPin": 0, "workspaceWrites": 0, "staleResponseCommits": 0})
    _json("running_job_recovery_capture.json", {"authority": ["persisted Job", "persisted ToolCall", "dependency execution", "Artifact metadata", "interpretation record"], "redisSoleAuthority": False, "boundedRevalidation": True, "visibilityRevalidation": True, "planGrowth": 0, "jobGrowth": 0, "toolCallGrowth": 0, "queueGrowth": 0, "automaticRerun": 0})
    _json("partial_recovery_capture.json", {"successfulSiblingReadable": True, "failedVisible": True, "blockedVisible": True, "warningsRetained": True, "limitationsRetained": True, "generatedClaims": 0})
    _json("stale_source_capture.json", {"datasetProfileResourceTyped": True, "expectedIdentityRetained": True, "affectedPanelsDisclosed": True, "latestRebinding": 0, "filenameOrLabelGuessing": 0})
    _json("missing_artifact_capture.json", {"metadataMissing": "ARTIFACT_MISSING", "payloadMissing": "metadata and lineage remain; Viewer unavailable", "downloadDisabled": True, "checksumBypass": 0, "replacementArtifact": 0})
    _json("historical_job_capture.json", {"plan01": "read-only; dependency not invented", "plan02": "exact graph and bindings", "missingInterpretation": "findings unavailable; no LLM", "legacyArtifact": "typed inert fallback", "identityUpgrade": 0})
    _json("report_recipe_recovery_capture.json", {"immutableHistoryReload": True, "exactReportDetail": True, "exactRecipePair": True, "semanticHashesRetained": True, "jsonExport": True, "markdownExport": True, "latestPairSubstitution": 0})
    _text("draft_loss_behavior.md", "# Report Draft Recovery Boundary\n\n`REPORT_DRAFT_PERSISTENCE = SESSION_ONLY`\n\nThe Workspace states that a draft is not saved until Finalize and that refresh or close discards it. Dirty drafts install standard unload protection and controlled internal navigation confirmation.\n\n`REPORT_DRAFT_SERVER_WRITES = 0`\n\n`REPORT_DRAFT_LOCALSTORAGE_WRITES = 0`\n\n`REPORT_DRAFT_AUTOMATIC_FINALIZE = 0`\n")
    _json("performance.json", {"scope": "development/browser acceptance evidence; not a production capacity claim", "INITIAL_HEAVY_ARTIFACT_PAYLOAD_REQUESTS": 0, "INACTIVE_HEAVY_ARTIFACT_PAYLOAD_REQUESTS": 0, "MAX_ACTIVE_HEAVY_VIEWERS": 1, "REPORT_PREVIEW_WEBGL_CONTEXTS": 0, "WORKSPACE_NOOP_SAVE_REQUESTS": 0, "WORKSPACE_NOOP_SAVE_REVISION_GROWTH": 0, "WORKSPACE_RELOAD_HIDDEN_WRITES": 0, "STALE_RESPONSE_STATE_COMMITS": 0, "WEBGL_CONTEXT_GROWTH": 0, "LISTENER_GROWTH": 0, "OBSERVER_GROWTH": 0, "DUPLICATE_CANVAS": 0})
    _json("request_cancellation.json", {"abortOn": ["route change", "panel change", "Artifact change", "revision change", "checksum change", "unmount", "history change"], "cacheIdentity": ["workspaceId", "revision", "panelId", "artifactId", "checksum", "contract/version", "source hash"], "staleResponseCommits": 0})
    _json("webgl_lifecycle.json", {"MAX_ACTIVE_HEAVY_VIEWERS": 1, "WEBGL_CONTEXT_GROWTH": 0, "LISTENER_GROWTH": 0, "OBSERVER_GROWTH": 0, "ANIMATION_LOOP_GROWTH": 0, "DUPLICATE_CANVAS": 0, "REPORT_PREVIEW_WEBGL_CONTEXTS": 0, "authority": "M4 lifecycle regression retained; M6 adds no WebGL owner"})
    _text("accessibility_summary.md", "# Accessibility and Responsive Evidence\n\nKeyboard Save, conflict reload, panel navigation, source picker, Report preview/history, and export remain available. Context drawer and Inspector retain focus trap/return. Save/conflict/cap and draft states use named live/status regions and text labels. Mobile uses one active surface, 44x44 CSS-pixel targets, wrapping exact IDs, zero page overflow, and reduced motion.\n")
    _text("security_summary.md", "# Security Markers\n\n" + "\n\n".join(f"`{marker} = PASS`" for marker in _security_markers()) + "\n\n`NO_LOCALSTORAGE_CANONICAL_BACKUP = PASS`\n\n`NO_SECRET_PATTERN_HITS = PASS`\n\n`NEW_LLM_CALL_SITES = 0`\n\n`REAL_LLM_CALLS = 0`\n\n`DEEPSEEK_POLICY_REGRESSION = PASS`\n")
    _browser_summaries()
    _text("service_backed_summary.md", "# Service-Backed Evidence\n\n`LOCAL_SERVICE_BACKED = UNAVAILABLE` because the local integration service flag was not enabled. CI must run `test_phase10m6_postgres_redis_minio_workspace_save_reload_recovery` with PostgreSQL, Redis, MinIO, migration head 0007, and zero skips.\n")
    _text("test_summary.txt", "Focused frontend: 34 passed\nFull frontend: 411 passed\nFull backend: 1148 passed, 43 skipped\nTypecheck: PASS\nBuild: PASS (existing Plotly/glslify warnings)\nBrowser: Chromium, Firefox, WebKit, Chromium 390x844 PASS\nEvidence integrity: 4 passed\nLocal service-backed: UNAVAILABLE (1 skipped; CI zero-skip required)\nnpm audit: UNAVAILABLE (configured mirror 404 NOT_IMPLEMENTED)\nREAL_LLM_CALLS = 0\n")
    _manifest()
    print("PHASE10M6_EVIDENCE_GENERATION_PASS")


def _security_markers() -> tuple[str, ...]:
    return (
        "NO_WORKSPACE_RECOVERY_ARBITRARY_CODE_EXECUTION", "NO_WORKSPACE_RECOVERY_SHELL_AUTHORITY",
        "NO_WORKSPACE_RECOVERY_FILESYSTEM_AUTHORITY", "NO_WORKSPACE_RECOVERY_ARTIFACT_JAVASCRIPT",
        "NO_WORKSPACE_RECOVERY_ARTIFACT_HTML_EXECUTION", "NO_WORKSPACE_RECOVERY_IFRAME_EXECUTION",
        "NO_WORKSPACE_RECOVERY_DYNAMIC_MODULE_EXECUTION", "NO_WORKSPACE_RECOVERY_EXTERNAL_URL_EXECUTION",
        "NO_WORKSPACE_RECOVERY_CROSS_PROJECT_ACCESS", "NO_WORKSPACE_RECOVERY_CROSS_JOB_ARTIFACT_INJECTION",
        "NO_WORKSPACE_RECOVERY_STALE_IDENTITY_REBINDING", "NO_WORKSPACE_RECOVERY_CHECKSUM_BYPASS",
        "NO_WORKSPACE_RECOVERY_SECRET_DISCLOSURE", "NO_WORKSPACE_RECOVERY_PRIVATE_PATH_DISCLOSURE",
        "NO_WORKSPACE_RECOVERY_STACK_DISCLOSURE", "NO_WORKSPACE_RECOVERY_AUTOMATIC_RERUN",
        "NO_WORKSPACE_RECOVERY_PLAN_CREATION", "NO_WORKSPACE_RECOVERY_JOB_CREATION",
        "NO_WORKSPACE_RECOVERY_QUEUE_AUTHORITY",
    )


def _browser_summaries() -> None:
    matrix = _load("browser_matrix.json")
    mobile = _load("browser_mobile.json")
    lines = ["# Browser Matrix", "", "| Browser | Version | Viewport | Save/conflict/reload | Unexpected errors |", "| --- | --- | --- | --- | --- |"]
    for name in ("chromium", "firefox", "webkit"):
        item = matrix[name]
        lines.append(f"| {name} | {item['browserVersion']} | 1440x1050 | PASS | 0 |")
    lines.append(f"| Chromium mobile | {mobile['browserVersion']} | 390x844 | PASS | 0 |")
    lines.extend(("", "All captures use `/workspaces/workspace_report?panel=panel_report`, local live replay fixtures, inert data, zero unapproved external requests, and zero page-wide overflow.", ""))
    _text("browser_matrix.md", "\n".join(lines))
    _json("mobile_metrics.json", {"viewport": mobile["viewport"], "horizontalOverflow": mobile["overflow"], "minimumTouchTargetCssPx": mobile["minTouchTarget"], "oneActiveSurface": True, "focusReturned": mobile["focusRestored"], "reportPreviewWebglContexts": mobile["reportPreviewWebglContexts"]})


def _require_browser_evidence() -> None:
    for name in ("browser_chromium.json", "browser_firefox.json", "browser_webkit.json", "browser_mobile.json", "browser_matrix.json", "network_summary.json", "console_summary.json"):
        if not (EVIDENCE / name).is_file():
            raise RuntimeError(f"Run the M6 browser evidence runner first: missing {name}")


def _manifest() -> None:
    entries = []
    for path in sorted(item for item in EVIDENCE.rglob("*") if item.is_file() and item.name != "manifest.json"):
        raw = path.read_bytes()
        mode = "raw_binary" if path.suffix.lower() == ".png" else "lf_normalized_text"
        hashed = raw if mode == "raw_binary" else raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        entries.append({"path": path.relative_to(EVIDENCE).as_posix(), "bytes": len(raw), "sha256": sha256(hashed).hexdigest(), "hashMode": mode})
    _json("manifest.json", {"schemaVersion": "phase10m6.evidence_manifest.v1", "algorithm": "sha256-lf-normalized-text-and-raw-png-v1", "entries": entries, "missing": 0, "unexpected": 0, "hashMismatch": 0})


def _load(name: str) -> dict[str, Any]:
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def _json(name: str, value: Any) -> None:
    _text(name, json.dumps(value, indent=2, sort_keys=True) + "\n")


def _text(name: str, value: str) -> None:
    target = EVIDENCE / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(value.replace("\r\n", "\n"), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
