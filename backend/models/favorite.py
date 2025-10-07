import uuid
import time
from tablestore import (
    SingleColumnCondition, ComparatorType, CompositeColumnCondition,
    LogicalOperator, INF_MIN, INF_MAX
)
from config import logger, FAVORITES_TABLE
from utils.database import ots_put_row, ots_get_row, ots_get_range


class Favorite:
    """收藏模型（对应Favorites表）"""
    def __init__(self, data):
        """初始化收藏对象（字段与原代码一致）"""
        self.favorite_id = data.get('favorite_id')  # 主键
        self.user_id = data.get('user_id', '')  # 用户ID
        self.book_id = data.get('book_id', '')  # 图书ID
        self.created_at = data.get('created_at', int(time.time()))  # 创建时间
        self.updated_at = data.get('updated_at', int(time.time()))  # 更新时间


    @classmethod
    def create(cls, user_id, book_id):
        """创建收藏（对应原代码add_favorite逻辑）"""
        # 1. 生成唯一favorite_id
        favorite_id = str(uuid.uuid4())
        current_time = int(time.time())

        # 2. 组装收藏数据
        favorite_data = {
            'favorite_id': favorite_id,
            'user_id': user_id,
            'book_id': book_id,
            'created_at': current_time,
            'updated_at': current_time
        }

        # 3. 插入OTS（Favorites表）
        primary_key = [('favorite_id', favorite_id)]
        attribute_columns = [
            ('user_id', favorite_data['user_id']),
            ('book_id', favorite_data['book_id']),
            ('created_at', favorite_data['created_at']),
            ('updated_at', favorite_data['updated_at'])
        ]
        success, err = ots_put_row(
            FAVORITES_TABLE,
            primary_key,
            attribute_columns,
            expect_exist=RowExistenceExpectation.IGNORE
        )
        if not success:
            logger.error(f"创建收藏失败: user_id={user_id}, book_id={book_id}, err={err}")
            return False
        logger.info(f"创建收藏成功: favorite_id={favorite_id}, user_id={user_id}, book_id={book_id}")
        return True


    @classmethod
    def delete_by_user_book(cls, user_id, book_id):
        """根据用户ID和图书ID删除收藏（对应原代码remove_favorite逻辑）"""
        # 1. 查找用户的该图书收藏记录
        condition = CompositeColumnCondition(LogicalOperator.AND)
        condition.add_sub_condition(SingleColumnCondition('user_id', user_id, ComparatorType.EQUAL))
        condition.add_sub_condition(SingleColumnCondition('book_id', book_id, ComparatorType.EQUAL))

        # 2. 范围查询匹配的收藏记录
        favorite_list = ots_get_range(
            FAVORITES_TABLE,
            start_pk=[('favorite_id', INF_MIN)],
            end_pk=[('favorite_id', INF_MAX)],
            column_filter=condition,
            limit=1
        )
        if not favorite_list:
            logger.warning(f"删除收藏失败: 未找到记录（user_id={user_id}, book_id={book_id}）")
            return False

        # 3. 删除找到的收藏记录
        favorite_id = favorite_list[0]['favorite_id']
        success, err = ots_delete_row(
            FAVORITES_TABLE,
            primary_key=[('favorite_id', favorite_id)]
        )
        if not success:
            logger.error(f"删除收藏失败: favorite_id={favorite_id}, err={err}")
            return False
        logger.info(f"删除收藏成功: favorite_id={favorite_id}, user_id={user_id}, book_id={book_id}")
        return True


    @classmethod
    def exists(cls, user_id, book_id):
        """检查用户是否收藏该图书（对应原代码check_favorite逻辑）"""
        condition = CompositeColumnCondition(LogicalOperator.AND)
        condition.add_sub_condition(SingleColumnCondition('user_id', user_id, ComparatorType.EQUAL))
        condition.add_sub_condition(SingleColumnCondition('book_id', book_id, ComparatorType.EQUAL))

        favorite_list = ots_get_range(
            FAVORITES_TABLE,
            start_pk=[('favorite_id', INF_MIN)],
            end_pk=[('favorite_id', INF_MAX)],
            column_filter=condition,
            limit=1
        )
        return len(favorite_list) > 0


    @classmethod
    def get_by_user_id(cls, user_id):
        """根据用户ID获取所有收藏（对应原代码get_user_favorites逻辑）"""
        condition = SingleColumnCondition('user_id', user_id, ComparatorType.EQUAL)
        favorite_list = ots_get_range(
            FAVORITES_TABLE,
            start_pk=[('favorite_id', INF_MIN)],
            end_pk=[('favorite_id', INF_MAX)],
            column_filter=condition
        )
        return [cls(record) for record in favorite_list]