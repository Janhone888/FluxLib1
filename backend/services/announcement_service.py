import json
from config import logger
from models.announcement import Announcement
from models.user import User
from utils.auth import get_current_user_id


def get_announcements():
    """获取公告列表（使用仓储层优化）"""
    try:
        # 通过仓储层获取公告
        announcements = Announcement.get_announcements()
        return {
            'statusCode': 200,
            'body': json.dumps(announcements)
        }
    except Exception as e:
        logger.error(f"获取公告失败: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': '获取公告失败'})
        }


def create_announcement(headers, title, content):
    """创建公告（需管理员权限，使用仓储层优化）"""
    try:
        # 权限校验
        user_id = get_current_user_id(headers)
        if not user_id:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': '未授权访问'})
            }

        # 通过仓储层获取用户
        user = User.get_by_id(user_id)
        if not user or user.role != 'admin':
            return {
                'statusCode': 403,
                'body': json.dumps({'error': '需要管理员权限'})
            }

        # 校验参数
        if not title or not content:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': '标题和内容不能为空'})
            }

        # 通过仓储层创建公告
        success = Announcement.create_announcement(title, content)
        if not success:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': '创建公告失败'})
            }

        return {
            'statusCode': 200,
            'body': json.dumps({'success': True})
        }

    except Exception as e:
        logger.error(f"创建公告失败: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': '创建公告失败'})
        }


def delete_announcement(headers, announcement_id):
    """删除公告（需管理员权限，使用仓储层优化）"""
    try:
        # 权限校验
        user_id = get_current_user_id(headers)
        if not user_id:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': '未授权访问'})
            }

        # 通过仓储层获取用户
        user = User.get_by_id(user_id)
        if not user or user.role != 'admin':
            return {
                'statusCode': 403,
                'body': json.dumps({'error': '需要管理员权限'})
            }

        # 通过仓储层删除公告
        success = Announcement.delete_announcement(announcement_id)
        if not success:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': '删除公告失败'})
            }

        return {
            'statusCode': 200,
            'body': json.dumps({'success': True})
        }

    except Exception as e:
        logger.error(f"删除公告失败: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': '删除公告失败'})
        }