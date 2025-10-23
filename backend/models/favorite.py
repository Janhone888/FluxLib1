import uuid
import time
from typing import List, Optional, Dict, Any
from config import logger
from repositories.favorite_repository import FavoriteRepository


class Favorite:
    """收藏模型（使用仓储层进行数据访问）"""

    def __init__(self, data: Dict[str, Any]):
        """初始化收藏对象"""
        self.favorite_id = data.get('favorite_id')
        self.user_id = data.get('user_id', '')
        self.book_id = data.get('book_id', '')
        self.created_at = data.get('created_at', int(time.time()))
        self.updated_at = data.get('updated_at', int(time.time()))

        # 初始化仓储
        self._repository = FavoriteRepository()

    @classmethod
    def create(cls, user_id: str, book_id: str) -> bool:
        """创建收藏"""
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

        # 3. 通过仓储层插入数据
        repository = FavoriteRepository()
        result = repository.create(favorite_data)

        if not result:
            logger.error(f"创建收藏失败: user_id={user_id}, book_id={book_id}")
            return False

        logger.info(f"创建收藏成功: favorite_id={favorite_id}, user_id={user_id}, book_id={book_id}")
        return True

    @classmethod
    def delete_by_user_book(cls, user_id: str, book_id: str) -> bool:
        """根据用户ID和图书ID删除收藏"""
        repository = FavoriteRepository()
        success = repository.delete_by_user_book(user_id, book_id)

        if not success:
            logger.error(f"删除收藏失败: user_id={user_id}, book_id={book_id}")
            return False

        return True

    @classmethod
    def exists(cls, user_id: str, book_id: str) -> bool:
        """检查用户是否收藏该图书"""
        repository = FavoriteRepository()
        return repository.exists_by_user_book(user_id, book_id)

    @classmethod
    def get_by_user_id(cls, user_id: str) -> List['Favorite']:
        """根据用户ID获取所有收藏"""
        repository = FavoriteRepository()
        data_list = repository.get_by_user_id(user_id)

        return [cls(data) for data in data_list]