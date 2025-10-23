import time
from typing import List, Dict, Any, Optional
from tablestore import RowExistenceExpectation
from config import logger, COMMENT_LIKES_TABLE
from utils.database import ots_put_row, ots_get_row, ots_delete_row
from repositories.base_repository import BaseRepository


class CommentLikeRepository(BaseRepository):
    """评论点赞仓储层，负责所有评论点赞数据的OTS访问操作"""

    def __init__(self):
        self.table_name = COMMENT_LIKES_TABLE

    def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """复合主键查询需要特殊处理，这里不适用"""
        return None

    def get_all(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """获取所有点赞记录"""
        # 由于复合主键，这个方法需要特殊实现
        from utils.database import ots_get_range
        from tablestore import INF_MIN, INF_MAX

        all_likes = ots_get_range(
            self.table_name,
            start_pk=[('comment_id', INF_MIN), ('user_id', INF_MIN)],
            end_pk=[('comment_id', INF_MAX), ('user_id', INF_MAX)]
        )

        return all_likes

    def create(self, entity_data: Dict[str, Any]) -> Optional[str]:
        """创建点赞记录"""
        comment_id = entity_data.get('comment_id')
        user_id = entity_data.get('user_id')

        if not comment_id or not user_id:
            logger.error("创建点赞失败：缺少comment_id或user_id")
            return None

        # 先检查是否已点赞
        if self.exists(comment_id, user_id):
            logger.warning(f"已点赞：comment_id={comment_id}, user_id={user_id}")
            return None

        current_time = int(time.time())
        primary_key = [('comment_id', comment_id), ('user_id', user_id)]
        attribute_columns = [('created_at', current_time)]

        success, err = ots_put_row(
            self.table_name,
            primary_key,
            attribute_columns,
            expect_exist=RowExistenceExpectation.EXPECT_NOT_EXIST
        )

        if not success:
            logger.error(f"创建点赞记录失败：err={err}")
            return None

        logger.info(f"点赞成功：comment_id={comment_id}, user_id={user_id}")
        return f"{comment_id}_{user_id}"

    def update(self, id: str, update_data: Dict[str, Any]) -> bool:
        """点赞记录不支持更新"""
        return False

    def delete(self, comment_id: str, user_id: str) -> bool:
        """删除点赞记录（复合主键：comment_id+user_id，适配基类*args签名）"""
        if not comment_id or not user_id:
            logger.error("取消点赞失败：缺少comment_id或user_id")
            return False

        # 先检查是否已点赞
        if not self.exists(comment_id, user_id):
            logger.warning(f"未点赞：comment_id={comment_id}, user_id={user_id}")
            return False

        primary_key = [('comment_id', comment_id), ('user_id', user_id)]
        success, err = ots_delete_row(self.table_name, primary_key=primary_key)

        if not success:
            logger.error(f"取消点赞失败：err={err}")
            return False

        logger.info(f"取消点赞成功：comment_id={comment_id}, user_id={user_id}")
        return True

    def count(self, filters: Dict[str, Any] = None) -> int:
        """统计点赞数量"""
        all_likes = self.get_all(filters)
        return len(all_likes)

    def exists(self, comment_id: str, user_id: str) -> bool:
        """检查用户是否已给评论点赞"""
        primary_key = [('comment_id', comment_id), ('user_id', user_id)]
        data = ots_get_row(self.table_name, primary_key=primary_key)
        return bool(data)

    def get_by_comment_id(self, comment_id: str) -> List[Dict[str, Any]]:
        """根据comment_id获取所有点赞记录"""
        from utils.database import ots_get_range
        from tablestore import SingleColumnCondition, ComparatorType, INF_MIN, INF_MAX

        condition = SingleColumnCondition('comment_id', comment_id, ComparatorType.EQUAL)
        like_list = ots_get_range(
            self.table_name,
            start_pk=[('comment_id', comment_id), ('user_id', INF_MIN)],
            end_pk=[('comment_id', comment_id), ('user_id', INF_MAX)],
            column_filter=condition
        )

        return like_list

    def get_likes_count_by_comment(self, comment_id: str) -> int:
        """获取评论的点赞数"""
        likes = self.get_by_comment_id(comment_id)
        return len(likes)