"""Platform builtin and custom Plotly adapters."""

from .basic_metrics import BasicMetricsAdapter
from .composition_summary import CompositionSummaryAdapter
from .error_distribution import ErrorDistributionAdapter
from .numeric_summary import NumericSummaryAdapter
from .outlier_table import OutlierTableAdapter
from .table_distribution import DistributionSummaryAdapter
from .viz import CorrelationAdapter, HistogramAdapter, ScatterAdapter

__all__ = [
    "BasicMetricsAdapter",
    "CompositionSummaryAdapter",
    "CorrelationAdapter",
    "DistributionSummaryAdapter",
    "ErrorDistributionAdapter",
    "HistogramAdapter",
    "NumericSummaryAdapter",
    "OutlierTableAdapter",
    "ScatterAdapter",
]
