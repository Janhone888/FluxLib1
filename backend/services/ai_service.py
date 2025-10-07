import json
import requests
import time
from config import logger, DEEPSEEK_API_KEY
from models.book import Book


def get_all_books_for_ai():
    """获取所有图书数据用于AI知识库（对应原版同名函数）"""
    try:
        # 调用Book模型获取所有图书
        books, _ = Book.get_list(page=1, size=1000)  # 单次获取1000本，可根据需求调整
        books_data = []
        for book in books:
            books_data.append({
                'title': book.title,
                'author': book.author,
                'category': book.category,
                'description': book.description[:200] + '...' if len(book.description) > 200 else book.description,
                'status': book.status,
                'stock': book.stock
            })
        return books_data
    except Exception as e:
        logger.error(f"获取AI图书数据失败: {str(e)}", exc_info=True)
        return []


def process_with_deepseek(message, books_data, user_id):
    """使用DeepSeek API处理消息（对应原版同名函数）"""
    system_prompt = f"""你是一个图书管理AI助手，名为"FluxLib助手"。请根据以下图书信息回答用户问题：
可用图书列表:
{json.dumps(books_data, ensure_ascii=False, indent=2)}
请遵循以下规则:
1. 只能推荐上述列表中的图书，不能编造不存在的图书
2. 对于图书内容相关问题，基于图书描述信息回答
3. 图书馆运营时间: 周一至周五 9:00-21:00, 周末 10:00-18:00
4. 借阅规则: 每次最多借阅5本，借期30天，可续借一次
5. 保持友好、专业的语气
6. 如果问题与图书无关，礼貌地表示你专注于图书相关问题
7. 回答要简洁明了，突出重点信息
当前时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
    try:
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            "temperature": 0.7,
            "max_tokens": 2000,
            "stream": False
        }
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response_data = response.json()
        if response.status_code == 200:
            return response_data['choices'][0]['message']['content']
        else:
            logger.error(f"DeepSeek API错误: {response_data}")
            return "抱歉，我现在遇到了一些技术问题，请稍后再试。"
    except requests.exceptions.Timeout:
        logger.error("DeepSeek API请求超时")
        return "请求超时，请稍后再试。"
    except Exception as e:
        logger.error(f"DeepSeek调用失败: {str(e)}", exc_info=True)
        return "处理您的请求时出现了问题，请稍后再试。"