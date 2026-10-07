import json
import math
import shutil
import subprocess
from pathlib import Path
from uuid import uuid4

from flask import Flask, jsonify, render_template, request, send_from_directory, url_for
from werkzeug.utils import secure_filename


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
ALLOWED_EXTENSIONS = {"mp4", "mov", "mkv", "webm", "avi"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024 * 1024  # 8 GB

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def ffprobe_available():
    return shutil.which("ffprobe") is not None


def probe_video(video_path):
    if not ffprobe_available():
        raise RuntimeError(
            "FFprobe no está disponible. Instala FFmpeg y asegúrate de que ffprobe esté en el PATH."
        )

    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration:stream=index,codec_type,codec_name,width,height,r_frame_rate",
        "-of",
        "json",
        str(video_path),
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True,
        encoding="utf-8",
        errors="replace",
    )

    data = json.loads(result.stdout)
    duration = float(data.get("format", {}).get("duration", 0) or 0)

    streams = data.get("streams", [])
    video_stream = next(
        (stream for stream in streams if stream.get("codec_type") == "video"),
        {},
    )
    audio_stream = next(
        (stream for stream in streams if stream.get("codec_type") == "audio"),
        None,
    )

    fps = 0.0
    frame_rate = video_stream.get("r_frame_rate", "0/1")

    if "/" in frame_rate:
        numerator, denominator = frame_rate.split("/", 1)
        denominator_value = float(denominator or 1)

        if denominator_value:
            fps = float(numerator or 0) / denominator_value

    return {
        "duration": duration,
        "width": video_stream.get("width"),
        "height": video_stream.get("height"),
        "video_codec": video_stream.get("codec_name"),
        "fps": round(fps, 3),
        "has_audio": audio_stream is not None,
        "audio_codec": audio_stream.get("codec_name") if audio_stream else None,
    }


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


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/upload")
def upload_video():
    if "video" not in request.files:
        return jsonify({"message": "No se recibió ningún video."}), 400

    video = request.files["video"]

    if not video.filename:
        return jsonify({"message": "Selecciona un archivo de video."}), 400

    if not allowed_file(video.filename):
        return jsonify({
            "message": "Formato no permitido. Usa MP4, MOV, MKV, WEBM o AVI."
        }), 400

    original_name = video.filename
    extension = original_name.rsplit(".", 1)[1].lower()
    safe_name = secure_filename(Path(original_name).stem) or "video"
    filename = f"{safe_name}-{uuid4().hex[:8]}.{extension}"
    destination = UPLOAD_FOLDER / filename

    video.save(destination)

    return jsonify({
        "message": "Video cargado correctamente.",
        "filename": filename,
        "original_name": original_name,
        "size": destination.stat().st_size,
        "url": url_for("uploaded_video", filename=filename),
        "ffprobe_available": ffprobe_available(),
    })


@app.post("/analyze")
def analyze_video():
    payload = request.get_json(silent=True) or {}

    filename = payload.get("filename", "")
    intro_seconds = payload.get("intro_seconds", 5)
    clip_seconds = payload.get("clip_seconds", 30)

    safe_filename = secure_filename(Path(filename).name)

    if not safe_filename or safe_filename != filename:
        return jsonify({"message": "Nombre de archivo inválido."}), 400

    video_path = UPLOAD_FOLDER / safe_filename

    if not video_path.exists() or not video_path.is_file():
        return jsonify({"message": "El video cargado ya no está disponible."}), 404

    try:
        intro_seconds = max(float(intro_seconds), 0)
        clip_seconds = max(float(clip_seconds), 1)
    except (TypeError, ValueError):
        return jsonify({"message": "La configuración de tiempos no es válida."}), 400

    try:
        metadata = probe_video(video_path)
    except FileNotFoundError:
        return jsonify({
            "message": "No se encontró FFprobe. Instala FFmpeg y agrégalo al PATH de Windows."
        }), 503
    except subprocess.CalledProcessError as error:
        detail = (error.stderr or "").strip()
        return jsonify({
            "message": "FFprobe no pudo analizar el video.",
            "detail": detail[-500:] if detail else None,
        }), 422
    except (RuntimeError, ValueError, json.JSONDecodeError) as error:
        return jsonify({"message": str(error)}), 503

    segments = build_segments(
        metadata["duration"],
        intro_seconds,
        clip_seconds,
    )

    return jsonify({
        "message": "Video analizado correctamente con FFprobe.",
        "metadata": metadata,
        "intro_seconds": intro_seconds,
        "clip_seconds": clip_seconds,
        "segments": segments,
        "total_segments": len(segments),
    })


@app.get("/uploads/<path:filename>")
def uploaded_video(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.errorhandler(413)
def file_too_large(_error):
    return jsonify({
        "message": "El video supera el límite actual de 8 GB."
    }), 413


if __name__ == "__main__":
    app.run(debug=True)
