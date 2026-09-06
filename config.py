"""Central configuration for FaceMatchingTool."""

# Initial configurable similarity threshold for InsightFace ArcFace embeddings.
# Note: Cosine similarity measures embedding vector alignment, not identity probability.
# This threshold can be tuned based on dataset performance and application requirements.
DEFAULT_SIMILARITY_THRESHOLD: float = 0.40

# InsightFace model parameters
MODEL_NAME: str = "buffalo_l"
DET_SIZE: tuple[int, int] = (640, 640)

# Supported image file extensions
SUPPORTED_EXTENSIONS: tuple[str, ...] = (
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp"
)
