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
    local_environment_constraints = {
        "type": "object",
        "properties": {
            "site_indices": {
                "type": "array", "maxItems": 5000, "uniqueItems": True,
                "items": {"type": "integer", "minimum": 0, "maximum": 4999},
            },
        },
        "additionalProperties": False,
    }
    rdf_constraints = {
        "type": "object",
        "properties": {
            "cutoff_angstrom": {"type": "number", "exclusiveMinimum": 0, "minimum": 0.5, "maximum": 30},
            "r_max_angstrom": {"type": "number", "minimum": 0.5, "maximum": 30},
            "bin_width_angstrom": {"type": "number", "minimum": 0.01, "maximum": 1.0},
        },
        "additionalProperties": False,
    }
    trajectory_window_properties = {
        "window_mode": {"enum": ["whole", "frame", "time"]},
        "frame_start": {"type": "integer", "minimum": 0, "maximum": 9999},
        "frame_end": {"type": "integer", "minimum": 1, "maximum": 10000},
        "time_start_ps": {"type": "number", "minimum": 0, "maximum": 1e12},
        "time_end_ps": {"type": "number", "minimum": 0, "maximum": 1e12},
    }
    trajectory_rdf_constraints = {
        "type": "object",
        "properties": {
            "r_min_angstrom": {"type": "number", "minimum": 0, "maximum": 30},
            "r_max_angstrom": {"type": "number", "exclusiveMinimum": 0, "maximum": 30},
            "bin_count": {"type": "integer", "minimum": 1, "maximum": 2048},
            "species_a": {"type": "string", "minLength": 1, "maxLength": 32},
            "species_b": {"type": "string", "minLength": 1, "maxLength": 32},
            **trajectory_window_properties,
        },
        "additionalProperties": False,
    }
    # Trajectory constraints mirror the already-registered adapter contract at
    # the scientific-requirement boundary.  They stay bounded and fail closed:
    # the orchestrator may preserve an explicit species or fit window from the
    # user's request, but it cannot inject arbitrary execution parameters.
    trajectory_msd_constraints = {
        "type": "object",
        "properties": {
            "species": {
                "type": "string",
                "minLength": 1,
                "maxLength": 32,
                "pattern": "^[A-Za-z0-9+_-]+$",
            },
            "max_lag_count": {"type": "integer", "minimum": 1, "maximum": 2048},
            "origin_stride": {"type": "integer", "minimum": 1, "maximum": 1000},
            "max_origins_per_lag": {
                "type": "integer",
                "minimum": 1,
                "maximum": 4096,
            },
            "drift_correction": {"const": "none"},
            **trajectory_window_properties,
        },
        "additionalProperties": False,
    }
    trajectory_diffusion_constraints = {
        "type": "object",
        "properties": {
            "fit_start_time_ps": {
                "type": "number",
                "minimum": 0,
                "maximum": 1e12,
            },
            "fit_end_time_ps": {
                "type": "number",
                "minimum": 0,
                "maximum": 1e12,
            },
            "direction": {"enum": ["total", "x", "y", "z"]},
            "minimum_fit_points": {
                "type": "integer",
                "minimum": 3,
                "maximum": 10000,
            },
            "minimum_fit_duration_ps": {
                "type": "number",
                "minimum": 0,
                "maximum": 1e9,
            },
            "minimum_origin_coverage": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
            },
            "minimum_r_squared": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
            },
            "alpha_min": {
                "type": "number",
                "minimum": 0.1,
                "maximum": 2,
            },
            "alpha_max": {
                "type": "number",
                "minimum": 0.1,
                "maximum": 3,
            },
        },
        "additionalProperties": False,
    }
    # Dataset exploration requests may carry bounded semantic hints from the
    # orchestrator (for example the selected property and sample identity).
    # These are planning constraints, not executable SQL, and remain strictly
    # typed/bounded at the requirement boundary.
    dataset_constraints = {
        "type": "object",
        "properties": {
            "property": {"type": "string", "minLength": 1, "maxLength": 128},
            "sample": {"type": "string", "minLength": 1, "maxLength": 256},
        },
        "additionalProperties": False,
    }
    manifests = (
        ("structure.inspect", "Summarize structure", "Publish authoritative composition, lattice, and symmetry facts for an authorized crystal structure.", "structure", ["structure.crystal"], object_constraints),
        ("structure.inspect_view", "Open structure viewer", "Build an authorized, inert structure viewer scene without inventing periodicity.", "structure", ["structure.crystal", "structure.atomic"], object_constraints),
        ("trajectory.inspect_view", "Open trajectory viewer", "Build an authorized, inert trajectory viewer product from an atomic trajectory.", "trajectory", ["trajectory.atomic"], object_constraints),
        ("structure.compute_rdf", "Compute RDF", "Compute a radial distribution function for a crystal structure.", "structure", ["structure.crystal"], rdf_constraints),
        ("structure.inspect_coordination", "Inspect coordination", "Characterize local atomic coordination.", "structure", ["structure.crystal"], object_constraints),
        ("diffraction.generate_theoretical_pattern", "Generate theoretical XRD", "Generate a theoretical diffraction pattern.", "diffraction", ["structure.crystal"], object_constraints),
        ("diffraction.compare_experimental_theoretical", "Compare XRD patterns", "Compare authorized experimental and theoretical diffraction data.", "diffraction", ["diffraction.xrd.experimental", "diffraction.xrd.theoretical", "structure.crystal"], object_constraints),
        ("trajectory.compute_msd", "Compute MSD", "Compute mean-squared displacement from an atomic trajectory.", "trajectory", ["trajectory.atomic"], trajectory_msd_constraints),
        ("trajectory.estimate_diffusion", "Estimate diffusion", "Estimate diffusion from trajectory-derived displacement evidence.", "trajectory", ["trajectory.atomic"], trajectory_diffusion_constraints),
        (
            "ml.evaluate_regression",
            "Evaluate regression",
            "Evaluate existing target/prediction columns: MAE, RMSE, R-squared, parity/residual views and high-error sample identities. No model training.",
            "machine_learning",
            ["materials.dataset", "materials.table"],
            object_constraints,
        ),
        (
            "ml.evaluate_uncertainty",
            "Evaluate uncertainty",
            "Evaluate uncertainty diagnostics for a materials prediction table.",
            "machine_learning",
            ["materials.dataset", "materials.table"],
            object_constraints,
        ),
        (
            "ml.evaluate_classification",
            "Evaluate classification",
            "Evaluate a materials classification result.",
            "machine_learning",
            ["materials.dataset", "materials.table"],
            object_constraints,
        ),
        ("phonon.inspect_band", "Inspect phonon band", "Inspect an authorized phonon band structure.", "phonon", ["phonon.band_structure"], object_constraints),
        ("phonon.inspect_dos", "Inspect phonon DOS", "Inspect an authorized phonon density of states.", "phonon", ["phonon.dos"], object_constraints),
        (
            "phonon.compose_band_dos",
            "Compose phonon band and DOS",
            "Compose authorized phonon band and density-of-states results into one compatible combined view.",
            "phonon",
            ["phonon.band_structure", "phonon.dos"],
            object_constraints,
        ),
        (
            "structure.inspect_brillouin_zone",
            "Inspect Brillouin-zone context",
            "Generate bounded reciprocal-lattice, Brillouin-zone, and high-symmetry-path context for an authorized periodic crystal structure.",
            "structure",
            ["structure.crystal"],
            object_constraints,
        ),
        ("data.query", "Query data", "Query authorized project scientific data without mutation.", "data", ["materials.dataset", "materials.table"], dataset_constraints),
        ("report.compose", "Compose report", "Prepare authorized result references for report composition.", "report", [], object_constraints),
        ("structure.inspect_coordination_hist", "Inspect coordination histogram", "Summarize validated distance-cutoff coordination distributions for a crystal structure.", "structure", ["structure.crystal"], object_constraints),
        ("structure.inspect_coordination_crystalnn", "Inspect CrystalNN coordination", "Inspect validated CrystalNN local coordination results.", "structure", ["structure.crystal"], object_constraints),
        ("structure.inspect_coordination_voronoi", "Inspect Voronoi coordination", "Inspect validated VoronoiNN local coordination results.", "structure", ["structure.crystal"], object_constraints),
        ("structure.inspect_local_environment_crystalnn", "Inspect CrystalNN polyhedra", "Build local-environment geometry and polyhedra from exact persisted CrystalNN neighbors. Preserve explicitly requested site indices.", "structure", ["structure.crystal"], local_environment_constraints),
        ("structure.inspect_local_environment_voronoi", "Inspect VoronoiNN polyhedra", "Build local-environment geometry and polyhedra from exact persisted VoronoiNN neighbors. Preserve explicitly requested site indices.", "structure", ["structure.crystal"], local_environment_constraints),
        ("trajectory.compute_rdf", "Compute trajectory RDF", "Compute a bounded radial distribution function from an authorized atomic trajectory.", "trajectory", ["trajectory.atomic"], trajectory_rdf_constraints),
        ("electronic.inspect_band", "Inspect electronic band", "Inspect supplied electronic band-structure data without running a new electronic calculation.", "electronic", ["electronic.band_structure"], object_constraints),
        ("electronic.inspect_dos", "Inspect electronic DOS", "Inspect supplied electronic density-of-states data without running a new electronic calculation.", "electronic", ["electronic.dos"], object_constraints),
        ("volumetric.inspect", "Inspect volumetric field", "Parse and expose one bounded volumetric field through the registered scientific Tool.", "volumetric", ["volumetric.field", "volumetric.charge_density"], object_constraints),
        ("data.explore_composition_space", "Explore composition space", "Explore an authorized materials table using the existing bounded composition-space projection.", "data", ["materials.dataset", "materials.table"], dataset_constraints),
        ("data.explore_materials", "Explore materials", "Summarize and compare an authorized materials dataset using the existing bounded explorer.", "data", ["materials.dataset", "materials.table"], dataset_constraints),
        (
            "data.analyze_composition",
            "Analyze formulas and chemical systems",
            "Summarize formulas and publish the supported element, periodic-table, and chemical-system distributions for an authorized materials table.",
            "data",
            ["materials.dataset", "materials.table"],
            object_constraints,
        ),
        (
            "data.analyze_table",
            "Analyze numeric table properties",
            "Publish the supported numeric summaries, distributions, correlations, histogram, and selected scatter products for an authorized table.",
            "data",
            ["materials.dataset", "materials.table"],
            object_constraints,
        ),
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
    from mdi_tool_registry.element_reference import element_reference_params_schema
    from mdi_tool_registry.project_parameters import PARAMETER_TOOLS, parameter_tool_schema
    for requirement_id, (title, description) in PARAMETER_TOOLS.items():
        registry.register(RequirementManifest(requirement_id=requirement_id, display_name=title, description=description,
            scientific_domain=requirement_id.split(".", 1)[0], accepted_object_types=[], requires_material=False,
            constraint_schema=parameter_tool_schema(requirement_id)))
    for requirement_id, title, description, comparison in (
        ("reference.periodic_table", "绘制元素周期表", "Draw a complete or filtered periodic table; highlight chosen elements and show atomic numbers or versioned Cordero covalent radii. No sample is required.", False),
        ("reference.compare_elements", "比较元素参考性质", "Compare 2–20 named elements by atomic number or Cordero covalent radius in angstrom. These are platform reference values, not sample measurements.", True),
    ):
        registry.register(RequirementManifest(requirement_id=requirement_id, display_name=title, description=description,
            scientific_domain="reference", accepted_object_types=[], requires_material=False,
            constraint_schema=element_reference_params_schema(comparison=comparison)))
    return registry
