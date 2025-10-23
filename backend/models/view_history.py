import uuid
import time
from typing import List, Optional, Dict, Any
from config import logger
from repositories.view_history_repository import ViewHistoryRepository


class ViewHistory:
    """浏览历史模型（使用仓储层进行数据访问）"""

    def __init__(self, data: Dict[str, Any]):
        """初始化浏览历史对象"""
        self.history_id = data.get('history_id')
        self.user_id = data.get('user_id', '')
        self.book_id = data.get('book_id', '')
        self.view_time = data.get('view_time', int(time.time()))
        self.created_at = data.get('created_at', int(time.time()))
        self.updated_at = data.get('updated_at', int(time.time()))

        # 初始化仓储
        self._repository = ViewHistoryRepository()

    @classmethod
    def create(cls, user_id: str, book_id: str) -> bool:
        """创建浏览历史"""
        repository = ViewHistoryRepository()
        success = repository.create_view_history(user_id, book_id)

        if not success:
            logger.error(f"创建浏览历史失败: user_id={user_id}, book_id={book_id}")
            return False

        logger.info(f"创建浏览历史成功: user_id={user_id}, book_id={book_id}")
        return True

    @classmethod
    def get_by_user_id(cls, user_id: str) -> List['ViewHistory']:
        """根据用户ID获取所有浏览历史"""
        repository = ViewHistoryRepository()
        data_list = repository.get_by_user_id(user_id)

        # 转换为ViewHistory对象并按浏览时间倒序排序
        history_objs = [cls(data) for data in data_list]
        history_objs.sort(key=lambda x: x.view_time, reverse=True)

        return history_objs
