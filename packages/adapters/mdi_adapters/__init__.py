"""Tool adapters for controlled pymatviz and MatterViz execution."""

from .base import BaseToolAdapter
from .context import ToolExecutionContext
from .errors import ToolExecutionError
from .executor import ToolExecutionResult, execute_tool_request
from .matterviz.structure_viewer_3d import StructureViewer3DAdapter
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
    StructureViewerExportPackageAdapter,
    StructureViewerSceneMetadataAdapter,
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
from .registry import ADAPTER_CLASSES, create_adapter, get_adapter_class

__all__ = [
    "ADAPTER_CLASSES",
    "BaseToolAdapter",
    "BasicMetricsAdapter",
    "ChemSysSunburstAdapter",
    "ChemSysTreemapAdapter",
    "CompositionSummaryAdapter",
    "CorrelationAdapter",
    "CoordinationHistAdapter",
    "DensityScatterAdapter",
    "ElementsHistAdapter",
    "ErrorDistributionAdapter",
    "FormulaStatisticsAdapter",
    "XrdPatternAdapter",
    "DistributionSummaryAdapter",
    "HistogramAdapter",
    "LatticeSummaryAdapter",
    "NumericSummaryAdapter",
    "OutlierTableAdapter",
    "PTableHeatmapAdapter",
    "RdfAdapter",
    "Structure3DAdapter",
    "SpacegroupSummaryAdapter",
    "StructureCompositionAdapter",
    "StructurePreviewMetadataAdapter",
    "StructureSummaryAdapter",
    "StructureViewerSceneAdapter",
    "StructureViewerExportPackageAdapter",
    "StructureViewerSceneMetadataAdapter",
    "StructureViewer3DAdapter",
    "ScatterAdapter",
    "ToolExecutionContext",
    "ToolExecutionError",
    "ToolExecutionResult",
    "create_adapter",
    "execute_tool_request",
    "get_adapter_class",
]
