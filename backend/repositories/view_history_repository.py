import time
import uuid
from typing import List, Dict, Any, Optional
from tablestore import (
    SingleColumnCondition, ComparatorType, INF_MIN, INF_MAX, RowExistenceExpectation
)
from config import logger, VIEW_HISTORY_TABLE
from utils.database import ots_put_row, ots_get_row, ots_get_range, ots_delete_row
from repositories.base_repository import BaseRepository


class ViewHistoryRepository(BaseRepository):
    """浏览历史数据仓储层，负责所有浏览历史数据的OTS访问操作"""

    def __init__(self):
        self.table_name = VIEW_HISTORY_TABLE

    def get_by_id(self, history_id: str) -> Optional[Dict[str, Any]]:
        """根据history_id获取浏览历史数据"""
        logger.info(f"查询ViewHistory表: history_id={history_id}")

        data = ots_get_row(self.table_name, primary_key=[('history_id', history_id)])
        if not data:
            logger.info(f"浏览历史不存在: history_id={history_id}")
            return None

        logger.info(f"获取浏览历史成功: history_id={history_id}")
        return data

    def get_all(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """获取所有浏览历史数据"""
        all_history = ots_get_range(
            self.table_name,
            start_pk=[('history_id', INF_MIN)],
            end_pk=[('history_id', INF_MAX)]
        )

        logger.info(f"查询到浏览历史总数: {len(all_history)}")
        return all_history

    def create(self, entity_data: Dict[str, Any]) -> Optional[str]:
        """创建新浏览历史"""
        history_id = entity_data.get('history_id')
        if not history_id:
            logger.error("创建浏览历史失败: 缺少history_id")
            return None

        primary_key = [('history_id', history_id)]
        attribute_columns = [
            ('user_id', entity_data['user_id']),
            ('book_id', entity_data['book_id']),
            ('view_time', entity_data['view_time']),
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
            logger.error(f"创建浏览历史失败: history_id={history_id}, err={err}")
            return None

        logger.info(
            f"创建浏览历史成功: history_id={history_id}, user_id={entity_data['user_id']}, book_id={entity_data['book_id']}")
        return history_id

    def update(self, history_id: str, update_data: Dict[str, Any]) -> bool:
        """更新浏览历史数据"""
        if not history_id:
            logger.error("更新浏览历史失败: 缺少history_id")
            return False

        primary_key = [('history_id', history_id)]
        update_columns = [(key, value) for key, value in update_data.items()]

        success, err = ots_put_row(
            self.table_name,
            primary_key,
            update_columns,
            expect_exist=RowExistenceExpectation.IGNORE
        )

        if not success:
            logger.error(f"更新浏览历史失败: history_id={history_id}, err={err}")
            return False

        logger.info(f"更新浏览历史成功: history_id={history_id}")
        return True

    def delete(self, history_id: str) -> bool:
        """删除浏览历史"""
        success, err = ots_delete_row(
            self.table_name,
            primary_key=[('history_id', history_id)]
        )

        if not success:
            logger.error(f"删除浏览历史失败: history_id={history_id}, err={err}")
            return False

        logger.info(f"删除浏览历史成功: history_id={history_id}")
        return True

    def count(self, filters: Dict[str, Any] = None) -> int:
        """统计浏览历史数量"""
        all_history = self.get_all(filters)
        return len(all_history)

    def get_by_user_id(self, user_id: str) -> List[Dict[str, Any]]:
        """根据user_id获取用户所有浏览历史"""
        condition = SingleColumnCondition('user_id', user_id, ComparatorType.EQUAL)
        history_list = ots_get_range(
            self.table_name,
            start_pk=[('history_id', INF_MIN)],
            end_pk=[('history_id', INF_MAX)],
            column_filter=condition
        )

        return history_list

    def create_view_history(self, user_id: str, book_id: str) -> bool:
        """创建浏览历史记录（封装创建逻辑）"""
        # 生成唯一history_id
        history_id = str(uuid.uuid4())
        current_time = int(time.time())

        # 组装浏览历史数据
        history_data = {
            'history_id': history_id,
            'user_id': user_id,
            'book_id': book_id,
            'view_time': current_time,
            'created_at': current_time,
            'updated_at': current_time
        }

        # 创建记录
        result = self.create(history_data)
        return result is not None