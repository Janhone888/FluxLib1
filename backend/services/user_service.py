import json
from config import logger
from utils.auth import get_current_user_id
from models.user import User
from models.book import Book
from utils.storage import generate_presigned_url


def get_current_user_info(headers):
    """获取当前用户信息（对应原代码handle_get_current_user逻辑）"""
    try:
        # 1. 校验用户登录
        user_id = get_current_user_id(headers)
        if not user_id:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': '未授权访问'})
            }
        # 2. 获取用户信息
        user = User.get_by_id(user_id)
        if not user:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': '用户不存在'})
            }
        # 3. 格式化用户信息（隐藏敏感字段）
        user_info = {
            'user_id': user.user_id,
            'email': user.email,
            'display_name': user.display_name,
            'avatar_url': user.avatar_url,
            'role': user.role,
            'is_admin': user.role == 'admin',
            'gender': user.gender,
            'created_at': user.created_at
        }
        return {
            'statusCode': 200,
            'body': json.dumps(user_info)
        }
    except Exception as e:
        logger.error(f"获取当前用户信息失败: user_id={get_current_user_id(headers)}, {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': '获取用户信息失败'})
        }


def update_user_profile(headers, data, is_form_data=False):
    """更新用户信息（对应原代码handle_update_profile逻辑，支持头像上传）"""
    try:
        # 1. 校验用户登录
        user_id = get_current_user_id(headers)
        if not user_id:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': '未授权访问'})
            }
        # 2. 获取用户
        user = User.get_by_id(user_id)
        if not user:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': '用户不存在'})
            }
        # 3. 解析更新字段（支持表单数据和JSON）
        display_name = None
        avatar_url = None
        gender = None
        if is_form_data:
            # 表单数据（含文件上传）
            display_name = data.get('display_name')
            gender = data.get('gender')
            # 处理头像文件
            avatar_file = data.get('avatar')
            if avatar_file:
                # 生成OSS预签名URL并上传
                file_name = avatar_file.filename
                file_type = avatar_file.content_type
                oss_res = generate_presigned_url(file_name, file_type)
                if oss_res['statusCode'] != 200:
                    return oss_res
                # 此处省略文件上传到OSS的HTTP请求（前端会通过预签名URL直接上传）
                avatar_url = oss_res['body']['access_url']
        else:
            # JSON数据
            display_name = data.get('display_name')
            avatar_url = data.get('avatar_url')
            gender = data.get('gender')
        # 4. 更新用户信息
        success, err = user.update_profile(
            display_name=display_name,
            avatar_url=avatar_url,
            gender=gender
        )
        if not success:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': err})
            }
        # 5. 组装响应
        return {
            'statusCode': 200,
            'body': json.dumps({'success': True})
        }
    except Exception as e:
        logger.error(f"更新用户信息失败: user_id={get_current_user_id(headers)}, {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': '更新失败'})
        }


def handle_user_favorite(book_id, headers, action='add'):
    """处理用户收藏（添加/移除，对应原代码handle_add_favorite/handle_remove_favorite）"""
    try:
        # 1. 校验用户登录
        user_id = get_current_user_id(headers)
        if not user_id:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': '未授权访问'})
            }
        # 2. 获取用户
        user = User.get_by_id(user_id)
        if not user:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': '用户不存在'})
            }
        # 3. 校验图书存在性
        book = Book.get_by_id(book_id)
        if not book:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': '图书不存在'})
            }
        # 4. 执行收藏/取消收藏
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
        # 5. 组装响应
        return {
            'statusCode': 200,
            'body': json.dumps({'success': True, 'message': msg})
        }
    except Exception as e:
        logger.error(f"处理收藏失败: action={action}, book_id={book_id}, user_id={get_current_user_id(headers)}, {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': '处理收藏失败'})
        }


def get_user_favorites(headers):
    """获取用户收藏列表（对应原代码handle_get_favorites逻辑）"""
    try:
        # 1. 校验用户登录
        user_id = get_current_user_id(headers)
        if not user_id:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': '未授权访问'})
            }
        # 2. 获取用户收藏
        user = User.get_by_id(user_id)
        if not user:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': '用户不存在'})
            }
        favorites = user.get_favorites()
        # 3. 格式化收藏列表（补充图书信息）
        formatted_favorites = []
        for fav in favorites:
            book = Book.get_by_id(fav.book_id)
            formatted_favorites.append({
                'favorite_id': fav.favorite_id,
                'book_id': fav.book_id,
                'book_title': book.title if book else '未知图书',
                'book_cover': book.cover if book else '',
                'book_author': book.author if book else '未知作者',
                'created_at': fav.created_at
            })
        # 4. 组装响应
        return {
            'statusCode': 200,
            'body': json.dumps(formatted_favorites)
        }
    except Exception as e:
        logger.error(f"获取用户收藏列表失败: user_id={get_current_user_id(headers)}, {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': '获取收藏列表失败'})
        }


def get_user_view_history(headers):
    """获取用户浏览历史（对应原代码handle_get_view_history逻辑）"""
    try:
        # 1. 校验用户登录
        user_id = get_current_user_id(headers)
        if not user_id:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': '未授权访问'})
            }
        # 2. 获取用户浏览历史
        user = User.get_by_id(user_id)
        if not user:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': '用户不存在'})
            }
        history = user.get_view_history()
        # 3. 格式化历史记录（补充图书信息+按时间排序）
        formatted_history = []
        for record in history:
            book = Book.get_by_id(record.book_id)
            formatted_history.append({
                'history_id': record.history_id,
                'book_id': record.book_id,
                'book_title': book.title if book else '未知图书',
                'book_cover': book.cover if book else '',
                'book_author': book.author if book else '未知作者',
                'view_time': record.view_time
            })
        # 按浏览时间倒序
        formatted_history.sort(key=lambda x: x['view_time'], reverse=True)
        # 4. 组装响应
        return {
            'statusCode': 200,
            'body': json.dumps(formatted_history)
        }
    except Exception as e:
        logger.error(f"获取用户浏览历史失败: user_id={get_current_user_id(headers)}, {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': '获取浏览历史失败'})
        }