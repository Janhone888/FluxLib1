import json
import time
from config import logger
from models.comment import Comment
from utils.auth import get_current_user_id


def get_comments(book_id: str) -> dict:
    """获取图书评论列表（使用仓储层优化）"""
    try:
        # 通过仓储层获取评论
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

        return {
            'statusCode': 200,
            'body': json.dumps(formatted_comments)
        }

    except Exception as e:
        logger.error(f"获取评论失败: book_id={book_id}, err={str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to get comments'})
        }


def create_comment(book_id: str, headers: dict, data: dict) -> dict:
    """创建评论（使用仓储层优化）"""
    try:
        user_id = get_current_user_id(headers)
        if not user_id:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': '未授权访问'})
            }

        content = data.get('content', '').strip()
        parent_id = data.get('parent_id', '')

        if not content:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': '评论内容不能为空'})
            }

        # 通过仓储层创建评论
        success, result = Comment.create_comment(book_id, user_id, content, parent_id)

        if success:
            return {
                'statusCode': 201,
                'body': json.dumps(result)
            }
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': result})
            }

    except Exception as e:
        logger.error(f"创建评论失败: book_id={book_id}, err={str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to create comment'})
        }


def like_comment(comment_id: str, headers: dict) -> dict:
    """点赞/取消点赞评论（使用仓储层优化）"""
    try:
        user_id = get_current_user_id(headers)
        if not user_id:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': '未授权访问'})
            }

        # 通过仓储层获取评论
        comment = Comment.get_by_id(comment_id)
        if not comment:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': '评论不存在'})
            }

        # 通过仓储层点赞/取消点赞
        success, result = comment.like_comment(user_id)

        if not success:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': result})
            }

        # 获取更新后的评论信息
        updated_comment = Comment.get_by_id(comment_id)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'likes': updated_comment.likes,
                'action': result.get('action'),
                'user_display_name': updated_comment.user_display_name,
                'user_avatar_url': updated_comment.user_avatar_url
            })
        }

    except Exception as e:
        logger.error(f"点赞失败：comment_id={comment_id}, err={str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to like comment'})
        }