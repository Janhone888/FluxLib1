import uuid
import time
from typing import List, Optional, Dict, Any
from config import logger
from repositories.comment_repository import CommentRepository
from repositories.comment_like_repository import CommentLikeRepository
from models.user import User


class Comment:
    """评论模型（使用仓储层进行数据访问）"""

    def __init__(self, data: Dict[str, Any]):
        """初始化评论对象"""
        self.comment_id = data.get('comment_id')
        self.book_id = data.get('book_id', '')
        self.user_id = data.get('user_id', '')
        self.user_display_name = data.get('user_display_name', '未知用户')
        self.user_avatar_url = data.get('user_avatar_url', '')
        self.content = data.get('content', '')
        self.parent_id = data.get('parent_id', '')
        self.likes = int(data.get('likes', 0))
        self.created_at = data.get('created_at', int(time.time()))
        self.updated_at = data.get('updated_at', int(time.time()))

        # 初始化仓储
        self._repository = CommentRepository()
        self._like_repository = CommentLikeRepository()

    @classmethod
    def create_comment(cls, book_id: str, user_id: str, content: str, parent_id: str = '') -> tuple:
        """创建评论"""
        # 1. 校验book_id非空
        if not book_id:
            logger.error("创建评论失败: 缺少book_id（图书ID）")
            return False, "图书ID不能为空"

        # 2. 校验用户存在性
        user = User.get_by_id(user_id)
        if not user:
            logger.error(f"创建评论失败: 用户不存在（user_id={user_id}）")
            return False, "用户不存在"

        # 3. 校验内容非空
        if not content.strip():
            logger.error("创建评论失败: 评论内容为空")
            return False, "评论内容不能为空"

        # 4. 生成comment_id+组装数据
        comment_id = str(uuid.uuid4())
        current_time = int(time.time())
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

        logger.info(f"【创建评论】待存储的book_id: {book_id}（comment_id={comment_id}）")

        # 5. 通过仓储层插入数据
        repository = CommentRepository()
        result = repository.create(comment_data)

        if not result:
            logger.error(f"创建评论失败: comment_id={comment_id}")
            return False, "创建评论失败"

        logger.info(f"创建评论成功: comment_id={comment_id}, book_id={book_id}, user_id={user_id}")
        return True, comment_data

    @classmethod
    def get_by_book_id(cls, book_id: str) -> List['Comment']:
        """获取图书的所有评论（含回复树结构）"""
        try:
            logger.info(f"【查询评论】目标图书ID: {book_id}，开始查询Comments表")

            # 通过仓储层获取数据
            repository = CommentRepository()
            comment_list_data = repository.get_by_book_id(book_id)

            logger.info(f"✅ 从OTS查询到的评论数量: {len(comment_list_data)} 条（book_id={book_id}）")

            # 转换为Comment对象
            comments = [cls(data) for data in comment_list_data]
            logger.info(f"✅ 转换为Comment对象的数量: {len(comments)} 条")

            # 构建评论树（父评论+回复）
            comment_map = {}
            comment_tree = []

            # 先构建所有评论的映射
            for comment in comments:
                comment_map[comment.comment_id] = comment
                comment.replies = []  # 初始化回复列表

            # 分类父评论和回复
            for comment in comments:
                if comment.parent_id and comment.parent_id in comment_map:
                    # 回复评论：添加到父评论的replies
                    comment_map[comment.parent_id].replies.append(comment)
                    logger.info(f"  🔗 回复关联: 父评论ID={comment.parent_id} → 子评论ID={comment.comment_id}")
                else:
                    # 父评论：添加到评论树
                    comment_tree.append(comment)
                    logger.info(f"  📌 父评论添加: comment_id={comment.comment_id}, likes={comment.likes}")

            # 按点赞数排序（父评论降序）
            comment_tree.sort(key=lambda x: x.likes, reverse=True)
            logger.info(f"✅ 最终返回的评论树数量: 父评论{len(comment_tree)} 条，总评论（含回复）{len(comments)} 条")

            return comment_tree

        except Exception as e:
            logger.error(f"获取评论失败: book_id={book_id}, err={str(e)}", exc_info=True)
            return []

    @classmethod
    def get_by_id(cls, comment_id: str) -> Optional['Comment']:
        """通过comment_id获取评论"""
        repository = CommentRepository()
        data = repository.get_by_id(comment_id)

        if not data:
            return None

        return cls(data)

    def like_comment(self, user_id: str) -> tuple:
        """点赞/取消点赞评论"""
        if not self.comment_id:
            logger.error("点赞失败：缺少comment_id")
            return False, "评论不存在"

        if not user_id:
            logger.error("点赞失败：缺少user_id")
            return False, "用户未登录"

        try:
            # 1. 检查用户是否已点赞
            has_liked = self._like_repository.exists(self.comment_id, user_id)

            if has_liked:
                # 2. 已点赞：取消点赞（删记录+点赞数-1）
                del_success = self._like_repository.delete(self.comment_id, user_id)
                if not del_success:
                    return False, "取消点赞失败"

                self.likes -= 1
                action = "取消点赞"
            else:
                # 3. 未点赞：点赞（增记录+点赞数+1）
                create_result = self._like_repository.create({
                    'comment_id': self.comment_id,
                    'user_id': user_id
                })
                if not create_result:
                    return False, "点赞失败"

                self.likes += 1
                action = "点赞"

            # 4. 更新OTS评论表（仅更新点赞数、时间，保留原作者信息）
            update_columns = {
                'likes': self.likes,
                'updated_at': int(time.time()),
                'user_display_name': self.user_display_name,
                'user_avatar_url': self.user_avatar_url,
                'book_id': self.book_id,
                'content': self.content
            }

            success = self._repository.update(self.comment_id, update_columns)

            if not success:
                # 回滚：恢复点赞记录（避免数据不一致）
                if has_liked:
                    self._like_repository.create({
                        'comment_id': self.comment_id,
                        'user_id': user_id
                    })
                    self.likes += 1
                else:
                    self._like_repository.delete(self.comment_id, user_id)
                    self.likes -= 1
                return False, "更新评论失败"

            return True, {"likes": self.likes, "action": action}

        except Exception as e:
            logger.error(f"点赞操作异常：err={str(e)}")
            return False, str(e)