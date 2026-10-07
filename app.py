from flask import Flask

from config import MAX_CONTENT_LENGTH, OUTPUT_FOLDER, UPLOAD_FOLDER
from routes.video_routes import video_bp


def create_app():
    app = Flask(__name__)

    app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
    app.config["OUTPUT_FOLDER"] = str(OUTPUT_FOLDER)
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    app.register_blueprint(video_bp)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
