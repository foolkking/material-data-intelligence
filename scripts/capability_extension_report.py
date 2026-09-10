"""Generate the canonical scientific capability extension health inventory."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
for relative in (
    "apps/api",
    "packages/schemas",
    "packages/tool-registry",
    "packages/adapters",
    "packages/artifact-core",
    "packages/material-parsers",
    "services/workers",
    "services/llm",
):
    value = str(ROOT / relative)
    if value not in sys.path:
        sys.path.insert(0, value)

import mdi_adapters  # noqa: E402,F401 - publishes the Adapter authority port
from mdi_adapters.registry import ADAPTER_CLASSES  # noqa: E402
from mdi_api.research_agent.capabilities.extension_validation import (  # noqa: E402
    CapabilityExtensionHealthReport,
    validate_capability_extension_platform,
)
from mdi_api.research_agent.registry_validation import DEFAULT_AGENT2_REGISTRIES  # noqa: E402
from mdi_api.scientific_viewers.registry import build_scientific_viewer_registry  # noqa: E402
from mdi_tool_registry import load_manifests, resolve_adapter_invocability  # noqa: E402


def _markdown(report: CapabilityExtensionHealthReport) -> str:
    lines = [
        "# Generated Scientific Capability Inventory",
        "",
        "> Generated from canonical Requirement, Capability Pack, Tool, Adapter,",
        "> Artifact-port, Result-projector and Viewer registries. Do not edit by hand.",
        "",
        "## Extension health",
        "",
        f"- Accepted: **{'YES' if report.accepted else 'NO'}**",
        f"- Capabilities: **{report.capability_count}** "
        f"({report.valid_capability_count} valid / {report.incomplete_capability_count} incomplete)",
        f"- Packs: **{report.pack_count}**",
        f"- Tools: **{report.tool_count}**",
        f"- Adapters: **{report.adapter_count if report.adapter_count is not None else 'not inspected'}**",
        f"- Result projectors: **{report.result_projector_count}**",
        f"- Viewer descriptors: **{report.viewer_descriptor_count}**",
        f"- Duplicate capability authorities: **{report.duplicate_capability_authority_count}**",
        f"- Inventory fingerprint: `{report.inventory_fingerprint}`",
        "",
        "## Capability contracts",
        "",
        "| Capability | Pack | Status | Requirements | Tool → Adapter | Inputs | Results | Ports | Result projector | I/V/R | Qualification |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for item in report.capabilities:
        tool_adapter = "<br>".join(
            f"`{tool}` → `{adapter}`"
            for tool, adapter in zip(item.tool_ids, item.adapter_names, strict=False)
        ) or "—"
        support = (
            f"{item.interpretation_support}/"
            f"{item.viewer_support}/"
            f"{item.report_support}"
        )
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{item.capability_id}@{item.capability_version}`",
                    f"`{item.pack_id}`" if item.pack_id else "—",
                    f"{item.status} / {item.completeness}",
                    "<br>".join(f"`{value}`" for value in item.requirements),
                    tool_adapter,
                    "<br>".join(f"`{value}`" for value in item.input_types),
                    "<br>".join(f"`{value}`" for value in item.result_types),
                    item.artifact_port_support,
                    f"`{item.result_projector}`" if item.result_projector else "NONE",
                    support,
                    item.qualification_level,
                ]
            )
            + " |"
        )

    lines.extend(["", "## Issues", ""])
    if report.issues:
        for issue in report.issues:
            scope = issue.capability_id or issue.component_ref or "platform"
            lines.append(f"- **{issue.severity} {issue.code}** (`{scope}`): {issue.message}")
    else:
        lines.append("- None.")

    lines.extend(
        [
            "",
            "## Classified non-Capability-reachable components",
            "",
            "These entries are classifications, not deletion candidates.",
            "",
            "| Kind | Component | Classification | Reason |",
            "|---|---|---|---|",
        ]
    )
    for orphan in report.orphans:
        lines.append(
            f"| {orphan.component_kind} | `{orphan.component_id}` | "
            f"{orphan.classification} | {orphan.reason} |"
        )
    return "\n".join(lines) + "\n"


def build_report() -> CapabilityExtensionHealthReport:
    return validate_capability_extension_platform(
        DEFAULT_AGENT2_REGISTRIES,
        load_manifests(),
        viewer_registry=build_scientific_viewer_registry(),
        adapter_invocability=resolve_adapter_invocability(),
        adapter_names=ADAPTER_CLASSES,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = build_report()
    payload = json.dumps(report.model_dump(mode="json"), indent=2, ensure_ascii=False) + "\n"
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(payload, encoding="utf-8")
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(_markdown(report), encoding="utf-8")
    if not args.json_output and not args.markdown_output:
        print(payload, end="")
    if args.check:
        print(
            "capabilities="
            f"{report.capability_count} valid={report.valid_capability_count} "
            f"incomplete={report.incomplete_capability_count} tools={report.tool_count} "
            f"adapters={report.adapter_count} errors={report.error_count}"
        )
    return 0 if report.accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
