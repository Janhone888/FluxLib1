import uuid
import time
from tablestore import (
    SingleColumnCondition, ComparatorType, CompositeColumnCondition,
    LogicalOperator, INF_MIN, INF_MAX, RowExistenceExpectation
)
from config import logger, FAVORITES_TABLE
from utils.database import ots_put_row, ots_get_row, ots_get_range, ots_delete_row


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
        """检查用户是否收藏该图书（修复：补充查询日志）"""
        # 1. 补充日志：打印查询的user_id和book_id，确认与创建时一致
        logger.info(f"【收藏检查】开始检查: user_id={user_id}, book_id={book_id}，表={FAVORITES_TABLE}")

        # 2. 构建过滤条件（保持原有逻辑，补充日志打印条件细节）
        condition = CompositeColumnCondition(LogicalOperator.AND)
        user_condition = SingleColumnCondition('user_id', user_id, ComparatorType.EQUAL)
        book_condition = SingleColumnCondition('book_id', book_id, ComparatorType.EQUAL)
        condition.add_sub_condition(user_condition)
        condition.add_sub_condition(book_condition)
        logger.info(f"【收藏检查】过滤条件: user_id匹配={user_id}, book_id匹配={book_id}")

        # 3. 范围查询（显式指定返回字段，确认存储的user_id和book_id）
        favorite_list = ots_get_range(
            FAVORITES_TABLE,
            start_pk=[('favorite_id', INF_MIN)],
            end_pk=[('favorite_id', INF_MAX)],
            column_filter=condition,
            limit=1,
            # 关键：显式返回user_id和book_id，确认OTS中实际存储值
            column_to_get=['favorite_id', 'user_id', 'book_id']
        )

        # 4. 补充日志：打印查询结果，暴露OTS返回的原始数据
        logger.info(f"【收藏检查】查询结果: 找到{len(favorite_list)}条记录")
        if favorite_list:
            # 打印原始记录，确认存储的user_id是否与查询条件一致（如是否有空格/特殊字符）
            logger.info(f"【收藏检查】匹配的原始记录: {favorite_list[0]}")
        else:
            # 若无结果，打印OTS表中该user_id的所有记录（帮助定位是否字段存储错误）
            all_user_favorites = ots_get_range(
                FAVORITES_TABLE,
                start_pk=[('favorite_id', INF_MIN)],
                end_pk=[('favorite_id', INF_MAX)],
                column_to_get=['favorite_id', 'user_id', 'book_id']
            )
            logger.info(f"【收藏检查】OTS中所有收藏记录: {all_user_favorites}")

        return len(favorite_list) > 0

    @classmethod
    def get_by_user_id(cls, user_id):
        """根据用户ID获取所有收藏（修复：补充查询日志）"""
        # 1. 补充日志：打印查询的user_id，确认与创建时一致
        logger.info(f"【收藏查询】开始查询: user_id={user_id}，表={FAVORITES_TABLE}")

        # 2. 构建过滤条件（补充日志）
        condition = SingleColumnCondition('user_id', user_id, ComparatorType.EQUAL)
        logger.info(f"【收藏查询】过滤条件: user_id匹配={user_id}（字符串精确匹配）")

        # 3. 范围查询（显式指定返回字段，确认存储的字段值）
        favorite_list = ots_get_range(
            FAVORITES_TABLE,
            start_pk=[('favorite_id', INF_MIN)],
            end_pk=[('favorite_id', INF_MAX)],
            column_filter=condition,
            # 关键：显式返回user_id和book_id，验证存储值
            column_to_get=['favorite_id', 'user_id', 'book_id', 'created_at']
        )

        # 4. 补充日志：打印查询结果和原始记录
        logger.info(f"【收藏查询】查询结果: 找到{len(favorite_list)}条记录")
        if favorite_list:
            logger.info(f"【收藏查询】原始记录示例: {favorite_list[0]}")
        else:
            # 无结果时打印所有记录，定位是否字段存储问题
            all_favorites = ots_get_range(
                FAVORITES_TABLE,
                start_pk=[('favorite_id', INF_MIN)],
                end_pk=[('favorite_id', INF_MAX)],
                column_to_get=['favorite_id', 'user_id', 'book_id']
            )
            logger.info(f"【收藏查询】OTS中所有收藏记录: {all_favorites}")

        return [cls(record) for record in favorite_list]