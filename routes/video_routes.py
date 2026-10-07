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

from services.project_service import (
    clear_projects,
    delete_project,
    get_project,
    list_projects,
    project_id_from_filename,
    register_project,
    update_project,
)
from services.video_service import (
    VideoServiceError,
    analyze_uploaded_video,
    generate_video_clip,
    save_uploaded_video,
)


video_bp = Blueprint("video", __name__)


def service_error_response(error):
    return jsonify(error.to_dict()), error.status_code


def project_with_url(project):
    data = dict(project)

    if data.get("available") and data.get("filename"):
        data["url"] = url_for(
            "video.uploaded_video",
            filename=data["filename"],
        )

    return data


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

    project = register_project(
        current_app.config["PROJECTS_FILE"],
        data["filename"],
        data["original_name"],
        data["size"],
    )

    data["project_id"] = project["id"]
    data["url"] = url_for(
        "video.uploaded_video",
        filename=data["filename"],
    )

    return jsonify(data)


@video_bp.post("/analyze")
def analyze_video():
    payload = request.get_json(silent=True) or {}
    filename = payload.get("filename", "")

    try:
        data = analyze_uploaded_video(
            filename,
            payload.get("intro_seconds", 5),
            payload.get("clip_seconds", 30),
            current_app.config["UPLOAD_FOLDER"],
        )
    except VideoServiceError as error:
        return service_error_response(error)

    if filename:
        project_id = project_id_from_filename(filename)
        update_project(
            current_app.config["PROJECTS_FILE"],
            project_id,
            duration=data["metadata"].get("duration"),
            intro_seconds=data["intro_seconds"],
            clip_seconds=data["clip_seconds"],
        )

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

    project_id = data["project_name"]

    update_project(
        current_app.config["PROJECTS_FILE"],
        project_id,
        output_format=payload.get("output_format", "original"),
        vertical_scale=payload.get("vertical_scale", 100),
        vertical_position=payload.get("vertical_position", "center"),
        blur_strength=payload.get("blur_strength", 25),
        branding_enabled=payload.get("branding_enabled") is True,
        branding_title=str(payload.get("branding_title") or "").strip(),
        branding_handle=str(payload.get("branding_handle") or "").strip(),
    )

    data["url"] = url_for(
        "video.generated_clip",
        project=data.pop("project_name"),
        format_folder=data.pop("format_folder"),
        filename=data["filename"],
    )

    return jsonify(data)


@video_bp.get("/projects")
def projects_index():
    projects = list_projects(
        current_app.config["PROJECTS_FILE"],
        current_app.config["UPLOAD_FOLDER"],
    )

    return jsonify({
        "projects": [project_with_url(project) for project in projects],
    })


@video_bp.get("/projects/<project_id>")
def project_detail(project_id):
    if secure_filename(project_id) != project_id:
        return jsonify({"message": "Proyecto inválido."}), 400

    project = get_project(
        current_app.config["PROJECTS_FILE"],
        project_id,
    )

    if project is None:
        return jsonify({"message": "Proyecto no encontrado."}), 404

    filename = project.get("filename", "")
    project["available"] = bool(
        filename
        and (
            Path(current_app.config["UPLOAD_FOLDER"]) / filename
        ).exists()
    )

    return jsonify(project_with_url(project))


@video_bp.delete("/projects/<project_id>")
def project_delete(project_id):
    if secure_filename(project_id) != project_id:
        return jsonify({"message": "Proyecto inválido."}), 400

    deleted = delete_project(
        current_app.config["PROJECTS_FILE"],
        project_id,
        current_app.config["UPLOAD_FOLDER"],
        current_app.config["OUTPUT_FOLDER"],
    )

    if not deleted:
        return jsonify({"message": "Proyecto no encontrado."}), 404

    return jsonify({"message": "Proyecto y archivos eliminados correctamente."})


@video_bp.delete("/projects")
def projects_clear():
    deleted = clear_projects(
        current_app.config["PROJECTS_FILE"],
        current_app.config["UPLOAD_FOLDER"],
        current_app.config["OUTPUT_FOLDER"],
    )

    return jsonify({
        "message": f"Se eliminaron {deleted} proyectos y sus archivos locales.",
        "deleted": deleted,
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
