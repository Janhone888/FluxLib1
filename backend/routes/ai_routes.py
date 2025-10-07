import json
from flask import request, jsonify
from services.ai_service import get_all_books_for_ai, process_with_deepseek
from utils.auth import get_current_user_id
from config import logger


def register_ai_routes(bp):
    @bp.route('/ai/chat', methods=['POST'])
    def handle_ai_chat():
        """AI聊天接口（对应原版handle_ai_chat）"""
        try:
            data = request.get_json()
            user_message = data.get('message', '')
            user_id = get_current_user_id(request.headers)
            if not user_id:
                return jsonify({'error': '未授权访问'}), 401
            if not user_message:
                return jsonify({'error': '消息不能为空'}), 400
            # 获取图书数据
            books_data = get_all_books_for_ai()
            # 调用AI处理
            response = process_with_deepseek(user_message, books_data, user_id)
            return jsonify({
                'response': response,
                'timestamp': int(time.time())
            }), 200
        except Exception as e:
            logger.error(f"AI聊天处理失败: {str(e)}", exc_info=True)
            return jsonify({'error': '处理请求时发生错误'}), 500