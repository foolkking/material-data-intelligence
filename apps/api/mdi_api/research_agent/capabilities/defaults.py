from __future__ import annotations

from mdi_api.research_agent.schemas import (
    CapabilityInputSlot,
    CapabilityManifest,
    CapabilityOutputSlot,
    CapabilityPrecondition,
    CapabilityStatus,
    ToolBinding,
)
from mdi_api.research_agent.capabilities.registry import InMemoryCapabilityRegistry


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
        evidence_projector="agent2.fixture.result",
        result_projector="agent2.fixture.result",
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
    ]
    for manifest in manifests:
        if manifest.capability_id == "structure.rdf":
            manifest = manifest.model_copy(update={"tool_bindings": [manifest.tool_bindings[0].model_copy(update={"parameter_mapping": {"cutoff_angstrom": "r_max_angstrom"}})]})
        registry.register(manifest)
    return registry
