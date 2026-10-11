from __future__ import annotations

from mdi_api.research_agent.schemas import (
    CapabilityInputSlot,
    CapabilityManifest,
    CapabilityOutputSlot,
    CapabilitySurfaceSupport,
    CapabilityStatus,
    ToolBinding,
)
from mdi_api.research_agent.capabilities.registry import InMemoryCapabilityRegistry
from mdi_api.research_agent.capabilities.packs import CapabilityExtensionRegistry, build_phase11_packs
from mdi_api.research_agent.capabilities.quality_evidence import (
    qualification_for_capability,
)
from mdi_tool_registry.project_parameters import PARAMETER_TOOLS


_DISPLAY_NAMES = {
    **{key: value[0] for key, value in PARAMETER_TOOLS.items()},
    "reference.periodic_table": "绘制元素周期表",
    "reference.compare_elements": "比较元素参考性质",
    "structure.rdf": "计算径向分布函数",
    "diffraction.theoretical_xrd": "生成理论 XRD 图谱",
    "diffraction.experimental_theoretical_comparison": "比较实验与理论 XRD 峰",
    "ml.regression_evaluation": "评估回归模型",
    "ml.uncertainty_evaluation": "评估预测不确定性",
    "ml.classification_evaluation": "评估分类模型",
    "structure.summary": "总结结构晶格与对称性",
    "structure.viewer_scene": "生成结构查看器场景",
    "trajectory.viewer_scene": "生成轨迹查看器产品",
    "trajectory.msd": "计算均方位移",
    "trajectory.diffusion": "估算扩散性质",
    "phonon.band": "检查声子能带",
    "phonon.dos": "检查声子态密度",
    "phonon.band_dos": "组合声子能带与态密度",
    "structure.brillouin_zone": "生成布里渊区与高对称路径",
    "structure.coordination_hist": "分析配位数分布",
    "structure.coordination_crystalnn": "检查 CrystalNN 局域配位",
    "structure.coordination_voronoinn": "检查 VoronoiNN 局域配位",
    "structure.local_environment_crystalnn": "生成 CrystalNN 配位多面体",
    "structure.local_environment_voronoi": "生成 VoronoiNN 配位多面体",
    "trajectory.rdf": "计算轨迹径向分布函数",
    "electronic.band_structure": "检查电子能带",
    "electronic.dos": "检查电子态密度",
    "data.composition_space": "探索材料组成空间",
    "data.materials_explorer": "浏览材料数据集",
    "data.composition_analysis": "分析材料组成与化学体系",
    "data.table_analysis": "分析数值表格分布与相关性",
    "structure.coordination_analysis": "综合分析局域配位环境",
    "volumetric.data": "处理体数据",
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
    viewer_bindings: list[str] | None = None,
    artifact_port_support: CapabilitySurfaceSupport = CapabilitySurfaceSupport.GENERIC,
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
        viewer_bindings=viewer_bindings or [],
        evidence_projector=None,
        result_projector=f"agent2.{capability_id}",
        report_projector=None,
        progress_projector="agent2.fixture.progress",
        artifact_port_support=artifact_port_support,
        viewer_support=(
            CapabilitySurfaceSupport.SUPPORTED
            if viewer_bindings
            else CapabilitySurfaceSupport.GENERIC
        ),
        qualification=qualification_for_capability(capability_id),
        status=CapabilityStatus.ACTIVE,
        planning_priority=priority,
    )


def _suite_manifest(
    capability_id: str,
    purpose: str,
    requirements: list[str],
    inputs: list[CapabilityInputSlot],
    outputs: list[CapabilityOutputSlot],
    tool_ids: list[str],
    *,
    priority: int = 100,
    viewer_bindings: list[str] | None = None,
    dependency_from_tool: dict[str, str] | None = None,
    version: str = "1.0",
) -> CapabilityManifest:
    manifest = _manifest(
        capability_id,
        purpose,
        requirements,
        inputs,
        outputs,
        tool_ids[0],
        priority=priority,
        viewer_bindings=viewer_bindings,
    )
    dependency_from_tool = dependency_from_tool or {}
    return manifest.model_copy(
        update={
            "version": version,
            "tool_bindings": [
                ToolBinding(
                    tool_id=tool_id,
                    version_constraint=">=0.1,<2.0",
                    priority=index,
                    output_mapping={
                        "mandatory_capability_tool": True,
                        **(
                            {"input_from_tool": dependency_from_tool[tool_id]}
                            if tool_id in dependency_from_tool
                            else {}
                        ),
                    },
                )
                for index, tool_id in enumerate(tool_ids, start=1)
            ]
        }
    )


def build_default_capability_registry() -> InMemoryCapabilityRegistry:
    structure = CapabilityInputSlot(name="structure", accepted_object_types=["structure.crystal"])
    trajectory = CapabilityInputSlot(name="trajectory", accepted_object_types=["trajectory.atomic"])
    registry = InMemoryCapabilityRegistry()
    manifests = [
        *[_manifest(key, description, [key], [], [CapabilityOutputSlot(name="calculation", result_type=key)], key)
          for key, (_title, description) in PARAMETER_TOOLS.items()],
        _manifest("reference.periodic_table", "Draw a complete or filtered periodic table from versioned platform element references.",
                  ["reference.periodic_table"], [], [CapabilityOutputSlot(name="reference", result_type="reference.periodic_table")], "reference.periodic_table"),
        _manifest("reference.compare_elements", "Compare explicitly selected elements using one versioned reference property and its units.",
                  ["reference.compare_elements"], [], [CapabilityOutputSlot(name="reference", result_type="reference.compare_elements")], "reference.compare_elements"),
        _manifest("structure.rdf", "Compute a radial distribution function.", ["structure.compute_rdf"], [structure], [CapabilityOutputSlot(name="rdf", result_type="structure.rdf")], "structure.rdf"),
        _manifest("diffraction.theoretical_xrd", "Generate a theoretical XRD pattern.", ["diffraction.generate_theoretical_pattern"], [structure], [CapabilityOutputSlot(name="theoretical_xrd", result_type="diffraction.xrd.theoretical", scientific_object_type="diffraction.xrd.theoretical")], "structure.xrd", viewer_bindings=["scientific.xrd"], artifact_port_support=CapabilitySurfaceSupport.SUPPORTED),
        _manifest("diffraction.experimental_theoretical_comparison", "Compare experimental and theoretical XRD patterns.", ["diffraction.compare_experimental_theoretical"], [CapabilityInputSlot(name="experimental", accepted_object_types=["diffraction.xrd.experimental"]), CapabilityInputSlot(name="theoretical", accepted_object_types=["diffraction.xrd.theoretical"])], [CapabilityOutputSlot(name="comparison", result_type="diffraction.xrd.comparison")], "structure.experimental_xrd_comparison", artifact_port_support=CapabilitySurfaceSupport.REQUIRED),
        _suite_manifest(
            "ml.regression_evaluation",
            "Evaluate a materials regression result.",
            ["ml.evaluate_regression"],
            [CapabilityInputSlot(name="dataset", accepted_object_types=["materials.dataset", "materials.table"])],
            [CapabilityOutputSlot(name="evaluation", result_type="ml.regression.evaluation")],
            [
                "ml.basic_metrics",
                "ml.density_scatter",
                "ml.error_distribution",
                "ml.outlier_table",
                "ml.regression_evaluation",
            ],
        ),
        _manifest(
            "ml.uncertainty_evaluation",
            "Evaluate prediction uncertainty diagnostics for a materials table.",
            ["ml.evaluate_uncertainty"],
            [CapabilityInputSlot(name="dataset", accepted_object_types=["materials.dataset", "materials.table"])],
            [CapabilityOutputSlot(name="evaluation", result_type="ml.uncertainty.evaluation")],
            "ml.uncertainty_evaluation",
        ),
        _manifest(
            "ml.classification_evaluation",
            "Evaluate a materials classification result.",
            ["ml.evaluate_classification"],
            [CapabilityInputSlot(name="dataset", accepted_object_types=["materials.dataset", "materials.table"])],
            [CapabilityOutputSlot(name="evaluation", result_type="ml.classification.evaluation")],
            "ml.classification_evaluation",
        ),
        _manifest("trajectory.msd", "Compute mean-squared displacement.", ["trajectory.compute_msd"], [trajectory], [CapabilityOutputSlot(name="msd", result_type="trajectory.msd")], "trajectory.msd", artifact_port_support=CapabilitySurfaceSupport.SUPPORTED),
        # Diffusion is a strict derived-result capability.  Its executable
        # Adapter consumes one exact persisted MSD Artifact, not the original
        # trajectory alongside that Artifact.  The trajectory identity is
        # retained transitively by the MSD Artifact lineage and remains the
        # requirement subject used to derive the explicit fit window.
        _manifest("trajectory.diffusion", "Estimate diffusion from MSD evidence.", ["trajectory.estimate_diffusion"], [CapabilityInputSlot(name="msd", accepted_object_types=["trajectory.msd"])], [CapabilityOutputSlot(name="diffusion", result_type="trajectory.diffusion")], "trajectory.diffusion", artifact_port_support=CapabilitySurfaceSupport.REQUIRED),
        _manifest("phonon.band", "Normalize and inspect a phonon band.", ["phonon.inspect_band"], [CapabilityInputSlot(name="band", accepted_object_types=["phonon.band_structure"])], [CapabilityOutputSlot(name="band", result_type="phonon.band", scientific_object_type="phonon.band_structure")], "phonon.band", viewer_bindings=["scientific.phonon-band"], artifact_port_support=CapabilitySurfaceSupport.SUPPORTED),
        _manifest("phonon.dos", "Normalize and inspect a phonon DOS.", ["phonon.inspect_dos"], [CapabilityInputSlot(name="dos", accepted_object_types=["phonon.dos"])], [CapabilityOutputSlot(name="dos", result_type="phonon.dos", scientific_object_type="phonon.dos")], "phonon.dos", viewer_bindings=["scientific.phonon-dos"], artifact_port_support=CapabilitySurfaceSupport.SUPPORTED),
        _manifest("phonon.band_dos", "Compose compatible phonon band and DOS views.", ["phonon.compose_band_dos"], [CapabilityInputSlot(name="band", accepted_object_types=["phonon.band_structure"]), CapabilityInputSlot(name="dos", accepted_object_types=["phonon.dos"])], [CapabilityOutputSlot(name="combined", result_type="phonon.band_dos")], "phonon.band_dos", artifact_port_support=CapabilitySurfaceSupport.REQUIRED),
        _manifest(
            "structure.brillouin_zone",
            "Generate bounded reciprocal-lattice, Brillouin-zone, and high-symmetry-path context.",
            ["structure.inspect_brillouin_zone"],
            [structure],
            [CapabilityOutputSlot(name="zone", result_type="reciprocal.brillouin_zone")],
            "structure.brillouin_zone",
        ),
        _manifest("structure.coordination_hist", "Summarize distance-cutoff coordination distributions.", ["structure.inspect_coordination_hist"], [structure], [CapabilityOutputSlot(name="coordination", result_type="structure.coordination.hist")], "structure.coordination_hist"),
        # The generic coordination requirement is the canonical router
        # contract.  Keep the algorithm-specific requirements as stricter
        # aliases so either trusted implementation can satisfy a request that
        # has not selected an algorithm yet; the planner still chooses the
        # concrete CrystalNN/VoronoiNN tool from the user's goal.
        _manifest("structure.coordination_crystalnn", "Inspect CrystalNN coordination results.", ["structure.inspect_coordination", "structure.inspect_coordination_crystalnn"], [structure], [CapabilityOutputSlot(name="coordination", result_type="structure.coordination.crystalnn")], "structure.coordination_crystalnn", artifact_port_support=CapabilitySurfaceSupport.SUPPORTED),
        _manifest("structure.coordination_voronoinn", "Inspect VoronoiNN coordination results.", ["structure.inspect_coordination", "structure.inspect_coordination_voronoi"], [structure], [CapabilityOutputSlot(name="coordination", result_type="structure.coordination.voronoi")], "structure.coordination_voronoinn", artifact_port_support=CapabilitySurfaceSupport.SUPPORTED),
        _manifest("trajectory.rdf", "Compute a bounded RDF from an atomic trajectory.", ["trajectory.compute_rdf"], [trajectory], [CapabilityOutputSlot(name="rdf", result_type="trajectory.rdf")], "trajectory.rdf", artifact_port_support=CapabilitySurfaceSupport.SUPPORTED),
        _manifest("electronic.band_structure", "Inspect supplied electronic band data.", ["electronic.inspect_band"], [CapabilityInputSlot(name="band", accepted_object_types=["electronic.band_structure"])], [CapabilityOutputSlot(name="band", result_type="electronic.band_structure", scientific_object_type="electronic.band_structure")], "electronic.band_structure", viewer_bindings=["scientific.band-structure"], artifact_port_support=CapabilitySurfaceSupport.SUPPORTED),
        _manifest("electronic.dos", "Inspect supplied electronic DOS data.", ["electronic.inspect_dos"], [CapabilityInputSlot(name="dos", accepted_object_types=["electronic.dos"])], [CapabilityOutputSlot(name="dos", result_type="electronic.dos", scientific_object_type="electronic.dos")], "electronic.dos", viewer_bindings=["scientific.density-of-states"], artifact_port_support=CapabilitySurfaceSupport.SUPPORTED),
        _manifest(
            "volumetric.data",
            "Parse a bounded volumetric field into an authoritative scientific result.",
            ["volumetric.inspect"],
            [CapabilityInputSlot(name="volumetric", accepted_object_types=["volumetric.field", "volumetric.charge_density"])],
            [CapabilityOutputSlot(name="field", result_type="volumetric.field")],
            "structure.volumetric_data",
            artifact_port_support=CapabilitySurfaceSupport.SUPPORTED,
        ),
        _suite_manifest(
            "structure.summary",
            "Summarize authoritative composition, lattice, and symmetry facts for a crystal structure.",
            ["structure.inspect"],
            [structure],
            [CapabilityOutputSlot(name="summary", result_type="structure.summary")],
            ["structure.summary"],
            version="1.1",
        ),
        _suite_manifest(
            "structure.viewer_scene",
            "Build an inert structure viewer scene.",
            ["structure.inspect_view"],
            [
                CapabilityInputSlot(
                    name="structure",
                    accepted_object_types=["structure.crystal", "structure.atomic"],
                )
            ],
            [CapabilityOutputSlot(name="scene", result_type="structure.viewer_scene")],
            ["structure.viewer_3d"],
            version="1.1",
            viewer_bindings=["scientific.structure-3d"],
        ),
        _manifest(
            "trajectory.viewer_scene",
            "Build an inert trajectory viewer product from one validated atomic trajectory.",
            ["trajectory.inspect_view"],
            [trajectory],
            [
                CapabilityOutputSlot(name="trajectory", result_type="trajectory.viewer"),
                CapabilityOutputSlot(name="summary", result_type="trajectory.viewer.summary"),
                CapabilityOutputSlot(name="report", result_type="trajectory.viewer.report"),
                CapabilityOutputSlot(name="manifest", result_type="trajectory.viewer.manifest"),
            ],
            "structure.trajectory_viewer",
        ),
        _manifest("data.composition_space", "Explore an authorized composition-space projection.", ["data.explore_composition_space"], [CapabilityInputSlot(name="dataset", accepted_object_types=["materials.dataset", "materials.table"])], [CapabilityOutputSlot(name="space", result_type="data.composition_space")], "dataset.composition_space"),
        _manifest("data.materials_explorer", "Summarize an authorized materials dataset.", ["data.explore_materials"], [CapabilityInputSlot(name="dataset", accepted_object_types=["materials.dataset", "materials.table"])], [CapabilityOutputSlot(name="explorer", result_type="data.materials_explorer")], "dataset.materials_explorer"),
        _suite_manifest(
            "data.composition_analysis",
            "Summarize formulas, elements, periodic-table distributions, and chemical systems from one authorized materials table.",
            ["data.analyze_composition"],
            [
                CapabilityInputSlot(
                    name="dataset",
                    accepted_object_types=["materials.dataset", "materials.table"],
                )
            ],
            [
                CapabilityOutputSlot(
                    name="composition",
                    result_type="data.composition_analysis",
                )
            ],
            [
                "composition.chem_sys_sunburst",
                "composition.chem_sys_treemap",
                "composition.elements_hist",
                "composition.formula_statistics",
                "composition.ptable_heatmap",
                "composition.summary",
                "structure.composition_from_structure",
            ],
            priority=20,
        ),
        _suite_manifest(
            "data.table_analysis",
            "Summarize numeric columns and publish bounded distribution, correlation, histogram, and scatter products.",
            ["data.analyze_table"],
            [
                CapabilityInputSlot(
                    name="dataset",
                    accepted_object_types=["materials.dataset", "materials.table"],
                )
            ],
            [CapabilityOutputSlot(name="analysis", result_type="data.table_analysis")],
            [
                "table.distribution_summary",
                "table.numeric_summary",
                "viz.correlation",
                "viz.histogram",
                "viz.scatter",
            ],
            priority=20,
        ),
        *[
            _suite_manifest(
                f"structure.local_environment_{method}",
                f"Build local-environment geometry and coordination polyhedra from exact persisted {label} neighbors.",
                [f"structure.inspect_local_environment_{method}"],
                [structure],
                [CapabilityOutputSlot(name="local_environment", result_type="structure.local_environment.polyhedra")],
                [producer, "structure.local_environment_polyhedra"],
                dependency_from_tool={"structure.local_environment_polyhedra": producer},
            )
            for method, label, producer in (
                ("crystalnn", "CrystalNN", "structure.coordination_crystalnn"),
                ("voronoi", "VoronoiNN", "structure.coordination_voronoinn"),
            )
        ],
        _suite_manifest(
            "structure.coordination_analysis",
            "Compare CrystalNN and VoronoiNN coordination, summarize coordination distributions, and build bounded local-environment polyhedra.",
            [
                "structure.inspect_coordination",
                "structure.inspect_coordination_crystalnn",
                "structure.inspect_coordination_voronoi",
            ],
            [structure],
            [
                CapabilityOutputSlot(
                    name="coordination",
                    result_type="structure.coordination.analysis",
                )
            ],
            [
                "structure.coordination_crystalnn",
                "structure.coordination_hist",
                "structure.coordination_voronoinn",
                "structure.local_environment_polyhedra",
            ],
            priority=10,
            dependency_from_tool={
                "structure.local_environment_polyhedra": "structure.coordination_crystalnn"
            },
        ),
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
