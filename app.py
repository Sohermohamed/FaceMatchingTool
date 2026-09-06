"""Application entry point and Composition Root for FaceMatchingTool."""
import sys
import logging

from PySide6.QtWidgets import QApplication

from infrastructure.image_processing.image_loader import ImageLoader
from infrastructure.face_recognition.insightface_matcher import InsightFaceFaceMatchingService
from application.use_cases.compare_faces import CompareFacesUseCase
from presentation.view_model import FaceMatchingViewModel
from presentation.main_window import MainWindow
from config import DEFAULT_SIMILARITY_THRESHOLD, MODEL_NAME, DET_SIZE


def configure_logging() -> None:
    """Configures application-wide logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def main() -> int:
    """Entry point initializing dependencies and starting PySide6 application."""
    configure_logging()
    logger = logging.getLogger("FaceMatchingTool")
    logger.info("Starting FaceMatchingTool application...")

    # Initialize PySide6 QApplication
    app = QApplication(sys.argv)

    try:
        # Manual Dependency Injection (Composition Root)
        logger.info("Constructing infrastructure dependencies...")
        image_loader = ImageLoader()
        
        # Initialize InsightFace model once
        matching_service = InsightFaceFaceMatchingService(
            threshold=DEFAULT_SIMILARITY_THRESHOLD,
            model_name=MODEL_NAME,
            det_size=DET_SIZE,
            image_loader=image_loader
        )

        logger.info("Constructing application use cases...")
        compare_use_case = CompareFacesUseCase(face_matching_service=matching_service)

        logger.info("Constructing presentation ViewModel and MainWindow...")
        view_model = FaceMatchingViewModel(compare_faces_use_case=compare_use_case)
        main_window = MainWindow(view_model=view_model)

        main_window.show()
        logger.info("FaceMatchingTool desktop interface launched successfully.")

        return app.exec()
    except Exception as e:
        logger.critical(f"Unhandled initialization error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
