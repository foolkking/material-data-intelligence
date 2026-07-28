"""Platform builtin and custom Plotly adapters."""

from .basic_metrics import BasicMetricsAdapter
from .brillouin_zone import (
    BRILLOUIN_ZONE_ADAPTER_VERSION,
    BRILLOUIN_ZONE_TOOL_ID,
    BrillouinZoneAdapter,
)
from .composition_summary import CompositionSummaryAdapter
from .composition_space import (
    COMPOSITION_SPACE_SCHEMA_VERSION,
    COMPOSITION_SPACE_TOOL_ID,
    CompositionSpaceAdapter,
)
from .dataset_materials_explorer import (
    DATASET_EXPLORER_SCHEMA_VERSION,
    DATASET_EXPLORER_TOOL_ID,
    DatasetMaterialsExplorerAdapter,
)
from .error_distribution import ErrorDistributionAdapter
from .materials_ml_evaluation import (
    CLASSIFICATION_SCHEMA_VERSION,
    CLASSIFICATION_TOOL_ID,
    REGRESSION_SCHEMA_VERSION,
    REGRESSION_TOOL_ID,
    UNCERTAINTY_SCHEMA_VERSION,
    UNCERTAINTY_TOOL_ID,
    ClassificationEvaluationAdapter,
    RegressionEvaluationAdapter,
    UncertaintyEvaluationAdapter,
    binary_roc_pr,
    classification_metric_values,
    regression_metric_values,
)
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
from .volumetric import (
    VOLUMETRIC_ADAPTER_VERSION,
    VOLUMETRIC_ARTIFACT_TYPES,
    VOLUMETRIC_TOOL_ID,
    VolumetricDataAdapter,
)
from .viz import CorrelationAdapter, HistogramAdapter, ScatterAdapter

__all__ = [
    "BasicMetricsAdapter",
    "BRILLOUIN_ZONE_ADAPTER_VERSION",
    "BRILLOUIN_ZONE_TOOL_ID",
    "BrillouinZoneAdapter",
    "CompositionSummaryAdapter",
    "COMPOSITION_SPACE_SCHEMA_VERSION",
    "COMPOSITION_SPACE_TOOL_ID",
    "CompositionSpaceAdapter",
    "CLASSIFICATION_SCHEMA_VERSION",
    "CLASSIFICATION_TOOL_ID",
    "ClassificationEvaluationAdapter",
    "DATASET_EXPLORER_SCHEMA_VERSION",
    "DATASET_EXPLORER_TOOL_ID",
    "DatasetMaterialsExplorerAdapter",
    "CorrelationAdapter",
    "DistributionSummaryAdapter",
    "ErrorDistributionAdapter",
    "HistogramAdapter",
    "LatticeSummaryAdapter",
    "NumericSummaryAdapter",
    "OutlierTableAdapter",
    "REGRESSION_SCHEMA_VERSION",
    "REGRESSION_TOOL_ID",
    "RegressionEvaluationAdapter",
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
    "UNCERTAINTY_SCHEMA_VERSION",
    "UNCERTAINTY_TOOL_ID",
    "UncertaintyEvaluationAdapter",
    "VOLUMETRIC_ADAPTER_VERSION",
    "VOLUMETRIC_ARTIFACT_TYPES",
    "VOLUMETRIC_TOOL_ID",
    "VolumetricDataAdapter",
    "binary_roc_pr",
    "classification_metric_values",
    "regression_metric_values",
]
