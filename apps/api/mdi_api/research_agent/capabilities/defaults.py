from __future__ import annotations

from mdi_api.research_agent.schemas import (
    CapabilityInputSlot,
    CapabilityManifest,
    CapabilityOutputSlot,
    CapabilityStatus,
    ToolBinding,
)
from mdi_api.research_agent.capabilities.registry import InMemoryCapabilityRegistry
from mdi_api.research_agent.capabilities.packs import CapabilityExtensionRegistry, build_phase11_packs


_DISPLAY_NAMES = {
    "structure.rdf": "计算径向分布函数",
    "diffraction.theoretical_xrd": "生成理论 XRD 图谱",
    "diffraction.experimental_theoretical_comparison": "比较实验与理论 XRD 峰",
    "ml.regression_evaluation": "评估回归模型",
    "trajectory.msd": "计算均方位移",
    "trajectory.diffusion": "估算扩散性质",
    "phonon.band": "检查声子能带",
    "phonon.dos": "检查声子态密度",
    "phonon.band_dos": "组合声子能带与态密度",
    "structure.coordination_hist": "分析配位数分布",
    "structure.coordination_crystalnn": "检查 CrystalNN 局域配位",
    "structure.coordination_voronoinn": "检查 VoronoiNN 局域配位",
    "trajectory.rdf": "计算轨迹径向分布函数",
    "electronic.band_structure": "检查电子能带",
    "electronic.dos": "检查电子态密度",
    "data.composition_space": "探索材料组成空间",
    "data.materials_explorer": "浏览材料数据集",
}


def _manifest(
    capability_id: str,
    purpose: str,
    requirements: list[str],
    inputs: list[CapabilityInputSlot],
    outputs: list[CapabilityOutputSlot],
    tool_id: str,
    *,
    priority: int = 100,
) -> CapabilityManifest:
    return CapabilityManifest(
        capability_id=capability_id,
        version="1.0",
        domain=capability_id.split(".", 1)[0],
        display_name=_DISPLAY_NAMES.get(capability_id, capability_id.replace(".", " ").title()),
        scientific_purpose=purpose,
        satisfies_requirements=requirements,
        input_slots=inputs,
        output_slots=outputs,
        preconditions=[],
        limitations=[],
        tool_bindings=[ToolBinding(tool_id=tool_id, version_constraint=">=0.1,<1.0")],
        viewer_bindings=[],
        evidence_projector=None,
        result_projector=f"agent2.{capability_id}",
        report_projector=None,
        progress_projector="agent2.fixture.progress",
        status=CapabilityStatus.ACTIVE,
        planning_priority=priority,
    )


def build_default_capability_registry() -> InMemoryCapabilityRegistry:
    structure = CapabilityInputSlot(name="structure", accepted_object_types=["structure.crystal"])
    trajectory = CapabilityInputSlot(name="trajectory", accepted_object_types=["trajectory.atomic"])
    registry = InMemoryCapabilityRegistry()
    manifests = [
        _manifest("structure.rdf", "Compute a radial distribution function.", ["structure.compute_rdf"], [structure], [CapabilityOutputSlot(name="rdf", result_type="structure.rdf")], "structure.rdf"),
        _manifest("diffraction.theoretical_xrd", "Generate a theoretical XRD pattern.", ["diffraction.generate_theoretical_pattern"], [structure], [CapabilityOutputSlot(name="theoretical_xrd", result_type="diffraction.xrd.theoretical", scientific_object_type="diffraction.xrd.theoretical")], "structure.xrd"),
        _manifest("diffraction.experimental_theoretical_comparison", "Compare experimental and theoretical XRD patterns.", ["diffraction.compare_experimental_theoretical"], [CapabilityInputSlot(name="experimental", accepted_object_types=["diffraction.xrd.experimental"]), CapabilityInputSlot(name="theoretical", accepted_object_types=["diffraction.xrd.theoretical"])], [CapabilityOutputSlot(name="comparison", result_type="diffraction.xrd.comparison")], "structure.experimental_xrd_comparison"),
        _manifest("ml.regression_evaluation", "Evaluate a materials regression result.", ["ml.evaluate_regression"], [CapabilityInputSlot(name="dataset", accepted_object_types=["materials.dataset"])], [CapabilityOutputSlot(name="evaluation", result_type="ml.regression.evaluation")], "ml.regression_evaluation"),
        _manifest("trajectory.msd", "Compute mean-squared displacement.", ["trajectory.compute_msd"], [trajectory], [CapabilityOutputSlot(name="msd", result_type="trajectory.msd")], "trajectory.msd"),
        _manifest("trajectory.diffusion", "Estimate diffusion from MSD evidence.", ["trajectory.estimate_diffusion"], [CapabilityInputSlot(name="trajectory", accepted_object_types=["trajectory.atomic"]), CapabilityInputSlot(name="msd", accepted_object_types=["trajectory.msd"])], [CapabilityOutputSlot(name="diffusion", result_type="trajectory.diffusion")], "trajectory.diffusion"),
        _manifest("phonon.band", "Normalize and inspect a phonon band.", ["phonon.inspect_band"], [CapabilityInputSlot(name="band", accepted_object_types=["phonon.band_structure"])], [CapabilityOutputSlot(name="band", result_type="phonon.band", scientific_object_type="phonon.band_structure")], "phonon.band"),
        _manifest("phonon.dos", "Normalize and inspect a phonon DOS.", ["phonon.inspect_dos"], [CapabilityInputSlot(name="dos", accepted_object_types=["phonon.dos"])], [CapabilityOutputSlot(name="dos", result_type="phonon.dos", scientific_object_type="phonon.dos")], "phonon.dos"),
        _manifest("phonon.band_dos", "Compose compatible phonon band and DOS views.", ["phonon.inspect_band", "phonon.inspect_dos"], [CapabilityInputSlot(name="band", accepted_object_types=["phonon.band_structure"]), CapabilityInputSlot(name="dos", accepted_object_types=["phonon.dos"])], [CapabilityOutputSlot(name="combined", result_type="phonon.band_dos")], "phonon.band_dos"),
        _manifest("structure.coordination_hist", "Summarize distance-cutoff coordination distributions.", ["structure.inspect_coordination_hist"], [structure], [CapabilityOutputSlot(name="coordination", result_type="structure.coordination.hist")], "structure.coordination_hist"),
        # The generic coordination requirement is the canonical router
        # contract.  Keep the algorithm-specific requirements as stricter
        # aliases so either trusted implementation can satisfy a request that
        # has not selected an algorithm yet; the planner still chooses the
        # concrete CrystalNN/VoronoiNN tool from the user's goal.
        _manifest("structure.coordination_crystalnn", "Inspect CrystalNN coordination results.", ["structure.inspect_coordination", "structure.inspect_coordination_crystalnn"], [structure], [CapabilityOutputSlot(name="coordination", result_type="structure.coordination.crystalnn")], "structure.coordination_crystalnn"),
        _manifest("structure.coordination_voronoinn", "Inspect VoronoiNN coordination results.", ["structure.inspect_coordination", "structure.inspect_coordination_voronoi"], [structure], [CapabilityOutputSlot(name="coordination", result_type="structure.coordination.voronoi")], "structure.coordination_voronoinn"),
        _manifest("trajectory.rdf", "Compute a bounded RDF from an atomic trajectory.", ["trajectory.compute_rdf"], [trajectory], [CapabilityOutputSlot(name="rdf", result_type="trajectory.rdf")], "trajectory.rdf"),
        _manifest("electronic.band_structure", "Inspect supplied electronic band data.", ["electronic.inspect_band"], [CapabilityInputSlot(name="band", accepted_object_types=["electronic.band_structure"])], [CapabilityOutputSlot(name="band", result_type="electronic.band_structure", scientific_object_type="electronic.band_structure")], "electronic.band_structure"),
        _manifest("electronic.dos", "Inspect supplied electronic DOS data.", ["electronic.inspect_dos"], [CapabilityInputSlot(name="dos", accepted_object_types=["electronic.dos"])], [CapabilityOutputSlot(name="dos", result_type="electronic.dos", scientific_object_type="electronic.dos")], "electronic.dos"),
        _manifest("data.composition_space", "Explore an authorized composition-space projection.", ["data.explore_composition_space"], [CapabilityInputSlot(name="dataset", accepted_object_types=["materials.dataset", "materials.table"])], [CapabilityOutputSlot(name="space", result_type="data.composition_space")], "dataset.composition_space"),
        _manifest("data.materials_explorer", "Summarize an authorized materials dataset.", ["data.explore_materials"], [CapabilityInputSlot(name="dataset", accepted_object_types=["materials.dataset", "materials.table"])], [CapabilityOutputSlot(name="explorer", result_type="data.materials_explorer")], "dataset.materials_explorer"),
    ]
    # Phase 11 trusted-pack boundary: default capabilities are still the
    # existing Phase 1-10 manifests, but are normalized through immutable
    # repository-owned packs before becoming resolver-visible.
    extension_registry = CapabilityExtensionRegistry(packs=build_phase11_packs(manifests))
    for manifest in extension_registry.list_capabilities():
        if manifest.capability_id == "structure.rdf":
            manifest = manifest.model_copy(update={"tool_bindings": [manifest.tool_bindings[0].model_copy(update={"parameter_mapping": {"cutoff_angstrom": "r_max_angstrom"}})]})
        registry.register(manifest)
    return registry
