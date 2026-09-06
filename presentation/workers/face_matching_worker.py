"""Background worker thread for running face comparison asynchronously."""
import logging
from PySide6.QtCore import QThread, Signal
from application.dto.comparison_result import ComparisonResultDTO
from application.use_cases.compare_faces import CompareFacesUseCase

logger = logging.getLogger(__name__)


class FaceMatchingWorker(QThread):
    """QThread worker to execute CompareFacesUseCase in background."""

    # Signal carrying the comparison result back to the main UI thread
    result_ready = Signal(ComparisonResultDTO)

    def __init__(self, use_case: CompareFacesUseCase, image_path1: str, image_path2: str) -> None:
        """Initialize worker with use case and target image paths.
        
        Args:
            use_case: Instance of CompareFacesUseCase.
            image_path1: Path to Face 1 image.
            image_path2: Path to Face 2 image.
        """
        super().__init__()
        self._use_case = use_case
        self._image_path1 = image_path1
        self._image_path2 = image_path2

    def run(self) -> None:
        """Executes the comparison in background thread."""
        logger.info("FaceMatchingWorker thread started execution.")
        try:
            result = self._use_case.execute(self._image_path1, self._image_path2)
        except Exception as e:
            logger.error(f"Error inside FaceMatchingWorker: {e}", exc_info=True)
            result = ComparisonResultDTO(
                success=False,
                error_message=f"Worker error: {str(e)}"
            )

        self.result_ready.emit(result)
        logger.info("FaceMatchingWorker thread finished execution.")
