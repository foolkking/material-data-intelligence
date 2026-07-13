"""Platform builtin and custom Plotly adapters."""

from .basic_metrics import BasicMetricsAdapter
from .composition_summary import CompositionSummaryAdapter
from .error_distribution import ErrorDistributionAdapter
from .numeric_summary import NumericSummaryAdapter
from .outlier_table import OutlierTableAdapter
from .structure import (
    LatticeSummaryAdapter,
    SpacegroupSummaryAdapter,
    StructureCompositionAdapter,
    StructurePreviewMetadataAdapter,
    StructureSummaryAdapter,
    StructureViewerSceneAdapter,
    StructureViewer3DAdapter,
    StructureViewerExportPackageAdapter,
    StructureViewerSceneMetadataAdapter,
)
from .table_distribution import DistributionSummaryAdapter
from .trajectory import (
    TRAJECTORY_VIEWER_BUDGETS,
    TRAJECTORY_VIEWER_CAPABILITIES,
    TRAJECTORY_VIEWER_TOOL_ID,
    TrajectoryImportAdapter,
    TrajectoryViewerAdapter,
)
from .viz import CorrelationAdapter, HistogramAdapter, ScatterAdapter

__all__ = [
    "BasicMetricsAdapter",
    "CompositionSummaryAdapter",
    "CorrelationAdapter",
    "DistributionSummaryAdapter",
    "ErrorDistributionAdapter",
    "HistogramAdapter",
    "LatticeSummaryAdapter",
    "NumericSummaryAdapter",
    "OutlierTableAdapter",
    "ScatterAdapter",
    "SpacegroupSummaryAdapter",
    "StructureCompositionAdapter",
    "StructurePreviewMetadataAdapter",
    "StructureSummaryAdapter",
    "StructureViewerSceneAdapter",
    "StructureViewer3DAdapter",
    "StructureViewerExportPackageAdapter",
    "StructureViewerSceneMetadataAdapter",
    "TrajectoryImportAdapter",
    "TRAJECTORY_VIEWER_BUDGETS",
    "TRAJECTORY_VIEWER_CAPABILITIES",
    "TRAJECTORY_VIEWER_TOOL_ID",
    "TrajectoryViewerAdapter",
]
