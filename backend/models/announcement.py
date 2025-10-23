import uuid
import time
from typing import List, Optional, Dict, Any
from config import logger
from repositories.announcement_repository import AnnouncementRepository


class Announcement:
    """公告模型（使用仓储层进行数据访问）"""

    def __init__(self, data: Dict[str, Any]):
        """初始化公告对象"""
        self.announcement_id = data.get('announcement_id')
        self.title = data.get('title', '')
        self.content = data.get('content', '')
        self.publish_time = data.get('publish_time', int(time.time()))
        self.created_at = data.get('created_at', int(time.time()))
        self.updated_at = data.get('updated_at', int(time.time()))

        # 初始化仓储
        self._repository = AnnouncementRepository()

    @classmethod
    def create_announcement(cls, title: str, content: str) -> bool:
        """创建公告"""
        repository = AnnouncementRepository()
        success = repository.create_announcement(title, content)

        if not success:
            logger.error(f"创建公告失败: title={title}")
            return False

        logger.info(f"创建公告成功: title={title}")
        return True

    @classmethod
    def delete_announcement(cls, announcement_id: str) -> bool:
        """删除公告"""
        repository = AnnouncementRepository()
        success = repository.delete(announcement_id)

        if not success:
            logger.error(f"删除公告失败: announcement_id={announcement_id}")
            return False

        logger.info(f"删除公告成功: announcement_id={announcement_id}")
        return True

    @classmethod
    def get_announcements(cls) -> List[Dict[str, Any]]:
        """获取所有公告（按发布时间倒序排序）"""
        repository = AnnouncementRepository()
        data_list = repository.get_all_sorted()

        # 转换为Announcement对象
        announcements = [cls(data) for data in data_list]

        # 格式化返回（与原版一致）
        formatted = []
        for ann in announcements:
            formatted.append({
                'announcement_id': ann.announcement_id,
                'title': ann.title,
                'content': ann.content,
                'publish_time': ann.publish_time,
                'created_at': ann.created_at
            })

        return formatted