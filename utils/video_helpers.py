import math
from pathlib import Path

from werkzeug.utils import secure_filename

from config import ALLOWED_EXTENSIONS


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def build_segments(duration, intro_seconds, clip_seconds):
    start = min(max(float(intro_seconds), 0), duration)
    clip_length = max(float(clip_seconds), 1)
    usable_duration = max(duration - start, 0)

    if usable_duration <= 0:
        return []

    total_clips = math.ceil(usable_duration / clip_length)
    segments = []

    for index in range(total_clips):
        segment_start = start + (index * clip_length)
        segment_end = min(segment_start + clip_length, duration)

        segments.append({
            "index": index + 1,
            "start": round(segment_start, 3),
            "end": round(segment_end, 3),
            "duration": round(segment_end - segment_start, 3),
        })

    return segments


def safe_uploaded_video(filename, upload_folder):
    safe_filename = secure_filename(Path(filename).name)

    if not safe_filename or safe_filename != filename:
        return None, None

    video_path = Path(upload_folder) / safe_filename

    if not video_path.exists() or not video_path.is_file():
        return safe_filename, None

    return safe_filename, video_path


def time_for_filename(seconds):
    total = max(0, int(float(seconds)))
    hours = total // 3600
    minutes = (total % 3600) // 60
    secs = total % 60

    if hours:
        return f"{hours:02d}-{minutes:02d}-{secs:02d}"

    return f"{minutes:02d}-{secs:02d}"
