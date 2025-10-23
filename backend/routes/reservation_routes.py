import json
from flask import request, jsonify
from config import logger
from services.reservation_service import (
    create_reservation,
    cancel_reservation,
    get_user_reservations,
    get_reservation_detail,
    fulfill_reservation,
    get_book_reservations
)


def register_reservation_routes(bp):
    """注册预约相关路由到蓝图"""

    @bp.route('/books/<book_id>/reserve', methods=['POST'])
    def handle_reserve_book(book_id):
        """预约图书"""
        try:
            data = request.get_json() or {}
            # 提取预约参数
            reserve_date = data.get('reserve_date')
            time_slot = data.get('time_slot')
            days = data.get('days', 30)
            headers = request.headers

            # 校验必填参数
            if not reserve_date or not time_slot:
                return jsonify({'error': '预约日期和时间段是必填项'}), 400

            result = create_reservation(book_id, headers, reserve_date, time_slot, days)
            status_code = result['statusCode']
            body = result['body']
            if isinstance(body, str):
                body = json.loads(body)
            return jsonify(body), status_code

        except Exception as e:
            logger.error(f"处理图书预约失败: book_id={book_id}, {str(e)}", exc_info=True)
            return jsonify({'error': 'Failed to reserve book'}), 500

    @bp.route('/reservations/<reservation_id>/cancel', methods=['POST'])
    def handle_cancel_reservation(reservation_id):
        """取消预约"""
        try:
            headers = request.headers
            result = cancel_reservation(reservation_id, headers)
            status_code = result['statusCode']
            body = result['body']
            if isinstance(body, str):
                body = json.loads(body)
            return jsonify(body), status_code

        except Exception as e:
            logger.error(f"取消预约失败: reservation_id={reservation_id}, {str(e)}", exc_info=True)
            return jsonify({'error': '取消预约失败'}), 500

    @bp.route('/user/reservations', methods=['GET'])
    def handle_get_user_reservations():
        """获取用户预约记录"""
        try:
            headers = request.headers
            result = get_user_reservations(headers)
            status_code = result['statusCode']
            body = result['body']
            if isinstance(body, str):
                body = json.loads(body)
            return jsonify(body), status_code

        except Exception as e:
            logger.error(f"处理用户预约记录查询失败: {str(e)}", exc_info=True)
            return jsonify({'error': 'Failed to get user reservations'}), 500

    @bp.route('/reservations/<reservation_id>', methods=['GET'])
    def handle_get_reservation_detail(reservation_id):
        """获取预约详情"""
        try:
            headers = request.headers
            result = get_reservation_detail(reservation_id, headers)
            status_code = result['statusCode']
            body = result['body']
            if isinstance(body, str):
                body = json.loads(body)
            return jsonify(body), status_code

        except Exception as e:
            logger.error(f"获取预约详情失败: reservation_id={reservation_id}, {str(e)}", exc_info=True)
            return jsonify({'error': '获取预约详情失败'}), 500

    @bp.route('/reservations/<reservation_id>/fulfill', methods=['POST'])
    def handle_fulfill_reservation(reservation_id):
        """标记预约为已完成（管理员）"""
        try:
            headers = request.headers
            result = fulfill_reservation(reservation_id, headers)
            status_code = result['statusCode']
            body = result['body']
            if isinstance(body, str):
                body = json.loads(body)
            return jsonify(body), status_code

        except Exception as e:
            logger.error(f"标记预约完成失败: reservation_id={reservation_id}, {str(e)}", exc_info=True)
            return jsonify({'error': '标记预约完成失败'}), 500

    @bp.route('/books/<book_id>/reservations', methods=['GET'])
    def handle_get_book_reservations(book_id):
        """获取图书的预约记录（管理员）"""
        try:
            headers = request.headers
            result = get_book_reservations(book_id, headers)
            status_code = result['statusCode']
            body = result['body']
            if isinstance(body, str):
                body = json.loads(body)
            return jsonify(body), status_code

        except Exception as e:
            logger.error(f"获取图书预约记录失败: book_id={book_id}, {str(e)}", exc_info=True)
            return jsonify({'error': '获取图书预约记录失败'}), 500