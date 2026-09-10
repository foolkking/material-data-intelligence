"""Generate and validate the canonical scientific quality inventory."""

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
    validate_capability_extension_platform,
)
from mdi_api.research_agent.capabilities.quality_validation import (  # noqa: E402
    ScientificQualityHealthReport,
    validate_scientific_quality,
)
from mdi_api.research_agent.registry_validation import DEFAULT_AGENT2_REGISTRIES  # noqa: E402
from mdi_api.scientific_viewers.registry import build_scientific_viewer_registry  # noqa: E402
from mdi_tool_registry import load_manifests, resolve_adapter_invocability  # noqa: E402


def build_report() -> ScientificQualityHealthReport:
    extension_report = validate_capability_extension_platform(
        DEFAULT_AGENT2_REGISTRIES,
        load_manifests(),
        viewer_registry=build_scientific_viewer_registry(),
        adapter_invocability=resolve_adapter_invocability(),
        adapter_names=ADAPTER_CLASSES,
    )
    return validate_scientific_quality(
        extension_report,
        registries=DEFAULT_AGENT2_REGISTRIES,
        repository_root=ROOT,
    )


def _markdown(report: ScientificQualityHealthReport) -> str:
    counts = report.qualification_counts
    lines = [
        "# Generated Scientific Quality Inventory",
        "",
        "> Generated from canonical Capability manifests and evidence-backed quality",
        "> records. Structural completeness and scientific qualification are separate.",
        "",
        "## Quality health",
        "",
        f"- Accepted: **{'YES' if report.accepted else 'NO'}**",
        f"- Capabilities: **{report.capability_count}**",
        f"- Structural only: **{counts.get('STRUCTURAL_ONLY', 0)}**",
        f"- Reference validated: **{counts.get('REFERENCE_VALIDATED', 0)}**",
        f"- Domain validated: **{counts.get('DOMAIN_VALIDATED', 0)}**",
        "- External implementation semantics validated: "
        f"**{counts.get('EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED', 0)}**",
        f"- Reference cases: **{report.reference_case_count}**",
        f"- Invariant cases: **{report.invariant_case_count}**",
        f"- Domain-negative cases: **{report.domain_negative_case_count}**",
        f"- Result projection cases: **{report.result_projection_case_count}**",
        f"- Interpretation evaluation cases: **{report.interpretation_evaluation_case_count}**",
        f"- Report evaluation cases: **{report.report_evaluation_case_count}**",
        f"- Inventory fingerprint: `{report.inventory_fingerprint}`",
        "",
        "## Capability quality",
        "",
        "| Capability | Qualification | Reproducibility | Evidence R/I/N/P/I/R | Reference authority | Status |",
        "|---|---|---|---|---|---|",
    ]
    for item in report.capabilities:
        evidence = item.evidence_counts
        summary = "/".join(
            str(evidence.get(kind, 0))
            for kind in (
                "REFERENCE",
                "INVARIANT",
                "DOMAIN_NEGATIVE",
                "RESULT_PROJECTION",
                "INTERPRETATION",
                "REPORT",
            )
        )
        lines.append(
            f"| `{item.capability_id}` | {item.qualification_level} | "
            f"{item.reproducibility} | {summary} | "
            f"{'<br>'.join(item.reference_authorities)} | {item.status} |"
        )

    lines.extend(["", "## Issues", ""])
    if report.issues:
        for issue in report.issues:
            scope = issue.capability_id or "platform"
            evidence = f" / {issue.evidence_id}" if issue.evidence_id else ""
            lines.append(
                f"- **{issue.severity} {issue.code}** (`{scope}{evidence}`): "
                f"{issue.message}"
            )
    else:
        lines.append("- None.")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `REFERENCE_VALIDATED` means independent/analytical/curated reference evidence exists.",
            "- `DOMAIN_VALIDATED` additionally requires invariants and negative applicability boundaries.",
            "- `EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED` validates parsing, units, projection and limitations owned by this platform; it does not claim to validate the upstream solver/library.",
            "- Evidence is stale when the qualified scientific contract fingerprint changes.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--json-output",
        type=Path,
        default=ROOT / "docs/scientific-quality/generated/scientific_quality_inventory.json",
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=ROOT / "docs/scientific-quality/generated/scientific_quality_inventory.md",
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = build_report()
    payload = json.dumps(report.model_dump(mode="json"), indent=2, ensure_ascii=False) + "\n"
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(payload, encoding="utf-8")
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.write_text(_markdown(report), encoding="utf-8")
    if args.check:
        print(
            "scientific-quality "
            f"capabilities={report.capability_count} "
            f"reference={report.reference_case_count} "
            f"invariant={report.invariant_case_count} "
            f"domain_negative={report.domain_negative_case_count} "
            f"errors={report.error_count}"
        )
    return 0 if report.accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
