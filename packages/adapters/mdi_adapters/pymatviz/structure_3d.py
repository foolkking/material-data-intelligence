from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pymatviz as pmv
from pymatgen.core import Structure

from mdi_artifact_core import ArtifactPayload
from mdi_schemas import Artifact, ArtifactType

from ..base import BaseToolAdapter
from ..context import ToolExecutionContext
from ..errors import ToolExecutionError
from ..plotly_export import plotly_payloads


@dataclass
class PreparedStructure3D:
    structures: dict[str, Structure]


class Structure3DAdapter(BaseToolAdapter):
    tool_id = "structure.structure_3d"

    def prepare(self, context: ToolExecutionContext, input_refs: list[Any], params: dict[str, Any]) -> PreparedStructure3D:
        resolved = self._resolved_inputs
        structures = self._coerce_structures(resolved[0] if len(resolved) == 1 else resolved)
        max_structures = int(params.get("maxStructures") or context.resource_limits.get("maxStructures") or 4)
        limited = dict(list(structures.items())[:max_structures])
        max_atoms = context.resource_limits.get("maxAtomsPerStructure", 5000)
        for label, structure in limited.items():
            self._validate_periodic_structure(label, structure, max_atoms=max_atoms)
        return PreparedStructure3D(structures=limited)

    def run(self, prepared: PreparedStructure3D, params: dict[str, Any]) -> dict[str, Any]:
        show_cell = bool(params.get("showCell", True))
        raw_show_bonds = params.get("showBonds", False)
        show_bonds = False if raw_show_bonds == "auto" else bool(raw_show_bonds)
        figure_input: Structure | dict[str, Structure]
        figure_input = next(iter(prepared.structures.values())) if len(prepared.structures) == 1 else prepared.structures
        fig = pmv.structure_3d(figure_input, show_cell=show_cell, show_bonds=show_bonds)
        fig.update_layout(title_text="3D Structure")
        return {"figure": fig, "prepared": prepared, "params": params}

    def export(self, result: dict[str, Any], artifact_types: list[ArtifactType]) -> list[Artifact]:
        prepared: PreparedStructure3D = result["prepared"]
        params = result["params"]
        payloads = plotly_payloads(result["figure"], artifact_types)
        if ArtifactType.summary_md in artifact_types:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.summary_md,
                    file_name="summary.md",
                    content=(
                        "# 3D Structure Plot\n\n"
                        f"- Tool: `{self.tool_id}`\n"
                        f"- Structures rendered: {len(prepared.structures)}\n"
                        f"- Structure labels: {', '.join(prepared.structures)}\n"
                    ),
                    media_type="text/markdown",
                )
            )
        if ArtifactType.recipe_json in artifact_types:
            payloads.append(
                ArtifactPayload(
                    artifact_type=ArtifactType.recipe_json,
                    file_name="recipe.json",
                    content=self.recipe_payload(name="3D Structure Plot", params=params, artifact_types=artifact_types),
                    media_type="application/json",
                )
            )
        return self.export_payloads(
            payloads,
            provenance={
                "sourceFunction": "pymatviz.structure_3d",
                "periodicity": "periodic_required",
                "renderedStructureCount": len(prepared.structures),
            },
        )

    def _coerce_structures(self, raw: Any) -> dict[str, Structure]:
        if isinstance(raw, Structure):
            return {raw.composition.reduced_formula: raw}
        if isinstance(raw, dict) and "@module" in raw and "@class" in raw:
            structure = Structure.from_dict(raw)
            return {structure.composition.reduced_formula: structure}
        if isinstance(raw, dict):
            coerced: dict[str, Structure] = {}
            for key, value in raw.items():
                coerced[str(key)] = self._coerce_single_structure(value)
            return coerced
        if isinstance(raw, (list, tuple)):
            return {f"structure_{idx + 1}": self._coerce_single_structure(value) for idx, value in enumerate(raw)}
        return {"structure_1": self._coerce_single_structure(raw)}

    def _coerce_single_structure(self, value: Any) -> Structure:
        if isinstance(value, Structure):
            return value
        if isinstance(value, dict):
            return Structure.from_dict(value)
        raise ToolExecutionError(
            "TOOL_INPUT_INVALID",
            "structure_3d only accepts pymatgen Structure objects or Structure dictionaries.",
            self.tool_id,
            details={"inputType": type(value).__name__},
        )

    def _validate_periodic_structure(self, label: str, structure: Structure, *, max_atoms: int) -> None:
        if structure.lattice is None or structure.lattice.volume <= 0:
            raise ToolExecutionError(
                "TOOL_INPUT_INVALID",
                "structure_3d requires periodic structures with a valid lattice.",
                self.tool_id,
                details={"structure": label},
            )
        if len(structure) > max_atoms:
            raise ToolExecutionError(
                "TOOL_RESOURCE_LIMIT",
                "Structure exceeds maxAtomsPerStructure.",
                self.tool_id,
                details={"structure": label, "atoms": len(structure), "maxAtomsPerStructure": max_atoms},
            )

