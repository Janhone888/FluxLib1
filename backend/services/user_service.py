import json
import time
from config import logger
from utils.storage import generate_presigned_url
from models.user import User
from models.book import Book
from utils.auth import get_current_user_id


def get_current_user_info(headers):
    """获取用户信息：通过仓储层优化"""
    try:
        user_id = get_current_user_id(headers)
        if not user_id:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': '未授权访问'})
            }

        # 通过仓储层获取用户信息
        user = User.get_by_id(user_id)
        if not user:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': '用户不存在'})
            }

        # 组装用户数据（仓储层确保字段完整）
        user_data = {
            'user_id': getattr(user, 'user_id', user_id),
            'email': getattr(user, 'email', ''),
            'display_name': getattr(user, 'display_name', ''),
            'avatar_url': getattr(user, 'avatar_url', ''),
            'gender': getattr(user, 'gender', ''),
            'background_url': getattr(user, 'background_url', ''),
            'is_verified': getattr(user, 'is_verified', False),
            'role': getattr(user, 'role', 'user'),
            'created_at': getattr(user, 'created_at', int(time.time())),
            'updated_at': getattr(user, 'updated_at', getattr(user, 'created_at', int(time.time())))
        }

        return {
            'statusCode': 200,
            'body': json.dumps(user_data)
        }

    except Exception as e:
        logger.error(
            f"获取当前用户信息失败: user_id={user_id}, 错误={str(e)}",
            exc_info=True
        )
        return {
            'statusCode': 500,
            'body': json.dumps({'error': '获取用户信息失败'})
        }


def update_user_profile(headers, data, is_form_data=False):
    """更新用户信息：通过仓储层优化"""
    try:
        user_id = get_current_user_id(headers)
        if not user_id:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': '未授权访问'})
            }

        # 通过仓储层获取原始用户
        original_user = User.get_by_id(user_id)
        if not original_user:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': '用户不存在'})
            }

        # 处理可更新字段
        update_data = {}
        if is_form_data:
            # 表单数据
            update_data['display_name'] = data['display_name'].strip() if (
                        data.get('display_name') and data['display_name'].strip()) else getattr(original_user,
                                                                                                'display_name', '')

            update_data['gender'] = data['gender'] if data.get('gender') else getattr(original_user, 'gender', '')

            # 处理头像上传
            avatar_file = data.get('avatar')
            if avatar_file:
                file_name = avatar_file.filename
                file_type = avatar_file.content_type
                oss_res = generate_presigned_url(file_name, file_type)
                if oss_res['statusCode'] != 200:
                    return oss_res
                update_data['avatar_url'] = oss_res['body']['access_url']
            else:
                update_data['avatar_url'] = getattr(original_user, 'avatar_url', '')

            # 处理background_url字段
            update_data['background_url'] = data['background_url'].strip() if (
                        data.get('background_url') and data['background_url'].strip()) else getattr(original_user,
                                                                                                    'background_url',
                                                                                                    '')

        else:
            # JSON数据
            update_data['display_name'] = data['display_name'].strip() if (
                        data.get('display_name') and data['display_name'].strip()) else getattr(original_user,
                                                                                                'display_name', '')
            update_data['gender'] = data['gender'] if data.get('gender') else getattr(original_user, 'gender', '')
            update_data['avatar_url'] = data['avatar_url'] if data.get('avatar_url') else getattr(original_user,
                                                                                                 'avatar_url', '')
            update_data['background_url'] = data['background_url'] if data.get('background_url') else getattr(
                original_user, 'background_url', '')

        # 通过仓储层更新用户信息
        success, err = original_user.update_profile(**update_data)
        if not success:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': err})
            }

        # 更新后重新获取完整用户数据
        updated_user = User.get_by_id(user_id)
        complete_user_data = {
            # 基础字段
            'user_id': getattr(updated_user, 'user_id', user_id),
            'email': getattr(updated_user, 'email', ''),
            'display_name': getattr(updated_user, 'display_name', ''),
            'avatar_url': getattr(updated_user, 'avatar_url', ''),
            'gender': getattr(updated_user, 'gender', ''),
            'background_url': getattr(updated_user, 'background_url', ''),
            # 核心字段
            'is_verified': getattr(updated_user, 'is_verified', False),
            'role': getattr(updated_user, 'role', 'user'),
            'created_at': getattr(updated_user, 'created_at', int(time.time())),
            'updated_at': int(time.time())
        }

        # 日志打印：验证字段是否完整
        logger.info(f"更新后用户完整数据: {json.dumps(complete_user_data, ensure_ascii=False)}")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'user': complete_user_data
            })
        }

    except Exception as e:
        logger.error(
            f"更新用户信息失败: user_id={user_id}, 错误={str(e)}",
            exc_info=True
        )
        return {
            'statusCode': 500,
            'body': json.dumps({'error': '更新失败'})
        }


def handle_user_favorite(book_id, headers, action='add'):
    """处理用户收藏（通过仓储层优化）"""
    try:
        user_id = get_current_user_id(headers)
        if not user_id:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': '未授权访问'})
            }

        # 通过仓储层获取用户
        user = User.get_by_id(user_id)
        if not user:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': '用户不存在'})
            }

        # 通过仓储层获取图书
        book = Book.get_by_id(book_id)
        if not book:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': '图书不存在'})
            }

        if action == 'add':
            success = user.add_favorite(book_id)
            msg = '已收藏' if success else '添加收藏失败'
        else:
            success = user.remove_favorite(book_id)
            msg = '已取消收藏' if success else '移除收藏失败'

        if not success:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': msg})
            }

        return {
            'statusCode': 200,
            'body': json.dumps({'success': True, 'message': msg})
        }

    except Exception as e:
        logger.error(
            f"处理收藏失败: action={action}, book_id={book_id}, user_id={user_id}, 错误={str(e)}",
            exc_info=True
        )
        return {
            'statusCode': 500,
            'body': json.dumps({'error': '处理收藏失败'})
        }


def get_user_favorites(headers):
    """获取用户收藏列表（通过仓储层优化）"""
    try:
        user_id = get_current_user_id(headers)
        if not user_id:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': '未授权访问'})
            }

        # 通过仓储层获取用户
        user = User.get_by_id(user_id)
        if not user:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': '用户不存在'})
            }

        # 通过仓储层获取收藏列表
        favorites = user.get_favorites()
        formatted_favorites = []

        for fav in favorites:
            book = Book.get_by_id(fav.book_id)
            formatted_favorites.append({
                'favorite_id': getattr(fav, 'favorite_id', ''),
                'book_id': getattr(fav, 'book_id', ''),
                'book_title': book.title if book else '未知图书',
                'book_cover': book.cover if book else '',
                'book_author': book.author if book else '未知作者',
                'created_at': getattr(fav, 'created_at', '')
            })

        return {
            'statusCode': 200,
            'body': json.dumps(formatted_favorites)
        }

    except Exception as e:
        logger.error(
            f"获取收藏列表失败: user_id={user_id}, 错误={str(e)}",
            exc_info=True
        )
        return {
            'statusCode': 500,
            'body': json.dumps({'error': '获取收藏列表失败'})
        }


def get_user_view_history(headers):
    """获取用户浏览历史（通过仓储层优化）"""
    try:
        user_id = get_current_user_id(headers)
        if not user_id:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': '未授权访问'})
            }

        # 通过仓储层获取用户
        user = User.get_by_id(user_id)
        if not user:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': '用户不存在'})
            }

        # 通过仓储层获取浏览历史
        history = user.get_view_history()
        formatted_history = []

        for record in history:
            book = Book.get_by_id(record.book_id)
            formatted_history.append({
                'history_id': getattr(record, 'history_id', ''),
                'book_id': getattr(record, 'book_id', ''),
                'book_title': book.title if book else '未知图书',
                'book_cover': book.cover if book else '',
                'book_author': book.author if book else '未知作者',
                'view_time': getattr(record, 'view_time', '')
            })

        formatted_history.sort(key=lambda x: x['view_time'], reverse=True)

        return {
            'statusCode': 200,
            'body': json.dumps(formatted_history)
        }

    except Exception as e:
        logger.error(
            f"获取浏览历史失败: user_id={user_id}, 错误={str(e)}",
            exc_info=True
        )
        return {
            'statusCode': 500,
            'body': json.dumps({'error': '获取浏览历史失败'})
        }


def check_user_favorite(book_id, headers):
    """检查用户收藏状态（通过仓储层优化）"""
    try:
        user_id = get_current_user_id(headers)
        if not user_id:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': '未授权访问'})
            }

        # 通过仓储层获取用户
        user = User.get_by_id(user_id)
        if not user:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': '用户不存在'})
            }

        # 通过仓储层检查收藏状态
        is_favorited = user.check_favorite(book_id)

        return {
            'statusCode': 200,
            'body': json.dumps({'is_favorited': is_favorited})
        }

    except Exception as e:
        logger.error(
            f"检查收藏状态失败: book_id={book_id}, user_id={user_id}, 错误={str(e)}",
            exc_info=True
        )
        return {
            'statusCode': 500,
            'body': json.dumps({'error': '检查收藏状态失败'})
        }