"""Interpretation compatibility package."""
from .schemas import ScientificFinding, ScientificInterpretationOutput
from .service import InterpretationFailure, ScientificInterpretationService
__all__ = ["InterpretationFailure", "ScientificFinding", "ScientificInterpretationOutput", "ScientificInterpretationService"]
