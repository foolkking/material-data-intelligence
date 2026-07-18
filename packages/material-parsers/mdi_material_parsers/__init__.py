"""Material file detection, parsing, normalization, and profiling."""

from .detector import detect_format
from .models import DetectedFormat, NormalizedObjectDraft, ParseResult
from .parsers import parse_dataset, parse_file
from .profile import build_data_profile
from .trajectory import (
    ParsedTrajectory,
    TrajectoryParseError,
    detect_trajectory_format,
    parse_trajectory_file,
)
from .volumetric import (
    ParsedVolumetricSource,
    VolumetricParseError,
    detect_volumetric_format,
    parse_volumetric_file,
)

__all__ = [
    "DetectedFormat",
    "NormalizedObjectDraft",
    "ParseResult",
    "build_data_profile",
    "detect_format",
    "parse_dataset",
    "parse_file",
    "ParsedTrajectory",
    "TrajectoryParseError",
    "detect_trajectory_format",
    "parse_trajectory_file",
    "ParsedVolumetricSource",
    "VolumetricParseError",
    "detect_volumetric_format",
    "parse_volumetric_file",
]

