# app/routes/task_routes.py
from flask import Blueprint, request, jsonify, send_file
import os, io
from app.utils.transcription import task_status
from app.config import Config

task_bp = Blueprint('task', __name__)

@task_bp.route('/transcription_result', methods=['GET'])
def get_transcription_result():
    task_id = request.args.get('id') or request.args.get('task_id')
    if not task_id:
        return jsonify({"error": "缺少任务ID"}), 400

    filepath = os.path.join(Config.TXT_DIR, f"{task_id}.txt")
    if not os.path.exists(filepath):
        return jsonify({"error": "转录文本不存在"}), 404

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    return jsonify({"result": content})

@task_bp.route('/download_txt', methods=['GET'])
def download_txt():
    task_id = request.args.get('id')
    filepath = os.path.join(Config.TXT_DIR, f"{task_id}.txt")
    if not os.path.exists(filepath):
        return jsonify({"error": "文件不存在"}), 404
    return send_file(filepath, mimetype='text/plain', as_attachment=True, download_name=f"{task_id}.txt")
