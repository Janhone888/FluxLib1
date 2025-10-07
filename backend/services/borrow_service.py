import json
import time
from config import logger
from utils.auth import get_current_user_id
from models.book import Book
from models.borrow import Borrow, Reservation
from utils.email import send_reservation_confirmation


def borrow_book(book_id, headers, days=30):
    """借阅图书（对应原代码handle_borrow_book逻辑，含库存校验）"""
    try:
        logger.info(f"借阅请求: book_id={book_id}, days={days}")
        # 1. 校验用户登录
        user_id = get_current_user_id(headers)
        if not user_id:
            logger.warning("借阅失败: 未授权访问")
            return {
                'statusCode': 401,
                'body': json.dumps({'error': '未授权访问'})
            }

        # 2. 校验图书存在性和库存
        book = Book.get_by_id(book_id)
        if not book:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': '图书不存在'})
            }
        if book.stock <= 0:
            logger.warning(f"借阅失败: 库存不足（book_id={book_id}, stock={book.stock}）")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': '图书库存不足'})
            }

        # 3. 检查用户是否已借阅该图书
        existing_borrow = Borrow.get_by_user_book(user_id, book_id)
        if existing_borrow and existing_borrow.status == 'borrowed':
            logger.warning(f"借阅失败: 用户已借阅（user_id={user_id}, book_id={book_id}）")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': '您已借阅该图书，无法重复借阅'})
            }

        # 4. 扣减库存
        stock_success, stock_err = book.update_stock(change=-1)  # 库存-1
        if not stock_success:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': stock_err})
            }

        # 5. 创建借阅记录
        borrow_success, borrow_result = Borrow.create_borrow(book_id, user_id, days)
        if not borrow_success:
            # 库存回滚
            book.update_stock(change=1)
            logger.error(f"借阅失败: 创建记录失败（err={borrow_result}）")
            return {
                'statusCode': 500,
                'body': json.dumps({'error': borrow_result})
            }

        # 6. 组装响应
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'borrow_id': borrow_result,
                'due_date': int(time.time()) + days * 24 * 3600
            })
        }
    except Exception as e:
        logger.error(f"借阅图书失败: book_id={book_id}, user_id={get_current_user_id(headers)}, {str(e)}",
                     exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': '借阅失败'})
        }


def return_book(book_id, headers, is_early_return=False):
    """归还图书（对应原代码handle_return_book和handle_return_early逻辑）"""
    try:
        user_id = get_current_user_id(headers)
        if not user_id:
            logger.warning("未授权访问，无法获取用户ID")
            return {
                'statusCode': 401,
                'body': json.dumps({'error': '未授权访问'})
            }

        # 获取用户的借阅记录（状态为borrowed）
        borrow_record = Borrow.get_by_user_book(user_id, book_id)
        if not borrow_record or borrow_record.status != 'borrowed':
            logger.warning(f"归还失败: 无有效借阅记录（user_id={user_id}, book_id={book_id}）")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': '未找到借阅记录'})
            }

        borrow_id = borrow_record.get('borrow_id')
        if not borrow_id:
            logger.warning("借阅记录中未找到borrow_id")
            return {
                'statusCode': 500,
                'body': json.dumps({'error': '借阅记录格式错误'})
            }

        # 获取图书并增加库存
        book = Book.get_by_id(book_id)
        if not book:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': '图书不存在'})
            }
        book.update_stock(change=1)  # 库存+1

        # 更新借阅记录状态
        status_success, status_err = borrow_record.update_status(
            status='returned',
            is_early_return=is_early_return
        )
        if not status_success:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': status_err})
            }

        # 组装响应信息
        message = '归还成功' + ('（提前归还）' if is_early_return else '')
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'is_early_return': is_early_return,
                'message': message
            })
        }
    except Exception as e:
        logger.error(f"归还图书失败: book_id={book_id}, user_id={get_current_user_id(headers)}, {str(e)}",
                     exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': '归还失败'})
        }


def reserve_book(book_id, headers, reserve_date, time_slot, days=30):
    """预约图书（对应原代码handle_reserve_book逻辑，含库存校验和邮件通知）"""
    try:
        logger.info(f"预约请求: book_id={book_id}, date={reserve_date}, slot={time_slot}")
        user_id = get_current_user_id(headers)
        if not user_id:
            logger.warning("未授权访问，无法获取用户ID")
            return {
                'statusCode': 401,
                'body': json.dumps({'error': '未授权访问'})
            }

        # 校验图书存在性和库存
        book = Book.get_by_id(book_id)
        if not book:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': '图书不存在'})
            }
        if book.stock <= 0:
            # 获取最早归还日期
            earliest_date = book.get_earliest_return_date()
            logger.warning(f"库存不足，无法预约: book_id={book_id}, stock={book.stock}")
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': '图书库存不足',
                    'earliest_available_date': earliest_date,
                    'message': f'抱歉，图书库存为0，您可以收藏此书，在{earliest_date}之后再来'
                })
            }

        # 创建预约记录
        reserve_success, reserve_id = Reservation.create_reservation(
            book_id=book_id,
            user_id=user_id,
            reserve_date=reserve_date,
            time_slot=time_slot,
            days=days
        )
        if not reserve_success:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': reserve_id})
            }

        # 发送预约确认邮件
        user = User.get_by_id(user_id)
        if user and user.email:
            book_info = {
                'title': book.title,
                'author': book.author
            }
            reserve_data = {
                'reserve_date': reserve_date,
                'time_slot': time_slot,
                'days': days,
                'expected_return_date': int(time.mktime(time.strptime(reserve_date, '%Y-%m-%d'))) + days * 24 * 3600
            }
            send_reservation_confirmation(user.email, book_info, reserve_data)

        # 组装响应
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'reservation_id': reserve_id,
                'expected_return_date': reserve_data['expected_return_date']
            })
        }
    except Exception as e:
        logger.error(f"预约图书失败: book_id={book_id}, user_id={get_current_user_id(headers)}, {str(e)}",
                     exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': '预约失败'})
        }


def batch_borrow_books(body, headers):
    """批量借阅（对应原代码handle_batch_borrow逻辑）"""
    try:
        # 1. 校验用户登录
        user_id = get_current_user_id(headers)
        if not user_id:
            logger.warning("未授权访问，无法获取用户ID")
            return {
                'statusCode': 401,
                'body': json.dumps({'error': '未授权访问'})
            }

        book_ids = body.get('book_ids', [])
        if not book_ids:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': '请选择要借阅的图书'})
            }

        results = []
        success_count = 0
        for book_id in book_ids:
            try:
                # 调用单个借阅接口
                borrow_res = borrow_book(book_id, headers)
                if borrow_res['statusCode'] == 200:
                    borrow_data = json.loads(borrow_res['body'])
                    results.append({
                        'book_id': book_id,
                        'success': True,
                        'borrow_id': borrow_data.get('borrow_id', ''),
                        'due_date': borrow_data.get('due_date', '')
                    })
                    success_count += 1
                else:
                    error_data = json.loads(borrow_res['body'])
                    results.append({
                        'book_id': book_id,
                        'success': False,
                        'error': error_data.get('error', '借阅失败')
                    })
            except Exception as e:
                results.append({
                    'book_id': book_id,
                    'success': False,
                    'error': str(e)
                })

        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'borrowed_count': success_count,
                'results': results
            })
        }
    except Exception as e:
        logger.error(f"批量借阅失败: user_id={get_current_user_id(headers)}, {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': '批量借阅失败'})
        }


def batch_return_books(body, headers):
    """批量归还（对应原代码handle_batch_return逻辑）"""
    try:
        # 1. 校验用户登录
        user_id = get_current_user_id(headers)
        if not user_id:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': 'Unauthorized'})
            }

        borrow_ids = body.get('borrow_ids', [])
        results = []
        for borrow_id in borrow_ids:
            # 3. 查找借阅记录并校验权限
            borrow_record = Borrow.get_by_id(borrow_id)
            if not borrow_record:
                results.append({'borrow_id': borrow_id, 'success': False, 'error': '记录不存在'})
                continue
            if borrow_record.user_id != user_id:
                results.append({'borrow_id': borrow_id, 'success': False, 'error': '无权操作'})
                continue
            if borrow_record.status != 'borrowed':
                results.append({'borrow_id': borrow_id, 'success': False, 'error': '记录已归还'})
                continue

            # 4. 归还图书
            return_res = return_book(borrow_record.book_id, headers)
            if return_res['statusCode'] == 200:
                results.append({'borrow_id': borrow_id, 'success': True})
            else:
                error_data = json.loads(return_res['body'])
                results.append({
                    'borrow_id': borrow_id,
                    'success': False,
                    'error': error_data.get('error', '归还失败')
                })

        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'results': results
            })
        }
    except Exception as e:
        logger.error(f"批量归还失败: user_id={get_current_user_id(headers)}, {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': '批量归还失败'})
        }


def get_user_borrows(headers):
    """获取用户借阅记录（对应原代码handle_get_user_borrows逻辑）"""
    try:
        # 1. 校验用户登录
        user_id = get_current_user_id(headers)
        if not user_id:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': 'Unauthorized'})
            }

        # 2. 获取借阅记录
        borrows = Borrow.get_by_user_id(user_id)
        formatted_borrows = []
        for borrow in borrows:
            # 3. 补充图书信息
            book = Book.get_by_id(borrow.book_id)
            book_title = book.title if book else '未知图书'
            book_cover = book.cover if book else ''
            formatted_borrows.append({
                'borrow_id': borrow.borrow_id,
                'book_id': borrow.book_id,
                'book_title': book_title,
                'book_cover': book_cover,
                'borrow_date': borrow.borrow_date,
                'due_date': borrow.due_date,
                'return_date': borrow.return_date,
                'status': borrow.status,
                'is_early_return': borrow.is_early_return
            })

        return {
            'statusCode': 200,
            'body': json.dumps({'items': formatted_borrows})
        }
    except Exception as e:
        logger.error(f"获取用户借阅记录失败: user_id={get_current_user_id(headers)}, {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to get borrow records'})
        }


# -------------------------- 新增：补充 return_book_by_borrow_id 函数 --------------------------
def return_book_by_borrow_id(borrow_id, headers):
    """通过借阅ID归还图书（对应原代码handle_return_by_borrow_id逻辑）"""
    try:
        # 1. 校验用户登录
        user_id = get_current_user_id(headers)
        if not user_id:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': '未授权访问'})
            }

        # 2. 获取借阅记录并校验合法性
        borrow_record = Borrow.get_by_id(borrow_id)
        if not borrow_record:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': '借阅记录不存在'})
            }
        # 校验用户权限（仅本人可归还）
        if borrow_record.user_id != user_id:
            return {
                'statusCode': 403,
                'body': json.dumps({'error': '无权操作此借阅记录'})
            }
        # 校验记录状态（仅未归还可操作）
        if borrow_record.status != 'borrowed':
            return {
                'statusCode': 400,
                'body': json.dumps({'error': '借阅记录已归还'})
            }

        # 3. 调用归还逻辑（复用已有的 return_book 函数，确保逻辑一致）
        return_result = return_book(borrow_record.book_id, headers, is_early_return=False)
        if return_result['statusCode'] != 200:
            return return_result

        # 4. 组装成功响应
        return {
            'statusCode': 200,
            'body': json.dumps({'success': True})
        }
    except Exception as e:
        logger.error(f"通过借阅ID归还失败: borrow_id={borrow_id}, user_id={get_current_user_id(headers)}, {str(e)}",
                     exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': '归还失败'})
        }