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

from services.ffmpeg_service import nvenc_available
from services.outro_service import (
    OutroServiceError,
    delete_hook_image,
    delete_outro_image,
    resolve_hook_image,
    resolve_outro_image,
    save_hook_image,
    save_outro_image,
)
from services.render_log_service import append_render_log
from services.render_manager import cancel_job, finish_job, is_job_cancelled
from services.system_service import open_folder
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


def outro_error_response(error):
    return jsonify({"message": error.message}), error.status_code


def project_with_url(project):
    data = dict(project)

    if data.get("available") and data.get("filename"):
        data["url"] = url_for(
            "video.uploaded_video",
            filename=data["filename"],
        )

    if data.get("hook_image") and data.get("id"):
        data["hook_image_url"] = url_for(
            "video.project_hook_image",
            project_id=data["id"],
        )

    if data.get("outro_image") and data.get("id"):
        data["outro_image_url"] = url_for(
            "video.project_outro_image",
            project_id=data["id"],
        )

    if data.get("id"):
        project_output = (
            Path(current_app.config["OUTPUT_FOLDER"])
            / data["id"]
        )
        data["output_available"] = project_output.exists()

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


@video_bp.get("/render-capabilities")
def render_capabilities():
    return jsonify({
        "nvenc_available": nvenc_available(),
        "default_engine": "auto",
    })


@video_bp.post("/render-jobs/<job_id>/cancel")
def render_job_cancel(job_id):
    if secure_filename(job_id) != job_id:
        return jsonify({"message": "Identificador de render inválido."}), 400

    cancel_job(job_id)

    return jsonify({
        "message": "Cancelación solicitada. FFmpeg se detendrá en cuanto sea posible.",
        "job_id": job_id,
    })


@video_bp.post("/render-jobs/<job_id>/finish")
def render_job_finish(job_id):
    if secure_filename(job_id) != job_id:
        return jsonify({"message": "Identificador de render inválido."}), 400

    finish_job(job_id)

    return jsonify({"message": "Trabajo de render finalizado."})


@video_bp.post("/generate-clip")
def generate_clip():
    payload = request.get_json(silent=True) or {}
    filename = str(payload.get("filename") or "")
    job_id = str(payload.get("job_id") or "").strip()
    project_id = project_id_from_filename(filename) if filename else ""
    project = (
        get_project(
            current_app.config["PROJECTS_FILE"],
            project_id,
        )
        if project_id
        else None
    )

    if job_id and is_job_cancelled(job_id):
        return jsonify({"message": "Render cancelado por el usuario."}), 409

    promo_config = {}

    if project and project.get("hook_enabled"):
        hook_path = resolve_hook_image(
            project_id,
            project.get("hook_image"),
            current_app.config["PROJECT_ASSETS_FOLDER"],
        )

        if hook_path is None:
            return jsonify({
                "message": "El hook está activo, pero su imagen ya no está disponible."
            }), 422

        promo_config["hook"] = {
            "image_path": hook_path,
            "duration": project.get("hook_duration", 0.5),
            "fade": bool(project.get("hook_fade", True)),
        }

    if project and project.get("outro_enabled"):
        outro_path = resolve_outro_image(
            project_id,
            project.get("outro_image"),
            current_app.config["PROJECT_ASSETS_FOLDER"],
        )

        if outro_path is None:
            return jsonify({
                "message": "El outro está activo, pero su imagen ya no está disponible."
            }), 422

        promo_config["outro"] = {
            "image_path": outro_path,
            "duration": project.get("outro_duration", 5),
            "fade": bool(project.get("outro_fade", True)),
        }

    try:
        data = generate_video_clip(
            payload,
            current_app.config["UPLOAD_FOLDER"],
            current_app.config["OUTPUT_FOLDER"],
            promo_config,
        )
    except VideoServiceError as error:
        append_render_log(
            current_app.config["RENDER_LOG_FILE"],
            status="cancelled" if error.status_code == 409 else "error",
            project_id=project_id or None,
            filename=filename or None,
            job_id=job_id or None,
            clip_index=payload.get("index"),
            output_format=payload.get("output_format", "vertical"),
            encoder_mode=payload.get("encoder_mode", "auto"),
            message=error.message,
            detail=error.detail,
        )
        return service_error_response(error)

    project_id = data["project_name"]

    update_project(
        current_app.config["PROJECTS_FILE"],
        project_id,
        output_format=payload.get("output_format", "vertical"),
        vertical_scale=payload.get("vertical_scale", 100),
        vertical_position=payload.get("vertical_position", "center"),
        blur_strength=payload.get("blur_strength", 25),
        branding_enabled=payload.get("branding_enabled") is True,
        branding_title=str(payload.get("branding_title") or "").strip(),
        branding_handle=str(payload.get("branding_handle") or "").strip(),
    )

    append_render_log(
        current_app.config["RENDER_LOG_FILE"],
        status="success",
        project_id=project_id,
        filename=filename,
        job_id=job_id or None,
        clip_index=data.get("index"),
        output_format=data.get("output_format"),
        duration=data.get("duration"),
        encoder_mode=data.get("encoder_mode"),
        encoder_used=data.get("encoder_used"),
        hook_enabled=data.get("hook_enabled"),
        outro_enabled=data.get("outro_enabled"),
        output_file=data.get("filename"),
    )

    data["url"] = url_for(
        "video.generated_clip",
        project=data.pop("project_name"),
        format_folder=data.pop("format_folder"),
        filename=data["filename"],
    )

    return jsonify(data)


@video_bp.post("/projects/<project_id>/open-output")
def project_open_output(project_id):
    if secure_filename(project_id) != project_id:
        return jsonify({"message": "Proyecto inválido."}), 400

    project = get_project(
        current_app.config["PROJECTS_FILE"],
        project_id,
    )

    if project is None:
        return jsonify({"message": "Proyecto no encontrado."}), 404

    project_output = Path(current_app.config["OUTPUT_FOLDER"]) / project_id

    try:
        open_folder(project_output)
    except (FileNotFoundError, OSError) as error:
        return jsonify({"message": str(error)}), 404

    return jsonify({"message": "Carpeta de resultados abierta."})


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
        current_app.config["PROJECT_ASSETS_FOLDER"],
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
        current_app.config["PROJECT_ASSETS_FOLDER"],
    )

    return jsonify({
        "message": f"Se eliminaron {deleted} proyectos y sus archivos locales.",
        "deleted": deleted,
    })


@video_bp.get("/projects/<project_id>/hook")
def project_hook(project_id):
    if secure_filename(project_id) != project_id:
        return jsonify({"message": "Proyecto inválido."}), 400

    project = get_project(
        current_app.config["PROJECTS_FILE"],
        project_id,
    )

    if project is None:
        return jsonify({"message": "Proyecto no encontrado."}), 404

    data = {
        "project_id": project_id,
        "hook_enabled": bool(project.get("hook_enabled", False)),
        "hook_image": project.get("hook_image"),
        "hook_image_original_name": project.get("hook_image_original_name"),
        "hook_image_size": project.get("hook_image_size"),
        "hook_duration": project.get("hook_duration", 0.5),
        "hook_fade": bool(project.get("hook_fade", True)),
    }

    if project.get("hook_image"):
        data["hook_image_url"] = url_for(
            "video.project_hook_image",
            project_id=project_id,
        )

    return jsonify(data)


@video_bp.patch("/projects/<project_id>/hook")
def project_hook_update(project_id):
    if secure_filename(project_id) != project_id:
        return jsonify({"message": "Proyecto inválido."}), 400

    project = get_project(
        current_app.config["PROJECTS_FILE"],
        project_id,
    )

    if project is None:
        return jsonify({"message": "Proyecto no encontrado."}), 404

    payload = request.get_json(silent=True) or {}

    try:
        duration = float(
            payload.get("hook_duration", project.get("hook_duration", 0.5))
        )
    except (TypeError, ValueError):
        return jsonify({"message": "La duración del hook no es válida."}), 400

    if not 0.2 <= duration <= 3:
        return jsonify({
            "message": "La duración del hook debe estar entre 0.2 y 3 segundos."
        }), 400

    enabled = payload.get("hook_enabled") is True
    fade = payload.get("hook_fade") is not False

    if enabled and not project.get("hook_image"):
        return jsonify({
            "message": "Sube primero una imagen de gancho antes de activar el hook."
        }), 400

    updated = update_project(
        current_app.config["PROJECTS_FILE"],
        project_id,
        hook_enabled=enabled,
        hook_duration=round(duration, 2),
        hook_fade=fade,
    )

    return jsonify(project_with_url(updated))


@video_bp.post("/projects/<project_id>/hook-image")
def project_hook_image_upload(project_id):
    if secure_filename(project_id) != project_id:
        return jsonify({"message": "Proyecto inválido."}), 400

    project = get_project(
        current_app.config["PROJECTS_FILE"],
        project_id,
    )

    if project is None:
        return jsonify({"message": "Proyecto no encontrado."}), 404

    if "image" not in request.files:
        return jsonify({"message": "No se recibió ninguna imagen."}), 400

    try:
        image_data = save_hook_image(
            request.files["image"],
            project_id,
            current_app.config["PROJECT_ASSETS_FOLDER"],
            current_app.config["OUTRO_IMAGE_MAX_SIZE"],
        )
    except OutroServiceError as error:
        return outro_error_response(error)

    updated = update_project(
        current_app.config["PROJECTS_FILE"],
        project_id,
        hook_image=image_data["filename"],
        hook_image_original_name=image_data["original_name"],
        hook_image_size=image_data["size"],
        hook_enabled=True,
    )

    data = project_with_url(updated)
    data["message"] = "Imagen de gancho guardada correctamente."

    return jsonify(data)


@video_bp.get("/projects/<project_id>/hook-image")
def project_hook_image(project_id):
    if secure_filename(project_id) != project_id:
        return jsonify({"message": "Proyecto inválido."}), 400

    project = get_project(
        current_app.config["PROJECTS_FILE"],
        project_id,
    )

    if project is None:
        return jsonify({"message": "Proyecto no encontrado."}), 404

    image_path = resolve_hook_image(
        project_id,
        project.get("hook_image"),
        current_app.config["PROJECT_ASSETS_FOLDER"],
    )

    if image_path is None:
        return jsonify({"message": "Imagen de gancho no encontrada."}), 404

    return send_from_directory(
        image_path.parent,
        image_path.name,
        as_attachment=False,
    )


@video_bp.delete("/projects/<project_id>/hook-image")
def project_hook_image_delete(project_id):
    if secure_filename(project_id) != project_id:
        return jsonify({"message": "Proyecto inválido."}), 400

    project = get_project(
        current_app.config["PROJECTS_FILE"],
        project_id,
    )

    if project is None:
        return jsonify({"message": "Proyecto no encontrado."}), 404

    try:
        delete_hook_image(
            project_id,
            current_app.config["PROJECT_ASSETS_FOLDER"],
        )
    except OutroServiceError as error:
        return outro_error_response(error)

    updated = update_project(
        current_app.config["PROJECTS_FILE"],
        project_id,
        hook_enabled=False,
        hook_image=None,
        hook_image_original_name=None,
        hook_image_size=None,
    )

    data = project_with_url(updated)
    data["message"] = "Imagen de gancho eliminada."

    return jsonify(data)


@video_bp.get("/projects/<project_id>/outro")
def project_outro(project_id):
    if secure_filename(project_id) != project_id:
        return jsonify({"message": "Proyecto inválido."}), 400

    project = get_project(
        current_app.config["PROJECTS_FILE"],
        project_id,
    )

    if project is None:
        return jsonify({"message": "Proyecto no encontrado."}), 404

    data = {
        "project_id": project_id,
        "outro_enabled": bool(project.get("outro_enabled", False)),
        "outro_image": project.get("outro_image"),
        "outro_image_original_name": project.get("outro_image_original_name"),
        "outro_image_size": project.get("outro_image_size"),
        "outro_duration": project.get("outro_duration", 5),
        "outro_fade": bool(project.get("outro_fade", True)),
    }

    if project.get("outro_image"):
        data["outro_image_url"] = url_for(
            "video.project_outro_image",
            project_id=project_id,
        )

    return jsonify(data)


@video_bp.patch("/projects/<project_id>/outro")
def project_outro_update(project_id):
    if secure_filename(project_id) != project_id:
        return jsonify({"message": "Proyecto inválido."}), 400

    project = get_project(
        current_app.config["PROJECTS_FILE"],
        project_id,
    )

    if project is None:
        return jsonify({"message": "Proyecto no encontrado."}), 404

    payload = request.get_json(silent=True) or {}

    try:
        duration = int(payload.get("outro_duration", project.get("outro_duration", 5)))
    except (TypeError, ValueError):
        return jsonify({"message": "La duración del outro no es válida."}), 400

    if not 2 <= duration <= 10:
        return jsonify({"message": "La duración del outro debe estar entre 2 y 10 segundos."}), 400

    enabled = payload.get("outro_enabled") is True
    fade = payload.get("outro_fade") is not False

    if enabled and not project.get("outro_image"):
        return jsonify({
            "message": "Sube primero una imagen promocional antes de activar el outro."
        }), 400

    updated = update_project(
        current_app.config["PROJECTS_FILE"],
        project_id,
        outro_enabled=enabled,
        outro_duration=duration,
        outro_fade=fade,
    )

    return jsonify(project_with_url(updated))


@video_bp.post("/projects/<project_id>/outro-image")
def project_outro_image_upload(project_id):
    if secure_filename(project_id) != project_id:
        return jsonify({"message": "Proyecto inválido."}), 400

    project = get_project(
        current_app.config["PROJECTS_FILE"],
        project_id,
    )

    if project is None:
        return jsonify({"message": "Proyecto no encontrado."}), 404

    if "image" not in request.files:
        return jsonify({"message": "No se recibió ninguna imagen."}), 400

    try:
        image_data = save_outro_image(
            request.files["image"],
            project_id,
            current_app.config["PROJECT_ASSETS_FOLDER"],
            current_app.config["OUTRO_IMAGE_MAX_SIZE"],
        )
    except OutroServiceError as error:
        return outro_error_response(error)

    updated = update_project(
        current_app.config["PROJECTS_FILE"],
        project_id,
        outro_image=image_data["filename"],
        outro_image_original_name=image_data["original_name"],
        outro_image_size=image_data["size"],
        outro_enabled=True,
    )

    data = project_with_url(updated)
    data["message"] = "Imagen promocional guardada correctamente."

    return jsonify(data)


@video_bp.get("/projects/<project_id>/outro-image")
def project_outro_image(project_id):
    if secure_filename(project_id) != project_id:
        return jsonify({"message": "Proyecto inválido."}), 400

    project = get_project(
        current_app.config["PROJECTS_FILE"],
        project_id,
    )

    if project is None:
        return jsonify({"message": "Proyecto no encontrado."}), 404

    image_path = resolve_outro_image(
        project_id,
        project.get("outro_image"),
        current_app.config["PROJECT_ASSETS_FOLDER"],
    )

    if image_path is None:
        return jsonify({"message": "Imagen promocional no encontrada."}), 404

    return send_from_directory(
        image_path.parent,
        image_path.name,
        as_attachment=False,
    )


@video_bp.delete("/projects/<project_id>/outro-image")
def project_outro_image_delete(project_id):
    if secure_filename(project_id) != project_id:
        return jsonify({"message": "Proyecto inválido."}), 400

    project = get_project(
        current_app.config["PROJECTS_FILE"],
        project_id,
    )

    if project is None:
        return jsonify({"message": "Proyecto no encontrado."}), 404

    try:
        delete_outro_image(
            project_id,
            current_app.config["PROJECT_ASSETS_FOLDER"],
        )
    except OutroServiceError as error:
        return outro_error_response(error)

    updated = update_project(
        current_app.config["PROJECTS_FILE"],
        project_id,
        outro_enabled=False,
        outro_image=None,
        outro_image_original_name=None,
        outro_image_size=None,
    )

    data = project_with_url(updated)
    data["message"] = "Imagen promocional eliminada."

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
