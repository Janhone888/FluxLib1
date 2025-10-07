import json
import time
from config import logger
from utils.storage import generate_presigned_url
from models.book import Book
from models.user import User
from utils.auth import get_current_user_id


def get_book_list(page=1, size=10, category=''):
    """获取图书列表（添加总数获取超时保护）"""
    try:
        logger.info(f"🔍 开始获取图书列表: page={page}, size={size}, category='{category}'")

        # 1. 调用Book模型获取数据
        logger.info("📚 调用 Book.get_list()...")
        books, total = Book.get_list(page=page, size=size, category=category)
        logger.info(f"📊 查询结果: 获取到 {len(books)} 本书, 总数={total}")

        # 2. 如果总数获取失败，使用估算值
        if total == 0 and len(books) > 0:
            logger.warning("⚠️ 总数获取失败，使用估算值")
            total = len(books) * page  # 简单估算

        # 3. 格式化返回数据
        formatted_books = []
        for i, book in enumerate(books):
            book_data = {
                'book_id': getattr(book, 'book_id', ''),
                'title': getattr(book, 'title', ''),
                'cover': getattr(book, 'cover', ''),
                'category': getattr(book, 'category', ''),
                'status': getattr(book, 'status', 'available'),
                'stock': getattr(book, 'stock', 0),
                'author': getattr(book, 'author', ''),
                'publisher': getattr(book, 'publisher', ''),
                'price': getattr(book, 'price', 0.0),
                'summary': getattr(book, 'summary', ''),
                'description': getattr(book, 'description', '')
            }
            formatted_books.append(book_data)
            if i < 3:  # 只打印前3本书的调试信息
                logger.info(f"📖 图书 {i + 1}: {book_data['title']} (ID: {book_data['book_id']})")

        logger.info(f"✅ 成功格式化 {len(formatted_books)} 本书")

        # 4. 组装响应
        response_body = {
            'items': formatted_books,
            'total': total,
            'page': page,
            'size': size
        }

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(response_body)
        }

    except Exception as e:
        logger.error(f"❌ 获取图书列表失败: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Failed to get books', 'detail': str(e)})
        }


def get_book_detail(book_id, headers=None):
    """获取图书详情（复刻原版handle_get_book逻辑，含浏览历史记录）"""
    try:
        # 1. 获取图书信息（与原版一致：校验图书存在性）
        book = Book.get_by_id(book_id)
        if not book:
            logger.warning(f"获取图书详情失败: 图书不存在（book_id={book_id}）")
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Book not found'})
            }

        # 2. 记录浏览历史（原版逻辑：仅登录用户记录）
        if headers:
            user_id = get_current_user_id(headers)
            if user_id:
                user = User.get_by_id(user_id)
                if user:
                    # 调用User模型添加浏览历史（与原版add_view_history一致）
                    user.add_view_history(book_id)
                    logger.info(f"记录浏览历史: user_id={user_id}, book_id={book_id}")

        # 3. 获取借阅历史（与原版一致）
        borrow_history = book.get_borrow_history()
        formatted_history = []
        for record in borrow_history:
            formatted_history.append({
                'borrow_id': record.borrow_id,
                'user_id': record.user_id,
                'borrow_date': record.borrow_date,
                'due_date': record.due_date,
                'return_date': record.return_date,
                'status': record.status
            })

        # 4. 格式化图书详情（与原版字段、类型完全一致）
        book_detail = {
            'book_id': book.book_id,
            'title': book.title,
            'author': book.author,
            'publisher': book.publisher,
            'isbn': book.isbn,
            'price': book.price,  # float类型
            'category': book.category,
            'description': book.description,
            'cover': book.cover,
            'summary': book.summary,
            'status': book.status,
            'stock': book.stock,  # int类型
            'created_at': book.created_at,
            'updated_at': book.updated_at,
            'borrow_history': formatted_history
        }

        return {
            'statusCode': 200,
            'body': json.dumps(book_detail)
        }
    except Exception as e:
        logger.error(f"获取图书详情失败: book_id={book_id}, err={str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to get book'})
        }


def create_book(book_data, headers):
    """创建图书（复刻原版handle_create_book逻辑，含管理员权限校验）"""
    try:
        # 1. 权限校验（原版逻辑：仅管理员可创建）
        user_id = get_current_user_id(headers)
        if not user_id:
            logger.warning("创建图书失败: 未授权访问（无用户ID）")
            return {
                'statusCode': 401,
                'body': json.dumps({'error': '未授权访问'})
            }
        # 校验用户角色（与原版一致：仅admin角色可操作）
        user = User.get_by_id(user_id)
        if not user or user.role != 'admin':
            logger.warning(f"创建图书失败: 权限不足（user_id={user_id}, role={user.role if user else 'unknown'}）")
            return {
                'statusCode': 403,
                'body': json.dumps({'error': '需要管理员权限'})
            }

        # 2. 调用Book模型创建图书（与原版一致）
        success, result = Book.create_book(book_data)
        if not success:
            logger.error(f"创建图书失败: 参数校验不通过（err={result}）")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': result})
            }

        # 3. 组装成功响应（与原版结构一致）
        return {
            'statusCode': 201,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'book_id': result,
                'message': '图书创建成功'
            })
        }
    except Exception as e:
        logger.error(f"创建图书失败: err={str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': '创建图书失败',
                'detail': str(e)
            })
        }


def update_book(book_id, book_data, headers):
    """更新图书（复刻原版handle_update_book逻辑，含权限与参数校验）"""
    try:
        # 1. 权限校验（与原版一致：仅管理员可更新）
        user_id = get_current_user_id(headers)
        if not user_id:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': '未授权访问'})
            }
        user = User.get_by_id(user_id)
        if not user or user.role != 'admin':
            return {
                'statusCode': 403,
                'body': json.dumps({'error': '需要管理员权限'})
            }

        # 2. 校验图书存在性（与原版一致）
        book = Book.get_by_id(book_id)
        if not book:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Book not found'})
            }

        # 3. 调用Book模型更新（与原版一致）
        success, err = book.update_book(book_data)
        if not success:
            logger.error(f"更新图书失败: book_id={book_id}, err={err}")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': err})
            }

        # 4. 组装响应（与原版一致）
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Book updated successfully'})
        }
    except Exception as e:
        logger.error(f"更新图书失败: book_id={book_id}, err={str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to update book'})
        }


def delete_book(book_id, headers):
    """删除图书（复刻原版handle_delete_book逻辑，含权限校验与错误处理）"""
    try:
        # 1. 权限校验（与原版一致：仅管理员可删除）
        user_id = get_current_user_id(headers)
        if not user_id:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': '未授权访问'})
            }
        user = User.get_by_id(user_id)
        if not user or user.role != 'admin':
            logger.warning(f"删除图书失败: 权限不足（user_id={user_id}, role={user.role if user else 'unknown'}）")
            return {
                'statusCode': 403,
                'body': json.dumps({'error': '需要管理员权限'})
            }

        # 2. 校验图书存在性（与原版一致）
        book = Book.get_by_id(book_id)
        if not book:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Book not found'})
            }

        # 3. 调用Book模型删除（与原版一致）
        success, err = book.delete_book()
        if not success:
            logger.error(f"删除图书失败: book_id={book_id}, err={err}")
            return {
                'statusCode': 500,
                'body': json.dumps({'error': err})
            }

        # 4. 组装响应（与原版一致）
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Book deleted successfully'})
        }
    except Exception as e:
        logger.error(f"删除图书失败: book_id={book_id}, err={str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': '删除失败'})
        }


def get_book_cover_url(file_name, file_type):
    """生成图书封面预签名URL（完全复刻原版handle_presigned_url逻辑）"""
    try:
        # 校验参数（与原版一致）
        if not file_name or not file_type:
            logger.error("生成预签名URL失败: 缺少file_name或file_type")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing file_name or file_type'})
            }

        # 调用storage工具生成URL（与原版一致）
        result = generate_presigned_url(file_name, file_type)
        return result
    except Exception as e:
        logger.error(f"生成封面预签名URL失败: err={str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': '生成预签名URL失败',
                'detail': str(e)
            })
        }