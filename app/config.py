import os

class Config:
    # OpenAI API 密钥
    OPENAI_API_KEY = "sk-dae37d100c8d46939183b6c7c5c8cb32"
    # OpenAI 基础 URL
    OPENAI_BASE_URL = "https://api.deepseek.com"
    # 模型大小
    MODEL_SIZE = "large"
    # 上传文件目录
    UPLOAD_DIR = os.path.join(os.getcwd(), 'uploads')
    # 文本输出目录
    TXT_DIR = os.path.join(os.getcwd(), 'txt')
    # 临时目录（用于音频转录缓存文件）
    TEMP_DIR = os.path.join(os.getcwd(), "custom_temp")

os.makedirs(Config.TEMP_DIR, exist_ok=True)

def get_system_prompt(task_type=None):
    if task_type == "pdf":
        return """
        请你从下面提供的整本 PDF 文本中，提取所有不重复的“核心知识点”，并标注它们**首次出现**的页码。你需要输出一个标准的 JSON 数组，每个元素包含以下字段：

        - pageNum：知识点首次出现的页码（整数）
        - knowledgeText：该页提到的核心知识点（不超过 15 个字）

        🌟 提取要求如下：
        1. 只保留**高质量、准确、有意义的知识点**，可用于教学或总结；
        2. 知识点需避免重复（如“创业定义”与“创业的定义”只保留一条）；
        3. 每个知识点仅输出一次，按首次出现的页码记录；
        4. 输出格式必须为严格的 JSON 数组格式；
        5. 不允许输出任何非 JSON 的内容（包括注释、解释、自然语言）；

        📌 示例输出格式如下：
        [
          {"pageNum": 1, "knowledgeText": "创业的定义"},
          {"pageNum": 2, "knowledgeText": "创业动机"},
          {"pageNum": 3, "knowledgeText": "创意与创新的关系"}
        ]
        """
    return """
    你是一个视频总结助手，请将字幕内容提炼为最多5个核心小节。
    输出必须为严格的JSON对象格式，示例：
    {
        "summary": [
            {
                "time": "mm:ss",
                "content": "小节内容"
            }
        ]
    }
    要求：
    1. 时间字段必须为mm:ss格式（例如30秒要写成00:30）
    2. 每个对象必须包含time和content字段
    3. 数组元素按时间顺序排列
    不允许以代码块格式输出，例如```json，不允许包裹 markdown 符号。
    """
