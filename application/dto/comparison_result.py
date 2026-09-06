"""Data Transfer Object for face comparison response."""
from dataclasses import dataclass
from typing import Optional
from domain.entities.face_match_result import FaceMatchResult


@dataclass(frozen=True)
class ComparisonResultDTO:
    """Carries comparison outcome or error information to presentation layer.
    
    Attributes:
        success: True if the operation succeeded without processing errors.
        result: FaceMatchResult object if success is True, else None.
        error_message: Friendly error description if success is False, else None.
    """
    success: bool
    result: Optional[FaceMatchResult] = None
    error_message: Optional[str] = None
