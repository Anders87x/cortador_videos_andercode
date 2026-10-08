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
    branding_items = []

    if branding_enabled and branding_title:
        branding_items.append(("title", branding_title))

    if branding_enabled and branding_handle:
        branding_items.append(("handle", branding_handle))

    if not branding_items:
        return [], input_label

    font_path = find_branding_font()

    if not font_path:
        raise RuntimeError(
            "No se encontró una fuente compatible para renderizar el branding."
        )

    escaped_font = escape_filter_path(font_path)
    current_label = input_label
    filters = []

    for index, (kind, text) in enumerate(branding_items, start=1):
        next_label = f"brand{index}"
        escaped_text = escape_drawtext_text(text)
        is_title = kind == "title"
        font_size = branding_font_size(text, large=is_title)
        y_position = "110" if is_title else "h-text_h-110"
        box_border = 24 if is_title else 18

        filters.append(
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
    source_metadata=None,
    hook=None,
    outro=None,
):
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
        )

    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True,
        encoding="utf-8",
        errors="replace",
    )
