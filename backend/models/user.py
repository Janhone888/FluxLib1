import uuid
import time
from tablestore import (
    SingleColumnCondition, ComparatorType, INF_MIN, INF_MAX,
    RowExistenceExpectation  # 显式导入RowExistenceExpectation以支持相关操作
)
from config import logger, USERS_TABLE, FAVORITES_TABLE, VIEW_HISTORY_TABLE
from utils.database import ots_put_row, ots_get_row, ots_get_range
from utils.auth import hash_password
from utils.storage import generate_presigned_url


class User:
    """用户数据模型（对应Users表）"""

    def __init__(self, data):
        """初始化用户对象（字段与原代码完全一致）"""
        self.email = data.get('email')  # 主键
        self.user_id = data.get('user_id', str(uuid.uuid4()))  # 唯一ID
        self.password = data.get('password')  # 哈希后的密码
        self.created_at = data.get('created_at', int(time.time()))  # 创建时间
        self.updated_at = data.get('updated_at', int(time.time()))  # 更新时间
        self.role = data.get('role', 'user')  # 角色（user/admin）
        self.is_verified = data.get('is_verified', 'true')  # 是否验证
        self.display_name = data.get('display_name', self.email.split('@')[0] if self.email else '')  # 显示名（默认邮箱前缀）
        self.avatar_url = data.get('avatar_url',
                                   f"https://api.dicebear.com/7.x/initials/svg?seed={self.display_name}")  # 默认头像
        self.gender = data.get('gender', '')  # 性别

    @classmethod
    def create_user(cls, email, password, gender=None):
        """创建用户（对应原代码register_user核心逻辑）"""
        # 1. 检查用户是否已存在
        existing_user = cls.get_by_email(email)
        if existing_user:
            logger.warning(f"用户已存在: email={email}")
            return False, "该邮箱已注册"

        # 2. 密码哈希（复用utils.auth逻辑）
        hashed_pw = hash_password(password)

        # 3. 组装用户数据（与原代码字段完全一致）
        user_data = {
            'email': email,
            'user_id': str(uuid.uuid4()),
            'password': hashed_pw,
            'created_at': int(time.time()),
            'updated_at': int(time.time()),
            'role': 'user',
            'is_verified': 'true',
            'display_name': email.split('@')[0],
            'avatar_url': f"https://api.dicebear.com/7.x/initials/svg?seed={email.split('@')[0]}",
            'gender': gender or ''
        }

        # 4. 插入OTS（Users表）
        primary_key = [('email', email)]
        attribute_columns = [
            ('user_id', user_data['user_id']),
            ('password', user_data['password']),
            ('created_at', user_data['created_at']),
            ('updated_at', user_data['updated_at']),
            ('role', user_data['role']),
            ('is_verified', user_data['is_verified']),
            ('display_name', user_data['display_name']),
            ('avatar_url', user_data['avatar_url']),
            ('gender', user_data['gender'])
        ]
        success, err = ots_put_row(
            USERS_TABLE,
            primary_key,
            attribute_columns,
            expect_exist=RowExistenceExpectation.EXPECT_NOT_EXIST  # 确保用户不存在
        )
        if not success:
            logger.error(f"创建用户失败: email={email}, err={err}")
            return False, str(err)

        logger.info(f"用户创建成功: email={email}, user_id={user_data['user_id']}")
        return True, user_data['user_id']

    @classmethod
    def get_by_email(cls, email):
        """通过邮箱获取用户（对应原代码get_user逻辑）"""
        data = ots_get_row(USERS_TABLE, primary_key=[('email', email)])
        if not data:
            return None
        return cls(data)

    @classmethod
    def get_by_id(cls, user_id):
        """通过user_id获取用户（对应原代码get_user_by_id逻辑，INF_MIN/INF_MAX已正常导入）"""
        # 范围查询：匹配user_id字段
        condition = SingleColumnCondition('user_id', user_id, ComparatorType.EQUAL)
        user_list = ots_get_range(
            USERS_TABLE,
            start_pk=[('email', INF_MIN)],  # 已导入INF_MIN，可正常使用
            end_pk=[('email', INF_MAX)],  # 已导入INF_MAX，可正常使用
            column_filter=condition,
            limit=1
        )
        if not user_list:
            return None
        return cls(user_list[0])

    def update_profile(self, display_name=None, avatar_url=None, gender=None):
        """更新用户信息（对应原代码update_user_profile逻辑）"""
        if not self.email:
            logger.error("更新用户信息失败: 缺少email主键")
            return False, "用户不存在"

        # 组装更新字段
        update_columns = []
        if display_name:
            self.display_name = display_name
            update_columns.append(('display_name', display_name))
        if avatar_url:
            self.avatar_url = avatar_url
            update_columns.append(('avatar_url', avatar_url))
        if gender is not None:
            self.gender = gender
            update_columns.append(('gender', gender))

        # 强制更新updated_at
        self.updated_at = int(time.time())
        update_columns.append(('updated_at', self.updated_at))

        if not update_columns:
            return False, "没有提供更新字段"

        # 调用OTS更新
        primary_key = [('email', self.email)]
        success, err = ots_put_row(
            USERS_TABLE,
            primary_key,
            update_columns,
            expect_exist=RowExistenceExpectation.IGNORE  # 忽略行存在性（存在则更新）
        )
        if not success:
            logger.error(f"更新用户信息失败: email={self.email}, err={err}")
            return False, str(err)

        logger.info(f"更新用户信息成功: email={self.email}")
        return True, None

    @classmethod
    def create_admin(cls):
        """创建默认管理员（对应原代码create_admin_user逻辑）"""
        from config import ADMIN_EMAIL, ADMIN_DEFAULT_PASSWORD
        admin_email = ADMIN_EMAIL
        admin_password = ADMIN_DEFAULT_PASSWORD

        # 检查管理员是否已存在
        existing_admin = cls.get_by_email(admin_email)
        if existing_admin:
            logger.info(f"管理员已存在: email={admin_email}")
            return True, "管理员已存在"

        # 组装管理员数据
        hashed_pw = hash_password(admin_password)
        admin_data = {
            'email': admin_email,
            'user_id': str(uuid.uuid4()),
            'password': hashed_pw,
            'created_at': int(time.time()),
            'updated_at': int(time.time()),
            'role': 'admin',  # 管理员角色
            'is_verified': 'true',
            'display_name': '管理员',
            'avatar_url': f"https://api.dicebear.com/7.x/initials/svg?seed=Admin",
            'gender': ''
        }

        # 插入OTS
        primary_key = [('email', admin_email)]
        attribute_columns = [
            ('user_id', admin_data['user_id']),
            ('password', admin_data['password']),
            ('created_at', admin_data['created_at']),
            ('updated_at', admin_data['updated_at']),
            ('role', admin_data['role']),
            ('is_verified', admin_data['is_verified']),
            ('display_name', admin_data['display_name']),
            ('avatar_url', admin_data['avatar_url']),
            ('gender', admin_data['gender'])
        ]
        success, err = ots_put_row(
            USERS_TABLE,
            primary_key,
            attribute_columns,
            expect_exist=RowExistenceExpectation.IGNORE
        )
        if not success:
            logger.error(f"创建管理员失败: err={err}")
            return False, str(err)

        logger.info(f"管理员创建成功: email={admin_email}")
        return True, None

    # -------------------------- 关联操作（收藏、浏览历史）--------------------------
    def add_favorite(self, book_id):
        """添加收藏（对应原代码add_favorite逻辑）"""
        from models.favorite import Favorite  # 明确导入路径，确保模块存在
        return Favorite.create(self.user_id, book_id)

    def remove_favorite(self, book_id):
        """移除收藏（对应原代码remove_favorite逻辑）"""
        from models.favorite import Favorite  # 明确导入路径，确保模块存在
        return Favorite.delete_by_user_book(self.user_id, book_id)

    def check_favorite(self, book_id):
        """检查是否收藏（对应原代码check_favorite逻辑）"""
        from models.favorite import Favorite  # 明确导入路径，确保模块存在
        return Favorite.exists(self.user_id, book_id)

    def get_favorites(self):
        """获取用户收藏列表（导入路径正确，确保模块存在无报错）"""
        from models.favorite import Favorite  # 确认模块路径正确
        return Favorite.get_by_user_id(self.user_id)

    def add_view_history(self, book_id):
        """添加浏览历史（对应原代码add_view_history逻辑）"""
        from models.view_history import ViewHistory  # 明确导入路径，确保模块存在
        return ViewHistory.create(self.user_id, book_id)

    def get_view_history(self):
        """获取用户浏览历史（导入路径正确，确保模块存在无报错）"""
        from models.view_history import ViewHistory  # 确认模块路径正确
        return ViewHistory.get_by_user_id(self.user_id)
