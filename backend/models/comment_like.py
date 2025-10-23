import time
from typing import Optional, Tuple
from config import logger
from repositories.comment_like_repository import CommentLikeRepository


class CommentLike:
    """评论点赞模型（使用仓储层进行数据访问）"""

    def __init__(self, data: dict):
        self.comment_id = data.get('comment_id')
        self.user_id = data.get('user_id')
        self.created_at = data.get('created_at', int(time.time()))

        # 初始化仓储
        self._repository = CommentLikeRepository()

    @classmethod
    def create(cls, comment_id: str, user_id: str) -> Tuple[bool, Optional[str]]:
        """创建点赞记录"""
        repository = CommentLikeRepository()
        result = repository.create({
            'comment_id': comment_id,
            'user_id': user_id
        })

        if not result:
            return False, "创建点赞记录失败"

        return True, None

    @classmethod
    def delete(cls, comment_id: str, user_id: str) -> Tuple[bool, Optional[str]]:
        """删除点赞记录（取消点赞）"""
        repository = CommentLikeRepository()
        success = repository.delete(comment_id, user_id)

        if not success:
            return False, "取消点赞失败"

        return True, None

    @classmethod
    def exists(cls, comment_id: str, user_id: str) -> bool:
        """检查用户是否已给评论点赞"""
        repository = CommentLikeRepository()
        return repository.exists(comment_id, user_id)