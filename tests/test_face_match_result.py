"""Unit tests for FaceMatchResult domain entity."""
import unittest
from domain.entities.face_match_result import FaceMatchResult


class TestFaceMatchResult(unittest.TestCase):
    """Test suite for FaceMatchResult domain entity."""

    def test_face_match_result_attributes_when_matched(self) -> None:
        """Verify attributes when matched is True."""
        result = FaceMatchResult(matched=True, similarity_score=0.85, threshold=0.40)
        self.assertTrue(result.matched)
        self.assertEqual(result.similarity_score, 0.85)
        self.assertEqual(result.threshold, 0.40)

    def test_face_match_result_attributes_when_not_matched(self) -> None:
        """Verify attributes when matched is False."""
        result = FaceMatchResult(matched=False, similarity_score=0.25, threshold=0.40)
        self.assertFalse(result.matched)
        self.assertEqual(result.similarity_score, 0.25)
        self.assertEqual(result.threshold, 0.40)

    def test_face_match_result_immutability(self) -> None:
        """Verify FaceMatchResult is immutable (frozen)."""
        result = FaceMatchResult(matched=True, similarity_score=0.85, threshold=0.40)
        with self.assertRaises(AttributeError):
            result.matched = False  # type: ignore


if __name__ == "__main__":
    unittest.main()
