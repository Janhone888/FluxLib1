import time
from typing import List, Dict, Any, Optional
from tablestore import (
    SingleColumnCondition, ComparatorType, CompositeColumnCondition,
    LogicalOperator, INF_MIN, INF_MAX, RowExistenceExpectation
)
from config import logger, RESERVATIONS_TABLE
from utils.database import ots_put_row, ots_get_row, ots_get_range, ots_delete_row
from repositories.base_repository import BaseRepository


class ReservationRepository(BaseRepository):
    """预约记录仓储层，负责所有预约数据的OTS访问操作"""

    def __init__(self):
        self.table_name = RESERVATIONS_TABLE

    def get_by_id(self, reservation_id: str) -> Optional[Dict[str, Any]]:
        """根据reservation_id获取预约数据"""
        logger.info(f"查询Reservations表: reservation_id={reservation_id}")

        data = ots_get_row(self.table_name, primary_key=[('reservation_id', reservation_id)])
        if not data:
            logger.info(f"预约记录不存在: reservation_id={reservation_id}")
            return None

        logger.info(f"获取预约记录成功: reservation_id={reservation_id}")
        return data

    def get_all(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """获取所有预约数据"""
        all_reservations = ots_get_range(
            self.table_name,
            start_pk=[('reservation_id', INF_MIN)],
            end_pk=[('reservation_id', INF_MAX)]
        )

        logger.info(f"查询到预约总数: {len(all_reservations)}")
        return all_reservations

    def create(self, entity_data: Dict[str, Any]) -> Optional[str]:
        """创建新预约记录"""
        reservation_id = entity_data.get('reservation_id')
        if not reservation_id:
            logger.error("创建预约记录失败: 缺少reservation_id")
            return None

        primary_key = [('reservation_id', reservation_id)]
        attribute_columns = [
            ('book_id', entity_data['book_id']),
            ('user_id', entity_data['user_id']),
            ('reserve_date', entity_data['reserve_date']),
            ('time_slot', entity_data['time_slot']),
            ('days', entity_data.get('days', 30)),
            ('expected_return_date', entity_data['expected_return_date']),
            ('status', entity_data.get('status', 'reserved')),
            ('created_at', entity_data['created_at']),
            ('updated_at', entity_data['updated_at'])
        ]

        success, err = ots_put_row(
            self.table_name,
            primary_key,
            attribute_columns,
            expect_exist=RowExistenceExpectation.IGNORE
        )

        if not success:
            logger.error(f"创建预约记录失败: reservation_id={reservation_id}, err={err}")
            return None

        logger.info(
            f"创建预约记录成功: reservation_id={reservation_id}, "
            f"user_id={entity_data['user_id']}, book_id={entity_data['book_id']}"
        )
        return reservation_id

    def update(self, reservation_id: str, update_data: Dict[str, Any]) -> bool:
        """更新预约记录"""
        if not reservation_id:
            logger.error("更新预约记录失败: 缺少reservation_id")
            return False

        primary_key = [('reservation_id', reservation_id)]
        update_columns = [(key, value) for key, value in update_data.items()]

        success, err = ots_put_row(
            self.table_name,
            primary_key,
            update_columns,
            expect_exist=RowExistenceExpectation.IGNORE
        )

        if not success:
            logger.error(f"更新预约记录失败: reservation_id={reservation_id}, err={err}")
            return False

        logger.info(f"更新预约记录成功: reservation_id={reservation_id}")
        return True

    def delete(self, reservation_id: str) -> bool:
        """删除预约记录"""
        success, err = ots_delete_row(
            self.table_name,
            primary_key=[('reservation_id', reservation_id)]
        )

        if not success:
            logger.error(f"删除预约记录失败: reservation_id={reservation_id}, err={err}")
            return False

        logger.info(f"删除预约记录成功: reservation_id={reservation_id}")
        return True

    def count(self, filters: Dict[str, Any] = None) -> int:
        """统计预约记录数量"""
        all_reservations = self.get_all(filters)
        return len(all_reservations)

    def get_by_user_id(self, user_id: str) -> List[Dict[str, Any]]:
        """根据user_id获取用户所有预约记录"""
        condition = SingleColumnCondition('user_id', user_id, ComparatorType.EQUAL)
        reservation_list = ots_get_range(
            self.table_name,
            start_pk=[('reservation_id', INF_MIN)],
            end_pk=[('reservation_id', INF_MAX)],
            column_filter=condition
        )

        return reservation_list

    def get_by_book_id(self, book_id: str) -> List[Dict[str, Any]]:
        """根据book_id获取图书的所有预约记录"""
        condition = SingleColumnCondition('book_id', book_id, ComparatorType.EQUAL)
        reservation_list = ots_get_range(
            self.table_name,
            start_pk=[('reservation_id', INF_MIN)],
            end_pk=[('reservation_id', INF_MAX)],
            column_filter=condition
        )

        return reservation_list

    def get_active_by_user_book(self, user_id: str, book_id: str) -> Optional[Dict[str, Any]]:
        """获取用户对某本图书的活跃预约记录"""
        condition = CompositeColumnCondition(LogicalOperator.AND)
        condition.add_sub_condition(SingleColumnCondition('user_id', user_id, ComparatorType.EQUAL))
        condition.add_sub_condition(SingleColumnCondition('book_id', book_id, ComparatorType.EQUAL))
        condition.add_sub_condition(SingleColumnCondition('status', 'reserved', ComparatorType.EQUAL))

        reservation_list = ots_get_range(
            self.table_name,
            start_pk=[('reservation_id', INF_MIN)],
            end_pk=[('reservation_id', INF_MAX)],
            column_filter=condition,
            limit=1
        )

        if not reservation_list:
            return None

        return reservation_list[0]