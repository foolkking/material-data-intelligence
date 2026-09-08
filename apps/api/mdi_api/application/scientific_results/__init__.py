"""Scientific-result application entrypoints and ports."""
from .entrypoints import ScientificResultProjectorPort, project_queued_result
__all__ = ["ScientificResultProjectorPort", "project_queued_result"]
