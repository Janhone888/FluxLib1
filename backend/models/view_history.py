import uuid
import time
# 关键修复：补充导入 RowExistenceExpectation（从 tablestore 库）
from tablestore import (
    SingleColumnCondition, ComparatorType, INF_MIN, INF_MAX,
    RowExistenceExpectation  # 新增：导入缺失的类
)
from config import logger, VIEW_HISTORY_TABLE
from utils.database import ots_put_row, ots_get_row, ots_get_range


class ViewHistory:
    """浏览历史模型（对应ViewHistory表）"""
    def __init__(self, data):
        """初始化浏览历史对象（字段与原代码一致）"""
        self.history_id = data.get('history_id')  # 主键
        self.user_id = data.get('user_id', '')  # 用户ID
        self.book_id = data.get('book_id', '')  # 图书ID
        self.view_time = data.get('view_time', int(time.time()))  # 浏览时间
        self.created_at = data.get('created_at', int(time.time()))  # 创建时间
        self.updated_at = data.get('updated_at', int(time.time()))  # 更新时间

    @classmethod
    def create(cls, user_id, book_id):
        """创建浏览历史（对应原代码add_view_history逻辑）"""
        # 1. 生成唯一history_id
        history_id = str(uuid.uuid4())
        current_time = int(time.time())

        # 2. 组装浏览历史数据
        history_data = {
            'history_id': history_id,
            'user_id': user_id,
            'book_id': book_id,
            'view_time': current_time,
            'created_at': current_time,
            'updated_at': current_time
        }

        # 3. 插入OTS（ViewHistory表）- 此处使用了RowExistenceExpectation.IGNORE
        primary_key = [('history_id', history_id)]
        attribute_columns = [
            ('user_id', history_data['user_id']),
            ('book_id', history_data['book_id']),
            ('view_time', history_data['view_time']),
            ('created_at', history_data['created_at']),
            ('updated_at', history_data['updated_at'])
        ]
        success, err = ots_put_row(
            VIEW_HISTORY_TABLE,
            primary_key,
            attribute_columns,
            expect_exist=RowExistenceExpectation.IGNORE  # 现在该类已导入，无报错
        )
        if not success:
            logger.error(f"创建浏览历史失败: user_id={user_id}, book_id={book_id}, err={err}")
            return False
        logger.info(f"创建浏览历史成功: history_id={history_id}, user_id={user_id}, book_id={book_id}")
        return True

    @classmethod
    def get_by_user_id(cls, user_id):
        """根据用户ID获取所有浏览历史（对应原代码get_user_view_history逻辑）"""
        condition = SingleColumnCondition('user_id', user_id, ComparatorType.EQUAL)
        history_list = ots_get_range(
            VIEW_HISTORY_TABLE,
            start_pk=[('history_id', INF_MIN)],
            end_pk=[('history_id', INF_MAX)],
            column_filter=condition
        )
        # 转换为ViewHistory对象并按浏览时间倒序排序
        history_objs = [cls(record) for record in history_list]
        history_objs.sort(key=lambda x: x.view_time, reverse=True)
        return history_objs
