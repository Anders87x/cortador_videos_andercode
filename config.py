from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
OUTPUT_FOLDER = BASE_DIR / "outputs"

ALLOWED_EXTENSIONS = {"mp4", "mov", "mkv", "webm", "avi"}
OUTPUT_FORMATS = {"original", "vertical"}

MAX_CONTENT_LENGTH = 8 * 1024 * 1024 * 1024  # 8 GB
