import time
from typing import List, Dict, Any, Optional
from tablestore import (
    SingleColumnCondition, ComparatorType, INF_MIN, INF_MAX, RowExistenceExpectation
)
from config import logger, COMMENTS_TABLE
from utils.database import ots_put_row, ots_get_row, ots_get_range, ots_delete_row
from repositories.base_repository import BaseRepository


class CommentRepository(BaseRepository):
    """评论数据仓储层，负责所有评论数据的OTS访问操作"""

    def __init__(self):
        self.table_name = COMMENTS_TABLE

    def get_by_id(self, comment_id: str) -> Optional[Dict[str, Any]]:
        """根据comment_id获取评论数据"""
        logger.info(f"查询Comments表: comment_id={comment_id}")

        data = ots_get_row(self.table_name, primary_key=[('comment_id', comment_id)])
        if not data:
            logger.info(f"评论不存在: comment_id={comment_id}")
            return None

        # 类型转换
        if 'likes' in data:
            data['likes'] = int(data['likes'])

        logger.info(f"获取评论成功: comment_id={comment_id}")
        return data

    def get_all(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """获取所有评论数据"""
        all_comments = ots_get_range(
            self.table_name,
            start_pk=[('comment_id', INF_MIN)],
            end_pk=[('comment_id', INF_MAX)]
        )

        logger.info(f"查询到评论总数: {len(all_comments)}")

        # 类型转换
        for comment in all_comments:
            if 'likes' in comment:
                comment['likes'] = int(comment['likes'])

        return all_comments

    def create(self, entity_data: Dict[str, Any]) -> Optional[str]:
        """创建新评论"""
        comment_id = entity_data.get('comment_id')
        if not comment_id:
            logger.error("创建评论失败: 缺少comment_id")
            return None

        primary_key = [('comment_id', comment_id)]
        attribute_columns = [
            ('book_id', entity_data['book_id']),
            ('user_id', entity_data['user_id']),
            ('user_display_name', entity_data['user_display_name']),
            ('user_avatar_url', entity_data['user_avatar_url']),
            ('content', entity_data['content']),
            ('parent_id', entity_data.get('parent_id', '')),
            ('likes', entity_data.get('likes', 0)),
            ('created_at', entity_data['created_at']),
            ('updated_at', entity_data['updated_at'])
        ]

        success, err = ots_put_row(
            self.table_name,
            primary_key,
            attribute_columns,
            expect_exist=RowExistenceExpectation.IGNORE
        )

        if not success:
            logger.error(f"创建评论失败: comment_id={comment_id}, err={err}")
            return None

        logger.info(
            f"创建评论成功: comment_id={comment_id}, book_id={entity_data['book_id']}, user_id={entity_data['user_id']}")
        return comment_id

    def update(self, comment_id: str, update_data: Dict[str, Any]) -> bool:
        """更新评论数据"""
        if not comment_id:
            logger.error("更新评论失败: 缺少comment_id")
            return False

        primary_key = [('comment_id', comment_id)]
        update_columns = [(key, value) for key, value in update_data.items()]

        success, err = ots_put_row(
            self.table_name,
            primary_key,
            update_columns,
            expect_exist=RowExistenceExpectation.IGNORE
        )

        if not success:
            logger.error(f"更新评论失败: comment_id={comment_id}, err={err}")
            return False

        logger.info(f"更新评论成功: comment_id={comment_id}")
        return True

    def delete(self, comment_id: str) -> bool:
        """删除评论"""
        success, err = ots_delete_row(
            self.table_name,
            primary_key=[('comment_id', comment_id)]
        )

        if not success:
            logger.error(f"删除评论失败: comment_id={comment_id}, err={err}")
            return False

        logger.info(f"删除评论成功: comment_id={comment_id}")
        return True

    def count(self, filters: Dict[str, Any] = None) -> int:
        """统计评论数量"""
        all_comments = self.get_all(filters)
        return len(all_comments)

    def get_by_book_id(self, book_id: str) -> List[Dict[str, Any]]:
        """根据book_id获取所有评论"""
        logger.info(f"【查询评论】目标图书ID: {book_id}，开始查询Comments表")

        condition = SingleColumnCondition('book_id', book_id, ComparatorType.EQUAL)
        comment_list = ots_get_range(
            self.table_name,
            start_pk=[('comment_id', INF_MIN)],
            end_pk=[('comment_id', INF_MAX)],
            column_filter=condition,
            column_to_get=[
                'comment_id', 'book_id', 'user_id', 'user_display_name', 'user_avatar_url',
                'content', 'parent_id', 'likes', 'created_at', 'updated_at'
            ]
        )

        logger.info(f"✅ 从OTS查询到的评论数量: {len(comment_list)} 条（book_id={book_id}）")

        # 类型转换
        for comment in comment_list:
            if 'likes' in comment:
                comment['likes'] = int(comment['likes'])

        return comment_list

    def get_by_user_id(self, user_id: str) -> List[Dict[str, Any]]:
        """根据user_id获取用户所有评论"""
        condition = SingleColumnCondition('user_id', user_id, ComparatorType.EQUAL)
        comment_list = ots_get_range(
            self.table_name,
            start_pk=[('comment_id', INF_MIN)],
            end_pk=[('comment_id', INF_MAX)],
            column_filter=condition
        )

        # 类型转换
        for comment in comment_list:
            if 'likes' in comment:
                comment['likes'] = int(comment['likes'])

        return comment_list