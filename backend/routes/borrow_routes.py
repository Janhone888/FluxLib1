import json
import time
from flask import request, jsonify
from services.borrow_service import (
    borrow_book, return_book,
    batch_borrow_books, batch_return_books, get_user_borrows,
    return_book_by_borrow_id
)
from config import logger


def register_borrow_routes(bp):
    """注册借阅相关路由到蓝图"""

    @bp.route('/books/<book_id>/borrow', methods=['POST'])
    def handle_borrow_book(book_id):
        """借阅图书（对应原代码同名路由，支持自定义借阅天数）"""
        try:
            # 提取借阅天数（默认30天，与原代码一致）
            data = request.get_json() or {}
            days = data.get('days', 30)
            headers = request.headers
            result = borrow_book(book_id, headers, days)
            status_code = result['statusCode']
            body = result['body']
            if isinstance(body, str):
                body = json.loads(body)
            return jsonify(body), status_code
        except Exception as e:
            logger.error(f"处理图书借阅失败: book_id={book_id}, {str(e)}", exc_info=True)
            return jsonify({'error': 'Failed to borrow book'}), 500

    @bp.route('/books/<book_id>/return', methods=['POST'])
    def handle_return_book(book_id):
        """按期归还图书（对应原代码同名路由）"""
        try:
            headers = request.headers
            # 调用归还服务（is_early_return=False表示按期归还）
            result = return_book(book_id, headers, is_early_return=False)
            status_code = result['statusCode']
            body = result['body']
            if isinstance(body, str):
                body = json.loads(body)
            return jsonify(body), status_code
        except Exception as e:
            logger.error(f"处理图书归还失败: book_id={book_id}, {str(e)}", exc_info=True)
            return jsonify({'error': 'Failed to return book'}), 500

    @bp.route('/books/<book_id>/return-early', methods=['POST'])
    def handle_return_early(book_id):
        """提前归还图书（对应原代码同名路由）"""
        try:
            headers = request.headers
            # 调用归还服务（is_early_return=True表示提前归还）
            result = return_book(book_id, headers, is_early_return=True)
            status_code = result['statusCode']
            body = result['body']
            if isinstance(body, str):
                body = json.loads(body)
            return jsonify(body), status_code
        except Exception as e:
            logger.error(f"处理图书提前归还失败: book_id={book_id}, {str(e)}", exc_info=True)
            return jsonify({'error': 'Failed to return book early'}), 500

    @bp.route('/books/batch-borrow', methods=['POST'])
    def handle_batch_borrow():
        """批量借阅（对应原代码同名路由）"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': '请求体为空'}), 400
            headers = request.headers
            result = batch_borrow_books(data, headers)
            status_code = result['statusCode']
            body = result['body']
            if isinstance(body, str):
                body = json.loads(body)
            return jsonify(body), status_code
        except Exception as e:
            logger.error(f"处理批量借阅失败: {str(e)}", exc_info=True)
            return jsonify({'error': '无效的JSON请求体'}), 400

    @bp.route('/batch-return', methods=['POST'])
    def handle_batch_return():
        """批量归还（对应原代码同名路由）"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': '请求体为空'}), 400
            headers = request.headers
            result = batch_return_books(data, headers)
            status_code = result['statusCode']
            body = result['body']
            if isinstance(body, str):
                body = json.loads(body)
            return jsonify(body), status_code
        except Exception as e:
            logger.error(f"处理批量归还失败: {str(e)}", exc_info=True)
            return jsonify({'error': '无效的JSON请求体'}), 400

    @bp.route('/user/borrows', methods=['GET'])
    def handle_get_user_borrows():
        """获取用户借阅记录（对应原代码同名路由）"""
        try:
            headers = request.headers
            result = get_user_borrows(headers)
            status_code = result['statusCode']
            body = result['body']
            if isinstance(body, str):
                body = json.loads(body)
            return jsonify(body), status_code
        except Exception as e:
            logger.error(f"处理用户借阅记录查询失败: {str(e)}", exc_info=True)
            return jsonify({'error': 'Failed to get user borrows'}), 500

    @bp.route('/return/<borrow_id>', methods=['POST'])
    def handle_return_by_borrow_id(borrow_id):
        """通过借阅ID归还图书（补充原代码遗漏的路由）"""
        try:
            headers = request.headers
            result = return_book_by_borrow_id(borrow_id, headers)
            status_code = result['statusCode']
            body = result['body']
            if isinstance(body, str):
                body = json.loads(body)
            return jsonify(body), status_code
        except Exception as e:
            logger.error(f"通过借阅ID归还图书失败: borrow_id={borrow_id}, {str(e)}", exc_info=True)
            return jsonify({'error': '归还失败'}), 500