from pathlib import Path

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

from services.video_service import (
    VideoServiceError,
    analyze_uploaded_video,
    generate_video_clip,
    save_uploaded_video,
)


video_bp = Blueprint("video", __name__)


def service_error_response(error):
    return jsonify(error.to_dict()), error.status_code


@video_bp.get("/")
def index():
    return render_template("index.html")


@video_bp.post("/upload")
def upload_video():
    if "video" not in request.files:
        return jsonify({"message": "No se recibió ningún video."}), 400

    try:
        data = save_uploaded_video(
            request.files["video"],
            current_app.config["UPLOAD_FOLDER"],
        )
    except VideoServiceError as error:
        return service_error_response(error)

    data["url"] = url_for(
        "video.uploaded_video",
        filename=data["filename"],
    )

    return jsonify(data)


@video_bp.post("/analyze")
def analyze_video():
    payload = request.get_json(silent=True) or {}

    try:
        data = analyze_uploaded_video(
            payload.get("filename", ""),
            payload.get("intro_seconds", 5),
            payload.get("clip_seconds", 30),
            current_app.config["UPLOAD_FOLDER"],
        )
    except VideoServiceError as error:
        return service_error_response(error)

    return jsonify(data)


@video_bp.post("/generate-clip")
def generate_clip():
    payload = request.get_json(silent=True) or {}

    try:
        data = generate_video_clip(
            payload,
            current_app.config["UPLOAD_FOLDER"],
            current_app.config["OUTPUT_FOLDER"],
        )
    except VideoServiceError as error:
        return service_error_response(error)

    data["url"] = url_for(
        "video.generated_clip",
        project=data.pop("project_name"),
        format_folder=data.pop("format_folder"),
        filename=data["filename"],
    )

    return jsonify(data)


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
