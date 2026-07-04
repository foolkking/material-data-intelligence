from __future__ import annotations

from .base import BaseToolAdapter
from .matterviz.structure_viewer_3d import StructureViewer3DAdapter
from .platform_builtin import BasicMetricsAdapter, ErrorDistributionAdapter, NumericSummaryAdapter, OutlierTableAdapter
from .pymatviz import ChemSysTreemapAdapter, CoordinationHistAdapter, DensityScatterAdapter, ElementsHistAdapter
from .pymatviz.ptable_heatmap import PTableHeatmapAdapter
from .pymatviz.structure_3d import Structure3DAdapter


ADAPTER_CLASSES: dict[str, type[BaseToolAdapter]] = {
    BasicMetricsAdapter.__name__: BasicMetricsAdapter,
    ChemSysTreemapAdapter.__name__: ChemSysTreemapAdapter,
    CoordinationHistAdapter.__name__: CoordinationHistAdapter,
    DensityScatterAdapter.__name__: DensityScatterAdapter,
    ElementsHistAdapter.__name__: ElementsHistAdapter,
    ErrorDistributionAdapter.__name__: ErrorDistributionAdapter,
    NumericSummaryAdapter.__name__: NumericSummaryAdapter,
    OutlierTableAdapter.__name__: OutlierTableAdapter,
    PTableHeatmapAdapter.__name__: PTableHeatmapAdapter,
    Structure3DAdapter.__name__: Structure3DAdapter,
    StructureViewer3DAdapter.__name__: StructureViewer3DAdapter,
}


def get_adapter_class(adapter_name: str) -> type[BaseToolAdapter]:
    return ADAPTER_CLASSES[adapter_name]


def create_adapter(adapter_name: str) -> BaseToolAdapter:
    return get_adapter_class(adapter_name)()
