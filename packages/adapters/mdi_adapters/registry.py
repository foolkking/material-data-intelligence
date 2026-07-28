from __future__ import annotations

from .base import BaseToolAdapter
from .platform_builtin import (
    BasicMetricsAdapter,
    BrillouinZoneAdapter,
    ClassificationEvaluationAdapter,
    CompositionSpaceAdapter,
    CompositionSummaryAdapter,
    DatasetMaterialsExplorerAdapter,
    CorrelationAdapter,
    DistributionSummaryAdapter,
    ErrorDistributionAdapter,
    HistogramAdapter,
    LatticeSummaryAdapter,
    NumericSummaryAdapter,
    OutlierTableAdapter,
    RegressionEvaluationAdapter,
    ScatterAdapter,
    SpacegroupSummaryAdapter,
    StructureCompositionAdapter,
    StructurePreviewMetadataAdapter,
    StructureSummaryAdapter,
    StructureViewerSceneAdapter,
    StructureViewer3DAdapter,
    StructureViewerExportPackageAdapter,
    StructureViewerSceneMetadataAdapter,
    TrajectoryImportAdapter,
    TrajectoryViewerAdapter,
    UncertaintyEvaluationAdapter,
    VolumetricDataAdapter,
)
from .pymatviz import (
    ChemSysSunburstAdapter,
    ChemSysTreemapAdapter,
    CoordinationHistAdapter,
    DensityScatterAdapter,
    ElementsHistAdapter,
    FormulaStatisticsAdapter,
    PhononBandAdapter,
    PhononBandDosAdapter,
    PhononAnimationAdapter,
    PhononDosAdapter,
    RdfAdapter,
    XrdPatternAdapter,
)
from .pymatviz.ptable_heatmap import PTableHeatmapAdapter
from .pymatviz.structure_3d import Structure3DAdapter


ADAPTER_CLASSES: dict[str, type[BaseToolAdapter]] = {
    BasicMetricsAdapter.__name__: BasicMetricsAdapter,
    BrillouinZoneAdapter.__name__: BrillouinZoneAdapter,
    ClassificationEvaluationAdapter.__name__: ClassificationEvaluationAdapter,
    CompositionSpaceAdapter.__name__: CompositionSpaceAdapter,
    ChemSysSunburstAdapter.__name__: ChemSysSunburstAdapter,
    ChemSysTreemapAdapter.__name__: ChemSysTreemapAdapter,
    CompositionSummaryAdapter.__name__: CompositionSummaryAdapter,
    DatasetMaterialsExplorerAdapter.__name__: DatasetMaterialsExplorerAdapter,
    CorrelationAdapter.__name__: CorrelationAdapter,
    CoordinationHistAdapter.__name__: CoordinationHistAdapter,
    DensityScatterAdapter.__name__: DensityScatterAdapter,
    DistributionSummaryAdapter.__name__: DistributionSummaryAdapter,
    ElementsHistAdapter.__name__: ElementsHistAdapter,
    ErrorDistributionAdapter.__name__: ErrorDistributionAdapter,
    FormulaStatisticsAdapter.__name__: FormulaStatisticsAdapter,
    HistogramAdapter.__name__: HistogramAdapter,
    LatticeSummaryAdapter.__name__: LatticeSummaryAdapter,
    NumericSummaryAdapter.__name__: NumericSummaryAdapter,
    OutlierTableAdapter.__name__: OutlierTableAdapter,
    RegressionEvaluationAdapter.__name__: RegressionEvaluationAdapter,
    PTableHeatmapAdapter.__name__: PTableHeatmapAdapter,
    PhononBandAdapter.__name__: PhononBandAdapter,
    PhononBandDosAdapter.__name__: PhononBandDosAdapter,
    PhononAnimationAdapter.__name__: PhononAnimationAdapter,
    PhononDosAdapter.__name__: PhononDosAdapter,
    RdfAdapter.__name__: RdfAdapter,
    Structure3DAdapter.__name__: Structure3DAdapter,
    SpacegroupSummaryAdapter.__name__: SpacegroupSummaryAdapter,
    StructureCompositionAdapter.__name__: StructureCompositionAdapter,
    StructurePreviewMetadataAdapter.__name__: StructurePreviewMetadataAdapter,
    StructureSummaryAdapter.__name__: StructureSummaryAdapter,
    StructureViewerSceneAdapter.__name__: StructureViewerSceneAdapter,
    StructureViewerExportPackageAdapter.__name__: StructureViewerExportPackageAdapter,
    StructureViewerSceneMetadataAdapter.__name__: StructureViewerSceneMetadataAdapter,
    StructureViewer3DAdapter.__name__: StructureViewer3DAdapter,
    TrajectoryImportAdapter.__name__: TrajectoryImportAdapter,
    TrajectoryViewerAdapter.__name__: TrajectoryViewerAdapter,
    UncertaintyEvaluationAdapter.__name__: UncertaintyEvaluationAdapter,
    VolumetricDataAdapter.__name__: VolumetricDataAdapter,
    XrdPatternAdapter.__name__: XrdPatternAdapter,
    ScatterAdapter.__name__: ScatterAdapter,
}


def get_adapter_class(adapter_name: str) -> type[BaseToolAdapter]:
    return ADAPTER_CLASSES[adapter_name]


def create_adapter(adapter_name: str) -> BaseToolAdapter:
    return get_adapter_class(adapter_name)()
