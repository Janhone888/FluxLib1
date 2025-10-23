import uuid
import time
from typing import Optional, Dict, Any, List, Tuple
from config import logger
from repositories.user_repository import UserRepository
from utils.auth import hash_password


class User:
    """用户数据模型（使用仓储层进行数据访问）"""

    def __init__(self, data: Dict[str, Any]):
        """初始化用户对象"""
        self.email = data.get('email', '')
        self.user_id = data.get('user_id', '')
        self.password = data.get('password', '')
        self.created_at = data.get('created_at', int(time.time()))
        self.updated_at = data.get('updated_at', int(time.time()))
        self.role = data.get('role', 'user')
        self.is_verified = data.get('is_verified', False)

        # 处理display_name
        self.display_name = data.get(
            'display_name',
            self.email.split('@')[0] if (self.email and '@' in self.email) else '未知用户'
        )

        # 处理avatar_url
        self.avatar_url = data.get(
            'avatar_url',
            f"https://api.dicebear.com/7.x/initials/svg?seed={self.display_name or 'User'}"
        )

        self.gender = data.get('gender', '')
        self.background_url = data.get('background_url', '')
        self.summary = data.get('summary', '')

        # 初始化仓储
        self._repository = UserRepository()

    @classmethod
    def create_user(cls, email: str, password: str, gender: str = None) -> tuple:
        """创建用户"""
        # 1. 检查用户是否已存在
        repository = UserRepository()
        if repository.check_email_exists(email):
            logger.warning(f"用户创建失败: 邮箱已注册（email={email}）")
            return False, "该邮箱已注册"

        # 2. 密码哈希处理
        hashed_pw = hash_password(password)
        if not hashed_pw:
            logger.error(f"用户创建失败: 密码哈希生成失败（email={email}）")
            return False, "密码处理异常"

        # 3. 组装完整用户数据
        user_id = str(uuid.uuid4())
        current_timestamp = int(time.time())
        user_data = {
            'email': email,
            'user_id': user_id,
            'password': hashed_pw,
            'created_at': current_timestamp,
            'updated_at': current_timestamp,
            'role': 'user',
            'is_verified': False,
            'display_name': email.split('@')[0] if (email and '@' in email) else email,
            'avatar_url': f"https://api.dicebear.com/7.x/initials/svg?seed={email.split('@')[0] if (email and '@' in email) else 'User'}",
            'gender': gender or '',
            'background_url': '',
            'summary': ''
        }

        # 4. 通过仓储层创建用户
        result = repository.create(user_data)
        if not result:
            logger.error(f"用户创建失败: OTS写入异常（email={email}）")
            return False, "创建用户失败"

        logger.info(f"用户创建成功: email={email}, user_id={user_id}（核心字段已完整写入）")
        return True, user_id

    @classmethod
    def get_by_email(cls, email: str) -> Optional['User']:
        """通过邮箱获取用户"""
        repository = UserRepository()
        data = repository.get_by_email(email)

        if not data:
            return None

        return cls(data)

    @classmethod
    def get_by_id(cls, user_id: str) -> Optional['User']:
        """通过user_id获取用户"""
        repository = UserRepository()
        data = repository.get_by_id(user_id)

        if not data:
            return None

        return cls(data)

    def update_profile(self, display_name: str = None, avatar_url: str = None,
                       gender: str = None, background_url: str = None,
                       summary: str = None) -> tuple:
        """更新用户资料"""
        if not self.email:
            logger.error("用户资料更新失败: 缺少email主键")
            return False, "用户不存在"

        # 获取当前用户的完整数据
        current_user_data = self._repository.get_by_email(self.email)
        if not current_user_data:
            logger.error(f"用户资料更新失败: 无法获取完整数据（email={self.email}）")
            return False, "用户数据已丢失，请重新登录"

        # 组装更新字段
        update_columns = {}
        current_timestamp = int(time.time())

        # 处理可修改字段
        if display_name is not None and display_name.strip():
            self.display_name = display_name.strip()
            update_columns['display_name'] = self.display_name

        if avatar_url is not None:
            self.avatar_url = avatar_url
            update_columns['avatar_url'] = self.avatar_url

        if gender is not None:
            self.gender = gender
            update_columns['gender'] = self.gender

        if background_url is not None:
            self.background_url = background_url
            update_columns['background_url'] = self.background_url

        if summary is not None:
            self.summary = summary
            update_columns['summary'] = self.summary

        # 强制添加核心不可修改字段
        update_columns.update({
            'user_id': current_user_data.get('user_id', ''),
            'password': current_user_data.get('password', ''),
            'role': current_user_data.get('role', 'user'),
            'is_verified': current_user_data.get('is_verified', False),
            'created_at': current_user_data.get('created_at', current_timestamp),
            'updated_at': current_timestamp
        })

        # 通过仓储层更新数据
        success = self._repository.update(self.email, update_columns)
        if not success:
            logger.error(f"用户资料更新失败: OTS写入异常（email={self.email}）")
            return False, "更新用户资料失败"

        # 更新成功后刷新实例字段
        self.user_id = current_user_data.get('user_id', '')
        self.password = current_user_data.get('password', '')
        self.role = current_user_data.get('role', 'user')
        self.is_verified = current_user_data.get('is_verified', False)
        self.created_at = current_user_data.get('created_at', current_timestamp)
        self.updated_at = current_timestamp

        logger.info(f"用户资料更新成功: email={self.email}，更新字段={list(update_columns.keys())}")
        return True, None

    def update_password(self, new_password: str) -> tuple:
        """更新用户密码"""
        if not self.email:
            logger.error("密码更新失败: 缺少email主键")
            return False, "用户不存在"

        # 获取当前用户完整数据
        current_user_data = self._repository.get_by_email(self.email)
        if not current_user_data:
            logger.error(f"密码更新失败: 无法获取完整数据（email={self.email}）")
            return False, "用户数据已丢失，请重新登录"

        # 密码哈希处理
        new_hashed_pw = hash_password(new_password)
        if not new_hashed_pw:
            logger.error(f"密码更新失败: 新密码哈希生成异常（email={self.email}）")
            return False, "密码处理异常"

        # 组装更新字段
        current_timestamp = int(time.time())
        update_columns = {
            'password': new_hashed_pw,
            'updated_at': current_timestamp,
            'user_id': current_user_data.get('user_id', ''),
            'role': current_user_data.get('role', 'user'),
            'is_verified': current_user_data.get('is_verified', False),
            'created_at': current_user_data.get('created_at', current_timestamp),
            'display_name': current_user_data.get('display_name', ''),
            'avatar_url': current_user_data.get('avatar_url', ''),
            'gender': current_user_data.get('gender', ''),
            'background_url': current_user_data.get('background_url', ''),
            'summary': current_user_data.get('summary', '')
        }

        # 通过仓储层更新数据
        success = self._repository.update(self.email, update_columns)
        if not success:
            logger.error(f"密码更新失败: OTS写入异常（email={self.email}）")
            return False, "更新密码失败"

        # 刷新实例密码字段
        self.password = new_hashed_pw
        self.updated_at = current_timestamp

        logger.info(f"密码更新成功: email={self.email}（其他核心字段已保留）")
        return True, None

    @classmethod
    def create_admin(cls) -> tuple:
        """创建默认管理员"""
        from config import ADMIN_EMAIL, ADMIN_DEFAULT_PASSWORD

        if not ADMIN_EMAIL or not ADMIN_DEFAULT_PASSWORD:
            logger.error("管理员创建失败: 配置中缺少ADMIN_EMAIL或ADMIN_DEFAULT_PASSWORD")
            return False, "管理员配置缺失"

        # 检查管理员是否已存在
        repository = UserRepository()
        if repository.check_email_exists(ADMIN_EMAIL):
            logger.info(f"管理员创建跳过: 已存在（email={ADMIN_EMAIL}）")
            return True, "管理员已存在"

        # 密码哈希处理
        hashed_pw = hash_password(ADMIN_DEFAULT_PASSWORD)
        if not hashed_pw:
            logger.error("管理员创建失败: 密码哈希生成异常")
            return False, "密码处理异常"

        # 组装管理员数据
        user_id = str(uuid.uuid4())
        current_timestamp = int(time.time())
        admin_data = {
            'email': ADMIN_EMAIL,
            'user_id': user_id,
            'password': hashed_pw,
            'created_at': current_timestamp,
            'updated_at': current_timestamp,
            'role': 'admin',
            'is_verified': True,
            'display_name': '管理员',
            'avatar_url': "https://api.dicebear.com/7.x/initials/svg?seed=Admin",
            'gender': '',
            'background_url': '',
            'summary': '系统管理员账号'
        }

        # 通过仓储层创建管理员
        result = repository.create(admin_data)
        if not result:
            logger.error("管理员创建失败: OTS写入异常")
            return False, "创建管理员失败"

        logger.info(f"默认管理员创建成功: email={ADMIN_EMAIL}, user_id={user_id}")
        return True, None

    # 用户关联操作（收藏、浏览历史）
    def add_favorite(self, book_id: str) -> tuple:
        """添加图书收藏"""
        if not self.user_id:
            logger.error(f"收藏添加失败: user_id为空（email={self.email}）")
            return False, "用户ID缺失，无法收藏"

        from models.favorite import Favorite
        return Favorite.create(self.user_id, book_id)

    def remove_favorite(self, book_id: str) -> tuple:
        """移除图书收藏"""
        if not self.user_id:
            logger.error(f"收藏移除失败: user_id为空（email={self.email}）")
            return False, "用户ID缺失，无法取消收藏"

        from models.favorite import Favorite
        return Favorite.delete_by_user_book(self.user_id, book_id)

    def check_favorite(self, book_id: str) -> bool:
        """检查图书是否已收藏"""
        if not self.user_id:
            logger.error(f"收藏检查失败: user_id为空（email={self.email}）")
            return False

        from models.favorite import Favorite
        return Favorite.exists(self.user_id, book_id)

    def get_favorites(self) -> List:
        """获取用户收藏列表"""
        if not self.user_id:
            logger.error(f"收藏列表获取失败: user_id为空（email={self.email}）")
            return []

        from models.favorite import Favorite
        return Favorite.get_by_user_id(self.user_id)

    def add_view_history(self, book_id: str) -> Tuple[bool, Optional[str]]:
        """添加浏览历史（使用仓储层优化）"""
        if not self.user_id:
            logger.error(f"浏览历史添加失败: user_id为空（email={self.email}）")
            return False, "用户ID缺失，无法记录历史"

        from models.view_history import ViewHistory
        success = ViewHistory.create(self.user_id, book_id)

        if not success:
            return False, "添加浏览历史失败"

        return True, None

    def get_view_history(self) -> List:
        """获取用户浏览历史（使用仓储层优化）"""
        if not self.user_id:
            logger.error(f"浏览历史获取失败: user_id为空（email={self.email}）")
            return []

        from models.view_history import ViewHistory
        return ViewHistory.get_by_user_id(self.user_id)