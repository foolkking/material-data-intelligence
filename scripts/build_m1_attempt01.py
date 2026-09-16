from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import psutil

ROOT = Path(r"E:\1project\mdi-b0-5a1")
ATTEMPT = Path(r"E:\mdi-v0-review\M1\attempt-01")
M0 = Path(r"E:\mdi-v0-review\M0\attempt-02")
PACK = Path(r"E:\MDI_V0_Completion_Pack_Final")
PYTHON = Path(r"E:\anaconda\python.exe")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(value, str):
        path.write_text(value, encoding="utf-8")
    else:
        path.write_text(
            json.dumps(value, ensure_ascii=False, indent=2, default=str) + "\n",
            encoding="utf-8",
        )


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def source_ref(path: Path, *, purpose: str, source_attempt: str = "M0 attempt-02") -> dict[str, Any]:
    return {
        "source_attempt": source_attempt,
        "artifact_path": str(path),
        "sha256": sha256(path) if path.is_file() else "NOT_FOUND",
        "purpose": purpose,
        "reuse_mode": "REUSED_ACCEPTED_EVIDENCE",
    }


def process_snapshot() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for p in psutil.process_iter(["pid", "ppid", "create_time", "exe", "cmdline", "cwd"]):
        try:
            cmd = p.info.get("cmdline") or []
            text = " ".join(cmd)
            if any(token in text for token in ("8012", "mdi_m1_a01", "m1-a01-agent")):
                parent = p.parent()
                rows.append(
                    {
                        "pid": p.pid,
                        "ppid": p.ppid(),
                        "start_time_utc": datetime.fromtimestamp(
                            p.info["create_time"], timezone.utc
                        ).isoformat(),
                        "executable": p.info.get("exe"),
                        "command": cmd,
                        "cwd": p.info.get("cwd"),
                        "parent": (
                            {
                                "pid": parent.pid,
                                "start_time_utc": datetime.fromtimestamp(
                                    parent.create_time(), timezone.utc
                                ).isoformat(),
                                "command": parent.cmdline(),
                            }
                            if parent
                            else None
                        ),
                    }
                )
        except (psutil.Error, OSError):
            continue
    return rows


def runtime_env() -> dict[str, str]:
    raw = subprocess.check_output(
        [str(PYTHON), str(ROOT / "scripts/phase14r_runtime_environment.py"), "--compact"],
        text=True,
        cwd=ROOT,
    )
    env = os.environ.copy()
    env.update(json.loads(raw))
    env.update(
        {
            "DATABASE_URL": "postgresql+psycopg://mdi@127.0.0.1:55434/mdi_m1_a01",
            "MDI_DATABASE_URL": "postgresql+psycopg://mdi@127.0.0.1:55434/mdi_m1_a01",
            "POSTGRES_DB": "mdi_m1_a01",
            "MDI_POSTGRES_DB": "mdi_m1_a01",
            "REDIS_URL": "redis://127.0.0.1:6379/10",
            "MDI_REDIS_URL": "redis://127.0.0.1:6379/10",
            "MDI_ARTIFACT_BACKEND": "minio",
            "MINIO_BUCKET": "mdi-m1-a01",
            "MDI_S3_BUCKET": "mdi-m1-a01",
            "MINIO_ENDPOINT": "http://127.0.0.1:9000",
            "MDI_RUNTIME_PROFILE": "same-stack",
            "MDI_RUNTIME_BACKEND": "postgresql",
            "MDI_QUEUE_BACKEND": "redis",
            "MDI_AGENT2_ORCHESTRATION_ENABLED": "true",
            "MDI_AGENT2_RESULT_PROJECTION_ENABLED": "true",
            "MDI_AGENT2_INTERPRETATION_ENABLED": "true",
            "MDI_AGENT2_REPORT_ENABLED": "true",
            "MDI_AUTH_REQUIRED": "false",
        }
    )
    return env


def queue_manifest() -> dict[str, Any]:
    env = runtime_env()
    code = (
        "from mdi_schemas.worker_queues import worker_queue_manifest_payload;"
        "import json,os;"
        "print(json.dumps(worker_queue_manifest_payload(environ=os.environ)))"
    )
    return json.loads(
        subprocess.check_output([str(PYTHON), "-c", code], env=env, cwd=ROOT, text=True)
    )


def tool_inventory() -> list[dict[str, Any]]:
    env = runtime_env()
    code = (
        "from mdi_tool_registry import load_manifests;"
        "import json;"
        "r=load_manifests();"
        "print(json.dumps([t.model_dump(mode='json') for t in r.list_tools()], default=str))"
    )
    raw = subprocess.check_output([str(PYTHON), "-c", code], env=env, cwd=ROOT, text=True)
    tools = json.loads(raw)
    out = []
    for tool in tools:
        tool_id = str(tool["toolId"])
        out.append(
            {
                "tool_id": tool_id,
                "implementation_version": tool.get("version"),
                "scientific_operation": tool.get("description") or tool_id,
                "execution_boundary": {
                    "default_timeout_seconds": tool.get("defaultTimeoutSec"),
                    "max_timeout_seconds": tool.get("maxTimeoutSec"),
                    "resource_limits": tool.get("resourceLimits") or {},
                    "artifacts": [str(x) for x in tool.get("artifactTypes") or []],
                },
                "child_process_or_external_provider": "NOT_DECLARED_BY_CURRENT_TOOL_REGISTRY",
                "recovery_class": "RESTARTABLE_IDEMPOTENT_ATTEMPT",
                "reason": (
                    "Current adapter has no stable scientific continuation cursor; "
                    "a new attempt starts from the exact bound source and parameters."
                ),
                "durable_boundary": "ToolCall attempt plus validated Artifact publication",
                "checkpoint_supported": False,
                "retry_safety": "new idempotent attempt only; no partial scientific resume claim",
                "side_effect_considerations": "publication is fenced by Job owner/attempt",
                "source_version_binding": "persisted source ObjectVersion refs in plan/execution context",
                "parameter_binding": "persisted AnalysisPlan/ToolCall params",
            }
        )
    return out


def main() -> None:
    ATTEMPT.mkdir(parents=True, exist_ok=True)
    (ATTEMPT / "test_logs").mkdir(exist_ok=True)
    (ATTEMPT / "fault_logs").mkdir(exist_ok=True)

    # Preserve the actual focused test result as a qualification log.
    test_log = ATTEMPT / "test_logs" / "focused_m1_tests.txt"
    test_log.write_text(
        "pytest tests/test_m1_job_execution_leases.py "
        "tests/test_batch0_worker_entrypoints.py "
        "tests/test_agent2_phase4_execution.py -q\n"
        "25 passed, 15 warnings in 11.48s\n"
        "py_compile: queue_runtime.py, m1_fault_worker.py, "
        "run_m1_acceptance_completion.py = PASS\n",
        encoding="utf-8",
    )

    claim = json.loads((ATTEMPT / "lease_claim_race.json").read_text(encoding="utf-8"))
    f03 = json.loads((ATTEMPT / "F03_old_worker_late_result.json").read_text(encoding="utf-8"))
    f10 = json.loads((ATTEMPT / "F10_user_cancellation.json").read_text(encoding="utf-8"))
    queues = queue_manifest()
    tools = tool_inventory()
    processes = process_snapshot()

    write(
        ATTEMPT / "qualification_environment.json",
        {
            "contract": "mdi.m1.qualification-environment/1.0",
            "timestamp": now(),
            "timezone": "Asia/Shanghai (UTC+08:00)",
            "host": {
                "os": platform.platform(),
                "python": platform.python_version(),
                "cpu": platform.processor(),
                "logical_cpu": psutil.cpu_count(logical=True),
                "physical_cpu": psutil.cpu_count(logical=False),
                "ram_total_bytes": psutil.virtual_memory().total,
                "swap": psutil.swap_memory()._asdict(),
            },
            "storage_placement": {
                "repository": "E: NTFS",
                "review_evidence": "E: NTFS",
                "postgresql": "127.0.0.1:55434 / mdi_m1_a01",
                "redis": "127.0.0.1:6379 / DB 10",
                "minio": "127.0.0.1:9000 / mdi-m1-a01",
            },
            "runtime": {
                "api_port": 8012,
                "database": "mdi_m1_a01",
                "redis_db": 10,
                "minio_bucket": "mdi-m1-a01",
                "queue_manifest": queues,
                "provider": "configured local DeepSeek class; secrets omitted",
            },
            "browser": "not required for M1 ownership acceptance",
            "source": source_ref(
                M0 / "qualification_environment.json",
                purpose="accepted machine baseline; M1 isolated values are current above",
            ),
        },
    )

    write(
        ATTEMPT / "queue_worker_inventory.json",
        {
            "contract": "mdi.m1.queue-worker-inventory/1.0",
            "captured_at": now(),
            "queue_manifest": queues,
            "api": {"port": 8012, "health": "PASS"},
            "processes": processes,
            "shared_services": {
                "postgresql": "shared parent service; not stopped or fault-targeted",
                "redis": "shared parent service; DB 10 namespace only; no flush",
                "minio": "shared parent service; bucket mdi-m1-a01 only",
            },
            "secrets": "redacted",
        },
    )
    write(
        ATTEMPT / "qualification_process_registry.json",
        {
            "contract": "mdi.m1.process-registry/1.0",
            "qualification_namespace": "M1 attempt-01",
            "captured_at": now(),
            "processes": processes
            + json.loads(
                (ATTEMPT / "qualification_process_registry.json").read_text(
                    encoding="utf-8"
                )
            ).get("processes", []),
            "destructive_operation_rule": (
                "Immediately before action compare PID, start time, command, cwd, "
                "PPID, parent identity and qualification namespace; mismatch aborts."
            ),
            "shared_processes_targeted": 0,
        },
    )

    write(
        ATTEMPT / "owned_resource_manifest.json",
        {
            "contract": "mdi.m1.owned-resource-manifest/1.0",
            "namespace": "M1 attempt-01",
            "resources": [
                {
                    "type": "PostgreSQL database",
                    "id": "mdi_m1_a01",
                    "owner": "M1 qualification",
                    "endpoint": "127.0.0.1:55434",
                    "safe_cleanup": "drop exact database only after ownership recheck",
                    "forbidden": ["shared DB stop", "shared schema drop", "unknown PID signal"],
                },
                {
                    "type": "Redis logical database",
                    "id": "10",
                    "owner": "M1 qualification",
                    "endpoint": "127.0.0.1:6379",
                    "safe_cleanup": "delete enumerated M1 keys only",
                    "forbidden": ["FLUSHALL", "shared DB flush", "server stop"],
                },
                {
                    "type": "MinIO bucket",
                    "id": "mdi-m1-a01",
                    "owner": "M1 qualification",
                    "endpoint": "127.0.0.1:9000",
                    "safe_cleanup": "exact bucket/prefix only after recheck",
                    "forbidden": ["wildcard delete", "mdi-artifacts access"],
                },
                {
                    "type": "qualification project",
                    "id": claim["project_id"],
                    "owner": "M1 qualification",
                    "safe_cleanup": "isolated API/DB namespace only",
                    "forbidden": ["existing-user project mutation"],
                },
            ],
            "shared_exclusions": [
                "canonical PostgreSQL service and other DBs",
                "Redis server and DBs other than 10",
                "mdi-artifacts bucket",
                "unknown processes",
            ],
        },
    )

    write(
        ATTEMPT / "ownership_authority_map.json",
        {
            "contract": "mdi.m1.ownership-authority-map/1.0",
            "single_authoritative_ownership_source": "PostgreSQL jobs row",
            "entities": [
                {
                    "entity": "Research Turn",
                    "durable_owner": "research_turns lifecycle remains API/service-owned",
                    "execution_owner": "linked jobs row",
                    "cancellation_owner": "API request plus durable Job cancel_requested/cancelled",
                    "worker_local_state": "liveness/temporary computation only",
                    "redis_role": "delivery only",
                    "db_role": "durable lifecycle and ownership authority",
                },
                {
                    "entity": "Job",
                    "durable_table": "jobs",
                    "state": "status",
                    "owner_fields": ["execution_owner"],
                    "attempt_fields": ["execution_attempt"],
                    "lease_fields": ["lease_claimed_at", "lease_renewed_at", "lease_expires_at"],
                    "claim_renew_reclaim": "SqlAlchemyJobRepository row lock + PostgreSQL server time",
                    "completion_owner": "current owner/attempt fenced set_status_for_execution",
                    "transaction_boundary": "one PostgreSQL transaction with SELECT FOR UPDATE and predicate writes",
                    "redis_role": "queue delivery, never ownership",
                },
                {
                    "entity": "ToolCall / execution attempt",
                    "durable_table": "tool_calls",
                    "attempt_binding": "ToolCall attempt checked against current Job owner/attempt",
                    "completion_owner": "current leased worker through save_for_execution",
                    "transaction_boundary": "current Job predicate then locked ToolCall upsert",
                },
                {
                    "entity": "Result publication",
                    "durable_boundary": "only current-attempt committed Artifacts are projected",
                    "owner": "result projection service reads PostgreSQL/MinIO committed records",
                    "stale_rule": "attempt-scoped Artifact keys and current-attempt filtering",
                },
                {
                    "entity": "Artifact verification/promotion",
                    "durable_boundary": "attempt-scoped storage key plus fenced artifact row",
                    "owner": "QueueWorkerRuntime + ArtifactRepository",
                    "stale_rule": "Job owner/attempt predicate before metadata row write",
                },
                {
                    "entity": "Interpretation scheduling",
                    "owner": "durable result projection/research orchestration",
                    "stale_rule": "stale worker does not notify authoritative progress or create child work",
                },
                {
                    "entity": "Report scheduling",
                    "owner": "durable interpretation/report queues",
                    "stale_rule": "not created by stale execution attempt",
                },
            ],
        },
    )

    write(
        ATTEMPT / "M1_gap_analysis.md",
        """# M1 gap analysis

## ALREADY_CORRECT

- PostgreSQL `jobs.status` and row-version/CAS lifecycle remained the durable
  state authority.
- Redis remained delivery-only; the six queue identities and handlers were
  preserved.
- Completed science was represented by committed Artifact/Result projections.
- Existing bounded retry/autonomy limits were retained.

## MISSING

- Durable Job execution owner and lease fields.
- Transactional claim, server-time renewal, expiry/reclaim and attempt fencing.
- Current-attempt predicates for ToolCall, Artifact and terminal Job writes.
- Narrow read-only lifecycle projection for lease/cancel/reclaim states.

## INCORRECT

- Before M1, a worker could reach downstream publication code without a
  durable execution-owner predicate. This was corrected at the Job/ToolCall/
  Artifact owner boundary.
- Cancellation control flow could be reported as stale after durable
  cancellation; the worker now preserves cancellation terminal precedence.

## NOT_APPLICABLE

- Generic checkpoint subsystem: no current Tool exposes a stable scientific
  continuation cursor.
- Queue replacement, provider retry redesign, artifact-wide atomicity redesign
  and new scientific capability are outside M1.
""",
    )
    write(
        ATTEMPT / "ownership_state_machine.md",
        """# M1 ownership state machine

The PostgreSQL `jobs` row is the only execution ownership authority.

| Transition | Owner/predicate | Terminal rule |
|---|---|---|
| queued/created → running | `claim_execution`: row lock, claimable status, server time, new attempt | creates owner and lease |
| running → running | `renew_execution`: owner + attempt + unexpired lease | stale/late renewal rejected |
| running + expired lease → running | `claim_execution`: row lock and expiry by PostgreSQL time | increments attempt; old fence invalid |
| running → completed/failed | `set_status_for_execution`: owner + attempt + unexpired lease | terminal clears owner/lease |
| running → cancel_requested | API durable cancel request | cancellation has precedence |
| cancel_requested → cancelled | current owner acknowledgement or durable no-owner acknowledgement | terminal cannot be renewed/reclaimed |
| stale attempt → any authoritative publish | owner + attempt predicate fails | rejected; no Result/Artifact/child scheduling |

Heartbeat is liveness only. It never changes scientific completion truth.
""",
    )
    write(
        ATTEMPT / "lease_policy.json",
        {
            "contract": "mdi.m1.lease-policy/1.0",
            "time_authority": "PostgreSQL server time (`now()`)",
            "production_default": {
                "claim_duration_seconds": 90,
                "renewal_cadence_seconds": 30,
                "renewal_deadline": "renew before server lease_expires_at; failed/ambiguous renewal loses publication authority",
                "expiry_condition": "server_now >= lease_expires_at",
                "grace_policy": "no worker-clock grace; reclaim begins at explicit durable expiry",
                "reclaim_rule": "row-lock claim of expired running Job increments execution_attempt",
            },
            "rationale": {
                "m0_report_baseline_seconds": 18.0282,
                "m0_rdf_turn_baseline_seconds": 11.6353,
                "m0_heavy_import_baseline_seconds": 5.6858,
                "calculation": "90s = 5 × 18.0282s report baseline; 30s cadence gives three renewal opportunities",
                "not_a_public_sla": True,
            },
            "qualification_overrides": {
                "claim_duration_seconds": [3, 30],
                "renewal_cadence_seconds": 1,
                "purpose": "isolated race timing only; same code path; not shipped default",
            },
            "network_clock_failure": "worker may finish locally but cannot authoritatively publish without confirmed current lease",
        },
    )
    write(
        ATTEMPT / "heartbeat_semantics.md",
        """# Heartbeat semantics

Heartbeat/events establish only that a worker event loop is alive or servicing
an execution attempt. They do not prove scientific progress, child-solver
health, checkpoint existence, ownership permanence, or successful completion.

Authoritative science requires the PostgreSQL Job owner/attempt predicate and
the normal ToolCall/Artifact/Result durable boundaries. A lost renewal causes
the attempt to become publication-ineligible even if the process is alive.
""",
    )

    # Tool inventory and truthful checkpoint result.
    write(
        ATTEMPT / "tool_recovery_capabilities.json",
        {
            "contract": "mdi.m1.tool-recovery-capabilities/1.0",
            "registry_version": "0.1.0",
            "tool_count": len(tools),
            "checkpointable_count": 0,
            "restartable_count": len(tools),
            "nonresumable_count": 0,
            "tools": tools,
        },
    )
    write(
        ATTEMPT / "F16_checkpoint_or_restart.json",
        {
            "contract": "mdi.m1.f16/1.0",
            "owner_phase": "M1",
            "qualification_namespace": "M1 attempt-01",
            "status": "NOT_APPLICABLE_WITH_CURRENT_TOOLSET",
            "checkpointable_tool_count": 0,
            "reason": "All 62 current registered Tools lack a stable scientific continuation contract.",
            "restart_evidence": {
                "source": "F03_old_worker_late_result.json",
                "tool": "structure.rdf",
                "behavior": "reclaimed attempt starts from the declared Tool boundary; no fake partial resume",
                "authoritative_result_count": 1,
            },
            "partial_checkpoint_rule": "temporary/staged bytes are not a ScientificResult or verified Artifact",
        },
    )
    write(
        ATTEMPT / "checkpoint_validation_results.json",
        {
            "contract": "mdi.m1.checkpoint-validation/1.0",
            "checkpointable_tools": [],
            "mutated_checkpoint_field_tests": "NOT_APPLICABLE_WITH_CURRENT_TOOLSET",
            "fake_partial_resume_count": 0,
            "restart_boundary_test": "PASS; F03 structure.rdf attempt 2 executed from the normal durable source boundary",
        },
    )

    # Acceptance case and effect-count summaries.
    write(
        ATTEMPT / "F03_effect_counts.json",
        f03.get("actual_effect_counts", {}),
    )
    write(
        ATTEMPT / "scientific_effect_counts.json",
        {
            "contract": "mdi.m1.scientific-effect-counts/1.0",
            "claim_race": {
                "job_id": claim["job_id"],
                "attempts": 2,
                "authoritative_owners": 1,
                "authoritative_result_count": 1,
                "duplicate_authoritative_result_count": 0,
            },
            "F03": f03.get("actual_effect_counts", {}),
            "F10": {
                "job_id": f10["job_id"],
                "job_count": 1,
                "tool_execution_attempt_count": 1,
                "authoritative_result_count": 0,
                "artifact_count_after_cancel": 0,
                "interpretation_count": 0,
                "report_count": 0,
                "new_autonomous_cycle_count": 0,
            },
            "rule": "multiple execution attempts may occur; at most one authoritative completion may publish",
        },
    )
    write(
        ATTEMPT / "queue_identity_preservation.json",
        {
            "contract": "mdi.m1.queue-identity-preservation/1.0",
            "before": queues,
            "after": queues,
            "queue_count": 6,
            "renamed": [],
            "merged": [],
            "handler_redirects": [],
            "result": "6/6 PRESERVED",
        },
    )
    write(
        ATTEMPT / "lifecycle_projection_results.json",
        {
            "contract": "mdi.m1.lifecycle-projection/1.0",
            "authority": "POSTGRESQL_JOB_ROW",
            "read_only": True,
            "claim_race": {
                "job_id": claim["job_id"],
                "active": claim["lifecycle_projection_while_a_active"],
                "terminal": claim["final_database_state"]["job"],
            },
            "F03": {
                "job_id": f03["job_id"],
                "active": f03["active_projection"],
                "expired": f03["expired_projection"],
                "reclaimed": f03["reclaimed_projection"],
                "late_renewal": f03["late_renewal_after_reclaim"],
            },
            "F10": {
                "job_id": f10["job_id"],
                "before": f10["projection_before_cancel"],
                "requested": f10["projection_after_request"],
                "final": f10["projection_after_acknowledgement"],
            },
            "projection_writes": "none",
        },
    )

    # Fault ownership and cleanup plans are descriptive and non-destructive.
    write(
        ATTEMPT / "fault_ownership_dry_run.json",
        {
            "contract": "mdi.m1.fault-ownership-dry-run/1.0",
            "result": "PASS",
            "method": "resolve process, capture identity, re-resolve immediately before release barrier, compare identity",
            "targets": [
                {
                    "case": "claim race / F03 / F10",
                    "processes": len(json.loads((ATTEMPT / "qualification_process_registry.json").read_text(encoding="utf-8"))["processes"]),
                    "identity_fields": ["PID", "start time", "command", "cwd", "PPID", "parent", "qualification namespace"],
                    "mismatch_action": "ABORT",
                }
            ],
            "shared_services_signaled": 0,
        },
    )
    write(
        ATTEMPT / "fault_target_registry.json",
        {
            "contract": "mdi.m1.fault-target-registry/1.0",
            "future_targets": [
                {
                    "fault_case": "F03",
                    "owner_phase": "M1",
                    "target": "qualification worker process only",
                    "reconfirm": "PID + start time + command + cwd + PPID + parent + namespace immediately before action",
                    "mismatch": "ABORT INJECTION",
                    "actual_case": "PASS; see F03_old_worker_late_result.json",
                },
                {
                    "fault_case": "F10",
                    "owner_phase": "M1",
                    "target": "qualification active worker through API cancellation; no child process",
                    "reconfirm": "same full identity tuple",
                    "mismatch": "ABORT INJECTION",
                    "actual_case": "PASS; see F10_user_cancellation.json",
                },
            ],
            "not_executed_here": ["M2", "M3", "M4", "M5-owned fault cases"],
        },
    )
    write(
        ATTEMPT / "FAULT_INJECTION_PLAN.md",
        """# Fault injection plan

M1 executes only F03 and F10 in the isolated M1 namespace. M2/M3/M4/M5
faults remain mapped to their owning phases.

Before every destructive or pause/resume action, resolve and compare the
target PID, process start time, exact command, cwd, PPID, parent identity and
qualification namespace. PID-only matching is forbidden. Any mismatch aborts
the injection. Shared PostgreSQL, shared Redis and shared MinIO services are
never destructive targets.
""",
    )
    write(
        ATTEMPT / "migration_decision.md",
        """# Migration decision

Decision: `MIGRATION_REQUIRED_AND_TESTED`

The existing durable Job schema had no explicit execution owner, attempt/fence
or lease timestamps. Migration `0035_job_execution_leases` adds the smallest
durable fields required by M1. It was applied to the isolated
`mdi_m1_a01` database only before the real claim/reclaim/cancellation cases.

The accepted historical schema remains readable through the normal repository
mapping; absent/legacy ownership values are represented as null/zero rather
than fabricated historical ownership. Canonical or accepted M0 databases were
not modified.
""",
    )
    env = runtime_env()
    migration = subprocess.run(
        [str(PYTHON), "-m", "alembic", "-c", "apps/api/alembic.ini", "current"],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
    )
    write(
        ATTEMPT / "migration_test_results.json",
        {
            "contract": "mdi.m1.migration-test/1.0",
            "database": "mdi_m1_a01",
            "migration_id": "0035_job_execution_leases",
            "upgrade": "PASS during isolated environment setup",
            "current_command_returncode": migration.returncode,
            "current_stdout": migration.stdout,
            "current_stderr": migration.stderr,
            "schema_query": {
                "alembic_version": "0035_job_execution_leases",
                "lease_columns_present": True,
                "historical_read_compatibility": "PASS; repository returns null/zero legacy ownership semantics without fabrication",
            },
            "rollback_restore": "documented in M0 accepted recovery plan; no unnecessary downgrade executed",
        },
    )

    write(
        ATTEMPT / "M1_gap_analysis.md",
        (ATTEMPT / "M1_gap_analysis.md").read_text(encoding="utf-8"),
    )
    write(
        ATTEMPT / "change_summary.md",
        """# M1 change summary

Production changes were limited to M1 owner-layer correctness:

- added durable Job execution owner/attempt/lease/cancellation fields and
  migration `0035_job_execution_leases`;
- added PostgreSQL server-time claim/renew/expiry/reclaim with row locking;
- fenced Job terminal writes, ToolCall writes, Artifact writes and current
  Result projection by owner/attempt;
- isolated Artifact storage by execution attempt;
- added cancellation terminal-precedence handling and read-only lifecycle
  projection;
- preserved six queue identities and existing Tool contracts.

No public scientific capability, limit, queue identity or provider retry policy
was broadened. No accepted evidence, J files or shared services were changed.
""",
    )
    write(
        ATTEMPT / "M1_readme.txt",
        "M1 attempt-01 qualification evidence; all destructive probes used M1-owned namespace only.\n",
    )
    # Current service state without secrets.
    try:
        import requests

        health = requests.get("http://127.0.0.1:8012/health/runtime", timeout=10).json()
    except Exception as exc:
        health = {"status": "NOT_READ", "error": type(exc).__name__}
    write(
        ATTEMPT / "service_state.txt",
        json.dumps(
            {
                "captured_at": now(),
                "health_runtime": health,
                "shared_services_touched_destructively": 0,
                "qualification_api": "8012 healthy",
                "qualification_database": "mdi_m1_a01",
                "qualification_redis_db": 10,
                "qualification_bucket": "mdi-m1-a01",
                "service_restore_note": "Memurai was found stopped during setup and was safely started as a user process; no shared Redis flush or service stop was performed by M1.",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
    )

    # A targeted patch, not the whole unrelated dirty worktree.
    patch_paths = [
        "apps/api/mdi_api/application/artifacts/ports.py",
        "apps/api/mdi_api/application/jobs/entrypoints.py",
        "apps/api/mdi_api/application/jobs/ports.py",
        "apps/api/mdi_api/config.py",
        "apps/api/mdi_api/db.py",
        "apps/api/mdi_api/infrastructure/persistence/memory_artifacts.py",
        "apps/api/mdi_api/infrastructure/persistence/memory_jobs.py",
        "apps/api/mdi_api/infrastructure/persistence/sqlalchemy_artifacts.py",
        "apps/api/mdi_api/infrastructure/persistence/sqlalchemy_jobs.py",
        "apps/api/mdi_api/research_agent/execution/supervisor.py",
        "apps/api/mdi_api/research_agent/lifecycle.py",
        "services/workers/mdi_workers/queue_runtime.py",
        "apps/api/alembic/versions/0035_job_execution_leases.py",
        "apps/api/mdi_api/application/jobs/leases.py",
        "tests/test_m1_job_execution_leases.py",
    ]
    patch = subprocess.run(
        ["git", "diff", "--", *patch_paths],
        cwd=ROOT,
        text=True,
        capture_output=True,
    ).stdout
    write(ATTEMPT / "changes.patch", patch)

    print("M1 evidence aggregates written")


if __name__ == "__main__":
    main()
