import json
import uuid
import time
from flask import request, jsonify
from config import logger
from utils.auth import get_current_user_id
from models.comment import Comment


def register_comments_routes(bp):
    """注册评论路由（完整实现版）"""

    @bp.route('/books/<book_id>/comments', methods=['GET'])
    def handle_get_comments(book_id):
        """获取图书评论列表"""
        try:
            comments = Comment.get_by_book_id(book_id)

            # 格式化评论数据
            formatted_comments = []
            for comment in comments:
                comment_data = {
                    'comment_id': comment.comment_id,
                    'user_id': comment.user_id,
                    'user_display_name': comment.user_display_name,
                    'user_avatar_url': comment.user_avatar_url,
                    'content': comment.content,
                    'parent_id': comment.parent_id,
                    'likes': comment.likes,
                    'created_at': comment.created_at
                }

                # 处理回复
                if hasattr(comment, 'replies') and comment.replies:
                    comment_data['replies'] = []
                    for reply in comment.replies:
                        comment_data['replies'].append({
                            'comment_id': reply.comment_id,
                            'user_id': reply.user_id,
                            'user_display_name': reply.user_display_name,
                            'user_avatar_url': reply.user_avatar_url,
                            'content': reply.content,
                            'parent_id': reply.parent_id,
                            'likes': reply.likes,
                            'created_at': reply.created_at
                        })

                formatted_comments.append(comment_data)

            return jsonify(formatted_comments), 200
        except Exception as e:
            logger.error(f"获取评论失败: book_id={book_id}, err={str(e)}")
            return jsonify({'error': 'Failed to get comments'}), 500

    @bp.route('/books/<book_id>/comments', methods=['POST'])
    def handle_create_comment(book_id):
        """创建评论"""
        try:
            user_id = get_current_user_id(request.headers)
            if not user_id:
                return jsonify({'error': '未授权访问'}), 401

            data = request.get_json() or {}
            content = data.get('content', '').strip()
            parent_id = data.get('parent_id', '')

            if not content:
                return jsonify({'error': '评论内容不能为空'}), 400

            # 创建评论
            success, result = Comment.create_comment(book_id, user_id, content, parent_id)

            if success:
                return jsonify(result), 201
            else:
                return jsonify({'error': result}), 400

        except Exception as e:
            logger.error(f"创建评论失败: book_id={book_id}, err={str(e)}")
            return jsonify({'error': 'Failed to create comment'}), 500

    @bp.route('/comments/<comment_id>/like', methods=['POST'])
    def handle_like_comment(comment_id):
        """点赞/取消点赞评论"""
        try:
            user_id = get_current_user_id(request.headers)  # 获取当前用户ID
            if not user_id:
                return jsonify({'error': '未授权访问'}), 401

            comment = Comment.get_by_id(comment_id)
            if not comment:
                return jsonify({'error': '评论不存在'}), 404

            # 关键修改：调用like_comment时传入user_id
            success, result = comment.like_comment(user_id)
            if not success:
                return jsonify({'error': result}), 400

            # 返回更新后的点赞数和操作类型（点赞/取消点赞）
            updated_comment = Comment.get_by_id(comment_id)
            return jsonify({
                'success': True,
                'likes': updated_comment.likes,
                'action': result.get('action'),  # 前端可根据action更新按钮状态
                'user_display_name': updated_comment.user_display_name,
                'user_avatar_url': updated_comment.user_avatar_url
            }), 200

        except Exception as e:
            logger.error(f"点赞失败：comment_id={comment_id}, err={str(e)}")
            return jsonify({'error': 'Failed to like comment'}), 500