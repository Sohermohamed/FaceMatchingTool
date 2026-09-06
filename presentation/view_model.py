"""ViewModel for managing presentation state and orchestrating face comparison."""
import logging
from typing import Optional
from PySide6.QtCore import QObject, Signal
from application.use_cases.compare_faces import CompareFacesUseCase
from application.dto.comparison_result import ComparisonResultDTO
from presentation.workers.face_matching_worker import FaceMatchingWorker

logger = logging.getLogger(__name__)


class FaceMatchingViewModel(QObject):
    """ViewModel holding UI state and managing asynchronous comparison workers."""

    # UI State Signals
    state_changed = Signal()
    comparison_started = Signal()
    comparison_finished = Signal(ComparisonResultDTO)

    def __init__(self, compare_faces_use_case: CompareFacesUseCase) -> None:
        """Initialize ViewModel with CompareFacesUseCase.
        
        Args:
            compare_faces_use_case: The use case instance.
        """
        super().__init__()
        self._compare_faces_use_case = compare_faces_use_case

        self._image_path1: Optional[str] = None
        self._image_path2: Optional[str] = None
        self._is_processing: bool = False
        self._last_result: Optional[ComparisonResultDTO] = None
        self._worker: Optional[FaceMatchingWorker] = None

    @property
    def image_path1(self) -> Optional[str]:
        return self._image_path1

    @image_path1.setter
    def image_path1(self, path: str) -> None:
        self._image_path1 = path
        self._last_result = None
        self.state_changed.emit()

    @property
    def image_path2(self) -> Optional[str]:
        return self._image_path2

    @image_path2.setter
    def image_path2(self, path: str) -> None:
        self._image_path2 = path
        self._last_result = None
        self.state_changed.emit()

    @property
    def is_processing(self) -> bool:
        return self._is_processing

    @property
    def can_compare(self) -> bool:
        return bool(self._image_path1 and self._image_path2 and not self._is_processing)

    @property
    def last_result(self) -> Optional[ComparisonResultDTO]:
        return self._last_result

    def compare_faces(self) -> None:
        """Triggers asynchronous comparison of selected images."""
        if not self.can_compare:
            logger.warning("Attempted to start comparison when can_compare is False.")
            return

        self._is_processing = True
        self.comparison_started.emit()

        # Create and start worker thread
        self._worker = FaceMatchingWorker(
            use_case=self._compare_faces_use_case,
            image_path1=self._image_path1,
            image_path2=self._image_path2
        )
        self._worker.result_ready.connect(self._on_comparison_complete)
        self._worker.start()

    def _on_comparison_complete(self, result: ComparisonResultDTO) -> None:
        """Slot called when worker finishes execution.
        
        Args:
            result: ComparisonResultDTO emitted by worker.
        """
        self._is_processing = False
        self._last_result = result
        self.comparison_finished.emit(result)
        self.state_changed.emit()

        if self._worker is not None:
            self._worker.quit()
            self._worker.wait()
            self._worker = None
