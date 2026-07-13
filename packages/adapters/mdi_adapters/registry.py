from __future__ import annotations

from .base import BaseToolAdapter
from .platform_builtin import (
    BasicMetricsAdapter,
    CompositionSummaryAdapter,
    CorrelationAdapter,
    DistributionSummaryAdapter,
    ErrorDistributionAdapter,
    HistogramAdapter,
    LatticeSummaryAdapter,
    NumericSummaryAdapter,
    OutlierTableAdapter,
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
)
from .pymatviz import (
    ChemSysSunburstAdapter,
    ChemSysTreemapAdapter,
    CoordinationHistAdapter,
    DensityScatterAdapter,
    ElementsHistAdapter,
    FormulaStatisticsAdapter,
    RdfAdapter,
    XrdPatternAdapter,
)
from .pymatviz.ptable_heatmap import PTableHeatmapAdapter
from .pymatviz.structure_3d import Structure3DAdapter


ADAPTER_CLASSES: dict[str, type[BaseToolAdapter]] = {
    BasicMetricsAdapter.__name__: BasicMetricsAdapter,
    ChemSysSunburstAdapter.__name__: ChemSysSunburstAdapter,
    ChemSysTreemapAdapter.__name__: ChemSysTreemapAdapter,
    CompositionSummaryAdapter.__name__: CompositionSummaryAdapter,
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
    PTableHeatmapAdapter.__name__: PTableHeatmapAdapter,
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
    XrdPatternAdapter.__name__: XrdPatternAdapter,
    ScatterAdapter.__name__: ScatterAdapter,
}


def get_adapter_class(adapter_name: str) -> type[BaseToolAdapter]:
    return ADAPTER_CLASSES[adapter_name]


def create_adapter(adapter_name: str) -> BaseToolAdapter:
    return get_adapter_class(adapter_name)()
