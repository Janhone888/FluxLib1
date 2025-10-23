import json
import time
from config import logger
from utils.auth import get_current_user_id
from models.user import User
from models.book import Book
from models.borrow import Borrow


def borrow_book(book_id, headers, days=30):
    """借阅图书（使用仓储层优化）"""
    try:
        # 获取用户ID
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

        # 检查图书库存
        if book.stock <= 0:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': '图书库存不足'})
            }

        # 检查用户是否已借阅该图书
        existing_borrow = Borrow.get_by_user_book(user_id, book_id)
        if existing_borrow:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': '您已借阅该图书'})
            }

        # 创建借阅记录
        success, result = Borrow.create_borrow(book_id, user_id, days)
        if not success:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': result})
            }

        # 更新图书库存
        stock_success, stock_err = book.update_stock(-1)
        if not stock_success:
            # 回滚借阅记录
            borrow_record = Borrow.get_by_id(result)
            if borrow_record:
                borrow_record.update_status('returned')
            return {
                'statusCode': 500,
                'body': json.dumps({'error': stock_err})
            }

        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'borrow_id': result,
                'message': '借阅成功'
            })
        }

    except Exception as e:
        logger.error(f"借阅图书失败: book_id={book_id}, err={str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': '借阅失败'})
        }


def return_book(book_id, headers, is_early_return=False):
    """归还图书（使用仓储层优化）"""
    try:
        # 获取用户ID
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

        # 查找借阅记录
        borrow_record = Borrow.get_by_user_book(user_id, book_id)
        if not borrow_record:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': '未找到借阅记录'})
            }

        # 更新借阅状态
        success, err = borrow_record.update_status('returned', is_early_return)
        if not success:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': err})
            }

        # 更新图书库存
        stock_success, stock_err = book.update_stock(1)
        if not stock_success:
            # 回滚借阅状态
            borrow_record.update_status('borrowed')
            return {
                'statusCode': 500,
                'body': json.dumps({'error': stock_err})
            }

        action_msg = "提前归还" if is_early_return else "归还"
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'message': f'{action_msg}成功'
            })
        }

    except Exception as e:
        logger.error(f"归还图书失败: book_id={book_id}, err={str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': '归还失败'})
        }


def return_book_by_borrow_id(borrow_id, headers):
    """通过借阅ID归还图书（使用仓储层优化）"""
    try:
        # 获取用户ID
        user_id = get_current_user_id(headers)
        if not user_id:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': '未授权访问'})
            }

        # 通过仓储层获取借阅记录
        borrow_record = Borrow.get_by_id(borrow_id)
        if not borrow_record:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': '借阅记录不存在'})
            }

        # 检查权限（只能归还自己的图书）
        if borrow_record.user_id != user_id:
            return {
                'statusCode': 403,
                'body': json.dumps({'error': '无权操作此借阅记录'})
            }

        # 通过仓储层获取图书
        book = Book.get_by_id(borrow_record.book_id)
        if not book:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': '图书不存在'})
            }

        # 更新借阅状态
        success, err = borrow_record.update_status('returned')
        if not success:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': err})
            }

        # 更新图书库存
        stock_success, stock_err = book.update_stock(1)
        if not stock_success:
            # 回滚借阅状态
            borrow_record.update_status('borrowed')
            return {
                'statusCode': 500,
                'body': json.dumps({'error': stock_err})
            }

        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'message': '归还成功'
            })
        }

    except Exception as e:
        logger.error(f"通过借阅ID归还图书失败: borrow_id={borrow_id}, err={str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': '归还失败'})
        }


def batch_borrow_books(data, headers):
    """批量借阅（使用仓储层优化）"""
    try:
        # 获取用户ID
        user_id = get_current_user_id(headers)
        if not user_id:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': '未授权访问'})
            }

        book_ids = data.get('book_ids', [])
        if not book_ids:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': '请选择要借阅的图书'})
            }

        results = []
        for book_id in book_ids:
            # 对每本图书执行借阅操作
            result = borrow_book(book_id, headers)
            results.append({
                'book_id': book_id,
                'success': result['statusCode'] == 200,
                'message': json.loads(result['body']).get('error', '借阅成功') if result['statusCode'] != 200 else '借阅成功'
            })

        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'results': results
            })
        }

    except Exception as e:
        logger.error(f"批量借阅失败: err={str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': '批量借阅失败'})
        }


def batch_return_books(data, headers):
    """批量归还（使用仓储层优化）"""
    try:
        # 获取用户ID
        user_id = get_current_user_id(headers)
        if not user_id:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': '未授权访问'})
            }

        borrow_ids = data.get('borrow_ids', [])
        if not borrow_ids:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': '请选择要归还的图书'})
            }

        results = []
        for borrow_id in borrow_ids:
            # 对每个借阅记录执行归还操作
            result = return_book_by_borrow_id(borrow_id, headers)
            results.append({
                'borrow_id': borrow_id,
                'success': result['statusCode'] == 200,
                'message': json.loads(result['body']).get('error', '归还成功') if result['statusCode'] != 200 else '归还成功'
            })

        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'results': results
            })
        }

    except Exception as e:
        logger.error(f"批量归还失败: err={str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': '批量归还失败'})
        }


def get_user_borrows(headers):
    """获取用户借阅记录（使用仓储层优化）"""
    try:
        # 获取用户ID
        user_id = get_current_user_id(headers)
        if not user_id:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': '未授权访问'})
            }

        # 通过仓储层获取借阅记录
        borrows = Borrow.get_by_user_id(user_id)

        # 格式化借阅记录
        formatted_borrows = []
        for borrow in borrows:
            # 通过仓储层获取图书信息
            book = Book.get_by_id(borrow.book_id)
            if book:
                formatted_borrows.append({
                    'borrow_id': borrow.borrow_id,
                    'book_id': borrow.book_id,
                    'book_title': book.title,
                    'book_cover': book.cover,
                    'book_author': book.author,
                    'borrow_date': borrow.borrow_date,
                    'due_date': borrow.due_date,
                    'return_date': borrow.return_date,
                    'status': borrow.status,
                    'is_early_return': borrow.is_early_return
                })

        return {
            'statusCode': 200,
            'body': json.dumps(formatted_borrows)
        }

    except Exception as e:
        logger.error(f"获取用户借阅记录失败: err={str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': '获取借阅记录失败'})
        }