import uuid
import time
from config import logger, COMMENTS_TABLE
from utils.database import ots_put_row, ots_get_row, ots_get_range
from tablestore import SingleColumnCondition, ComparatorType, INF_MIN, INF_MAX, RowExistenceExpectation
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
        # 新增：1. 校验book_id非空（关键修复）
        if not book_id:
            logger.error("创建评论失败: 缺少book_id（图书ID）")
            return False, "图书ID不能为空"

        # 原有逻辑：2. 校验用户存在性
        user = User.get_by_id(user_id)
        if not user:
            logger.error(f"创建评论失败: 用户不存在（user_id={user_id}）")
            return False, "用户不存在"

        # 原有逻辑：3. 校验内容非空
        if not content.strip():
            logger.error("创建评论失败: 评论内容为空")
            return False, "评论内容不能为空"

        # 原有逻辑：4. 生成comment_id+组装数据
        comment_id = str(uuid.uuid4())
        current_time = int(time.time())
        comment_data = {
            'comment_id': comment_id,
            'book_id': book_id,  # 此时已校验book_id非空
            'user_id': user_id,
            'user_display_name': user.display_name or user.email.split('@')[0],
            'user_avatar_url': user.avatar_url,
            'content': content.strip(),
            'parent_id': parent_id or '',
            'likes': 0,
            'created_at': current_time,
            'updated_at': current_time
        }

        # 新增：打印book_id具体值，确认存储的正确性
        logger.info(f"【创建评论】待存储的book_id: {book_id}（comment_id={comment_id}）")

        # 原有逻辑：5. 插入OTS
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
        # 优化日志：显示book_id的具体值，而非变量名
        logger.info(f"【写评论】表={COMMENTS_TABLE}, PK={primary_key}, "
                    f"属性包含: book_id={comment_data['book_id']}, user_id={comment_data['user_id']}")

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
        """获取图书的所有评论（含回复树结构）"""
        try:
            # 新增：打印查询用的book_id，确认与存储的一致
            logger.info(f"【查询评论】目标图书ID: {book_id}，开始查询Comments表")

            # 原有逻辑：1. 构建查询条件（已修复：column_to_get新增'comment_id'主键）
            condition = SingleColumnCondition('book_id', book_id, ComparatorType.EQUAL)
            comment_list = ots_get_range(
                COMMENTS_TABLE,
                start_pk=[('comment_id', INF_MIN)],
                end_pk=[('comment_id', INF_MAX)],
                column_filter=condition,
                column_to_get=[  # ✅ 核心修复：新增'comment_id'（主键字段），确保主键与属性列关联
                    'comment_id',
                    'book_id', 'user_id', 'user_display_name', 'user_avatar_url',
                    'content', 'parent_id', 'likes', 'created_at', 'updated_at'
                ]
            )

            # 优化日志：打印原始评论的book_id和content，确认字段是否存在
            logger.info(f"✅ 从OTS查询到的评论数量: {len(comment_list)} 条（book_id={book_id}）")
            for idx, raw_comment in enumerate(comment_list):
                raw_comment_id = raw_comment.get('comment_id', '未知ID')
                raw_book_id = raw_comment.get('book_id', '未知book_id')
                raw_content = raw_comment.get('content', '无内容')  # 新增：获取content字段
                logger.info(f"  评论{idx + 1}: comment_id={raw_comment_id}, "
                            f"book_id={raw_book_id}, content={raw_content[:20]}...")

            # 2. 转换为Comment对象
            comments = [cls(data) for data in comment_list]

            # -------------------------- 新增日志2：打印转换后的Comment对象 --------------------------
            logger.info(f"✅ 转换为Comment对象的数量: {len(comments)} 条")
            for idx, comment_obj in enumerate(comments):
                logger.info(
                    f"  Comment{idx + 1}: comment_id={comment_obj.comment_id}, parent_id={comment_obj.parent_id}, likes={comment_obj.likes}")

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
                    # -------------------------- 新增日志3：打印回复关联关系 --------------------------
                    logger.info(f"  🔗 回复关联: 父评论ID={comment.parent_id} → 子评论ID={comment.comment_id}")
                else:
                    # 父评论：添加到评论树
                    comment_tree.append(comment)
                    # -------------------------- 新增日志4：打印父评论 --------------------------
                    logger.info(f"  📌 父评论添加: comment_id={comment.comment_id}, likes={comment.likes}")

            # 4. 按点赞数排序（父评论降序）
            comment_tree.sort(key=lambda x: x.likes, reverse=True)
            logger.info(f"✅ 最终返回的评论树数量: 父评论{len(comment_tree)} 条，总评论（含回复）{len(comments)} 条")
            return comment_tree
        except Exception as e:
            logger.error(f"获取评论失败: book_id={book_id}, err={str(e)}", exc_info=True)  # 新增exc_info=True，打印完整错误栈
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

        # 1. 增加点赞数 + 更新时间（原有逻辑不变）
        self.likes += 1
        self.updated_at = int(time.time())

        # 2. 重新加载用户信息（原有逻辑不变）
        user = User.get_by_id(self.user_id)
        if user:
            self.user_display_name = user.display_name or user.email.split('@')[0]
            self.user_avatar_url = user.avatar_url

        # -------------------------- 核心修复：补充 book_id 和 content 字段 --------------------------
        # 从当前 Comment 实例中获取原有值（点赞前已通过 __init__ 加载，非空）
        current_book_id = self.book_id
        current_content = self.content
        # 新增日志：验证保留的字段值
        logger.info(f"【点赞保留字段】book_id={current_book_id}, content={current_content[:20]}...")
        # ------------------------------------------------------------------------------------------

        # 3. 调用OTS更新（补充 book_id 和 content，避免字段丢失）
        primary_key = [('comment_id', self.comment_id)]
        update_columns = [
            ('likes', self.likes),
            ('updated_at', self.updated_at),
            ('user_display_name', self.user_display_name),  # 原有字段
            ('user_avatar_url', self.user_avatar_url),  # 原有字段
            # ✅ 新增：保留点赞前的 book_id 和 content，防止被清空
            ('book_id', current_book_id),
            ('content', current_content)
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