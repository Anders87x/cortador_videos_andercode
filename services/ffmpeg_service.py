import json
import shutil
import subprocess
from functools import lru_cache
from pathlib import Path

from services.render_manager import (
    is_job_cancelled,
    register_process,
    unregister_process,
)


def ffprobe_available():
    return shutil.which("ffprobe") is not None


def ffmpeg_available():
    return shutil.which("ffmpeg") is not None


class RenderCancelledError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def encoder_capabilities():
    if not ffmpeg_available():
        return {"nvenc": False}

    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-encoders"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    output = f"{result.stdout}\n{result.stderr}"

    return {
        "nvenc": "h264_nvenc" in output,
    }


def nvenc_available():
    return bool(encoder_capabilities().get("nvenc"))


def _video_encoder_args(encoder):
    if encoder == "gpu":
        return [
            "-c:v",
            "h264_nvenc",
            "-preset",
            "p5",
            "-tune",
            "hq",
            "-rc",
            "vbr",
            "-cq",
            "20",
            "-b:v",
            "0",
        ]

    return [
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "20",
    ]


def _run_ffmpeg(command, job_id=None):
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    register_process(job_id, process)

    try:
        stdout, stderr = process.communicate()
    finally:
        unregister_process(job_id, process)

    if is_job_cancelled(job_id):
        raise RenderCancelledError("Render cancelado por el usuario.")

    result = subprocess.CompletedProcess(
        command,
        process.returncode,
        stdout,
        stderr,
    )

    if process.returncode != 0:
        raise subprocess.CalledProcessError(
            process.returncode,
            command,
            output=stdout,
            stderr=stderr,
        )

    return result


def _nvenc_runtime_error(stderr):
    text = (stderr or "").lower()

    markers = (
        "nvenc",
        "cuda",
        "no capable devices found",
        "cannot load",
        "driver does not support",
        "unsupported device",
    )

    return any(marker in text for marker in markers)


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


def balance_branding_title(text, max_chars=24, max_lines=3):
    clean_text = " ".join(str(text or "").split())

    if not clean_text:
        return []

    words = clean_text.split(" ")
    total_chars = len(clean_text)
    line_count = max(
        1,
        min(
            max_lines,
            len(words),
            (total_chars + max_chars - 1) // max_chars,
        ),
    )

    if line_count == 1:
        return [clean_text]

    target = total_chars / line_count
    best_lines = None
    best_score = None

    def evaluate(lines):
        nonlocal best_lines, best_score

        lengths = [len(line) for line in lines]
        overflow = sum(
            max(0, length - max_chars) ** 2 * 100
            for length in lengths
        )
        balance = sum(
            (length - target) ** 2
            for length in lengths
        )
        spread = (max(lengths) - min(lengths)) ** 2
        score = overflow + balance + spread

        if best_score is None or score < best_score:
            best_score = score
            best_lines = lines

    def search(start_index, remaining_lines, current_lines):
        if remaining_lines == 1:
            final_line = " ".join(words[start_index:])

            if final_line:
                evaluate(current_lines + [final_line])

            return

        max_end = len(words) - remaining_lines + 1

        for end_index in range(start_index + 1, max_end + 1):
            line = " ".join(words[start_index:end_index])
            search(
                end_index,
                remaining_lines - 1,
                current_lines + [line],
            )

    search(0, line_count, [])

    return best_lines or [clean_text]


def branding_font_size(text, large=True):
    length = len(text)

    if large:
        if length <= 18:
            return 52
        if length <= 24:
            return 48
        return 44

    if length <= 16:
        return 38

    if length <= 24:
        return 32

    if length <= 32:
        return 28

    return 24

def _safe_fps(value):
    try:
        fps = float(value)
    except (TypeError, ValueError):
        fps = 30.0

    if fps <= 0 or fps > 120:
        fps = 30.0

    return round(fps, 3)


def _even_dimension(value, fallback):
    try:
        dimension = int(value)
    except (TypeError, ValueError):
        dimension = fallback

    dimension = max(2, dimension)

    if dimension % 2:
        dimension -= 1

    return dimension


def _build_branding_filters(
    input_label,
    branding_enabled,
    branding_title,
    branding_handle,
):
    if not branding_enabled:
        return [], input_label

    if not branding_title and not branding_handle:
        return [], input_label

    font_path = find_branding_font()

    if not font_path:
        raise RuntimeError(
            "No se encontró una fuente compatible para renderizar el branding."
        )

    escaped_font = escape_filter_path(font_path)
    current_label = input_label
    filters = []

    if branding_title:
        title_lines = balance_branding_title(branding_title)
        longest_line = max(title_lines, key=len)
        font_size = branding_font_size(longest_line, large=True)
        line_height = round(font_size * 1.15)
        box_width = round(1080 * 0.84)
        box_top = round(1920 * 0.058)
        padding_y = 24
        box_height = (
            len(title_lines) * line_height
            + (padding_y * 2)
        )

        box_label = "brand_title_box"
        filters.append(
            (
                f"[{current_label}]drawbox="
                f"x=(iw-{box_width})/2:"
                f"y={box_top}:"
                f"w={box_width}:"
                f"h={box_height}:"
                "color=black@0.56:"
                "t=fill"
                f"[{box_label}]"
            )
        )
        current_label = box_label

        for line_index, line in enumerate(title_lines, start=1):
            next_label = f"brand_title_{line_index}"
            escaped_line = escape_drawtext_text(line)
            y_position = (
                box_top
                + padding_y
                + ((line_index - 1) * line_height)
            )

            filters.append(
                (
                    f"[{current_label}]drawtext="
                    f"fontfile='{escaped_font}':"
                    f"text='{escaped_line}':"
                    "expansion=none:"
                    "fontcolor=white:"
                    f"fontsize={font_size}:"
                    "x=(w-text_w)/2:"
                    f"y={y_position}:"
                    "borderw=1:"
                    "bordercolor=black@0.35"
                    f"[{next_label}]"
                )
            )
            current_label = next_label

    if branding_handle:
        next_label = "brand_handle"
        escaped_handle = escape_drawtext_text(branding_handle)
        font_size = branding_font_size(
            branding_handle,
            large=False,
        )

        filters.append(
            (
                f"[{current_label}]drawtext="
                f"fontfile='{escaped_font}':"
                f"text='{escaped_handle}':"
                "expansion=none:"
                "fontcolor=white:"
                f"fontsize={font_size}:"
                "x=(w-text_w)/2:"
                "y=h-text_h-110:"
                "box=1:"
                "boxcolor=black@0.52:"
                "boxborderw=18:"
                "borderw=1:"
                "bordercolor=black@0.35"
                f"[{next_label}]"
            )
        )
        current_label = next_label

    return filters, current_label

def _build_main_video_filters(
    output_format,
    target_width,
    target_height,
    fps,
    vertical_scale,
    vertical_position,
    blur_strength,
    branding_enabled,
    branding_title,
    branding_handle,
):
    filters = []

    if output_format == "vertical":
        content_width = _even_dimension(
            round(target_width * vertical_scale / 100),
            target_width,
        )
        content_height = _even_dimension(
            round(target_height * vertical_scale / 100),
            target_height,
        )

        y_expression = {
            "top": "0",
            "center": "(H-h)/2",
            "bottom": "H-h",
        }[vertical_position]

        filters.extend([
            "[0:v]setpts=PTS-STARTPTS,split=2[mainbg][mainfg]",
            (
                f"[mainbg]scale={target_width}:{target_height}:"
                "force_original_aspect_ratio=increase,"
                f"crop={target_width}:{target_height},"
                f"boxblur={blur_strength}:2[mainbgv]"
            ),
            (
                f"[mainfg]scale={content_width}:{content_height}:"
                "force_original_aspect_ratio=decrease[mainfgv]"
            ),
            (
                f"[mainbgv][mainfgv]overlay=(W-w)/2:{y_expression},"
                "setsar=1[mainbase]"
            ),
        ])
        current_label = "mainbase"
    else:
        filters.append(
            (
                f"[0:v]setpts=PTS-STARTPTS,"
                f"scale={target_width}:{target_height},"
                "setsar=1[mainbase]"
            )
        )
        current_label = "mainbase"

    branding_filters, current_label = _build_branding_filters(
        current_label,
        branding_enabled,
        branding_title,
        branding_handle,
    )
    filters.extend(branding_filters)

    filters.append(
        (
            f"[{current_label}]fps={fps},"
            "settb=AVTB,format=yuv420p[clipv]"
        )
    )

    return filters


def _promo_fade_chain(duration, enabled):
    if not enabled:
        return ""

    fade_duration = min(0.4, max(0.05, duration / 4))
    fade_out_start = max(0, duration - fade_duration)

    return (
        f",fade=t=in:st=0:d={fade_duration:.3f}"
        f",fade=t=out:st={fade_out_start:.3f}:d={fade_duration:.3f}"
    )


def _build_promo_filters(
    input_index,
    prefix,
    target_width,
    target_height,
    fps,
    duration,
    fade_enabled,
):
    fade_chain = _promo_fade_chain(duration, fade_enabled)

    filters = [
        (
            f"[{input_index}:v]setpts=PTS-STARTPTS,"
            f"scale={target_width}:{target_height}:"
            "force_original_aspect_ratio=decrease:"
            "force_divisible_by=2,"
            f"pad={target_width}:{target_height}:"
            "(ow-iw)/2:(oh-ih)/2:color=black,"
            f"setsar=1,fps={fps},"
            f"trim=duration={duration:.3f},"
            f"setpts=PTS-STARTPTS,format=yuv420p"
            f"{fade_chain}[{prefix}v]"
        ),
        (
            "anullsrc=channel_layout=stereo:sample_rate=48000,"
            "aformat=sample_fmts=fltp:channel_layouts=stereo,"
            f"atrim=duration={duration:.3f},"
            f"asetpts=PTS-STARTPTS[{prefix}a]"
        ),
    ]

    return filters


def _build_promo_command(
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
    source_metadata,
    hook,
    outro,
    encoder="cpu",
):
    fps = _safe_fps(source_metadata.get("fps"))

    if output_format == "vertical":
        target_width = 1080
        target_height = 1920
    else:
        target_width = _even_dimension(source_metadata.get("width"), 1920)
        target_height = _even_dimension(source_metadata.get("height"), 1080)

    command = [
        "ffmpeg",
        "-y",
        "-ss",
        f"{start:.3f}",
        "-t",
        f"{clip_duration:.3f}",
        "-i",
        str(video_path),
    ]

    segments = []
    input_index = 1

    if hook:
        command.extend([
            "-loop",
            "1",
            "-framerate",
            str(fps),
            "-t",
            f"{hook['duration']:.3f}",
            "-i",
            str(hook["image_path"]),
        ])
        segments.append(("hook", input_index, hook))
        input_index += 1

    if outro:
        command.extend([
            "-loop",
            "1",
            "-framerate",
            str(fps),
            "-t",
            f"{outro['duration']:.3f}",
            "-i",
            str(outro["image_path"]),
        ])
        outro_input_index = input_index
    else:
        outro_input_index = None

    filters = _build_main_video_filters(
        output_format,
        target_width,
        target_height,
        fps,
        vertical_scale,
        vertical_position,
        blur_strength,
        branding_enabled,
        branding_title,
        branding_handle,
    )

    if source_metadata.get("has_audio"):
        filters.append(
            (
                "[0:a:0]aresample=48000,"
                "aformat=sample_fmts=fltp:channel_layouts=stereo,"
                f"atrim=duration={clip_duration:.3f},"
                "asetpts=PTS-STARTPTS[clipa]"
            )
        )
    else:
        filters.append(
            (
                "anullsrc=channel_layout=stereo:sample_rate=48000,"
                "aformat=sample_fmts=fltp:channel_layouts=stereo,"
                f"atrim=duration={clip_duration:.3f},"
                "asetpts=PTS-STARTPTS[clipa]"
            )
        )

    concat_segments = []

    if hook:
        filters.extend(
            _build_promo_filters(
                segments[0][1],
                "hook",
                target_width,
                target_height,
                fps,
                hook["duration"],
                hook["fade"],
            )
        )
        concat_segments.append(("hookv", "hooka"))

    concat_segments.append(("clipv", "clipa"))

    if outro:
        filters.extend(
            _build_promo_filters(
                outro_input_index,
                "outro",
                target_width,
                target_height,
                fps,
                outro["duration"],
                outro["fade"],
            )
        )
        concat_segments.append(("outrov", "outroa"))

    concat_inputs = "".join(
        f"[{video_label}][{audio_label}]"
        for video_label, audio_label in concat_segments
    )
    filters.append(
        (
            f"{concat_inputs}concat=n={len(concat_segments)}:"
            "v=1:a=1[vconcat][afinal]"
        )
    )
    filters.append(
        f"[vconcat]fps={fps},format=yuv420p[vfinal]"
    )

    command.extend([
        "-filter_complex",
        ";".join(filters),
        "-map",
        "[vfinal]",
        "-map",
        "[afinal]",
        "-sn",
        "-r",
        str(fps),
        *_video_encoder_args(encoder),
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-ar",
        "48000",
        "-ac",
        "2",
        "-movflags",
        "+faststart",
        str(output_path),
    ])

    return command


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
        f"[bgv][fgv]overlay=(W-w)/2:{y_expression}[basev]",
    ]

    branding_filters, current_label = _build_branding_filters(
        "basev",
        branding_enabled,
        branding_title,
        branding_handle,
    )
    filter_parts.extend(branding_filters)
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
    encoder="cpu",
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
            *_video_encoder_args(encoder),
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
        *_video_encoder_args(encoder),
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
    source_metadata=None,
    hook=None,
    outro=None,
    encoder_mode="auto",
    job_id=None,
):
    if encoder_mode not in {"auto", "gpu", "cpu"}:
        raise RuntimeError("El motor de render seleccionado no es válido.")

    if encoder_mode == "gpu" and not nvenc_available():
        raise RuntimeError(
            "NVIDIA NVENC no está disponible en esta instalación/equipo."
        )

    if encoder_mode == "auto":
        encoders = ["gpu", "cpu"] if nvenc_available() else ["cpu"]
    else:
        encoders = [encoder_mode]

    last_error = None

    for encoder in encoders:
        if hook or outro:
            if not source_metadata:
                raise RuntimeError(
                    "No se recibieron los metadatos necesarios para renderizar hook/outro."
                )

            command = _build_promo_command(
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
                source_metadata,
                hook,
                outro,
                encoder,
            )
        else:
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
                encoder,
            )

        try:
            result = _run_ffmpeg(command, job_id)
            result.encoder_used = (
                "NVIDIA NVENC"
                if encoder == "gpu"
                else "CPU · libx264"
            )
            return result
        except RenderCancelledError:
            raise
        except subprocess.CalledProcessError as error:
            last_error = error

            if (
                encoder_mode == "auto"
                and encoder == "gpu"
                and _nvenc_runtime_error(error.stderr)
            ):
                continue

            raise

    if last_error is not None:
        raise last_error

    raise RuntimeError("No se pudo seleccionar un motor de render.")
