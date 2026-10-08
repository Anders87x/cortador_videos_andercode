from flask import Flask

from config import (
    DATA_FOLDER,
    MAX_CONTENT_LENGTH,
    OUTRO_IMAGE_MAX_SIZE,
    OUTPUT_FOLDER,
    PROJECTS_FILE,
    PROJECT_ASSETS_FOLDER,
    RENDER_LOG_FILE,
    UPLOAD_FOLDER,
)
from routes.video_routes import video_bp


def create_app():
    app = Flask(__name__)

    app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
    app.config["OUTPUT_FOLDER"] = str(OUTPUT_FOLDER)
    app.config["PROJECTS_FILE"] = str(PROJECTS_FILE)
    app.config["PROJECT_ASSETS_FOLDER"] = str(PROJECT_ASSETS_FOLDER)
    app.config["RENDER_LOG_FILE"] = str(RENDER_LOG_FILE)
    app.config["OUTRO_IMAGE_MAX_SIZE"] = OUTRO_IMAGE_MAX_SIZE
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
    DATA_FOLDER.mkdir(parents=True, exist_ok=True)
    PROJECT_ASSETS_FOLDER.mkdir(parents=True, exist_ok=True)

    app.register_blueprint(video_bp)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
