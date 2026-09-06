"""OpenCV-based image loading utility."""
import os
import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)


class ImageLoader:
    """Helper class to load and validate images using OpenCV."""

    @staticmethod
    def load_image(file_path: str) -> np.ndarray:
        """Loads an image from file path using OpenCV.
        
        Uses np.fromfile and cv2.imdecode to safely handle Unicode/special character paths on Windows.
        
        Args:
            file_path: Absolute or relative path to the image file.
            
        Returns:
            Loaded image as BGR numpy array.
            
        Raises:
            ValueError: If the file cannot be read or is corrupted.
            FileNotFoundError: If the file path does not exist.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Image file not found: {file_path}")

        try:
            # Use np.fromfile + cv2.imdecode for Windows Unicode file path compatibility
            img_array = np.fromfile(file_path, dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

            if img is None or img.size == 0:
                raise ValueError(f"Failed to decode image from path: {file_path}. File may be corrupted or in an invalid format.")

            logger.info(f"Successfully loaded image '{file_path}' with shape {img.shape}")
            return img
        except Exception as e:
            logger.error(f"Error loading image from {file_path}: {e}")
            raise ValueError(f"Could not load image file '{file_path}': {str(e)}") from e
