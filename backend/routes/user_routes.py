import json
from flask import request, jsonify
from services.user_service import (
    get_current_user_info, update_user_profile,
    handle_user_favorite, get_user_favorites, get_user_view_history,
    check_user_favorite  # 新增导入
)
from config import logger
from utils.auth import get_current_user_id  # 直接导入工具函数，避免循环导入


def register_user_routes(bp):
    """注册用户相关路由到蓝图（核心函数，修复导入问题）"""

    @bp.route('/user/current', methods=['GET'])
    def handle_get_current_user():
        """获取当前用户信息（对应原代码handle_get_current_user逻辑）"""
        try:
            headers = request.headers
            result = get_current_user_info(headers)
            status_code = result['statusCode']
            body = result['body']
            if isinstance(body, str):
                body = json.loads(body)
            return jsonify(body), status_code
        except Exception as e:
            logger.error(f"处理当前用户信息查询失败: {str(e)}", exc_info=True)
            return jsonify({'error': 'Failed to get current user'}), 500

    @bp.route('/user/profile', methods=['PUT'])
    def handle_update_profile():
        """更新用户信息（对应原代码handle_update_profile逻辑，支持头像上传）"""
        try:
            headers = request.headers
            # 判断请求类型（表单数据/JSON）
            is_form_data = request.content_type and request.content_type.startswith('multipart/form-data')
            # 解析请求数据
            if is_form_data:
                # 处理表单数据（含头像文件）
                data = request.form.to_dict()
                if 'avatar' in request.files:
                    data['avatar'] = request.files['avatar']
            else:
                # 处理JSON数据
                data = request.get_json() or {}

            # 调用用户服务更新信息
            result = update_user_profile(headers, data, is_form_data)
            status_code = result['statusCode']
            body = result['body']
            if isinstance(body, str):
                body = json.loads(body)
            return jsonify(body), status_code
        except Exception as e:
            logger.error(f"处理用户信息更新失败: {str(e)}", exc_info=True)
            return jsonify({'error': 'Failed to update user profile'}), 500

    @bp.route('/favorites/<book_id>', methods=['POST'])
    def handle_add_favorite(book_id):
        """添加收藏（对应原代码handle_add_favorite逻辑）"""
        try:
            headers = request.headers
            # 调用用户服务（action='add'表示添加收藏）
            result = handle_user_favorite(book_id, headers, action='add')
            status_code = result['statusCode']
            body = result['body']
            if isinstance(body, str):
                body = json.loads(body)
            return jsonify(body), status_code
        except Exception as e:
            logger.error(f"处理添加收藏失败: book_id={book_id}, {str(e)}", exc_info=True)
            return jsonify({'error': 'Failed to add favorite'}), 500

    @bp.route('/favorites/<book_id>', methods=['DELETE'])
    def handle_remove_favorite(book_id):
        """移除收藏（对应原代码handle_remove_favorite逻辑）"""
        try:
            headers = request.headers
            # 调用用户服务（action='remove'表示移除收藏）
            result = handle_user_favorite(book_id, headers, action='remove')
            status_code = result['statusCode']
            body = result['body']
            if isinstance(body, str):
                body = json.loads(body)
            return jsonify(body), status_code
        except Exception as e:
            logger.error(f"处理移除收藏失败: book_id={book_id}, {str(e)}", exc_info=True)
            return jsonify({'error': 'Failed to remove favorite'}), 500

    @bp.route('/favorites/<book_id>/check', methods=['GET'])
    def handle_check_favorite(book_id):
        """检查收藏状态（使用仓储层优化）"""
        try:
            headers = request.headers
            result = check_user_favorite(book_id, headers)
            status_code = result['statusCode']
            body = result['body']
            if isinstance(body, str):
                body = json.loads(body)
            return jsonify(body), status_code
        except Exception as e:
            logger.error(f"处理收藏状态检查失败: book_id={book_id}, {str(e)}", exc_info=True)
            return jsonify({'error': 'Failed to check favorite'}), 500

    @bp.route('/favorites', methods=['GET'])
    def handle_get_favorites():
        """获取用户收藏列表（对应原代码handle_get_favorites逻辑）"""
        try:
            headers = request.headers
            result = get_user_favorites(headers)
            status_code = result['statusCode']
            body = result['body']
            if isinstance(body, str):
                body = json.loads(body)
            return jsonify(body), status_code
        except Exception as e:
            logger.error(f"处理收藏列表查询失败: {str(e)}", exc_info=True)
            return jsonify({'error': 'Failed to get favorites'}), 500

    @bp.route('/history', methods=['GET'])
    def handle_get_view_history():
        """获取用户浏览历史（对应原代码handle_get_view_history逻辑）"""
        try:
            headers = request.headers
            result = get_user_view_history(headers)
            status_code = result['statusCode']
            body = result['body']
            if isinstance(body, str):
                body = json.loads(body)
            return jsonify(body), status_code
        except Exception as e:
            logger.error(f"处理浏览历史查询失败: {str(e)}", exc_info=True)
            return jsonify({'error': 'Failed to get view history'}), 500