# app/utils/transcription.py
import os, json, requests, fitz, whisper, re
from app.config import get_system_prompt, Config

task_status = {}

def transcribe_audio_task(task_id, file_path, model_size, output_path):
    task_status[task_id] = {"progress": 0, "result": None, "error": None}
    try:
        model = whisper.load_model(model_size)
        print(f"[任务 {task_id}] 开始音频转录: {file_path}")
        segments = []
        result = model.transcribe(file_path, verbose=False, word_timestamps=False)
        total_duration = result.get("duration", None)
        segment_list = result.get("segments", [])
        total_segments = len(segment_list)

        for i, seg in enumerate(segment_list):
            segments.append(seg)
            progress = int(((i + 1) / total_segments) * 90)  # 提前结束前预留10%
            task_status[task_id]["progress"] = min(progress, 90)

        task_status[task_id] = {"progress": 95, "result": segments, "error": None}  # 写入文件前再更新进度

        with open(output_path, "w", encoding="utf-8") as f:
            for seg in segments:
                f.write(f"[{seg['start']:.2f}s - {seg['end']:.2f}s] {seg['text']}\n")

        task_status[task_id]["progress"] = 100
        print(f"[任务 {task_id}] 转录完成，已生成 {output_path}")

    except Exception as e:
        task_status[task_id] = {"progress": 100, "result": None, "error": str(e)}
        print(f"[任务 {task_id}] 转录失败: {e}")

def process_pdf(file_path, config):
    try:
        doc = fitz.open(file_path)
        text = "\n".join([
            f"第{i+1}页：\n" + page.get_text().strip()
            for i, page in enumerate(doc) if page.get_text().strip()
        ])
        txt_path = os.path.join(config.TXT_DIR, f"{os.path.splitext(os.path.basename(file_path))[0]}.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)
        return text
    except Exception as e:
        raise RuntimeError(f"PDF 解析失败: {e}")

def generate_summary(task_id, config):
    result = task_status.get(task_id, {}).get("result")
    if not result:
        print(f"[任务 {task_id}] 无转录结果，无法生成摘要")
        return None, "无转录结果"

    full_text = result if isinstance(result, str) else "\n".join([seg['text'] for seg in result])
    messages = [
        {"role": "system", "content": get_system_prompt("pdf") if isinstance(result, str) else get_system_prompt()},
        {"role": "user", "content": full_text[:15000]}
    ]

    try:
        print(f"[任务 {task_id}] 正在请求模型接口生成摘要...")
        response = requests.post(
            f"{config.OPENAI_BASE_URL}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {config.OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": messages,
                "temperature": 0.1,
                "max_tokens": 1024
            },
            timeout=60
        )
        print(f"[任务 {task_id}] 响应状态码: {response.status_code}")
        print(f"[任务 {task_id}] 响应原始内容: {response.text[:500]}")

        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content'].strip()

        # 清理 markdown 包裹的 JSON 内容，如```json\n{...}\n```
        if content.startswith("```"):
            content = re.sub(r"```json|```", "", content).strip()

        try:
            parsed = json.loads(content)
            return parsed, None
        except Exception as parse_error:
            print(f"[任务 {task_id}] JSON 解析失败: {parse_error}")
            return None, f"模型输出非 JSON 格式: {parse_error}"

    except Exception as e:
        print(f"[任务 {task_id}] 模型请求异常: {e}")
        return None, str(e)