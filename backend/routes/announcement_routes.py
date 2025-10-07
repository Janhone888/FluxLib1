import json
from flask import request, jsonify
from services.announcement_service import get_announcements, create_announcement, delete_announcement
from config import logger


def register_announcement_routes(bp):
    @bp.route('/announcements', methods=['GET'])
    def handle_get_announcements():
        """获取公告列表（对应原版handle_get_announcements）"""
        result = get_announcements()
        status_code = result['statusCode']
        body = json.loads(result['body']) if isinstance(result['body'], str) else result['body']
        return jsonify(body), status_code

    @bp.route('/announcements', methods=['POST'])
    def handle_create_announcement():
        """创建公告（对应原版handle_create_announcement）"""
        try:
            data = request.get_json()
            title = data.get('title')
            content = data.get('content')
            headers = request.headers
            result = create_announcement(headers, title, content)
            status_code = result['statusCode']
            body = json.loads(result['body']) if isinstance(result['body'], str) else result['body']
            return jsonify(body), status_code
        except Exception as e:
            logger.error(f"处理创建公告请求失败: {str(e)}", exc_info=True)
            return jsonify({'error': '无效的JSON请求体'}), 400

    @bp.route('/announcements/<announcement_id>', methods=['DELETE'])
    def handle_delete_announcement(announcement_id):
        """删除公告（对应原版handle_delete_announcement）"""
        headers = request.headers
        result = delete_announcement(headers, announcement_id)
        status_code = result['statusCode']
        body = json.loads(result['body']) if isinstance(result['body'], str) else result['body']
        return jsonify(body), status_code