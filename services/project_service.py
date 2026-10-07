import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _read_projects(projects_file):
    projects_file = Path(projects_file)

    if not projects_file.exists():
        return []

    try:
        data = json.loads(projects_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []

    return data if isinstance(data, list) else []


def _write_projects(projects_file, projects):
    projects_file = Path(projects_file)
    projects_file.parent.mkdir(parents=True, exist_ok=True)

    temp_file = projects_file.with_suffix(".tmp")
    temp_file.write_text(
        json.dumps(projects, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temp_file.replace(projects_file)


def project_id_from_filename(filename):
    return Path(filename).stem


def register_project(projects_file, filename, original_name, size):
    projects = _read_projects(projects_file)
    project_id = project_id_from_filename(filename)
    now = _now_iso()

    project = {
        "id": project_id,
        "filename": filename,
        "original_name": original_name,
        "size": size,
        "created_at": now,
        "updated_at": now,
        "duration": None,
        "intro_seconds": 5,
        "clip_seconds": 30,
        "output_format": "original",
        "vertical_scale": 100,
        "vertical_position": "center",
        "blur_strength": 25,
        "branding_enabled": False,
        "branding_title": "",
        "branding_handle": "@AnderCode",
    }

    projects = [item for item in projects if item.get("id") != project_id]
    projects.insert(0, project)
    _write_projects(projects_file, projects)

    return project


def update_project(projects_file, project_id, **changes):
    projects = _read_projects(projects_file)
    updated = None

    for project in projects:
        if project.get("id") == project_id:
            project.update(changes)
            project["updated_at"] = _now_iso()
            updated = project
            break

    if updated is not None:
        projects.sort(
            key=lambda item: item.get("updated_at", ""),
            reverse=True,
        )
        _write_projects(projects_file, projects)

    return updated


def get_project(projects_file, project_id):
    projects = _read_projects(projects_file)

    return next(
        (project for project in projects if project.get("id") == project_id),
        None,
    )


def list_projects(projects_file, upload_folder, limit=12):
    projects = _read_projects(projects_file)
    upload_folder = Path(upload_folder)
    visible = []

    for project in projects:
        filename = project.get("filename", "")
        project["available"] = bool(filename and (upload_folder / filename).exists())
        visible.append(project)

    return visible[:limit]


def delete_project(
    projects_file,
    project_id,
    upload_folder,
    output_folder,
):
    projects = _read_projects(projects_file)
    project = next(
        (item for item in projects if item.get("id") == project_id),
        None,
    )

    if project is None:
        return False

    filename = project.get("filename")

    if filename:
        upload_path = Path(upload_folder) / filename

        if upload_path.exists() and upload_path.is_file():
            upload_path.unlink()

    project_output = Path(output_folder) / project_id

    if project_output.exists() and project_output.is_dir():
        shutil.rmtree(project_output)

    projects = [item for item in projects if item.get("id") != project_id]
    _write_projects(projects_file, projects)

    return True


def clear_projects(projects_file, upload_folder, output_folder):
    projects = _read_projects(projects_file)

    for project in projects:
        filename = project.get("filename")

        if filename:
            upload_path = Path(upload_folder) / filename

            if upload_path.exists() and upload_path.is_file():
                upload_path.unlink()

        project_id = project.get("id")

        if project_id:
            project_output = Path(output_folder) / project_id

            if project_output.exists() and project_output.is_dir():
                shutil.rmtree(project_output)

    _write_projects(projects_file, [])

    return len(projects)
