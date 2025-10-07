import json
from flask import request, jsonify
from services.book_service import (
    get_book_list, get_book_detail, create_book,
    update_book, delete_book, get_book_cover_url
)
from config import logger


def register_book_routes(bp):
    """注册图书相关路由到蓝图"""

    @bp.route('/books', methods=['GET'])
    def handle_get_books():
        """获取图书列表（添加请求日志）"""
        try:
            logger.info("🌐 收到获取图书列表请求")

            # 提取查询参数
            page = request.args.get('page', default=1, type=int)
            size = request.args.get('size', default=10, type=int)
            category = request.args.get('category', default='', type=str)

            logger.info(f"📋 请求参数: page={page}, size={size}, category='{category}'")

            # 调用图书服务
            result = get_book_list(page=page, size=size, category=category)

            # 记录响应状态
            status_code = result['statusCode']
            logger.info(f"📤 响应状态码: {status_code}")

            body = result['body']
            # 兼容原代码的响应格式
            if isinstance(body, str):
                body = json.loads(body)

            logger.info(f"📄 响应数据长度: {len(str(body))} 字符")

            return jsonify(body), status_code

        except Exception as e:
            logger.error(f"💥 处理图书列表查询失败: {str(e)}", exc_info=True)
            return jsonify({'error': 'Failed to get books'}), 500

    @bp.route('/books', methods=['POST'])
    def handle_create_book():
        """创建图书（对应原代码同名路由，仅管理员可操作）"""
        try:
            # 提取请求体和请求头（权限校验需headers中的Authorization）
            book_data = request.get_json() or {}
            headers = request.headers
            # 调用图书服务（服务层已处理管理员权限校验）
            result = create_book(book_data, headers)
            status_code = result['statusCode']
            body = result['body']
            if isinstance(body, str):
                body = json.loads(body)
            return jsonify(body), status_code
        except Exception as e:
            logger.error(f"处理图书创建失败: {str(e)}", exc_info=True)
            return jsonify({'error': 'Failed to create book'}), 500

    @bp.route('/books/<book_id>', methods=['GET'])
    def handle_get_book(book_id):
        """获取图书详情（对应原代码同名路由，自动记录浏览历史）"""
        try:
            headers = request.headers  # 用于获取当前登录用户，记录浏览历史
            result = get_book_detail(book_id, headers)
            status_code = result['statusCode']
            body = result['body']
            if isinstance(body, str):
                body = json.loads(body)
            return jsonify(body), status_code
        except Exception as e:
            logger.error(f"处理图书详情查询失败: book_id={book_id}, {str(e)}", exc_info=True)
            return jsonify({'error': 'Failed to get book'}), 500

    @bp.route('/books/<book_id>', methods=['PUT'])
    def handle_update_book(book_id):
        """更新图书（对应原代码同名路由，仅管理员可操作）"""
        try:
            book_data = request.get_json() or {}
            headers = request.headers
            result = update_book(book_id, book_data, headers)
            status_code = result['statusCode']
            body = result['body']
            if isinstance(body, str):
                body = json.loads(body)
            return jsonify(body), status_code
        except Exception as e:
            logger.error(f"处理图书更新失败: book_id={book_id}, {str(e)}", exc_info=True)
            return jsonify({'error': 'Failed to update book'}), 500

    @bp.route('/books/<book_id>', methods=['DELETE'])
    def handle_delete_book(book_id):
        """删除图书（对应原代码同名路由，仅管理员可操作）"""
        try:
            headers = request.headers
            result = delete_book(book_id, headers)
            status_code = result['statusCode']
            body = result['body']
            if isinstance(body, str):
                body = json.loads(body)
            return jsonify(body), status_code
        except Exception as e:
            logger.error(f"处理图书删除失败: book_id={book_id}, {str(e)}", exc_info=True)
            return jsonify({'error': 'Failed to delete book'}), 500

    @bp.route('/presigned-url', methods=['GET'])
    def handle_presigned_url():
        """生成图书封面上传预签名URL（对应原代码同名路由）"""
        try:
            # 提取参数（与原代码一致：file_name和file_type）
            file_name = request.args.get('file_name')
            file_type = request.args.get('file_type')
            result = get_book_cover_url(file_name, file_type)
            status_code = result['statusCode']
            body = result['body']
            if isinstance(body, str):
                body = json.loads(body)
            return jsonify(body), status_code
        except Exception as e:
            logger.error(f"处理预签名URL生成失败: {str(e)}", exc_info=True)
            return jsonify({'error': 'Failed to generate presigned URL'}), 500