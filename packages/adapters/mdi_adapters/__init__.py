"""Tool adapters for controlled pymatviz and MatterViz execution."""

from .base import BaseToolAdapter
from .context import ToolExecutionContext
from .errors import ToolExecutionError
from .executor import ToolExecutionResult, execute_tool_request
from .matterviz.structure_viewer_3d import StructureViewer3DAdapter
from .platform_builtin import BasicMetricsAdapter, ErrorDistributionAdapter, NumericSummaryAdapter, OutlierTableAdapter
from .pymatviz import ChemSysTreemapAdapter, CoordinationHistAdapter, DensityScatterAdapter, ElementsHistAdapter
from .pymatviz.ptable_heatmap import PTableHeatmapAdapter
from .pymatviz.structure_3d import Structure3DAdapter
from .registry import ADAPTER_CLASSES, create_adapter, get_adapter_class

__all__ = [
    "ADAPTER_CLASSES",
    "BaseToolAdapter",
    "BasicMetricsAdapter",
    "ChemSysTreemapAdapter",
    "CoordinationHistAdapter",
    "DensityScatterAdapter",
    "ElementsHistAdapter",
    "ErrorDistributionAdapter",
    "NumericSummaryAdapter",
    "OutlierTableAdapter",
    "PTableHeatmapAdapter",
    "Structure3DAdapter",
    "StructureViewer3DAdapter",
    "ToolExecutionContext",
    "ToolExecutionError",
    "ToolExecutionResult",
    "create_adapter",
    "execute_tool_request",
    "get_adapter_class",
]
