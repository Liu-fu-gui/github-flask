from flask import Flask
from app.routes import unified_upload, summary_routes, task_routes

def create_app():
    app = Flask(__name__)
    for bp in [unified_upload.upload_bp, summary_routes.summary_bp, task_routes.task_bp]:
        app.register_blueprint(bp)
    return app
