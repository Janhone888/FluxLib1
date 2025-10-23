# Code/services/reservation_service.py

import json
import time
from typing import Dict, Any, List
from config import logger
from utils.auth import get_current_user_id
from models.user import User
from models.book import Book
from models.reservation import Reservation


def create_reservation(book_id: str, headers: Dict[str, str],
                       reserve_date: str, time_slot: str, days: int = 30) -> Dict[str, Any]:
    """创建预约记录"""
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

        # 检查用户是否已有该图书的活跃预约
        existing_reservation = Reservation.get_active_by_user_book(user_id, book_id)
        if existing_reservation:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': '您已有该图书的活跃预约'})
            }

        # 检查图书库存
        if book.stock <= 0:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': '图书库存不足，无法预约'})
            }

        # 创建预约记录
        success, result = Reservation.create_reservation(book_id, user_id, reserve_date, time_slot, days)

        if not success:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': result})
            }

        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'reservation_id': result,
                'message': '预约成功'
            })
        }

    except Exception as e:
        logger.error(f"预约图书失败: book_id={book_id}, err={str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': '预约失败'})
        }


def cancel_reservation(reservation_id: str, headers: Dict[str, str]) -> Dict[str, Any]:
    """取消预约"""
    try:
        # 获取用户ID
        user_id = get_current_user_id(headers)
        if not user_id:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': '未授权访问'})
            }

        # 通过仓储层获取预约记录
        reservation = Reservation.get_by_id(reservation_id)
        if not reservation:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': '预约记录不存在'})
            }

        # 检查权限：只能取消自己的预约
        if reservation.user_id != user_id:
            return {
                'statusCode': 403,
                'body': json.dumps({'error': '无权操作此预约记录'})
            }

        # 检查预约状态
        if reservation.status != 'reserved':
            return {
                'statusCode': 400,
                'body': json.dumps({'error': '只能取消进行中的预约'})
            }

        # 取消预约
        success, err = reservation.cancel_reservation()
        if not success:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': err})
            }

        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'message': '取消预约成功'
            })
        }

    except Exception as e:
        logger.error(f"取消预约失败: reservation_id={reservation_id}, err={str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': '取消预约失败'})
        }


def get_user_reservations(headers: Dict[str, str]) -> Dict[str, Any]:
    """获取用户预约记录"""
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

        # 获取用户所有预约记录
        reservations = Reservation.get_by_user_id(user_id)

        # 格式化预约记录
        formatted_reservations = []
        for reservation in reservations:
            # 通过仓储层获取图书信息
            book = Book.get_by_id(reservation.book_id)
            if book:
                formatted_reservations.append({
                    'reservation_id': reservation.reservation_id,
                    'book_id': reservation.book_id,
                    'book_title': book.title,
                    'book_cover': book.cover,
                    'book_author': book.author,
                    'reserve_date': reservation.reserve_date,
                    'time_slot': reservation.time_slot,
                    'days': reservation.days,
                    'expected_return_date': reservation.expected_return_date,
                    'status': reservation.status,
                    'created_at': reservation.created_at
                })

        return {
            'statusCode': 200,
            'body': json.dumps(formatted_reservations)
        }

    except Exception as e:
        logger.error(f"获取用户预约记录失败: err={str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': '获取预约记录失败'})
        }


def get_reservation_detail(reservation_id: str, headers: Dict[str, str]) -> Dict[str, Any]:
    """获取预约详情"""
    try:
        # 获取用户ID
        user_id = get_current_user_id(headers)
        if not user_id:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': '未授权访问'})
            }

        # 通过仓储层获取预约记录
        reservation = Reservation.get_by_id(reservation_id)
        if not reservation:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': '预约记录不存在'})
            }

        # 检查权限：只能查看自己的预约
        if reservation.user_id != user_id:
            return {
                'statusCode': 403,
                'body': json.dumps({'error': '无权查看此预约记录'})
            }

        # 通过仓储层获取图书信息
        book = Book.get_by_id(reservation.book_id)
        if not book:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': '关联图书不存在'})
            }

        # 格式化预约详情
        reservation_detail = {
            'reservation_id': reservation.reservation_id,
            'book_id': reservation.book_id,
            'book_title': book.title,
            'book_cover': book.cover,
            'book_author': book.author,
            'book_isbn': book.isbn,
            'book_publisher': book.publisher,
            'reserve_date': reservation.reserve_date,
            'time_slot': reservation.time_slot,
            'days': reservation.days,
            'expected_return_date': reservation.expected_return_date,
            'status': reservation.status,
            'created_at': reservation.created_at,
            'updated_at': reservation.updated_at
        }

        return {
            'statusCode': 200,
            'body': json.dumps(reservation_detail)
        }

    except Exception as e:
        logger.error(f"获取预约详情失败: reservation_id={reservation_id}, err={str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': '获取预约详情失败'})
        }


def fulfill_reservation(reservation_id: str, headers: Dict[str, str]) -> Dict[str, Any]:
    """标记预约为已完成（管理员功能）"""
    try:
        # 获取用户ID
        user_id = get_current_user_id(headers)
        if not user_id:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': '未授权访问'})
            }

        # 权限校验 - 仅管理员可操作
        user = User.get_by_id(user_id)
        if not user or user.role != 'admin':
            return {
                'statusCode': 403,
                'body': json.dumps({'error': '需要管理员权限'})
            }

        # 通过仓储层获取预约记录
        reservation = Reservation.get_by_id(reservation_id)
        if not reservation:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': '预约记录不存在'})
            }

        # 标记为已完成
        success, err = reservation.fulfill_reservation()
        if not success:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': err})
            }

        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'message': '预约已完成标记'
            })
        }

    except Exception as e:
        logger.error(f"标记预约完成失败: reservation_id={reservation_id}, err={str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': '标记预约完成失败'})
        }


def get_book_reservations(book_id: str, headers: Dict[str, str]) -> Dict[str, Any]:
    """获取图书的预约记录（管理员功能）"""
    try:
        # 获取用户ID
        user_id = get_current_user_id(headers)
        if not user_id:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': '未授权访问'})
            }

        # 权限校验 - 仅管理员可操作
        user = User.get_by_id(user_id)
        if not user or user.role != 'admin':
            return {
                'statusCode': 403,
                'body': json.dumps({'error': '需要管理员权限'})
            }

        # 通过仓储层获取图书
        book = Book.get_by_id(book_id)
        if not book:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': '图书不存在'})
            }

        # 获取图书的所有预约记录
        reservations = Reservation.get_by_book_id(book_id)

        # 格式化预约记录
        formatted_reservations = []
        for reservation in reservations:
            # 获取用户信息
            user = User.get_by_id(reservation.user_id)
            if user:
                formatted_reservations.append({
                    'reservation_id': reservation.reservation_id,
                    'user_id': reservation.user_id,
                    'user_email': user.email,
                    'user_display_name': user.display_name,
                    'reserve_date': reservation.reserve_date,
                    'time_slot': reservation.time_slot,
                    'days': reservation.days,
                    'expected_return_date': reservation.expected_return_date,
                    'status': reservation.status,
                    'created_at': reservation.created_at
                })

        return {
            'statusCode': 200,
            'body': json.dumps(formatted_reservations)
        }

    except Exception as e:
        logger.error(f"获取图书预约记录失败: book_id={book_id}, err={str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': '获取图书预约记录失败'})
        }