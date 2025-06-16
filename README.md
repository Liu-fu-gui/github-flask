# Flask-Threading 异步文件处理系统
## 项目简介
本项目是一个基于 Flask 的异步文件处理系统，支持 PDF 文本提取 和 音视频转录+总结 两大核心功能。通过异步线程处理机制，避免阻塞主线程，支持文件上传或 URL 提交两种方式，并提供任务进度查询、结果获取等接口。

## 技术栈
分类 技术/工具 说明 Web 框架 Flask 轻量级 Python Web 框架 异步处理 threading 原生线程实现异步任务 语音识别 Whisper OpenAI 开源语音识别模型 PDF 解析 PyMuPDF (fitz) PDF 文本提取库 总结生成 DeepSeek Chat API 调用大模型生成结构化总结 依赖管理 requirements.txt 项目依赖列表 系统配置 app/config.py 全局配置（API 密钥、目录等）
## 项目结构
```
falsk/
├── app/
│   ├── __init__.py                 # 创建 Flask 应用
│   ├── config.py                   # 配置项（API 密钥、路径等）
│   ├── routes/
│   │   ├── unified_upload.py       # 整合后的上传+进度+结果查询接口
│   │   ├── summary_routes.py       # 摘要相关接口（含 /transcription_summary）
│   │   └── task_routes.py          # 可并入 unified_upload，但可选保留（返回txt文件）
│   ├── utils/
│   │   └── transcription.py        # 核心逻辑：音频转录 / PDF 解析 / 摘要生成
├── txt/                            # 转录后的 txt 输出（自动生成）
├── uploads/                        # 上传的 PDF 文件（自动生成）
├── custom_temp/                    # 暂存 MP4 文件（自动生成）
├── run.py                          # Flask 启动入口
```

## 路由说明总览
| 接口路径                              | 方法 | 说明                                   |
|---------------------------------------|------|----------------------------------------|
| `/submit`                            | POST | 上传 PDF 或 MP4 并异步处理             |
| `/progress?id=xxx`                   | GET  | 查询进度                               |
| `/result?id=xxx`                     | GET  | 返回原始字幕或PDF文本                  |
| `/transcription_result?id=xxx`       | GET  | 返回 .txt 文件转录内容                 |
| `/transcription_summary?id=xxx`      | GET  | 自动摘要生成                           |
| `/generate_summary_by_result?id=xxx` | GET  | 纯文本摘要接口（可选）                 |

## 上传接口 `/submit`

### 方式 1：本地文件上传
- **URL**：`POST /submit`
- **Content-Type**：`multipart/form-data`
- **参数说明**：

| 参数名      | 类型   | 是否必填 | 说明                                  |
|-------------|--------|----------|---------------------------------------|
| `file`      | 文件   | ✅       | MP4 或 PDF 文件                       |
| `type`      | 字符串 | ✅       | `"pdf"` 或 `"mp4"`                    |
| `model_size`| 字符串 | 否       | Whisper 模型大小（如 `"base"`、`"large"`），仅 MP4 有效 |

- **curl 示例（上传 PDF）**：
```bash
curl -X POST http://localhost:6006/submit \
  -F "file=@sample.pdf" \
  -F "type=pdf"
```

- **curl 示例（上传 MP4）**：
```bash
curl -X POST http://localhost:6006/submit \
  -F "file=@sample.mp4" \
  -F "type=mp4" \
  -F "model_size=base"
```

### 方式 2：URL 下载上传
- **Content-Type**：`application/json`
- **请求体示例**：
```json
{
  "url": "https://example.com/file.mp4",
  "type": "mp4",
  "model_size": "base"
}
```

- **curl 示例**：
```bash
curl -X POST http://localhost:6006/submit \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/sample.pdf", "type": "pdf"}'
```

## 查询进度 `/progress`
- **URL**：`GET /progress?id=<task_id>`
- **curl 示例**：
```bash
curl "http://localhost:6006/progress?id=ac123456-7890"
```

## 获取原始转录/提取结果 `/result`
- **URL**：`GET /result?id=<task_id>`
- **返回**：字幕段落数组（MP4）或 PDF 文本（PDF）
- **curl 示例**：
```bash
curl "http://localhost:6006/result?id=ac123456-7890"
```

## 生成摘要 `/summary`
- **URL**：`GET /summary?id=<task_id>`
- **说明**：自动识别音频或 PDF 类型并生成摘要
- **curl 示例**：
```bash
curl "http://localhost:6006/summary?id=ac123456-7890"
```

## 可选接口（`task_routes` 保留）
### `/transcription_result`
- **URL**：`GET /transcription_result?id=<task_id>`
- **说明**：获取 .txt 文本内容（适用于转录后查看）
- **curl 示例**：
```bash
curl "http://localhost:6006/transcription_result?id=ac123456-7890"
```

### `/download_txt`
- **URL**：`GET /download_txt?id=<task_id>`
- **说明**：下载 .txt 文件作为附件
- **curl 示例**：
```bash
curl -O "http://localhost:6006/download_txt?id=ac123456-7890"
```