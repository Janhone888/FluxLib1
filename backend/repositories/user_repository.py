import time
from typing import List, Dict, Any, Optional
from tablestore import (
    SingleColumnCondition, ComparatorType, INF_MIN, INF_MAX, RowExistenceExpectation
)
from config import logger, USERS_TABLE
from utils.database import ots_put_row, ots_get_row, ots_get_range, ots_delete_row
from repositories.base_repository import BaseRepository


class UserRepository(BaseRepository):
    """用户数据仓储层，负责所有用户数据的OTS访问操作"""

    def __init__(self):
        self.table_name = USERS_TABLE

    def get_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """根据user_id获取用户数据"""
        logger.info(f"查询Users表: user_id={user_id}")

        # 通过email主键范围查询 + user_id过滤
        condition = SingleColumnCondition('user_id', user_id, ComparatorType.EQUAL)
        user_list = ots_get_range(
            self.table_name,
            start_pk=[('email', INF_MIN)],
            end_pk=[('email', INF_MAX)],
            column_filter=condition,
            limit=1
        )

        if not user_list:
            logger.info(f"用户不存在: user_id={user_id}")
            return None

        user_data = user_list[0]
        logger.info(f"获取用户成功: user_id={user_id}, email={user_data.get('email')}")
        return user_data

    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """根据email获取用户数据"""
        logger.info(f"查询Users表: email={email}")

        data = ots_get_row(self.table_name, primary_key=[('email', email)])
        if not data:
            logger.info(f"用户不存在: email={email}")
            return None

        logger.info(f"获取用户成功: email={email}")
        return data

    def get_all(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """获取所有用户数据"""
        all_users = ots_get_range(
            self.table_name,
            start_pk=[('email', INF_MIN)],
            end_pk=[('email', INF_MAX)]
        )

        logger.info(f"查询到用户总数: {len(all_users)}")
        return all_users

    def create(self, entity_data: Dict[str, Any]) -> Optional[str]:
        """创建新用户"""
        email = entity_data.get('email')
        if not email:
            logger.error("创建用户失败: 缺少email")
            return None

        primary_key = [('email', email)]
        attribute_columns = [
            ('user_id', entity_data['user_id']),
            ('password', entity_data['password']),
            ('created_at', entity_data['created_at']),
            ('updated_at', entity_data['updated_at']),
            ('role', entity_data['role']),
            ('is_verified', entity_data['is_verified']),
            ('display_name', entity_data['display_name']),
            ('avatar_url', entity_data['avatar_url']),
            ('gender', entity_data['gender']),
            ('background_url', entity_data.get('background_url', '')),
            ('summary', entity_data.get('summary', ''))
        ]

        success, err = ots_put_row(
            self.table_name,
            primary_key,
            attribute_columns,
            expect_exist=RowExistenceExpectation.EXPECT_NOT_EXIST
        )

        if not success:
            logger.error(f"创建用户失败: email={email}, err={err}")
            return None

        logger.info(f"创建用户成功: email={email}, user_id={entity_data['user_id']}")
        return entity_data['user_id']

    def update(self, email: str, update_data: Dict[str, Any]) -> bool:
        """更新用户数据"""
        if not email:
            logger.error("更新用户失败: 缺少email")
            return False

        primary_key = [('email', email)]
        update_columns = [(key, value) for key, value in update_data.items()]

        success, err = ots_put_row(
            self.table_name,
            primary_key,
            update_columns,
            expect_exist=RowExistenceExpectation.IGNORE
        )

        if not success:
            logger.error(f"更新用户失败: email={email}, err={err}")
            return False

        logger.info(f"更新用户成功: email={email}")
        return True

    def delete(self, email: str) -> bool:
        """删除用户（单主键：email，适配基类*args签名）"""
        success, err = ots_delete_row(
            self.table_name,
            primary_key=[('email', email)]
        )

        if not success:
            logger.error(f"删除用户失败: email={email}, err={err}")
            return False

        logger.info(f"删除用户成功: email={email}")
        return True

    def count(self, filters: Dict[str, Any] = None) -> int:
        """统计用户数量"""
        all_users = self.get_all(filters)
        return len(all_users)

    def check_email_exists(self, email: str) -> bool:
        """检查邮箱是否已存在"""
        user_data = self.get_by_email(email)
        return user_data is not None