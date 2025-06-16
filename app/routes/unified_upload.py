# unified_upload.py
from flask import Blueprint, request, jsonify
import os, uuid, threading, requests, json
from app.config import Config, get_system_prompt
from app.utils.transcription import transcribe_audio_task, process_pdf, generate_summary, task_status

upload_bp = Blueprint("upload", __name__)

@upload_bp.route('/submit', methods=['POST'])
def submit():
    upload_type = request.form.get("type") or request.json.get("type")
    if upload_type not in ["pdf", "mp4"]:
        return jsonify({"error": "type 参数必须为 'pdf' 或 'mp4'"}), 400

    task_id = str(uuid.uuid4())
    ext = ".pdf" if upload_type == "pdf" else ".mp4"
    path = os.path.join(Config.UPLOAD_DIR if upload_type == "pdf" else Config.TEMP_DIR, f"{task_id}{ext}")
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # 处理文件上传或 URL 下载
    if 'file' in request.files:
        request.files['file'].save(path)
    else:
        url = request.json.get('url')
        if not url:
            return jsonify({"error": "缺少文件或URL"}), 400
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            with open(path, 'wb') as f:
                f.write(resp.content)
        except Exception as e:
            return jsonify({"error": f"文件下载失败: {e}"}), 500

    # 分别处理 PDF 或 MP4
    def pdf_task():
        try:
            task_status[task_id] = {'progress': 0, 'result': None, 'error': None}
            result = process_pdf(path, Config)
            task_status[task_id] = {'progress': 100, 'result': result, 'error': None if result else '处理失败'}
        except Exception as e:
            task_status[task_id] = {'progress': 100, 'result': None, 'error': str(e)}

    if upload_type == "pdf":
        threading.Thread(target=pdf_task).start()
    else:
        model_size = request.form.get("model_size") or request.json.get("model_size", Config.MODEL_SIZE)
        output_path = os.path.join(Config.TXT_DIR, f"{task_id}.txt")
        threading.Thread(
            target=transcribe_audio_task,
            args=(task_id, path, model_size, output_path)
        ).start()

    return jsonify({"task_id": task_id, "status": "started"})


# 进度查询接口： /progress?id=xxx
@upload_bp.route('/progress', methods=['GET'])
def get_progress():
    task_id = request.args.get('id')
    if not task_id or task_id not in task_status:
        return jsonify({"error": "任务不存在"}), 404
    return jsonify({"progress": task_status[task_id].get("progress", 0)})


# 返回原始文本： /result?id=xxx
@upload_bp.route('/result', methods=['GET'])
def get_result():
    task_id = request.args.get('id')
    if not task_id or task_id not in task_status:
        return jsonify({"error": "任务不存在"}), 404
    data = task_status[task_id]
    if data['error']:
        return jsonify({"error": data['error']}), 400
    if not data['result']:
        return jsonify({"error": "未完成"}), 202
    return jsonify({"result": data['result']})


# 摘要接口： /summary?id=xxx
@upload_bp.route('/summary', methods=['GET'])
def generate_task_summary():
    task_id = request.args.get('id')
    if not task_id or task_id not in task_status:
        return jsonify({"error": "任务不存在"}), 404
    if task_status[task_id].get("progress", 0) < 100:
        return jsonify({"error": "任务未完成"}), 202

    summary, err = generate_summary(task_id, Config)
    if err:
        return jsonify({"error": err}), 400
    return jsonify({"summary": summary})
