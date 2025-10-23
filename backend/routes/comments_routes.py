import json
from flask import request, jsonify
from config import logger
from services.comments_service import get_comments, create_comment, like_comment


def register_comments_routes(bp):
    """注册评论路由（使用仓储层优化）"""

    @bp.route('/books/<book_id>/comments', methods=['GET'])
    def handle_get_comments(book_id):
        """获取图书评论列表"""
        try:
            result = get_comments(book_id)
            status_code = result['statusCode']
            body = result['body']
            if isinstance(body, str):
                body = json.loads(body)
            return jsonify(body), status_code
        except Exception as e:
            logger.error(f"获取评论失败: book_id={book_id}, err={str(e)}")
            return jsonify({'error': 'Failed to get comments'}), 500

    @bp.route('/books/<book_id>/comments', methods=['POST'])
    def handle_create_comment(book_id):
        """创建评论"""
        try:
            data = request.get_json() or {}
            headers = request.headers
            result = create_comment(book_id, headers, data)
            status_code = result['statusCode']
            body = result['body']
            if isinstance(body, str):
                body = json.loads(body)
            return jsonify(body), status_code
        except Exception as e:
            logger.error(f"创建评论失败: book_id={book_id}, err={str(e)}")
            return jsonify({'error': 'Failed to create comment'}), 500

    @bp.route('/comments/<comment_id>/like', methods=['POST'])
    def handle_like_comment(comment_id):
        """点赞/取消点赞评论"""
        try:
            headers = request.headers
            result = like_comment(comment_id, headers)
            status_code = result['statusCode']
            body = result['body']
            if isinstance(body, str):
                body = json.loads(body)
            return jsonify(body), status_code
        except Exception as e:
            logger.error(f"点赞失败：comment_id={comment_id}, err={str(e)}")
            return jsonify({'error': 'Failed to like comment'}), 500