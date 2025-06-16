# app/routes/summary_routes.py
from flask import Blueprint, request, jsonify
from app.utils.transcription import generate_summary, task_status
from app.config import Config

summary_bp = Blueprint('summary', __name__)

@summary_bp.route('/transcription_summary', methods=['GET'])
def transcription_summary():
    task_id = request.args.get('id')
    if not task_id:
        return jsonify({"error": "缺少任务 id"}), 400
    if task_id not in task_status:
        return jsonify({"error": "任务不存在"}), 404
    if task_status[task_id]['progress'] != 100:
        return jsonify({"error": "任务未完成"}), 202

    summary, err = generate_summary(task_id, Config)
    if err:
        return jsonify({"error": err}), 400
    return jsonify({"summary": summary})