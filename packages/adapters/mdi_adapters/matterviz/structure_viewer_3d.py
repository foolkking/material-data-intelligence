from __future__ import annotations

import html
from dataclasses import dataclass
from typing import Any

import pymatviz as pmv
from pymatgen.core import Structure

from mdi_artifact_core import ArtifactPayload
from mdi_schemas import Artifact, ArtifactType

from ..base import BaseToolAdapter
from ..context import ToolExecutionContext
from ..errors import ToolExecutionError


@dataclass
class PreparedStructureViewer:
    structure: Structure
    source_type: str


class StructureViewer3DAdapter(BaseToolAdapter):
    tool_id = "structure.viewer_3d"

    def prepare(self, context: ToolExecutionContext, input_refs: list[Any], params: dict[str, Any]) -> PreparedStructureViewer:
        resolved = self._resolved_inputs
        if not resolved:
            raise ToolExecutionError("TOOL_INPUT_INVALID", "viewer_3d requires one structure input.", self.tool_id)
        raw = resolved[0]
        if isinstance(raw, (list, tuple)):
            raw = raw[0]
        if isinstance(raw, dict) and "structures" in raw:
            raw = raw["structures"][0]
        structure, source_type = self._coerce_structure(raw)
        max_atoms = context.resource_limits.get("maxAtomsPerStructure", 5000)
        if len(structure) > max_atoms:
            raise ToolExecutionError(
                "TOOL_RESOURCE_LIMIT",
                "Structure exceeds maxAtomsPerStructure.",
                self.tool_id,
                details={"atoms": len(structure), "maxAtomsPerStructure": max_atoms},
            )
        return PreparedStructureViewer(structure=structure, source_type=source_type)

    def run(self, prepared: PreparedStructureViewer, params: dict[str, Any]) -> dict[str, Any]:
        show_cell = bool(params.get("showCell", True))
        raw_show_bonds = params.get("showBonds", "auto")
        show_bonds = False if raw_show_bonds == "auto" else bool(raw_show_bonds)
        fallback = False
        try:
            widget = pmv.StructureWidget(
                prepared.structure,
                show_cell_vectors=show_cell,
                show_bonds=show_bonds,
            )
            viewer_html = widget.to_html()
        except Exception as exc:
            fallback = True
            viewer_html = self._fallback_html(prepared.structure, str(exc))
        return {
            "viewer_html": viewer_html,
            "structure": prepared.structure,
            "source_type": prepared.source_type,
            "fallback": fallback,
            "params": params,
        }

    def export(self, result: dict[str, Any], artifact_types: list[ArtifactType]) -> list[Artifact]:
        structure: Structure = result["structure"]
        payloads: list[ArtifactPayload] = []
        if ArtifactType.matterviz_html in artifact_types:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.matterviz_html,
                    file_name="viewer.html",
                    content=result["viewer_html"],
                    media_type="text/html",
                )
            )
        if ArtifactType.structure_json in artifact_types:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.structure_json,
                    file_name="structure.json",
                    content={
                        "structure": structure.as_dict(),
                        "metadata": self._structure_metadata(structure, result),
                    },
                    media_type="application/json",
                )
            )
        if ArtifactType.summary_md in artifact_types:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.summary_md,
                    file_name="summary.md",
                    content=(
                        "# 3D Structure Viewer\n\n"
                        f"- Tool: `{self.tool_id}`\n"
                        f"- Formula: `{structure.composition.reduced_formula}`\n"
                        f"- Atoms: {len(structure)}\n"
                        f"- MatterViz fallback: {str(result['fallback']).lower()}\n"
                    ),
                    media_type="text/markdown",
                )
            )
        if ArtifactType.recipe_json in artifact_types:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.recipe_json,
                    file_name="recipe.json",
                    content=self.recipe_payload(name="3D Structure Viewer", params=result["params"], artifact_types=artifact_types),
                    media_type="application/json",
                )
            )
        return self.export_payloads(
            payloads,
            provenance={
                "sourceClass": "pymatviz.StructureWidget",
                "mattervizFallback": result["fallback"],
                "sourceInputType": result["source_type"],
            },
        )

    def _coerce_structure(self, raw: Any) -> tuple[Structure, str]:
        if isinstance(raw, Structure):
            return raw, "pymatgen.Structure"
        if isinstance(raw, dict):
            return Structure.from_dict(raw), "StructureDict"
        try:
            from ase import Atoms
            from pymatgen.io.ase import AseAtomsAdaptor

            if isinstance(raw, Atoms):
                if raw.cell is None or raw.cell.volume <= 0:
                    raise ToolExecutionError(
                        "TOOL_INPUT_INVALID",
                        "ASE Atoms input requires a valid cell for MVP viewer conversion.",
                        self.tool_id,
                    )
                return AseAtomsAdaptor.get_structure(raw), "ase.Atoms"
        except ToolExecutionError:
            raise
        except Exception:
            pass
        raise ToolExecutionError(
            "TOOL_INPUT_INVALID",
            "viewer_3d accepts pymatgen Structure, Structure dict, or ASE Atoms with a valid cell.",
            self.tool_id,
            details={"inputType": type(raw).__name__},
        )

    @staticmethod
    def _structure_metadata(structure: Structure, result: dict[str, Any]) -> dict[str, Any]:
        return {
            "formula": structure.composition.reduced_formula,
            "nAtoms": len(structure),
            "latticeVolume": structure.lattice.volume,
            "sourceInputType": result["source_type"],
            "mattervizFallback": result["fallback"],
        }

    @staticmethod
    def _fallback_html(structure: Structure, reason: str) -> str:
        formula = html.escape(structure.composition.reduced_formula)
        escaped_reason = html.escape(reason)
        return (
            "<!DOCTYPE html><html><head><meta charset='utf-8'>"
            "<title>Structure Viewer Fallback</title></head>"
            "<body><h1>Structure Viewer Fallback</h1>"
            f"<p>Formula: <strong>{formula}</strong></p>"
            f"<p>Atoms: {len(structure)}</p>"
            f"<p>Reason: {escaped_reason}</p>"
            "<p>This fallback is a sandbox-safe MVP artifact, not a rendered snapshot.</p>"
            "</body></html>"
        )

