"""Use case for comparing two face images."""
import os
import logging
from application.dto.comparison_result import ComparisonResultDTO
from application.interfaces.face_matching_service import IFaceMatchingService
from config import SUPPORTED_EXTENSIONS

logger = logging.getLogger(__name__)


class CompareFacesUseCase:
    """Use case responsible for validating inputs and delegating face comparison."""

    def __init__(self, face_matching_service: IFaceMatchingService) -> None:
        """Initialize the use case with a face matching service instance.
        
        Args:
            face_matching_service: Implementation of IFaceMatchingService.
        """
        self._face_matching_service = face_matching_service

    def execute(self, image_path1: str, image_path2: str) -> ComparisonResultDTO:
        """Validates input image paths and executes face comparison.
        
        Args:
            image_path1: Path to Face 1 image file.
            image_path2: Path to Face 2 image file.
            
        Returns:
            ComparisonResultDTO containing result or validation error.
        """
        logger.info(f"Executing CompareFacesUseCase for '{image_path1}' and '{image_path2}'")

        # Validate inputs provided
        if not image_path1 or not image_path2:
            return ComparisonResultDTO(
                success=False,
                error_message="Please select both Face 1 and Face 2 images before comparing."
            )

        # Validate file existence
        if not os.path.exists(image_path1):
            return ComparisonResultDTO(
                success=False,
                error_message=f"Face 1 image file not found: {image_path1}"
            )

        if not os.path.exists(image_path2):
            return ComparisonResultDTO(
                success=False,
                error_message=f"Face 2 image file not found: {image_path2}"
            )

        # Validate supported file extensions
        ext1 = os.path.splitext(image_path1)[1].lower()
        ext2 = os.path.splitext(image_path2)[1].lower()

        if ext1 not in SUPPORTED_EXTENSIONS:
            return ComparisonResultDTO(
                success=False,
                error_message=f"Unsupported format for Face 1: '{ext1}'. Supported: {', '.join(SUPPORTED_EXTENSIONS)}"
            )

        if ext2 not in SUPPORTED_EXTENSIONS:
            return ComparisonResultDTO(
                success=False,
                error_message=f"Unsupported format for Face 2: '{ext2}'. Supported: {', '.join(SUPPORTED_EXTENSIONS)}"
            )

        # Delegate to face matching service
        try:
            return self._face_matching_service.compare_faces(image_path1, image_path2)
        except Exception as e:
            logger.error(f"Unexpected error during face comparison: {e}", exc_info=True)
            return ComparisonResultDTO(
                success=False,
                error_message=f"An unexpected error occurred during face comparison: {str(e)}"
            )
