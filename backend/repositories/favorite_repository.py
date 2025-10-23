import time
from typing import List, Dict, Any, Optional
from tablestore import (
    SingleColumnCondition, ComparatorType, CompositeColumnCondition,
    LogicalOperator, INF_MIN, INF_MAX, RowExistenceExpectation
)
from config import logger, FAVORITES_TABLE
from utils.database import ots_put_row, ots_get_row, ots_get_range, ots_delete_row
from repositories.base_repository import BaseRepository


class FavoriteRepository(BaseRepository):
    """收藏数据仓储层，负责所有收藏数据的OTS访问操作"""

    def __init__(self):
        self.table_name = FAVORITES_TABLE

    def get_by_id(self, favorite_id: str) -> Optional[Dict[str, Any]]:
        """根据favorite_id获取收藏数据"""
        logger.info(f"查询Favorites表: favorite_id={favorite_id}")

        data = ots_get_row(self.table_name, primary_key=[('favorite_id', favorite_id)])
        if not data:
            logger.info(f"收藏记录不存在: favorite_id={favorite_id}")
            return None

        logger.info(f"获取收藏记录成功: favorite_id={favorite_id}")
        return data

    def get_all(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """获取所有收藏数据"""
        all_favorites = ots_get_range(
            self.table_name,
            start_pk=[('favorite_id', INF_MIN)],
            end_pk=[('favorite_id', INF_MAX)]
        )

        logger.info(f"查询到收藏总数: {len(all_favorites)}")
        return all_favorites

    def create(self, entity_data: Dict[str, Any]) -> Optional[str]:
        """创建新收藏"""
        favorite_id = entity_data.get('favorite_id')
        if not favorite_id:
            logger.error("创建收藏失败: 缺少favorite_id")
            return None

        primary_key = [('favorite_id', favorite_id)]
        attribute_columns = [
            ('user_id', entity_data['user_id']),
            ('book_id', entity_data['book_id']),
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
            logger.error(f"创建收藏失败: favorite_id={favorite_id}, err={err}")
            return None

        logger.info(
            f"创建收藏成功: favorite_id={favorite_id}, user_id={entity_data['user_id']}, book_id={entity_data['book_id']}")
        return favorite_id

    def update(self, favorite_id: str, update_data: Dict[str, Any]) -> bool:
        """更新收藏数据"""
        if not favorite_id:
            logger.error("更新收藏失败: 缺少favorite_id")
            return False

        primary_key = [('favorite_id', favorite_id)]
        update_columns = [(key, value) for key, value in update_data.items()]

        success, err = ots_put_row(
            self.table_name,
            primary_key,
            update_columns,
            expect_exist=RowExistenceExpectation.IGNORE
        )

        if not success:
            logger.error(f"更新收藏失败: favorite_id={favorite_id}, err={err}")
            return False

        logger.info(f"更新收藏成功: favorite_id={favorite_id}")
        return True

    def delete(self, favorite_id: str) -> bool:
        """删除收藏"""
        success, err = ots_delete_row(
            self.table_name,
            primary_key=[('favorite_id', favorite_id)]
        )

        if not success:
            logger.error(f"删除收藏失败: favorite_id={favorite_id}, err={err}")
            return False

        logger.info(f"删除收藏成功: favorite_id={favorite_id}")
        return True

    def count(self, filters: Dict[str, Any] = None) -> int:
        """统计收藏数量"""
        all_favorites = self.get_all(filters)
        return len(all_favorites)

    def exists_by_user_book(self, user_id: str, book_id: str) -> bool:
        """检查用户是否收藏该图书"""
        logger.info(f"【收藏检查】开始检查: user_id={user_id}, book_id={book_id}，表={self.table_name}")

        condition = CompositeColumnCondition(LogicalOperator.AND)
        user_condition = SingleColumnCondition('user_id', user_id, ComparatorType.EQUAL)
        book_condition = SingleColumnCondition('book_id', book_id, ComparatorType.EQUAL)
        condition.add_sub_condition(user_condition)
        condition.add_sub_condition(book_condition)

        logger.info(f"【收藏检查】过滤条件: user_id匹配={user_id}, book_id匹配={book_id}")

        favorite_list = ots_get_range(
            self.table_name,
            start_pk=[('favorite_id', INF_MIN)],
            end_pk=[('favorite_id', INF_MAX)],
            column_filter=condition,
            limit=1,
            column_to_get=['favorite_id', 'user_id', 'book_id']
        )

        logger.info(f"【收藏检查】查询结果: 找到{len(favorite_list)}条记录")

        if favorite_list:
            logger.info(f"【收藏检查】匹配的原始记录: {favorite_list[0]}")
        else:
            # 无结果时打印所有记录，定位是否字段存储问题
            all_favorites = ots_get_range(
                self.table_name,
                start_pk=[('favorite_id', INF_MIN)],
                end_pk=[('favorite_id', INF_MAX)],
                column_to_get=['favorite_id', 'user_id', 'book_id']
            )
            logger.info(f"【收藏检查】OTS中所有收藏记录: {all_favorites}")

        return len(favorite_list) > 0

    def get_by_user_id(self, user_id: str) -> List[Dict[str, Any]]:
        """根据user_id获取用户所有收藏"""
        logger.info(f"【收藏查询】开始查询: user_id={user_id}，表={self.table_name}")

        condition = SingleColumnCondition('user_id', user_id, ComparatorType.EQUAL)
        logger.info(f"【收藏查询】过滤条件: user_id匹配={user_id}（字符串精确匹配）")

        favorite_list = ots_get_range(
            self.table_name,
            start_pk=[('favorite_id', INF_MIN)],
            end_pk=[('favorite_id', INF_MAX)],
            column_filter=condition,
            column_to_get=['favorite_id', 'user_id', 'book_id', 'created_at']
        )

        logger.info(f"【收藏查询】查询结果: 找到{len(favorite_list)}条记录")

        if favorite_list:
            logger.info(f"【收藏查询】原始记录示例: {favorite_list[0]}")
        else:
            # 无结果时打印所有记录，定位是否字段存储问题
            all_favorites = ots_get_range(
                self.table_name,
                start_pk=[('favorite_id', INF_MIN)],
                end_pk=[('favorite_id', INF_MAX)],
                column_to_get=['favorite_id', 'user_id', 'book_id']
            )
            logger.info(f"【收藏查询】OTS中所有收藏记录: {all_favorites}")

        return favorite_list

    def get_by_user_book(self, user_id: str, book_id: str) -> Optional[Dict[str, Any]]:
        """根据用户ID和图书ID获取收藏记录"""
        condition = CompositeColumnCondition(LogicalOperator.AND)
        condition.add_sub_condition(SingleColumnCondition('user_id', user_id, ComparatorType.EQUAL))
        condition.add_sub_condition(SingleColumnCondition('book_id', book_id, ComparatorType.EQUAL))

        favorite_list = ots_get_range(
            self.table_name,
            start_pk=[('favorite_id', INF_MIN)],
            end_pk=[('favorite_id', INF_MAX)],
            column_filter=condition,
            limit=1
        )

        if not favorite_list:
            return None

        return favorite_list[0]

    def delete_by_user_book(self, user_id: str, book_id: str) -> bool:
        """根据用户ID和图书ID删除收藏"""
        # 1. 查找用户的该图书收藏记录
        favorite_data = self.get_by_user_book(user_id, book_id)
        if not favorite_data:
            logger.warning(f"删除收藏失败: 未找到记录（user_id={user_id}, book_id={book_id}）")
            return False

        # 2. 删除找到的收藏记录
        favorite_id = favorite_data['favorite_id']
        success = self.delete(favorite_id)

        if not success:
            logger.error(f"删除收藏失败: favorite_id={favorite_id}")
            return False

        logger.info(f"删除收藏成功: favorite_id={favorite_id}, user_id={user_id}, book_id={book_id}")
        return True