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
OUTPUT_FOLDER = BASE_DIR / "outputs"
ALLOWED_EXTENSIONS = {"mp4", "mov", "mkv", "webm", "avi"}
OUTPUT_FORMATS = {"original", "vertical"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.config["OUTPUT_FOLDER"] = str(OUTPUT_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024 * 1024  # 8 GB

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def ffprobe_available():
    return shutil.which("ffprobe") is not None


def ffmpeg_available():
    return shutil.which("ffmpeg") is not None


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


def safe_uploaded_video(filename):
    safe_filename = secure_filename(Path(filename).name)

    if not safe_filename or safe_filename != filename:
        return None, None

    video_path = UPLOAD_FOLDER / safe_filename

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


def build_ffmpeg_command(
    video_path,
    output_path,
    start,
    clip_duration,
    output_format,
    vertical_scale=100,
    vertical_position="center",
    blur_strength=25,
):
    base = [
        "ffmpeg",
        "-y",
        "-ss",
        f"{start:.3f}",
        "-i",
        str(video_path),
        "-t",
        f"{clip_duration:.3f}",
    ]

    if output_format == "vertical":
        target_width = max(2, int(round(1080 * vertical_scale / 100)))
        target_height = max(2, int(round(1920 * vertical_scale / 100)))

        if target_width % 2:
            target_width -= 1

        if target_height % 2:
            target_height -= 1

        y_expression = {
            "top": "max(0,min(H-h,160))",
            "center": "(H-h)/2",
            "bottom": "max(0,H-h-220)",
        }[vertical_position]

        filter_complex = (
            "[0:v]split=2[bg][fg];"
            "[bg]scale=1080:1920:force_original_aspect_ratio=increase,"
            f"crop=1080:1920,boxblur={blur_strength}:2[bgv];"
            f"[fg]scale={target_width}:{target_height}:force_original_aspect_ratio=decrease[fgv];"
            f"[bgv][fgv]overlay=(W-w)/2:{y_expression},format=yuv420p[vout]"
        )

        return base + [
            "-filter_complex",
            filter_complex,
            "-map",
            "[vout]",
            "-map",
            "0:a?",
            "-sn",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "20",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-movflags",
            "+faststart",
            str(output_path),
        ]

    return base + [
        "-map",
        "0:v:0",
        "-map",
        "0:a?",
        "-sn",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "20",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-movflags",
        "+faststart",
        str(output_path),
    ]


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
        "ffmpeg_available": ffmpeg_available(),
    })


@app.post("/analyze")
def analyze_video():
    payload = request.get_json(silent=True) or {}

    filename = payload.get("filename", "")
    intro_seconds = payload.get("intro_seconds", 5)
    clip_seconds = payload.get("clip_seconds", 30)

    safe_filename, video_path = safe_uploaded_video(filename)

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


@app.post("/generate-clip")
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

    safe_filename, video_path = safe_uploaded_video(filename)

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
    except (RuntimeError, ValueError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        return jsonify({"message": f"No se pudo validar el video: {error}"}), 422

    source_duration = float(metadata["duration"])

    if start >= source_duration or end > source_duration + 0.25:
        return jsonify({"message": "El clip está fuera de la duración del video."}), 400

    end = min(end, source_duration)
    clip_duration = end - start

    project_name = secure_filename(Path(safe_filename).stem) or "video"
    format_folder = "vertical_9x16" if output_format == "vertical" else "original"
    project_output = OUTPUT_FOLDER / project_name / format_folder
    project_output.mkdir(parents=True, exist_ok=True)

    prefix = "reel" if output_format == "vertical" else "clip"
    output_name = (
        f"{prefix}_{clip_index:02d}_"
        f"{time_for_filename(start)}_"
        f"{time_for_filename(end)}.mp4"
    )
    output_path = project_output / output_name

    command = build_ffmpeg_command(
        video_path,
        output_path,
        start,
        clip_duration,
        output_format,
        vertical_scale,
        vertical_position,
        blur_strength,
    )

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="replace",
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
        "resolution": "1080x1920" if output_format == "vertical" else f"{metadata.get('width')}x{metadata.get('height')}",
        "vertical_scale": vertical_scale if output_format == "vertical" else None,
        "vertical_position": vertical_position if output_format == "vertical" else None,
        "blur_strength": blur_strength if output_format == "vertical" else None,
        "output_folder": str(project_output.resolve()),
        "url": url_for(
            "generated_clip",
            project=project_name,
            format_folder=format_folder,
            filename=output_name,
        ),
        "ffmpeg_log": (result.stderr or "")[-500:],
    })


@app.get("/uploads/<path:filename>")
def uploaded_video(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.get("/outputs/<project>/<format_folder>/<filename>")
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
        Path(app.config["OUTPUT_FOLDER"]) / safe_project / safe_format,
        safe_filename,
        as_attachment=False,
    )


@app.errorhandler(413)
def file_too_large(_error):
    return jsonify({
        "message": "El video supera el límite actual de 8 GB."
    }), 413


if __name__ == "__main__":
    app.run(debug=True)
