from pathlib import Path

from werkzeug.utils import secure_filename


ALLOWED_PROMO_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


class OutroServiceError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _validate_project_id(project_id):
    return bool(project_id and secure_filename(project_id) == project_id)


def project_asset_folder(assets_root, project_id):
    if not _validate_project_id(project_id):
        raise OutroServiceError("Proyecto inválido.", 400)

    return Path(assets_root) / project_id


def _validate_image(image, max_size_bytes):
    if image is None or not image.filename:
        raise OutroServiceError("Selecciona una imagen promocional.", 400)

    if "." not in image.filename:
        raise OutroServiceError(
            "Formato no permitido. Usa PNG, JPG, JPEG o WEBP.",
            400,
        )

    extension = image.filename.rsplit(".", 1)[1].lower()

    if extension not in ALLOWED_PROMO_EXTENSIONS:
        raise OutroServiceError(
            "Formato no permitido. Usa PNG, JPG, JPEG o WEBP.",
            400,
        )

    stream = image.stream
    stream.seek(0, 2)
    size = stream.tell()
    stream.seek(0)

    if size <= 0:
        raise OutroServiceError("La imagen está vacía.", 400)

    if size > max_size_bytes:
        max_mb = max_size_bytes // (1024 * 1024)
        raise OutroServiceError(
            f"La imagen supera el límite de {max_mb} MB.",
            413,
        )

    return extension


def _save_project_image(
    image,
    project_id,
    assets_root,
    max_size_bytes,
    asset_name,
):
    extension = _validate_image(image, max_size_bytes)
    folder = project_asset_folder(assets_root, project_id)
    folder.mkdir(parents=True, exist_ok=True)

    for existing in folder.glob(f"{asset_name}.*"):
        if existing.is_file():
            existing.unlink()

    filename = f"{asset_name}.{extension}"
    destination = folder / filename
    image.save(destination)

    return {
        "filename": filename,
        "original_name": image.filename,
        "size": destination.stat().st_size,
        "path": destination,
    }


def _delete_project_image(project_id, assets_root, asset_name):
    folder = project_asset_folder(assets_root, project_id)
    deleted = False

    if folder.exists():
        for existing in folder.glob(f"{asset_name}.*"):
            if existing.is_file():
                existing.unlink()
                deleted = True

        try:
            folder.rmdir()
        except OSError:
            pass

    return deleted


def _resolve_project_image(project_id, filename, assets_root, asset_name):
    if not filename:
        return None

    folder = project_asset_folder(assets_root, project_id)
    safe_filename = secure_filename(Path(filename).name)

    if safe_filename != filename or not safe_filename.startswith(f"{asset_name}."):
        return None

    path = folder / safe_filename

    if not path.exists() or not path.is_file():
        return None

    return path


def save_outro_image(image, project_id, assets_root, max_size_bytes):
    return _save_project_image(
        image,
        project_id,
        assets_root,
        max_size_bytes,
        "outro",
    )


def delete_outro_image(project_id, assets_root):
    return _delete_project_image(project_id, assets_root, "outro")


def resolve_outro_image(project_id, filename, assets_root):
    return _resolve_project_image(
        project_id,
        filename,
        assets_root,
        "outro",
    )


def save_hook_image(image, project_id, assets_root, max_size_bytes):
    return _save_project_image(
        image,
        project_id,
        assets_root,
        max_size_bytes,
        "hook",
    )


def delete_hook_image(project_id, assets_root):
    return _delete_project_image(project_id, assets_root, "hook")


def resolve_hook_image(project_id, filename, assets_root):
    return _resolve_project_image(
        project_id,
        filename,
        assets_root,
        "hook",
    )
