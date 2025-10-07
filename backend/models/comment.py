import uuid
import time
from config import logger, COMMENTS_TABLE
from utils.database import ots_put_row, ots_get_row, ots_get_range
from tablestore import SingleColumnCondition, ComparatorType, INF_MIN, INF_MAX, RowExistenceExpectation  # 添加缺失的导入
from models.user import User

class Comment:
    """评论模型（对应Comments表）"""
    def __init__(self, data):
        """初始化评论对象（字段与原代码一致）"""
        self.comment_id = data.get('comment_id')  # 主键
        self.book_id = data.get('book_id', '')  # 图书ID
        self.user_id = data.get('user_id', '')  # 用户ID
        self.user_display_name = data.get('user_display_name', '未知用户')  # 用户显示名
        self.user_avatar_url = data.get('user_avatar_url', '')  # 用户头像
        self.content = data.get('content', '')  # 评论内容
        self.parent_id = data.get('parent_id', '')  # 父评论ID（回复时使用）
        self.likes = int(data.get('likes', 0))  # 点赞数
        self.created_at = data.get('created_at', int(time.time()))  # 创建时间
        self.updated_at = data.get('updated_at', int(time.time()))  # 更新时间

    @classmethod
    def create_comment(cls, book_id, user_id, content, parent_id=''):
        """创建评论（对应原代码create_comment逻辑）"""
        # 1. 校验用户存在性
        user = User.get_by_id(user_id)
        if not user:
            logger.error(f"创建评论失败: 用户不存在（user_id={user_id}）")
            return False, "用户不存在"

        # 2. 校验内容非空
        if not content.strip():
            logger.error("创建评论失败: 评论内容为空")
            return False, "评论内容不能为空"

        # 3. 生成comment_id
        comment_id = str(uuid.uuid4())
        current_time = int(time.time())

        # 4. 组装评论数据（与原代码一致）
        comment_data = {
            'comment_id': comment_id,
            'book_id': book_id,
            'user_id': user_id,
            'user_display_name': user.display_name or user.email.split('@')[0],
            'user_avatar_url': user.avatar_url,
            'content': content.strip(),
            'parent_id': parent_id or '',
            'likes': 0,
            'created_at': current_time,
            'updated_at': current_time
        }

        # 5. 插入OTS（Comments表）
        primary_key = [('comment_id', comment_id)]
        attribute_columns = [
            ('book_id', comment_data['book_id']),
            ('user_id', comment_data['user_id']),
            ('user_display_name', comment_data['user_display_name']),
            ('user_avatar_url', comment_data['user_avatar_url']),
            ('content', comment_data['content']),
            ('parent_id', comment_data['parent_id']),
            ('likes', comment_data['likes']),
            ('created_at', comment_data['created_at']),
            ('updated_at', comment_data['updated_at'])
        ]
        success, err = ots_put_row(
            COMMENTS_TABLE,
            primary_key,
            attribute_columns,
            expect_exist=RowExistenceExpectation.IGNORE
        )
        if not success:
            logger.error(f"创建评论失败: comment_id={comment_id}, err={err}")
            return False, str(err)

        logger.info(f"创建评论成功: comment_id={comment_id}, book_id={book_id}, user_id={user_id}")
        return True, comment_data

    @classmethod
    def get_by_book_id(cls, book_id):
        """获取图书的所有评论（含回复树结构，对应原代码get_book_comments逻辑）"""
        try:
            # 1. 查询该图书的所有评论
            condition = SingleColumnCondition('book_id', book_id, ComparatorType.EQUAL)
            comment_list = ots_get_range(
                COMMENTS_TABLE,
                start_pk=[('comment_id', INF_MIN)],  # 使用导入的 INF_MIN
                end_pk=[('comment_id', INF_MAX)],    # 使用导入的 INF_MAX
                column_filter=condition
            )

            # 2. 转换为Comment对象
            comments = [cls(data) for data in comment_list]

            # 3. 构建评论树（父评论+回复）
            comment_map = {}
            comment_tree = []

            # 3.1 先构建所有评论的映射
            for comment in comments:
                comment_map[comment.comment_id] = comment
                comment.replies = []  # 初始化回复列表

            # 3.2 分类父评论和回复
            for comment in comments:
                if comment.parent_id and comment.parent_id in comment_map:
                    # 回复评论：添加到父评论的replies
                    comment_map[comment.parent_id].replies.append(comment)
                else:
                    # 父评论：添加到评论树
                    comment_tree.append(comment)

            # 4. 按点赞数排序（父评论降序）
            comment_tree.sort(key=lambda x: x.likes, reverse=True)
            return comment_tree
        except Exception as e:
            logger.error(f"获取评论失败: book_id={book_id}, err={str(e)}")
            return []

    @classmethod
    def get_by_id(cls, comment_id):
        """通过comment_id获取评论"""
        data = ots_get_row(COMMENTS_TABLE, primary_key=[('comment_id', comment_id)])
        if not data:
            logger.info(f"评论不存在: comment_id={comment_id}")
            return None
        return cls(data)

    def like_comment(self):
        """点赞评论（对应原代码like_comment逻辑）"""
        if not self.comment_id:
            logger.error("点赞评论失败: 缺少comment_id主键")
            return False, "评论不存在"

        # 1. 增加点赞数
        self.likes += 1
        self.updated_at = int(time.time())

        # 2. 调用OTS更新
        primary_key = [('comment_id', self.comment_id)]
        update_columns = [
            ('likes', self.likes),
            ('updated_at', self.updated_at)
        ]
        success, err = ots_put_row(
            COMMENTS_TABLE,
            primary_key,
            update_columns,
            expect_exist=RowExistenceExpectation.IGNORE
        )
        if not success:
            logger.error(f"点赞评论失败: comment_id={self.comment_id}, err={err}")
            return False, str(err)

        logger.info(f"点赞评论成功: comment_id={self.comment_id}, 点赞数={self.likes}")
        return True, None