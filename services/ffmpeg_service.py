import json
import shutil
import subprocess
from pathlib import Path


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


def find_branding_font():
    candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
    ]

    return next((path for path in candidates if path.exists()), None)


def escape_drawtext_text(value):
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace("'", "\\'")
        .replace(":", "\\:")
        .replace("%", "\\%")
        .replace("\n", " ")
        .replace("\r", " ")
    )


def escape_filter_path(path):
    return (
        str(path)
        .replace("\\", "/")
        .replace(":", "\\:")
        .replace("'", "\\'")
    )


def branding_font_size(text, large=True):
    length = len(text)

    if large:
        if length <= 32:
            return 52
        if length <= 50:
            return 44
        return 36

    return 38 if length <= 24 else 32


def build_vertical_filter(
    vertical_scale,
    vertical_position,
    blur_strength,
    branding_enabled=False,
    branding_title="",
    branding_handle="",
):
    target_width = max(2, int(round(1080 * vertical_scale / 100)))
    target_height = max(2, int(round(1920 * vertical_scale / 100)))

    if target_width % 2:
        target_width -= 1

    if target_height % 2:
        target_height -= 1

    y_expression = {
        "top": "0",
        "center": "(H-h)/2",
        "bottom": "H-h",
    }[vertical_position]

    branding_items = []

    if branding_enabled and branding_title:
        branding_items.append(("title", branding_title))

    if branding_enabled and branding_handle:
        branding_items.append(("handle", branding_handle))

    base_label = "basev"

    filter_parts = [
        "[0:v]split=2[bg][fg]",
        (
            "[bg]scale=1080:1920:force_original_aspect_ratio=increase,"
            f"crop=1080:1920,boxblur={blur_strength}:2[bgv]"
        ),
        (
            f"[fg]scale={target_width}:{target_height}:"
            "force_original_aspect_ratio=decrease[fgv]"
        ),
        f"[bgv][fgv]overlay=(W-w)/2:{y_expression}[{base_label}]",
    ]

    current_label = base_label

    if branding_items:
        font_path = find_branding_font()

        if not font_path:
            raise RuntimeError(
                "No se encontró una fuente compatible para renderizar el branding."
            )

        escaped_font = escape_filter_path(font_path)

        for index, (kind, text) in enumerate(branding_items, start=1):
            next_label = f"brand{index}"
            escaped_text = escape_drawtext_text(text)
            is_title = kind == "title"
            font_size = branding_font_size(text, large=is_title)
            y_position = "110" if is_title else "h-text_h-110"
            box_border = 24 if is_title else 18

            filter_parts.append(
                (
                    f"[{current_label}]drawtext="
                    f"fontfile='{escaped_font}':"
                    f"text='{escaped_text}':"
                    "expansion=none:"
                    "fontcolor=white:"
                    f"fontsize={font_size}:"
                    "x=(w-text_w)/2:"
                    f"y={y_position}:"
                    "box=1:"
                    "boxcolor=black@0.52:"
                    f"boxborderw={box_border}:"
                    "borderw=1:"
                    "bordercolor=black@0.35"
                    f"[{next_label}]"
                )
            )
            current_label = next_label

    filter_parts.append(f"[{current_label}]format=yuv420p[vout]")

    return ";".join(filter_parts)


def build_ffmpeg_command(
    video_path,
    output_path,
    start,
    clip_duration,
    output_format,
    vertical_scale=100,
    vertical_position="center",
    blur_strength=25,
    branding_enabled=False,
    branding_title="",
    branding_handle="",
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
        filter_complex = build_vertical_filter(
            vertical_scale,
            vertical_position,
            blur_strength,
            branding_enabled,
            branding_title,
            branding_handle,
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


def render_clip(
    video_path,
    output_path,
    start,
    clip_duration,
    output_format,
    vertical_scale=100,
    vertical_position="center",
    blur_strength=25,
    branding_enabled=False,
    branding_title="",
    branding_handle="",
):
    command = build_ffmpeg_command(
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
    )

    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True,
        encoding="utf-8",
        errors="replace",
    )
