import uuid
import time
from tablestore import SingleColumnCondition, ComparatorType, INF_MIN, INF_MAX
from config import logger, ANNOUNCEMENTS_TABLE
from utils.database import ots_put_row, ots_get_row, ots_get_range, ots_delete_row


class Announcement:
    """公告模型（对应Announcements表）"""
    def __init__(self, data):
        self.announcement_id = data.get('announcement_id')  # 主键
        self.title = data.get('title', '')  # 公告标题
        self.content = data.get('content', '')  # 公告内容
        self.publish_time = data.get('publish_time', int(time.time()))  # 发布时间
        self.created_at = data.get('created_at', int(time.time()))  # 创建时间
        self.updated_at = data.get('updated_at', int(time.time()))  # 更新时间

    @classmethod
    def create_announcement(cls, title, content):
        """创建公告（对应原版create_announcement）"""
        announcement_id = str(uuid.uuid4())
        current_time = int(time.time())
        announcement_data = {
            'announcement_id': announcement_id,
            'title': title,
            'content': content,
            'publish_time': current_time,
            'created_at': current_time,
            'updated_at': current_time
        }
        # 插入OTS
        primary_key = [('announcement_id', announcement_id)]
        attribute_columns = [
            ('title', announcement_data['title']),
            ('content', announcement_data['content']),
            ('publish_time', announcement_data['publish_time']),
            ('created_at', announcement_data['created_at']),
            ('updated_at', announcement_data['updated_at'])
        ]
        success, err = ots_put_row(
            ANNOUNCEMENTS_TABLE,
            primary_key,
            attribute_columns,
            expect_exist=RowExistenceExpectation.IGNORE
        )
        if not success:
            logger.error(f"创建公告失败: {err}")
            return False
        logger.info(f"创建公告成功: announcement_id={announcement_id}")
        return True

    @classmethod
    def delete_announcement(cls, announcement_id):
        """删除公告（对应原版delete_announcement）"""
        success, err = ots_delete_row(
            ANNOUNCEMENTS_TABLE,
            primary_key=[('announcement_id', announcement_id)]
        )
        if not success:
            logger.error(f"删除公告失败: {err}")
            return False
        logger.info(f"删除公告成功: announcement_id={announcement_id}")
        return True

    @classmethod
    def get_announcements(cls):
        """获取所有公告（对应原版get_announcements）"""
        announcement_list = ots_get_range(
            ANNOUNCEMENTS_TABLE,
            start_pk=[('announcement_id', INF_MIN)],
            end_pk=[('announcement_id', INF_MAX)]
        )
        # 按发布时间倒序排序
        announcements = [cls(data) for data in announcement_list]
        announcements.sort(key=lambda x: x.publish_time, reverse=True)
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