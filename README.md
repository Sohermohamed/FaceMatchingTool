# FaceMatchingTool - Desktop Face Verification Application

A modern, high-performance Windows desktop application for face matching and similarity verification built with **Python 3.11**, **PySide6**, **InsightFace**, **OpenCV**, **NumPy**, and **ONNX Runtime** under a strict **Clean Architecture** design.

---

## 1. Overview

**FaceMatchingTool** enables users to compare two face images side by side, detect faces using pretrained deep learning models, generate L2-normalized 512-dimensional face embeddings, and calculate cosine similarity to determine if both images depict the same person.

> [!NOTE]
> The application leverages InsightFace's pretrained `buffalo_l` ArcFace recognition model running locally via ONNX Runtime CPU execution provider. **The application does not train any neural network models.**

---

## 2. Features

- **Side-by-Side Image Selection & Preview**: Select images (JPG, PNG, BMP, WEBP) with automatic aspect-ratio scaling.
- **Single-Initialization Model Loading**: The InsightFace model is loaded once upon application startup and reused across face comparisons for optimal responsiveness.
- **In-Memory SHA-256 Embedding Caching**: Extracted face embeddings are cached in memory using a SHA-256 hash of the image content as key. Repeated comparisons of identical images skip neural network inference and execute instantly (~200x+ speedup).
- **Strict Face Detection Rules**: Enforces exactly 1 face per image. Displays clear, user-friendly errors if 0 faces or >1 faces are present.
- **Asynchronous GUI Responsiveness**: Model inference runs on a background `QThread` (`FaceMatchingWorker`), keeping the PySide6 user interface responsive with visual status feedback.
- **Cosine Similarity Verification**: Computes embedding vector alignment and compares it against a centralized similarity threshold.
- **Clean Architecture & Dependency Injection**: Pure Domain entities, abstract Application interfaces, clean Infrastructure implementations, and manual dependency injection.

---

## 3. Technology Stack

- **Language**: Python 3.11
- **GUI Framework**: PySide6 (Qt for Python 6)
- **Face Detection & Recognition**: InsightFace (`buffalo_l` model)
- **Inference Engine**: ONNX Runtime (`CPUExecutionProvider`)
- **Image Processing**: OpenCV (`opencv-python`)
- **Numerical Operations**: NumPy
- **Testing**: Python `unittest` framework

---

## 4. Architecture

The codebase follows a **Clean Architecture** layered layout:

```
Presentation Layer  (PySide6 UI, ViewModels, QThread Workers)
        ↓
Application Layer   (Use Cases, DTOs, Service Interfaces)
        ↓
Domain Layer        (Pure Business Entities & Value Objects)

Infrastructure Layer (InsightFace Service, OpenCV Image Loader)
        ↓
Application / Domain Layers
```

- **Domain Layer (`domain/`)**: Pure business logic (`FaceMatchResult`). Free of external framework dependencies (No PySide6, OpenCV, InsightFace, or NumPy).
- **Application Layer (`application/`)**: High-level use cases (`CompareFacesUseCase`), DTOs (`ComparisonResultDTO`), and service interfaces (`IFaceMatchingService`).
- **Infrastructure Layer (`infrastructure/`)**: Concrete implementations (`InsightFaceFaceMatchingService`, `ImageLoader`).
- **Presentation Layer (`presentation/`)**: Desktop interface (`MainWindow`), state management (`FaceMatchingViewModel`), and non-blocking threading (`FaceMatchingWorker`).

---

## 5. Folder Structure

```
FaceMatchingTool/
│
├── config.py                            # Central configuration (Threshold, model settings)
├── domain/
│   ├── __init__.py
│   └── entities/
│       ├── __init__.py
│       └── face_match_result.py         # FaceMatchResult entity
│
├── application/
│   ├── __init__.py
│   ├── interfaces/
│   │   ├── __init__.py
│   │   └── face_matching_service.py     # IFaceMatchingService interface
│   ├── dto/
│   │   ├── __init__.py
│   │   └── comparison_result.py         # ComparisonResultDTO
│   └── use_cases/
│       ├── __init__.py
│       └── compare_faces.py             # CompareFacesUseCase
│
├── infrastructure/
│   ├── __init__.py
│   ├── face_recognition/
│   │   ├── __init__.py
│   │   └── insightface_matcher.py       # InsightFaceFaceMatchingService
│   └── image_processing/
│       ├── __init__.py
│       └── image_loader.py              # OpenCV ImageLoader
│
├── presentation/
│   ├── __init__.py
│   ├── view_model.py                    # FaceMatchingViewModel
│   ├── main_window.py                   # PySide6 MainWindow GUI
│   └── workers/
│       ├── __init__.py
│       └── face_matching_worker.py      # Background QThread worker
│
├── tests/
│   ├── __init__.py
│   ├── test_compare_faces.py            # Use case unit tests with mock service
│   └── test_face_match_result.py        # Domain entity unit tests
│
├── app.py                               # Application composition root & entry point
├── requirements.txt                      # Project dependencies
├── README.md                            # Documentation
└── .gitignore                           # Git ignore rules
```

---

## 6. Installation

1. Ensure **Python 3.11** is installed.
2. Clone or navigate to the project directory:
   ```bash
   cd FaceMatchingTool
   ```
3. Activate your virtual environment (or create one):
   ```bash
   # Windows PowerShell:
   .venv\Scripts\Activate.ps1
   ```
4. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## 7. Running the Application

Launch the desktop application using `python app.py`:

```bash
python app.py
```

The PySide6 graphical interface will open. Select Face 1 and Face 2 image files, then click **Compare Faces**.

---

## 8. How Face Matching Works

1. **Image Loading**: Images are safely decoded using OpenCV (handling Unicode file paths on Windows).
2. **Face Detection**: InsightFace RetinaFace/SCRFD detector locates faces in both images.
3. **Validation Rules**:
   - If no face is detected in an image → Returns a clear error message.
   - If more than 1 face is detected in an image → Returns an error requesting an image containing exactly one face.
4. **Embedding Generation**: ArcFace extracts 512-dimensional feature vectors representing facial geometry and features.
5. **Cosine Similarity**: NumPy computes the dot product of the normalized embedding vectors.
6. **Decision**: If `similarity_score >= DEFAULT_SIMILARITY_THRESHOLD`, the result is **MATCH**, otherwise **NO MATCH**.

---

## 9. Similarity Score vs Probability

> [!IMPORTANT]
> The similarity score displayed by the application (e.g. `0.7652`) is a **Cosine Similarity Score** ranging between `-1.0` and `+1.0`.
> - **It is NOT a percentage or probability of identity certainty.**
> - High values (e.g., > 0.40–0.50) indicate high feature vector alignment.
> - The score measures vector similarity in feature space produced by ArcFace embedding models.

---

## 10. Threshold Configuration

The similarity threshold is centralized in `config.py`:

```python
# config.py
DEFAULT_SIMILARITY_THRESHOLD: float = 0.40
```

- **Tuning Guidance**: `0.40` is an initial baseline threshold for InsightFace `buffalo_l`.
- Depending on image quality, lighting, pose variations, or security requirements (false acceptance rate vs. false rejection rate), this threshold can be tuned in `config.py` based on testing against target validation image pairs.

---

## 11. Error Handling

The application handles edge cases gracefully without crashing or displaying raw stack traces in the GUI:
- **Missing or Invalid Image Files**: Friendly UI notification.
- **Corrupted Files**: Handled by OpenCV loading validation.
- **Zero Faces Detected**: Asks user to select an image with a visible face.
- **Multiple Faces Detected**: Asks user to provide an image with a single face.
- **Technical Logging**: Errors and system events are logged via Python's standard `logging` library for debugging.

---

## 12. Testing

Unit tests cover the Domain entity and Application use cases using a mock `IFaceMatchingService` to isolate test execution from machine learning model inference.

Run tests using unittest:

```bash
python -m unittest discover -s tests
```

or with pytest:

```bash
pytest
```
