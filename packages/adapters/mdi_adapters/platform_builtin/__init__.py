"""Platform builtin and custom Plotly adapters."""

from .basic_metrics import BasicMetricsAdapter
from .error_distribution import ErrorDistributionAdapter
from .outlier_table import OutlierTableAdapter

__all__ = ["BasicMetricsAdapter", "ErrorDistributionAdapter", "OutlierTableAdapter"]
