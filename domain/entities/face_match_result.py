"""Domain entity representing a face matching result."""
from dataclasses import dataclass


@dataclass(frozen=True)
class FaceMatchResult:
    """Represents the domain result of comparing two faces.
    
    Attributes:
        matched: True if similarity score is greater than or equal to threshold.
        similarity_score: Cosine similarity score between the two face embeddings.
        threshold: The threshold value used to determine a match.
    """
    matched: bool
    similarity_score: float
    threshold: float
