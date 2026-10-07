import json
import subprocess
from pathlib import Path
from uuid import uuid4

from flask import (
    Blueprint,
    current_app,
    jsonify,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from werkzeug.utils import secure_filename

from config import OUTPUT_FORMATS
from services.ffmpeg_service import (
    ffmpeg_available,
    ffprobe_available,
    probe_video,
    render_clip,
)
from utils.video_helpers import (
    allowed_file,
    build_segments,
    safe_uploaded_video,
    time_for_filename,
)


video_bp = Blueprint("video", __name__)


@video_bp.get("/")
def index():
    return render_template("index.html")


@video_bp.post("/upload")
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
    destination = Path(current_app.config["UPLOAD_FOLDER"]) / filename

    video.save(destination)

    return jsonify({
        "message": "Video cargado correctamente.",
        "filename": filename,
        "original_name": original_name,
        "size": destination.stat().st_size,
        "url": url_for("video.uploaded_video", filename=filename),
        "ffprobe_available": ffprobe_available(),
        "ffmpeg_available": ffmpeg_available(),
    })


@video_bp.post("/analyze")
def analyze_video():
    payload = request.get_json(silent=True) or {}

    filename = payload.get("filename", "")
    intro_seconds = payload.get("intro_seconds", 5)
    clip_seconds = payload.get("clip_seconds", 30)

    safe_filename, video_path = safe_uploaded_video(
        filename,
        current_app.config["UPLOAD_FOLDER"],
    )

    if not safe_filename:
        return jsonify({"message": "Nombre de archivo inválido."}), 400

    if video_path is None:
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
        "ffmpeg_available": ffmpeg_available(),
    })


@video_bp.post("/generate-clip")
def generate_clip():
    payload = request.get_json(silent=True) or {}

    filename = payload.get("filename", "")
    clip_index = payload.get("index")
    start = payload.get("start")
    end = payload.get("end")
    output_format = payload.get("output_format", "original")
    vertical_scale = payload.get("vertical_scale", 100)
    vertical_position = payload.get("vertical_position", "center")
    blur_strength = payload.get("blur_strength", 25)

    if output_format not in OUTPUT_FORMATS:
        return jsonify({"message": "El formato de salida no es válido."}), 400

    try:
        vertical_scale = int(vertical_scale)
        blur_strength = int(blur_strength)
    except (TypeError, ValueError):
        return jsonify({"message": "La personalización vertical no es válida."}), 400

    if not 70 <= vertical_scale <= 100:
        return jsonify({"message": "El tamaño vertical debe estar entre 70% y 100%."}), 400

    if vertical_position not in {"top", "center", "bottom"}:
        return jsonify({"message": "La posición vertical no es válida."}), 400

    if not 5 <= blur_strength <= 40:
        return jsonify({"message": "El desenfoque debe estar entre 5 y 40."}), 400

    safe_filename, video_path = safe_uploaded_video(
        filename,
        current_app.config["UPLOAD_FOLDER"],
    )

    if not safe_filename:
        return jsonify({"message": "Nombre de archivo inválido."}), 400

    if video_path is None:
        return jsonify({"message": "El video cargado ya no está disponible."}), 404

    if not ffmpeg_available():
        return jsonify({
            "message": "FFmpeg no está disponible en el PATH de Windows."
        }), 503

    try:
        clip_index = int(clip_index)
        start = float(start)
        end = float(end)
    except (TypeError, ValueError):
        return jsonify({"message": "Los datos del clip no son válidos."}), 400

    if clip_index < 1 or start < 0 or end <= start:
        return jsonify({"message": "El rango del clip no es válido."}), 400

    try:
        metadata = probe_video(video_path)
    except (
        RuntimeError,
        ValueError,
        json.JSONDecodeError,
        subprocess.CalledProcessError,
    ) as error:
        return jsonify({"message": f"No se pudo validar el video: {error}"}), 422

    source_duration = float(metadata["duration"])

    if start >= source_duration or end > source_duration + 0.25:
        return jsonify({"message": "El clip está fuera de la duración del video."}), 400

    end = min(end, source_duration)
    clip_duration = end - start

    project_name = secure_filename(Path(safe_filename).stem) or "video"
    format_folder = "vertical_9x16" if output_format == "vertical" else "original"
    project_output = (
        Path(current_app.config["OUTPUT_FOLDER"])
        / project_name
        / format_folder
    )
    project_output.mkdir(parents=True, exist_ok=True)

    prefix = "reel" if output_format == "vertical" else "clip"
    output_name = (
        f"{prefix}_{clip_index:02d}_"
        f"{time_for_filename(start)}_"
        f"{time_for_filename(end)}.mp4"
    )
    output_path = project_output / output_name

    try:
        result = render_clip(
            video_path,
            output_path,
            start,
            clip_duration,
            output_format,
            vertical_scale,
            vertical_position,
            blur_strength,
        )
    except subprocess.CalledProcessError as error:
        detail = (error.stderr or "").strip()
        return jsonify({
            "message": f"FFmpeg no pudo generar el clip {clip_index:02d}.",
            "detail": detail[-1000:] if detail else None,
        }), 422

    if not output_path.exists():
        return jsonify({
            "message": f"FFmpeg finalizó, pero no se encontró el clip {clip_index:02d}."
        }), 500

    return jsonify({
        "message": f"Clip {clip_index:02d} generado correctamente.",
        "index": clip_index,
        "filename": output_name,
        "size": output_path.stat().st_size,
        "duration": round(clip_duration, 3),
        "output_format": output_format,
        "resolution": (
            "1080x1920"
            if output_format == "vertical"
            else f"{metadata.get('width')}x{metadata.get('height')}"
        ),
        "vertical_scale": vertical_scale if output_format == "vertical" else None,
        "vertical_position": (
            vertical_position if output_format == "vertical" else None
        ),
        "blur_strength": blur_strength if output_format == "vertical" else None,
        "output_folder": str(project_output.resolve()),
        "url": url_for(
            "video.generated_clip",
            project=project_name,
            format_folder=format_folder,
            filename=output_name,
        ),
        "ffmpeg_log": (result.stderr or "")[-500:],
    })


@video_bp.get("/uploads/<path:filename>")
def uploaded_video(filename):
    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        filename,
    )


@video_bp.get("/outputs/<project>/<format_folder>/<filename>")
def generated_clip(project, format_folder, filename):
    safe_project = secure_filename(project)
    safe_format = secure_filename(format_folder)
    safe_filename = secure_filename(filename)

    if (
        safe_project != project
        or safe_format != format_folder
        or safe_filename != filename
        or format_folder not in {"original", "vertical_9x16"}
    ):
        return jsonify({"message": "Ruta de salida inválida."}), 400

    return send_from_directory(
        Path(current_app.config["OUTPUT_FOLDER"]) / safe_project / safe_format,
        safe_filename,
        as_attachment=False,
    )


@video_bp.app_errorhandler(413)
def file_too_large(_error):
    return jsonify({
        "message": "El video supera el límite actual de 8 GB."
    }), 413
