"""Unit tests for CompareFacesUseCase application layer logic."""
import unittest
from unittest.mock import MagicMock, patch
from application.use_cases.compare_faces import CompareFacesUseCase
from application.interfaces.face_matching_service import IFaceMatchingService
from application.dto.comparison_result import ComparisonResultDTO
from domain.entities.face_match_result import FaceMatchResult


class TestCompareFacesUseCase(unittest.TestCase):
    """Test suite for CompareFacesUseCase."""

    def setUp(self) -> None:
        """Set up mock service and use case instance."""
        self.mock_service = MagicMock(spec=IFaceMatchingService)
        self.use_case = CompareFacesUseCase(face_matching_service=self.mock_service)

    def test_compare_faces_matching_result(self) -> None:
        """Verify use case returns matched=True when service returns similarity above threshold."""
        expected_result = ComparisonResultDTO(
            success=True,
            result=FaceMatchResult(matched=True, similarity_score=0.87, threshold=0.40)
        )
        self.mock_service.compare_faces.return_value = expected_result

        with patch("os.path.exists", return_value=True):
            result = self.use_case.execute("face1.jpg", "face2.jpg")

        self.assertTrue(result.success)
        self.assertIsNotNone(result.result)
        self.assertTrue(result.result.matched)
        self.assertEqual(result.result.similarity_score, 0.87)

    def test_compare_faces_non_matching_result(self) -> None:
        """Verify use case returns matched=False when service returns similarity below threshold."""
        expected_result = ComparisonResultDTO(
            success=True,
            result=FaceMatchResult(matched=False, similarity_score=0.18, threshold=0.40)
        )
        self.mock_service.compare_faces.return_value = expected_result

        with patch("os.path.exists", return_value=True):
            result = self.use_case.execute("face1.jpg", "face2.jpg")

        self.assertTrue(result.success)
        self.assertIsNotNone(result.result)
        self.assertFalse(result.result.matched)
        self.assertEqual(result.result.similarity_score, 0.18)

    def test_empty_image_paths_handled(self) -> None:
        """Verify error is returned when image paths are empty."""
        result = self.use_case.execute("", "face2.jpg")
        self.assertFalse(result.success)
        self.assertIn("select both", result.error_message.lower())

    def test_missing_file_handled(self) -> None:
        """Verify error is returned when an image file does not exist on disk."""
        with patch("os.path.exists", side_effect=lambda path: path == "exists.jpg"):
            result = self.use_case.execute("missing.jpg", "exists.jpg")

        self.assertFalse(result.success)
        self.assertIn("not found", result.error_message.lower())

    def test_unsupported_file_extension_handled(self) -> None:
        """Verify error is returned when an unsupported file format is passed."""
        with patch("os.path.exists", return_value=True):
            result = self.use_case.execute("image.txt", "face.jpg")

        self.assertFalse(result.success)
        self.assertIn("unsupported format", result.error_message.lower())


if __name__ == "__main__":
    unittest.main()
