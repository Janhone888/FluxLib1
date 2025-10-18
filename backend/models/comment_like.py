import time
from tablestore import RowExistenceExpectation
from config import logger, COMMENT_LIKES_TABLE
from utils.database import ots_put_row, ots_get_row, ots_delete_row


class CommentLike:
    """评论点赞模型（对应CommentLikes表，复合主键comment_id+user_id）"""

    def __init__(self, data):
        self.comment_id = data.get('comment_id')  # 评论ID（主键1）
        self.user_id = data.get('user_id')  # 用户ID（主键2）
        self.created_at = data.get('created_at', int(time.time()))  # 点赞时间

    @classmethod
    def create(cls, comment_id, user_id):
        """创建点赞记录（确保用户未点赞过）"""
        if not comment_id or not user_id:
            logger.error("创建点赞失败：缺少comment_id或user_id")
            return False, "参数不完整"

        # 先检查是否已点赞（避免重复）
        if cls.exists(comment_id, user_id):
            logger.warning(f"已点赞：comment_id={comment_id}, user_id={user_id}")
            return False, "您已点赞过这条评论"

        current_time = int(time.time())
        primary_key = [('comment_id', comment_id), ('user_id', user_id)]  # 复合主键
        attribute_columns = [('created_at', current_time)]

        # 插入OTS（确保记录不存在才创建）
        success, err = ots_put_row(
            COMMENT_LIKES_TABLE,
            primary_key,
            attribute_columns,
            expect_exist=RowExistenceExpectation.EXPECT_NOT_EXIST
        )
        if not success:
            logger.error(f"创建点赞记录失败：err={err}")
            return False, str(err)

        logger.info(f"点赞成功：comment_id={comment_id}, user_id={user_id}")
        return True, None

    @classmethod
    def delete(cls, comment_id, user_id):
        """删除点赞记录（取消点赞）"""
        if not comment_id or not user_id:
            logger.error("取消点赞失败：缺少comment_id或user_id")
            return False, "参数不完整"

        # 先检查是否已点赞（避免无效删除）
        if not cls.exists(comment_id, user_id):
            logger.warning(f"未点赞：comment_id={comment_id}, user_id={user_id}")
            return False, "您未点赞这条评论"

        primary_key = [('comment_id', comment_id), ('user_id', user_id)]
        success, err = ots_delete_row(COMMENT_LIKES_TABLE, primary_key=primary_key)
        if not success:
            logger.error(f"取消点赞失败：err={err}")
            return False, str(err)

        logger.info(f"取消点赞成功：comment_id={comment_id}, user_id={user_id}")
        return True, None

    @classmethod
    def exists(cls, comment_id, user_id):
        """检查用户是否已给评论点赞"""
        primary_key = [('comment_id', comment_id), ('user_id', user_id)]
        data = ots_get_row(COMMENT_LIKES_TABLE, primary_key=primary_key)
        return bool(data)  # 有数据则返回True（已点赞）