from __future__ import annotations

from .base import BaseToolAdapter
from .matterviz.structure_viewer_3d import StructureViewer3DAdapter
from .platform_builtin import (
    BasicMetricsAdapter,
    CompositionSummaryAdapter,
    CorrelationAdapter,
    DistributionSummaryAdapter,
    ErrorDistributionAdapter,
    HistogramAdapter,
    NumericSummaryAdapter,
    OutlierTableAdapter,
    ScatterAdapter,
)
from .pymatviz import (
    ChemSysSunburstAdapter,
    ChemSysTreemapAdapter,
    CoordinationHistAdapter,
    DensityScatterAdapter,
    ElementsHistAdapter,
    FormulaStatisticsAdapter,
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
    NumericSummaryAdapter.__name__: NumericSummaryAdapter,
    OutlierTableAdapter.__name__: OutlierTableAdapter,
    PTableHeatmapAdapter.__name__: PTableHeatmapAdapter,
    Structure3DAdapter.__name__: Structure3DAdapter,
    StructureViewer3DAdapter.__name__: StructureViewer3DAdapter,
    ScatterAdapter.__name__: ScatterAdapter,
}


def get_adapter_class(adapter_name: str) -> type[BaseToolAdapter]:
    return ADAPTER_CLASSES[adapter_name]


def create_adapter(adapter_name: str) -> BaseToolAdapter:
    return get_adapter_class(adapter_name)()
