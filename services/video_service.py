import json
import subprocess
from pathlib import Path
from uuid import uuid4

from werkzeug.utils import secure_filename

from config import OUTPUT_FORMATS
from services.ffmpeg_service import (
    RenderCancelledError,
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


class VideoServiceError(Exception):
    def __init__(self, message, status_code=400, detail=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.detail = detail

    def to_dict(self):
        payload = {"message": self.message}

        if self.detail:
            payload["detail"] = self.detail

        return payload


def save_uploaded_video(video, upload_folder):
    if not video.filename:
        raise VideoServiceError("Selecciona un archivo de video.", 400)

    if not allowed_file(video.filename):
        raise VideoServiceError(
            "Formato no permitido. Usa MP4, MOV, MKV, WEBM o AVI.",
            400,
        )

    original_name = video.filename
    extension = original_name.rsplit(".", 1)[1].lower()
    safe_name = secure_filename(Path(original_name).stem) or "video"
    filename = f"{safe_name}-{uuid4().hex[:8]}.{extension}"
    destination = Path(upload_folder) / filename

    video.save(destination)

    return {
        "message": "Video cargado correctamente.",
        "filename": filename,
        "original_name": original_name,
        "size": destination.stat().st_size,
        "ffprobe_available": ffprobe_available(),
        "ffmpeg_available": ffmpeg_available(),
    }


def analyze_uploaded_video(
    filename,
    intro_seconds,
    clip_seconds,
    upload_folder,
):
    safe_filename, video_path = safe_uploaded_video(
        filename,
        upload_folder,
    )

    if not safe_filename:
        raise VideoServiceError("Nombre de archivo inválido.", 400)

    if video_path is None:
        raise VideoServiceError(
            "El video cargado ya no está disponible.",
            404,
        )

    try:
        intro_seconds = max(float(intro_seconds), 0)
        clip_seconds = max(float(clip_seconds), 1)
    except (TypeError, ValueError):
        raise VideoServiceError(
            "La configuración de tiempos no es válida.",
            400,
        ) from None

    try:
        metadata = probe_video(video_path)
    except FileNotFoundError:
        raise VideoServiceError(
            "No se encontró FFprobe. Instala FFmpeg y agrégalo al PATH de Windows.",
            503,
        ) from None
    except subprocess.CalledProcessError as error:
        detail = (error.stderr or "").strip()
        raise VideoServiceError(
            "FFprobe no pudo analizar el video.",
            422,
            detail[-500:] if detail else None,
        ) from error
    except (RuntimeError, ValueError, json.JSONDecodeError) as error:
        raise VideoServiceError(str(error), 503) from error

    segments = build_segments(
        metadata["duration"],
        intro_seconds,
        clip_seconds,
    )

    return {
        "message": "Video analizado correctamente con FFprobe.",
        "metadata": metadata,
        "intro_seconds": intro_seconds,
        "clip_seconds": clip_seconds,
        "segments": segments,
        "total_segments": len(segments),
        "ffmpeg_available": ffmpeg_available(),
    }


def generate_video_clip(
    payload,
    upload_folder,
    output_folder,
    promo_config=None,
):
    filename = payload.get("filename", "")
    clip_index = payload.get("index")
    start = payload.get("start")
    end = payload.get("end")
    output_format = payload.get("output_format", "vertical")
    vertical_scale = payload.get("vertical_scale", 100)
    vertical_position = payload.get("vertical_position", "center")
    blur_strength = payload.get("blur_strength", 25)
    branding_enabled = payload.get("branding_enabled") is True
    branding_title = str(payload.get("branding_title") or "").strip()
    branding_handle = str(payload.get("branding_handle") or "").strip()
    encoder_mode = str(payload.get("encoder_mode") or "auto").lower()
    job_id = str(payload.get("job_id") or "").strip()

    if encoder_mode not in {"auto", "gpu", "cpu"}:
        raise VideoServiceError(
            "El motor de render seleccionado no es válido.",
            400,
        )

    if output_format not in OUTPUT_FORMATS:
        raise VideoServiceError(
            "El formato de salida no es válido.",
            400,
        )

    try:
        vertical_scale = int(vertical_scale)
        blur_strength = int(blur_strength)
    except (TypeError, ValueError):
        raise VideoServiceError(
            "La personalización vertical no es válida.",
            400,
        ) from None

    if not 70 <= vertical_scale <= 100:
        raise VideoServiceError(
            "El tamaño vertical debe estar entre 70% y 100%.",
            400,
        )

    if vertical_position not in {"top", "center", "bottom"}:
        raise VideoServiceError(
            "La posición vertical no es válida.",
            400,
        )

    if not 5 <= blur_strength <= 40:
        raise VideoServiceError(
            "El desenfoque debe estar entre 5 y 40.",
            400,
        )

    if len(branding_title) > 70:
        raise VideoServiceError(
            "El título de branding no puede superar 70 caracteres.",
            400,
        )

    if len(branding_handle) > 40:
        raise VideoServiceError(
            "La firma de branding no puede superar 40 caracteres.",
            400,
        )

    branding_title = " ".join(branding_title.splitlines())
    branding_handle = " ".join(branding_handle.splitlines())

    if output_format != "vertical":
        branding_enabled = False

    safe_filename, video_path = safe_uploaded_video(
        filename,
        upload_folder,
    )

    if not safe_filename:
        raise VideoServiceError("Nombre de archivo inválido.", 400)

    if video_path is None:
        raise VideoServiceError(
            "El video cargado ya no está disponible.",
            404,
        )

    if not ffmpeg_available():
        raise VideoServiceError(
            "FFmpeg no está disponible en el PATH de Windows.",
            503,
        )

    try:
        clip_index = int(clip_index)
        start = float(start)
        end = float(end)
    except (TypeError, ValueError):
        raise VideoServiceError(
            "Los datos del clip no son válidos.",
            400,
        ) from None

    if clip_index < 1 or start < 0 or end <= start:
        raise VideoServiceError(
            "El rango del clip no es válido.",
            400,
        )

    try:
        metadata = probe_video(video_path)
    except (
        RuntimeError,
        ValueError,
        json.JSONDecodeError,
        subprocess.CalledProcessError,
    ) as error:
        raise VideoServiceError(
            f"No se pudo validar el video: {error}",
            422,
        ) from error

    source_duration = float(metadata["duration"])

    if start >= source_duration or end > source_duration + 0.25:
        raise VideoServiceError(
            "El clip está fuera de la duración del video.",
            400,
        )

    end = min(end, source_duration)
    clip_duration = end - start

    project_name = secure_filename(Path(safe_filename).stem) or "video"
    format_folder = (
        "vertical_9x16"
        if output_format == "vertical"
        else "original"
    )
    project_output = Path(output_folder) / project_name / format_folder
    project_output.mkdir(parents=True, exist_ok=True)

    prefix = "reel" if output_format == "vertical" else "clip"
    output_name = (
        f"{prefix}_{clip_index:02d}_"
        f"{time_for_filename(start)}_"
        f"{time_for_filename(end)}.mp4"
    )
    output_path = project_output / output_name

    promo_config = promo_config or {}
    hook = promo_config.get("hook")
    outro = promo_config.get("outro")

    promo_duration = 0.0

    if hook:
        try:
            hook_duration = float(hook.get("duration", 0.5))
        except (TypeError, ValueError):
            raise VideoServiceError(
                "La duración del hook no es válida.",
                400,
            ) from None

        if not 0.2 <= hook_duration <= 3:
            raise VideoServiceError(
                "La duración del hook debe estar entre 0.2 y 3 segundos.",
                400,
            )

        hook = {
            "image_path": Path(hook["image_path"]),
            "duration": round(hook_duration, 3),
            "fade": bool(hook.get("fade", True)),
        }
        promo_duration += hook["duration"]

    if outro:
        try:
            outro_duration = float(outro.get("duration", 5))
        except (TypeError, ValueError):
            raise VideoServiceError(
                "La duración del outro no es válida.",
                400,
            ) from None

        if not 2 <= outro_duration <= 10:
            raise VideoServiceError(
                "La duración del outro debe estar entre 2 y 10 segundos.",
                400,
            )

        outro = {
            "image_path": Path(outro["image_path"]),
            "duration": round(outro_duration, 3),
            "fade": bool(outro.get("fade", True)),
        }
        promo_duration += outro["duration"]

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
            branding_enabled,
            branding_title,
            branding_handle,
            metadata,
            hook,
            outro,
            encoder_mode,
            job_id,
        )
    except RenderCancelledError as error:
        raise VideoServiceError(str(error), 409) from error
    except RuntimeError as error:
        raise VideoServiceError(str(error), 503) from error
    except subprocess.CalledProcessError as error:
        detail = (error.stderr or "").strip()
        raise VideoServiceError(
            f"FFmpeg no pudo generar el clip {clip_index:02d}.",
            422,
            detail[-4000:] if detail else None,
        ) from error

    if not output_path.exists():
        raise VideoServiceError(
            f"FFmpeg finalizó, pero no se encontró el clip {clip_index:02d}.",
            500,
        )

    return {
        "message": f"Clip {clip_index:02d} generado correctamente.",
        "index": clip_index,
        "filename": output_name,
        "size": output_path.stat().st_size,
        "duration": round(clip_duration + promo_duration, 3),
        "content_duration": round(clip_duration, 3),
        "hook_enabled": hook is not None,
        "hook_duration": hook["duration"] if hook else 0,
        "outro_enabled": outro is not None,
        "outro_duration": outro["duration"] if outro else 0,
        "output_format": output_format,
        "resolution": (
            "1080x1920"
            if output_format == "vertical"
            else f"{metadata.get('width')}x{metadata.get('height')}"
        ),
        "vertical_scale": (
            vertical_scale if output_format == "vertical" else None
        ),
        "vertical_position": (
            vertical_position if output_format == "vertical" else None
        ),
        "blur_strength": (
            blur_strength if output_format == "vertical" else None
        ),
        "branding_enabled": branding_enabled,
        "branding_title": branding_title if branding_enabled else None,
        "branding_handle": branding_handle if branding_enabled else None,
        "encoder_mode": encoder_mode,
        "encoder_used": getattr(result, "encoder_used", "CPU · libx264"),
        "output_folder": str(project_output.resolve()),
        "project_name": project_name,
        "format_folder": format_folder,
        "ffmpeg_log": (result.stderr or "")[-500:],
    }
