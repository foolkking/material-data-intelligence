from __future__ import annotations

from typing import Protocol

from mdi_api.agent2_errors import RequirementNotRegistered
from mdi_api.research_agent.schemas import RequirementManifest


class ScientificRequirementRegistry(Protocol):
    def register(self, manifest: RequirementManifest) -> None: ...
    def require(self, requirement_id: str) -> RequirementManifest: ...
    def contains(self, requirement_id: str) -> bool: ...
    def list_active(self) -> list[RequirementManifest]: ...


class InMemoryScientificRequirementRegistry:
    def __init__(self) -> None:
        self._manifests: dict[str, RequirementManifest] = {}

    def register(self, manifest: RequirementManifest) -> None:
        if manifest.requirement_id in self._manifests:
            raise ValueError(f"Duplicate requirement: {manifest.requirement_id}")
        self._manifests[manifest.requirement_id] = manifest

    def require(self, requirement_id: str) -> RequirementManifest:
        try:
            return self._manifests[requirement_id]
        except KeyError as exc:
            raise RequirementNotRegistered(requirement_id) from exc

    def contains(self, requirement_id: str) -> bool:
        return requirement_id in self._manifests

    def list_active(self) -> list[RequirementManifest]:
        return sorted(
            (item for item in self._manifests.values() if item.status == "ACTIVE"),
            key=lambda item: item.requirement_id,
        )


def build_default_requirement_registry() -> InMemoryScientificRequirementRegistry:
    registry = InMemoryScientificRequirementRegistry()
    object_constraints = {"type": "object", "additionalProperties": False}
    rdf_constraints = {
        "type": "object",
        "properties": {"cutoff_angstrom": {"type": "number", "exclusiveMinimum": 0}},
        "additionalProperties": False,
    }
    manifests = (
        ("structure.inspect", "Inspect structure", "Inspect an authorized crystal structure.", "structure", ["structure.crystal"], object_constraints),
        ("structure.compute_rdf", "Compute RDF", "Compute a radial distribution function for a crystal structure.", "structure", ["structure.crystal"], rdf_constraints),
        ("structure.inspect_coordination", "Inspect coordination", "Characterize local atomic coordination.", "structure", ["structure.crystal"], object_constraints),
        ("diffraction.generate_theoretical_pattern", "Generate theoretical XRD", "Generate a theoretical diffraction pattern.", "diffraction", ["structure.crystal"], object_constraints),
        ("diffraction.compare_experimental_theoretical", "Compare XRD patterns", "Compare authorized experimental and theoretical diffraction data.", "diffraction", ["diffraction.xrd.experimental", "diffraction.xrd.theoretical", "structure.crystal"], object_constraints),
        ("trajectory.compute_msd", "Compute MSD", "Compute mean-squared displacement from an atomic trajectory.", "trajectory", ["trajectory.atomic"], object_constraints),
        ("trajectory.estimate_diffusion", "Estimate diffusion", "Estimate diffusion from trajectory-derived displacement evidence.", "trajectory", ["trajectory.atomic"], object_constraints),
        ("ml.evaluate_regression", "Evaluate regression", "Evaluate a materials regression result.", "machine_learning", ["materials.dataset"], object_constraints),
        ("phonon.inspect_band", "Inspect phonon band", "Inspect an authorized phonon band structure.", "phonon", ["phonon.band_structure"], object_constraints),
        ("phonon.inspect_dos", "Inspect phonon DOS", "Inspect an authorized phonon density of states.", "phonon", ["phonon.dos"], object_constraints),
        ("data.query", "Query data", "Query authorized project scientific data without mutation.", "data", ["materials.dataset"], object_constraints),
        ("report.compose", "Compose report", "Prepare authorized result references for report composition.", "report", [], object_constraints),
        ("structure.inspect_coordination_hist", "Inspect coordination histogram", "Summarize validated distance-cutoff coordination distributions for a crystal structure.", "structure", ["structure.crystal"], object_constraints),
        ("structure.inspect_coordination_crystalnn", "Inspect CrystalNN coordination", "Inspect validated CrystalNN local coordination results.", "structure", ["structure.crystal"], object_constraints),
        ("structure.inspect_coordination_voronoi", "Inspect Voronoi coordination", "Inspect validated VoronoiNN local coordination results.", "structure", ["structure.crystal"], object_constraints),
        ("trajectory.compute_rdf", "Compute trajectory RDF", "Compute a bounded radial distribution function from an authorized atomic trajectory.", "trajectory", ["trajectory.atomic"], rdf_constraints),
        ("electronic.inspect_band", "Inspect electronic band", "Inspect supplied electronic band-structure data without running a new electronic calculation.", "electronic", ["electronic.band_structure"], object_constraints),
        ("electronic.inspect_dos", "Inspect electronic DOS", "Inspect supplied electronic density-of-states data without running a new electronic calculation.", "electronic", ["electronic.dos"], object_constraints),
        ("data.explore_composition_space", "Explore composition space", "Explore an authorized materials table using the existing bounded composition-space projection.", "data", ["materials.dataset", "materials.table"], object_constraints),
        ("data.explore_materials", "Explore materials", "Summarize and compare an authorized materials dataset using the existing bounded explorer.", "data", ["materials.dataset", "materials.table"], object_constraints),
    )
    for requirement_id, display_name, description, domain, accepted, constraints in manifests:
        registry.register(RequirementManifest(
            requirement_id=requirement_id,
            display_name=display_name,
            description=description,
            scientific_domain=domain,
            accepted_object_types=accepted,
            constraint_schema=constraints,
        ))
    return registry
