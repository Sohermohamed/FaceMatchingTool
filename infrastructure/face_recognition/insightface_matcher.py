"""InsightFace implementation of face matching service."""
import logging
import hashlib
from typing import Optional
import numpy as np
from insightface.app import FaceAnalysis
from application.interfaces.face_matching_service import IFaceMatchingService
from application.dto.comparison_result import ComparisonResultDTO
from domain.entities.face_match_result import FaceMatchResult
from infrastructure.image_processing.image_loader import ImageLoader
from config import DEFAULT_SIMILARITY_THRESHOLD, MODEL_NAME, DET_SIZE

logger = logging.getLogger(__name__)


class InsightFaceFaceMatchingService(IFaceMatchingService):
    """Face matching service powered by InsightFace ArcFace model with in-memory embedding caching."""

    def __init__(
        self,
        threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
        model_name: str = MODEL_NAME,
        det_size: tuple[int, int] = DET_SIZE,
        image_loader: ImageLoader = None
    ) -> None:
        """Initializes InsightFace FaceAnalysis model ONCE and sets up embedding cache.
        
        Args:
            threshold: Similarity threshold to determine face match.
            model_name: Pretrained model name (default: buffalo_l).
            det_size: Detection resolution size tuple (default: 640x640).
            image_loader: ImageLoader instance for image reading.
        """
        self._threshold = threshold
        self._image_loader = image_loader or ImageLoader()

        # In-memory session cache mapping SHA-256 image content hash -> cached result dict
        self._embedding_cache: dict[str, dict] = {}

        logger.info(f"Initializing InsightFace model '{model_name}' on CPUExecutionProvider...")
        try:
            self._app = FaceAnalysis(
                name=model_name,
                providers=["CPUExecutionProvider"]
            )
            self._app.prepare(ctx_id=0, det_size=det_size)
            logger.info("InsightFace model initialized and prepared successfully.")
        except Exception as e:
            logger.critical(f"Failed to initialize InsightFace model '{model_name}': {e}", exc_info=True)
            raise RuntimeError(f"InsightFace model initialization failed: {str(e)}") from e

    def _compute_sha256(self, file_path: str) -> str:
        """Computes SHA-256 hash of image file content."""
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _get_or_extract_embedding(
        self, image_path: str, image_label: str
    ) -> tuple[Optional[np.ndarray], Optional[ComparisonResultDTO]]:
        """Retrieves cached embedding or computes it via InsightFace if cache miss."""
        try:
            file_hash = self._compute_sha256(image_path)
        except Exception as e:
            return None, ComparisonResultDTO(
                success=False,
                error_message=f"Could not read {image_label} file: {str(e)}"
            )

        # Check in-memory cache
        if file_hash in self._embedding_cache:
            logger.info(f"Cache HIT for {image_label} ('{image_path}', sha256: {file_hash[:10]}...). Reusing cached face embedding.")
            cached = self._embedding_cache[file_hash]
            return cached["embedding"], cached["error"]

        # Cache MISS: Execute face detection & embedding extraction
        logger.info(f"Cache MISS for {image_label} ('{image_path}', sha256: {file_hash[:10]}...). Running InsightFace inference.")

        # Load image
        try:
            img = self._image_loader.load_image(image_path)
        except Exception as e:
            err = ComparisonResultDTO(
                success=False,
                error_message=f"Could not load {image_label} image: {str(e)}"
            )
            self._embedding_cache[file_hash] = {"embedding": None, "error": err}
            return None, err

        # Detect faces
        faces = self._app.get(img)
        logger.info(f"Detected {len(faces)} face(s) in {image_label} image.")

        if len(faces) == 0:
            err = ComparisonResultDTO(
                success=False,
                error_message=f"No face detected in {image_label} image. Please select an image with a clear face."
            )
            self._embedding_cache[file_hash] = {"embedding": None, "error": err}
            return None, err

        if len(faces) > 1:
            err = ComparisonResultDTO(
                success=False,
                error_message=f"Multiple faces ({len(faces)}) detected in {image_label} image. Please provide an image containing exactly one face."
            )
            self._embedding_cache[file_hash] = {"embedding": None, "error": err}
            return None, err

        # Extract normalized embedding and cache
        emb = faces[0].normed_embedding
        self._embedding_cache[file_hash] = {"embedding": emb, "error": None}
        return emb, None

    def compare_faces(self, image_path1: str, image_path2: str) -> ComparisonResultDTO:
        """Compares two face images using cached or freshly extracted face embeddings.
        
        Args:
            image_path1: Path to Face 1 image file.
            image_path2: Path to Face 2 image file.
            
        Returns:
            ComparisonResultDTO containing FaceMatchResult or error details.
        """
        # Step 1: Retrieve / extract embedding for Image 1
        emb1, err1 = self._get_or_extract_embedding(image_path1, "Face 1")
        if err1:
            return err1

        # Step 2: Retrieve / extract embedding for Image 2
        emb2, err2 = self._get_or_extract_embedding(image_path2, "Face 2")
        if err2:
            return err2

        # Step 3: Compute cosine similarity
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)

        if norm1 == 0 or norm2 == 0:
            return ComparisonResultDTO(
                success=False,
                error_message="Zero-magnitude embedding vector encountered during comparison."
            )

        similarity_score = float(np.dot(emb1, emb2) / (norm1 * norm2))
        matched = similarity_score >= self._threshold

        logger.info(
            f"Comparison completed: similarity={similarity_score:.4f}, "
            f"threshold={self._threshold:.2f}, matched={matched}"
        )

        return ComparisonResultDTO(
            success=True,
            result=FaceMatchResult(
                matched=matched,
                similarity_score=round(similarity_score, 4),
                threshold=self._threshold
            )
        )
