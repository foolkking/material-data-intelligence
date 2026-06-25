"""Material file detection, parsing, normalization, and profiling."""

from .detector import detect_format
from .models import DetectedFormat, NormalizedObjectDraft, ParseResult
from .parsers import parse_dataset, parse_file
from .profile import build_data_profile

__all__ = [
    "DetectedFormat",
    "NormalizedObjectDraft",
    "ParseResult",
    "build_data_profile",
    "detect_format",
    "parse_dataset",
    "parse_file",
]

