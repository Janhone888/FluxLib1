import time
import uuid
from typing import List, Dict, Any, Optional
from tablestore import INF_MIN, INF_MAX, RowExistenceExpectation
from config import logger, ANNOUNCEMENTS_TABLE
from utils.database import ots_put_row, ots_get_row, ots_get_range, ots_delete_row
from repositories.base_repository import BaseRepository


class AnnouncementRepository(BaseRepository):
    """公告数据仓储层，负责所有公告数据的OTS访问操作"""

    def __init__(self):
        self.table_name = ANNOUNCEMENTS_TABLE

    def get_by_id(self, announcement_id: str) -> Optional[Dict[str, Any]]:
        """根据announcement_id获取公告数据"""
        logger.info(f"查询Announcements表: announcement_id={announcement_id}")

        data = ots_get_row(self.table_name, primary_key=[('announcement_id', announcement_id)])
        if not data:
            logger.info(f"公告不存在: announcement_id={announcement_id}")
            return None

        logger.info(f"获取公告成功: announcement_id={announcement_id}")
        return data

    def get_all(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """获取所有公告数据"""
        all_announcements = ots_get_range(
            self.table_name,
            start_pk=[('announcement_id', INF_MIN)],
            end_pk=[('announcement_id', INF_MAX)]
        )

        logger.info(f"查询到公告总数: {len(all_announcements)}")
        return all_announcements

    def create(self, entity_data: Dict[str, Any]) -> Optional[str]:
        """创建新公告"""
        announcement_id = entity_data.get('announcement_id')
        if not announcement_id:
            logger.error("创建公告失败: 缺少announcement_id")
            return None

        primary_key = [('announcement_id', announcement_id)]
        attribute_columns = [
            ('title', entity_data['title']),
            ('content', entity_data['content']),
            ('publish_time', entity_data['publish_time']),
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
            logger.error(f"创建公告失败: announcement_id={announcement_id}, err={err}")
            return None

        logger.info(f"创建公告成功: announcement_id={announcement_id}")
        return announcement_id

    def update(self, announcement_id: str, update_data: Dict[str, Any]) -> bool:
        """更新公告数据"""
        if not announcement_id:
            logger.error("更新公告失败: 缺少announcement_id")
            return False

        primary_key = [('announcement_id', announcement_id)]
        update_columns = [(key, value) for key, value in update_data.items()]

        success, err = ots_put_row(
            self.table_name,
            primary_key,
            update_columns,
            expect_exist=RowExistenceExpectation.IGNORE
        )

        if not success:
            logger.error(f"更新公告失败: announcement_id={announcement_id}, err={err}")
            return False

        logger.info(f"更新公告成功: announcement_id={announcement_id}")
        return True

    def delete(self, announcement_id: str) -> bool:
        """删除公告"""
        success, err = ots_delete_row(
            self.table_name,
            primary_key=[('announcement_id', announcement_id)]
        )

        if not success:
            logger.error(f"删除公告失败: announcement_id={announcement_id}, err={err}")
            return False

        logger.info(f"删除公告成功: announcement_id={announcement_id}")
        return True

    def count(self, filters: Dict[str, Any] = None) -> int:
        """统计公告数量"""
        all_announcements = self.get_all(filters)
        return len(all_announcements)

    def create_announcement(self, title: str, content: str) -> bool:
        """创建公告（封装创建逻辑）"""
        # 生成announcement_id
        announcement_id = str(uuid.uuid4())
        current_time = int(time.time())

        # 组装公告数据
        announcement_data = {
            'announcement_id': announcement_id,
            'title': title,
            'content': content,
            'publish_time': current_time,
            'created_at': current_time,
            'updated_at': current_time
        }

        # 创建记录
        result = self.create(announcement_data)
        return result is not None

    def get_all_sorted(self) -> List[Dict[str, Any]]:
        """获取所有公告并按发布时间倒序排序"""
        all_announcements = self.get_all()

        # 按发布时间倒序排序
        all_announcements.sort(key=lambda x: x.get('publish_time', 0), reverse=True)

        return all_announcements