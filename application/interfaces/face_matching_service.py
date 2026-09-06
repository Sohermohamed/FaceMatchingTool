"""Abstract interface for face matching service."""
from abc import ABC, abstractmethod
from application.dto.comparison_result import ComparisonResultDTO


class IFaceMatchingService(ABC):
    """Abstract interface defining face comparison capabilities."""

    @abstractmethod
    def compare_faces(self, image_path1: str, image_path2: str) -> ComparisonResultDTO:
        """Compares two face images given their file paths.
        
        Args:
            image_path1: Path to the first image file.
            image_path2: Path to the second image file.
            
        Returns:
            ComparisonResultDTO containing the comparison result or error details.
        """
        pass
