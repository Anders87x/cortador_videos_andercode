from pathlib import Path
from uuid import uuid4

from flask import Flask, jsonify, render_template, request, send_from_directory, url_for
from werkzeug.utils import secure_filename


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
ALLOWED_EXTENSIONS = {"mp4", "mov", "mkv", "webm", "avi"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024 * 1024  # 8 GB

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


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
    })


@app.get("/uploads/<path:filename>")
def uploaded_video(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.errorhandler(413)
def file_too_large(_error):
    return jsonify({
        "message": "El video supera el límite actual de 8 GB."
    }), 413


if __name__ == "__main__":
    app.run(debug=True)
