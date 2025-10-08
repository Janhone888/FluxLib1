import json
import time  # 添加time模块导入，用于生成时间戳
from flask import request, jsonify
from services.ai_service import get_all_books_for_ai, process_with_deepseek
from utils.auth import get_current_user_id
from config import logger


def register_ai_routes(bp):
    @bp.route('/ai/chat', methods=['POST'])
    def handle_ai_chat():
        """AI聊天接口（处理用户与AI的交互，基于图书数据提供响应）"""
        try:
            # 获取请求数据
            data = request.get_json()
            user_message = data.get('message', '')

            # 验证用户身份
            user_id = get_current_user_id(request.headers)
            if not user_id:
                return jsonify({'error': '未授权访问'}), 401

            # 验证消息内容
            if not user_message:
                return jsonify({'error': '消息不能为空'}), 400

            # 获取图书数据供AI参考
            books_data = get_all_books_for_ai()

            # 调用AI服务处理请求
            response = process_with_deepseek(user_message, books_data, user_id)

            # 返回AI响应及时间戳
            return jsonify({
                'response': response,
                'timestamp': int(time.time())  # 使用time模块生成时间戳
            }), 200

        except Exception as e:
            # 记录错误日志
            logger.error(f"AI聊天处理失败: {str(e)}", exc_info=True)
            return jsonify({'error': '处理请求时发生错误'}), 500