"""PySide6 main window interface for FaceMatchingTool."""
import os
import logging
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QIcon, QFont
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QFrame, QGroupBox,
    QSizePolicy, QGraphicsDropShadowEffect
)
from presentation.view_model import FaceMatchingViewModel
from application.dto.comparison_result import ComparisonResultDTO
from config import SUPPORTED_EXTENSIONS

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main window for the FaceMatchingTool application."""

    def __init__(self, view_model: FaceMatchingViewModel) -> None:
        """Initialize MainWindow with ViewModel.
        
        Args:
            view_model: Instance of FaceMatchingViewModel.
        """
        super().__init__()
        self._vm = view_model

        self.setWindowTitle("FaceMatchingTool - InsightFace Verification")
        self.setMinimumSize(950, 760)
        self.resize(1020, 800)

        # Apply custom application stylesheet
        self._apply_stylesheet()

        # Build UI layout
        self._init_ui()

        # Connect ViewModel signals
        self._vm.state_changed.connect(self._update_ui_state)
        self._vm.comparison_started.connect(self._on_comparison_started)
        self._vm.comparison_finished.connect(self._on_comparison_finished)

        # Initial UI update
        self._update_ui_state()

    def _init_ui(self) -> None:
        """Builds the main user interface layout."""
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(28, 20, 28, 20)
        main_layout.setSpacing(16)

        # -------------------------------------------------------------
        # Header Section
        # -------------------------------------------------------------
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)

        title_label = QLabel("Face Matching Tool")
        title_label.setObjectName("HeaderTitle")
        title_label.setAlignment(Qt.AlignCenter)

        subtitle_label = QLabel("AI-Powered Face Comparison & Similarity Verification")
        subtitle_label.setObjectName("HeaderSubtitle")
        subtitle_label.setAlignment(Qt.AlignCenter)

        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        main_layout.addLayout(header_layout)

        # -------------------------------------------------------------
        # Side-by-Side Face Preview Cards Section
        # -------------------------------------------------------------
        faces_layout = QHBoxLayout()
        faces_layout.setSpacing(24)

        # Face 1 Card
        self._face1_card, self._preview1_label, self._select1_btn, self._path1_label = (
            self._create_face_card("FACE 1", self._on_select_face1)
        )
        faces_layout.addWidget(self._face1_card, 1)

        # Face 2 Card
        self._face2_card, self._preview2_label, self._select2_btn, self._path2_label = (
            self._create_face_card("FACE 2", self._on_select_face2)
        )
        faces_layout.addWidget(self._face2_card, 1)

        main_layout.addLayout(faces_layout, 1)

        # -------------------------------------------------------------
        # Action & Comparison Controls Section
        # -------------------------------------------------------------
        action_layout = QVBoxLayout()
        action_layout.setAlignment(Qt.AlignCenter)
        action_layout.setSpacing(8)

        self._compare_btn = QPushButton("Compare Faces")
        self._compare_btn.setObjectName("CompareButton")
        self._compare_btn.setMinimumSize(220, 48)
        self._compare_btn.setCursor(Qt.PointingHandCursor)
        self._compare_btn.clicked.connect(self._vm.compare_faces)

        self._status_label = QLabel("")
        self._status_label.setObjectName("StatusLabel")
        self._status_label.setAlignment(Qt.AlignCenter)

        action_layout.addWidget(self._compare_btn, 0, Qt.AlignCenter)
        action_layout.addWidget(self._status_label, 0, Qt.AlignCenter)

        main_layout.addLayout(action_layout)

        # -------------------------------------------------------------
        # Results Display Card Section
        # -------------------------------------------------------------
        self._result_card = QFrame()
        self._result_card.setObjectName("ResultCard")
        result_card_layout = QVBoxLayout(self._result_card)
        result_card_layout.setContentsMargins(24, 16, 24, 16)
        result_card_layout.setSpacing(10)

        self._badge_label = QLabel("READY")
        self._badge_label.setObjectName("ResultBadgePlaceholder")
        self._badge_label.setAlignment(Qt.AlignCenter)

        self._score_label = QLabel("")
        self._score_label.setObjectName("ScoreLabel")
        self._score_label.setAlignment(Qt.AlignCenter)
        self._score_label.setVisible(False)

        self._error_label = QLabel("")
        self._error_label.setObjectName("ErrorLabel")
        self._error_label.setAlignment(Qt.AlignCenter)
        self._error_label.setWordWrap(True)
        self._error_label.setVisible(False)

        result_card_layout.addWidget(self._badge_label, 0, Qt.AlignCenter)
        result_card_layout.addWidget(self._score_label, 0, Qt.AlignCenter)
        result_card_layout.addWidget(self._error_label)

        main_layout.addWidget(self._result_card)

    def _create_face_card(self, title: str, on_select_callback) -> tuple[QFrame, QLabel, QPushButton, QLabel]:
        """Helper to construct a styled face preview card."""
        card = QFrame()
        card.setObjectName("FaceCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # Card Title
        card_title = QLabel(title)
        card_title.setObjectName("CardTitle")
        card_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(card_title)

        # Preview Container Frame
        preview_frame = QFrame()
        preview_frame.setObjectName("PreviewFrame")
        preview_frame.setMinimumHeight(220)
        preview_layout = QVBoxLayout(preview_frame)
        preview_layout.setContentsMargins(0, 0, 0, 0)

        preview_label = QLabel("No Image Selected")
        preview_label.setObjectName("PreviewLabel")
        preview_label.setAlignment(Qt.AlignCenter)
        preview_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        preview_layout.addWidget(preview_label)

        layout.addWidget(preview_frame, 1)

        # Image File Path Label
        path_label = QLabel("No file selected")
        path_label.setObjectName("PathLabel")
        path_label.setAlignment(Qt.AlignCenter)
        path_label.setWordWrap(True)
        layout.addWidget(path_label)

        # Select Image Button
        select_btn = QPushButton(f"Select {title}")
        select_btn.setObjectName("SelectButton")
        select_btn.setMinimumHeight(38)
        select_btn.setCursor(Qt.PointingHandCursor)
        select_btn.clicked.connect(on_select_callback)
        layout.addWidget(select_btn)

        return card, preview_label, select_btn, path_label

    def _on_select_face1(self) -> None:
        """Handles selecting Face 1 image via file dialog."""
        file_path = self._open_file_dialog("Select Face 1 Image")
        if file_path:
            self._vm.image_path1 = file_path
            self._update_preview(self._preview1_label, self._path1_label, file_path)

    def _on_select_face2(self) -> None:
        """Handles selecting Face 2 image via file dialog."""
        file_path = self._open_file_dialog("Select Face 2 Image")
        if file_path:
            self._vm.image_path2 = file_path
            self._update_preview(self._preview2_label, self._path2_label, file_path)

    def _open_file_dialog(self, dialog_title: str) -> str:
        """Opens a file dialog for image selection."""
        ext_filter = "Image Files (" + " ".join(f"*{ext}" for ext in SUPPORTED_EXTENSIONS) + ")"
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            dialog_title,
            "",
            f"{ext_filter};;All Files (*.*)"
        )
        return file_path

    def _update_preview(self, label: QLabel, path_label: QLabel, image_path: str) -> None:
        """Loads and displays image preview preserving aspect ratio."""
        if not image_path or not os.path.exists(image_path):
            label.setText("No Image Selected")
            path_label.setText("No file selected")
            return

        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            label.setText("Failed to load image preview")
            path_label.setText(os.path.basename(image_path))
            return

        # Scale image preserving aspect ratio
        scaled_pixmap = pixmap.scaled(
            label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        label.setPixmap(scaled_pixmap)
        path_label.setText(os.path.basename(image_path))

    def resizeEvent(self, event) -> None:
        """Re-scales preview pixmaps when window size changes."""
        super().resizeEvent(event)
        if self._vm.image_path1:
            self._update_preview(self._preview1_label, self._path1_label, self._vm.image_path1)
        if self._vm.image_path2:
            self._update_preview(self._preview2_label, self._path2_label, self._vm.image_path2)

    def _update_ui_state(self) -> None:
        """Updates control availability based on ViewModel state."""
        self._compare_btn.setEnabled(self._vm.can_compare)

        if not self._vm.is_processing:
            if not self._vm.last_result:
                self._status_label.setText("")

    def _on_comparison_started(self) -> None:
        """UI updates when background comparison starts."""
        self._compare_btn.setEnabled(False)
        self._select1_btn.setEnabled(False)
        self._select2_btn.setEnabled(False)
        self._compare_btn.setText("Comparing...")
        self._status_label.setText("Processing InsightFace face detection & feature extraction...")
        self._error_label.setVisible(False)
        self._badge_label.setText("RUNNING")
        self._badge_label.setObjectName("ResultBadgePlaceholder")
        self._badge_label.setStyle(self._badge_label.style())

    def _on_comparison_finished(self, result: ComparisonResultDTO) -> None:
        """UI updates when background comparison completes."""
        self._compare_btn.setEnabled(True)
        self._select1_btn.setEnabled(True)
        self._select2_btn.setEnabled(True)
        self._compare_btn.setText("Compare Faces")
        self._status_label.setText("")

        if result.success and result.result:
            res = result.result
            self._error_label.setVisible(False)
            self._score_label.setVisible(False)

            if res.matched:
                self._badge_label.setText("MATCH")
                self._badge_label.setObjectName("ResultBadgeMatch")
            else:
                self._badge_label.setText("NO MATCH")
                self._badge_label.setObjectName("ResultBadgeNoMatch")
        else:
            self._badge_label.setText("ERROR")
            self._badge_label.setObjectName("ResultBadgeError")
            self._score_label.setVisible(False)
            self._error_label.setText(result.error_message or "An unknown error occurred.")
            self._error_label.setVisible(True)

        # Force stylesheet re-evaluation for dynamic object name changes
        self._badge_label.style().unpolish(self._badge_label)
        self._badge_label.style().polish(self._badge_label)

    def _apply_stylesheet(self) -> None:
        """Applies custom dark mode CSS stylesheet to application."""
        qss = """
        QMainWindow {
            background-color: #0F111A;
        }

        #HeaderTitle {
            font-size: 26px;
            font-weight: bold;
            color: #ECEFF4;
            letter-spacing: 0.5px;
        }

        #HeaderSubtitle {
            font-size: 13px;
            color: #8892B0;
        }

        #FaceCard {
            background-color: #1A1D2B;
            border: 1px solid #2A2F45;
            border-radius: 12px;
        }

        #CardTitle {
            font-size: 14px;
            font-weight: bold;
            color: #82AAFF;
            letter-spacing: 1px;
        }

        #PreviewFrame {
            background-color: #11131F;
            border: 1px dashed #343B58;
            border-radius: 8px;
        }

        #PreviewLabel {
            font-size: 13px;
            color: #565F89;
        }

        #PathLabel {
            font-size: 12px;
            color: #A9B1D6;
        }

        #SelectButton {
            background-color: #24293E;
            color: #C0CAF5;
            border: 1px solid #3B4261;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 500;
        }
        #SelectButton:hover {
            background-color: #2F354F;
            border-color: #7AA2F7;
            color: #FFFFFF;
        }
        #SelectButton:disabled {
            background-color: #161822;
            color: #414868;
            border-color: #1F2335;
        }

        #CompareButton {
            background-color: #7AA2F7;
            color: #15161E;
            border: none;
            border-radius: 10px;
            font-size: 15px;
            font-weight: bold;
            padding: 8px 24px;
        }
        #CompareButton:hover {
            background-color: #89DDFF;
        }
        #CompareButton:disabled {
            background-color: #2AC3DE;
            opacity: 0.6;
            color: #15161E;
        }

        #StatusLabel {
            font-size: 12px;
            color: #7AA2F7;
            font-style: italic;
        }

        #ResultCard {
            background-color: #1A1D2B;
            border: 1px solid #2A2F45;
            border-radius: 12px;
        }

        #ResultBadgePlaceholder {
            background-color: #24293E;
            color: #7AA2F7;
            font-size: 14px;
            font-weight: bold;
            border-radius: 14px;
            padding: 6px 20px;
        }

        #ResultBadgeMatch {
            background-color: #103B2C;
            color: #9ECE6A;
            border: 1px solid #73DACA;
            font-size: 16px;
            font-weight: bold;
            border-radius: 14px;
            padding: 6px 24px;
        }

        #ResultBadgeNoMatch {
            background-color: #3D2229;
            color: #F7768E;
            border: 1px solid #F7768E;
            font-size: 16px;
            font-weight: bold;
            border-radius: 14px;
            padding: 6px 24px;
        }

        #ResultBadgeError {
            background-color: #4A151B;
            color: #FF7B72;
            border: 1px solid #FF7B72;
            font-size: 16px;
            font-weight: bold;
            border-radius: 14px;
            padding: 6px 24px;
        }

        #ScoreLabel {
            font-size: 14px;
            color: #C0CAF5;
        }

        #ErrorLabel {
            font-size: 13px;
            font-weight: bold;
            color: #FFFFFF;
            background-color: #B02A37;
            border: 1px solid #F85149;
            border-radius: 8px;
            padding: 10px 16px;
            margin-top: 4px;
        }
        """
        self.setStyleSheet(qss)
