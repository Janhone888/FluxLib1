import uuid
import time
from typing import List, Optional, Dict, Any
from config import logger
from repositories.reservation_repository import ReservationRepository


class Reservation:
    """预约记录模型（使用仓储层进行数据访问）"""

    def __init__(self, data: Dict[str, Any]):
        """初始化预约记录"""
        self.reservation_id = data.get('reservation_id')
        self.book_id = data.get('book_id', '')
        self.user_id = data.get('user_id', '')
        self.reserve_date = data.get('reserve_date', '')
        self.time_slot = data.get('time_slot', '')
        self.days = data.get('days', 30)
        self.expected_return_date = data.get('expected_return_date', int(time.time()) + 30 * 24 * 3600)
        self.status = data.get('status', 'reserved')
        self.created_at = data.get('created_at', int(time.time()))
        self.updated_at = data.get('updated_at', int(time.time()))

        # 初始化仓储
        self._repository = ReservationRepository()

    @classmethod
    def create_reservation(cls, book_id: str, user_id: str, reserve_date: str,
                          time_slot: str, days: int = 30) -> tuple:
        """创建预约记录（使用仓储层）"""
        from models.user import User

        # 1. 生成reservation_id
        reservation_id = str(uuid.uuid4())
        current_time = int(time.time())

        # 2. 校验用户存在性
        user = User.get_by_id(user_id)
        if not user:
            logger.error(f"创建预约记录失败: 用户不存在（user_id={user_id}）")
            return False, "用户不存在"

        # 3. 计算预计归还时间
        try:
            reserve_timestamp = int(time.mktime(time.strptime(reserve_date, '%Y-%m-%d')))
            expected_return_date = reserve_timestamp + days * 24 * 3600
        except Exception as e:
            logger.error(f"计算预约归还日期失败: {str(e)}")
            expected_return_date = int(time.time()) + days * 24 * 3600

        # 4. 组装预约数据
        reservation_data = {
            'reservation_id': reservation_id,
            'book_id': book_id,
            'user_id': user_id,
            'reserve_date': reserve_date,
            'time_slot': time_slot,
            'days': days,
            'expected_return_date': expected_return_date,
            'status': 'reserved',
            'created_at': current_time,
            'updated_at': current_time
        }

        # 5. 通过仓储层插入数据
        repository = ReservationRepository()
        result = repository.create(reservation_data)

        if not result:
            logger.error(f"创建预约记录失败: reservation_id={reservation_id}")
            return False, "创建预约记录失败"

        logger.info(
            f"创建预约记录成功: reservation_id={reservation_id}, "
            f"user_id={user_id}, book_id={book_id}"
        )
        return True, reservation_id

    @classmethod
    def get_by_id(cls, reservation_id: str) -> Optional['Reservation']:
        """通过reservation_id获取预约记录"""
        repository = ReservationRepository()
        data = repository.get_by_id(reservation_id)

        if not data:
            return None

        return cls(data)

    @classmethod
    def get_by_user_id(cls, user_id: str) -> List['Reservation']:
        """获取用户所有预约记录"""
        repository = ReservationRepository()
        data_list = repository.get_by_user_id(user_id)

        return [cls(data) for data in data_list]

    @classmethod
    def get_by_book_id(cls, book_id: str) -> List['Reservation']:
        """获取图书的所有预约记录"""
        repository = ReservationRepository()
        data_list = repository.get_by_book_id(book_id)

        return [cls(data) for data in data_list]

    @classmethod
    def get_active_by_user_book(cls, user_id: str, book_id: str) -> Optional['Reservation']:
        """获取用户对某本图书的活跃预约记录"""
        repository = ReservationRepository()
        data = repository.get_active_by_user_book(user_id, book_id)

        if not data:
            return None

        return cls(data)

    def update_status(self, status: str) -> tuple:
        """更新预约状态"""
        if not self.reservation_id:
            logger.error("更新预约状态失败: 缺少reservation_id主键")
            return False, "预约记录不存在"

        # 1. 校验状态合法性
        if status not in ['reserved', 'fulfilled', 'cancelled', 'expired']:
            return False, "无效状态（仅支持reserved/fulfilled/cancelled/expired）"

        # 2. 组装更新字段
        update_columns = {
            'status': status,
            'updated_at': int(time.time())
        }

        # 3. 通过仓储层更新数据
        success = self._repository.update(self.reservation_id, update_columns)

        if not success:
            logger.error(f"更新预约状态失败: reservation_id={self.reservation_id}")
            return False, "更新预约状态失败"

        # 更新实例状态
        self.status = status
        self.updated_at = int(time.time())

        logger.info(f"更新预约状态成功: reservation_id={self.reservation_id}, 新状态={status}")
        return True, None

    def cancel_reservation(self) -> tuple:
        """取消预约"""
        return self.update_status('cancelled')

    def fulfill_reservation(self) -> tuple:
        """标记预约已完成"""
        return self.update_status('fulfilled')

    def delete_reservation(self) -> tuple:
        """删除预约记录"""
        if not self.reservation_id:
            logger.error("删除预约记录失败: 缺少reservation_id主键")
            return False, "预约记录不存在"

        # 通过仓储层删除数据
        success = self._repository.delete(self.reservation_id)

        if not success:
            logger.error(f"删除预约记录失败: reservation_id={self.reservation_id}")
            return False, "删除预约记录失败"

        logger.info(f"删除预约记录成功: reservation_id={self.reservation_id}")
        return True, None