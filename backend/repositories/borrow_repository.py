import time
from typing import List, Dict, Any, Optional
from tablestore import (
    SingleColumnCondition, ComparatorType, CompositeColumnCondition,
    LogicalOperator, INF_MIN, INF_MAX, RowExistenceExpectation
)
from config import logger, BORROW_RECORDS_TABLE
from utils.database import ots_put_row, ots_get_row, ots_get_range, ots_delete_row
from repositories.base_repository import BaseRepository


class BorrowRepository(BaseRepository):
    """借阅记录仓储层，负责所有借阅数据的OTS访问操作"""

    def __init__(self):
        self.table_name = BORROW_RECORDS_TABLE

    def get_by_id(self, borrow_id: str) -> Optional[Dict[str, Any]]:
        """根据borrow_id获取借阅记录"""
        logger.info(f"查询BorrowRecords表: borrow_id={borrow_id}")

        data = ots_get_row(self.table_name, primary_key=[('borrow_id', borrow_id)])
        if not data:
            logger.info(f"借阅记录不存在: borrow_id={borrow_id}")
            return None

        logger.info(f"获取借阅记录成功: borrow_id={borrow_id}")
        return data

    def get_all(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """获取所有借阅记录"""
        all_borrows = ots_get_range(
            self.table_name,
            start_pk=[('borrow_id', INF_MIN)],
            end_pk=[('borrow_id', INF_MAX)]
        )

        logger.info(f"查询到借阅记录总数: {len(all_borrows)}")
        return all_borrows

    def create(self, entity_data: Dict[str, Any]) -> Optional[str]:
        """创建新借阅记录"""
        borrow_id = entity_data.get('borrow_id')
        if not borrow_id:
            logger.error("创建借阅记录失败: 缺少borrow_id")
            return None

        primary_key = [('borrow_id', borrow_id)]
        attribute_columns = [
            ('book_id', entity_data['book_id']),
            ('user_id', entity_data['user_id']),
            ('borrow_date', entity_data['borrow_date']),
            ('due_date', entity_data['due_date']),
            ('return_date', entity_data.get('return_date', 0)),
            ('status', entity_data['status']),
            ('is_early_return', entity_data.get('is_early_return', False)),
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
            logger.error(f"创建借阅记录失败: borrow_id={borrow_id}, err={err}")
            return None

        logger.info(
            f"创建借阅记录成功: borrow_id={borrow_id}, user_id={entity_data['user_id']}, book_id={entity_data['book_id']}")
        return borrow_id

    def update(self, borrow_id: str, update_data: Dict[str, Any]) -> bool:
        """更新借阅记录"""
        if not borrow_id:
            logger.error("更新借阅记录失败: 缺少borrow_id")
            return False

        primary_key = [('borrow_id', borrow_id)]
        update_columns = [(key, value) for key, value in update_data.items()]

        success, err = ots_put_row(
            self.table_name,
            primary_key,
            update_columns,
            expect_exist=RowExistenceExpectation.IGNORE
        )

        if not success:
            logger.error(f"更新借阅记录失败: borrow_id={borrow_id}, err={err}")
            return False

        logger.info(f"更新借阅记录成功: borrow_id={borrow_id}")
        return True

    def delete(self, borrow_id: str) -> bool:
        """删除借阅记录（单主键：borrow_id，适配基类*args签名）"""
        success, err = ots_delete_row(
            self.table_name,
            primary_key=[('borrow_id', borrow_id)]
        )

        if not success:
            logger.error(f"删除借阅记录失败: borrow_id={borrow_id}, err={err}")
            return False

        logger.info(f"删除借阅记录成功: borrow_id={borrow_id}")
        return True

    def count(self, filters: Dict[str, Any] = None) -> int:
        """统计借阅记录数量"""
        all_borrows = self.get_all(filters)
        return len(all_borrows)

    def get_by_user_book(self, user_id: str, book_id: str) -> Optional[Dict[str, Any]]:
        """获取用户的某本图书借阅记录"""
        condition = CompositeColumnCondition(LogicalOperator.AND)
        condition.add_sub_condition(SingleColumnCondition('user_id', user_id, ComparatorType.EQUAL))
        condition.add_sub_condition(SingleColumnCondition('book_id', book_id, ComparatorType.EQUAL))
        condition.add_sub_condition(SingleColumnCondition('status', 'borrowed', ComparatorType.EQUAL))

        borrow_list = ots_get_range(
            self.table_name,
            start_pk=[('borrow_id', INF_MIN)],
            end_pk=[('borrow_id', INF_MAX)],
            column_filter=condition,
            limit=1
        )

        if not borrow_list:
            return None

        return borrow_list[0]

    def get_by_user_id(self, user_id: str) -> List[Dict[str, Any]]:
        """获取用户所有借阅记录"""
        condition = SingleColumnCondition('user_id', user_id, ComparatorType.EQUAL)
        borrow_list = ots_get_range(
            self.table_name,
            start_pk=[('borrow_id', INF_MIN)],
            end_pk=[('borrow_id', INF_MAX)],
            column_filter=condition
        )

        return borrow_list

    def get_by_book_id(self, book_id: str) -> List[Dict[str, Any]]:
        """获取图书的所有借阅记录"""
        condition = SingleColumnCondition('book_id', book_id, ComparatorType.EQUAL)
        borrow_list = ots_get_range(
            self.table_name,
            start_pk=[('borrow_id', INF_MIN)],
            end_pk=[('borrow_id', INF_MAX)],
            column_filter=condition
        )

        return borrow_list

    def get_borrowed_records_by_book(self, book_id: str) -> List[Dict[str, Any]]:
        """获取图书的已借出记录"""
        condition = CompositeColumnCondition(LogicalOperator.AND)
        condition.add_sub_condition(SingleColumnCondition('book_id', book_id, ComparatorType.EQUAL))
        condition.add_sub_condition(SingleColumnCondition('status', 'borrowed', ComparatorType.EQUAL))

        borrow_list = ots_get_range(
            self.table_name,
            start_pk=[('borrow_id', INF_MIN)],
            end_pk=[('borrow_id', INF_MAX)],
            column_filter=condition
        )

        return borrow_list