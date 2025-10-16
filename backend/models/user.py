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
        """初始化用户对象（确保所有核心字段都被赋值，避免None）"""
        self.email = data.get('email', '')  # 主键（必传，用于定位用户）
        self.user_id = data.get('user_id', '')  # 用户唯一ID（登录/关联数据关键）
        self.password = data.get('password', '')  # 密码哈希（登录验证核心）
        self.created_at = data.get('created_at', int(time.time()))  # 注册时间（不可修改）
        self.updated_at = data.get('updated_at', int(time.time()))  # 更新时间（每次更新刷新）
        self.role = data.get('role', 'user')  # 用户角色（admin/user，权限控制核心）
        self.is_verified = data.get('is_verified', False)  # 邮箱验证状态（布尔值，避免字符串类型问题）
        # 处理display_name：避免email为空或无@符号时报错
        self.display_name = data.get(
            'display_name',
            self.email.split('@')[0] if (self.email and '@' in self.email) else '未知用户'
        )
        # 处理avatar_url：默认头像兜底（避免空值导致前端渲染错误）
        self.avatar_url = data.get(
            'avatar_url',
            f"https://api.dicebear.com/7.x/initials/svg?seed={self.display_name or 'User'}"
        )
        self.gender = data.get('gender', '')  # 性别（可修改，允许空值）

    @classmethod
    def create_user(cls, email, password, gender=None):
        """创建用户（确保初始核心字段完整写入OTS，避免后续缺失）"""
        # 1. 检查用户是否已存在（通过邮箱查重）
        existing_user = cls.get_by_email(email)
        if existing_user:
            logger.warning(f"用户创建失败: 邮箱已注册（email={email}）")
            return False, "该邮箱已注册"

        # 2. 密码哈希处理（复用utils.auth的加密逻辑，确保安全）
        hashed_pw = hash_password(password)
        if not hashed_pw:
            logger.error(f"用户创建失败: 密码哈希生成失败（email={email}）")
            return False, "密码处理异常"

        # 3. 组装完整用户数据（包含所有核心字段，无遗漏）
        user_id = str(uuid.uuid4())  # 生成唯一用户ID
        current_timestamp = int(time.time())
        user_data = {
            'email': email,
            'user_id': user_id,
            'password': hashed_pw,
            'created_at': current_timestamp,
            'updated_at': current_timestamp,
            'role': 'user',  # 新用户默认普通角色
            'is_verified': False,  # 新用户默认未验证（后续通过邮箱验证修改）
            'display_name': email.split('@')[0] if (email and '@' in email) else email,
            'avatar_url': f"https://api.dicebear.com/7.x/initials/svg?seed={email.split('@')[0] if (email and '@' in email) else 'User'}",
            'gender': gender or ''
        }

        # 4. 写入OTS（Users表）- 明确包含所有核心字段，避免缺失
        primary_key = [('email', email)]  # 主键：email
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
            expect_exist=RowExistenceExpectation.EXPECT_NOT_EXIST  # 防止重复注册
        )
        if not success:
            logger.error(f"用户创建失败: OTS写入异常（email={email}, err={err}）")
            return False, str(err)

        logger.info(f"用户创建成功: email={email}, user_id={user_id}（核心字段已完整写入）")
        return True, user_id

    @classmethod
    def get_by_email(cls, email):
        """通过邮箱获取用户（确保返回完整核心字段）"""
        # 调用database工具函数，获取完整用户数据（无列过滤）
        user_data = ots_get_row(USERS_TABLE, primary_key=[('email', email)])
        if not user_data:
            logger.warning(f"用户查询失败: 邮箱不存在（email={email}）")
            return None
        # 初始化User实例（__init__会自动填充所有核心字段）
        return cls(user_data)

    @classmethod
    def get_by_id(cls, user_id):
        """通过user_id获取用户（范围查询+过滤，确保返回完整核心字段）"""
        # 构建user_id过滤条件（精确匹配）
        column_filter = SingleColumnCondition('user_id', user_id, ComparatorType.EQUAL)
        # 范围查询（email从最小到最大，配合过滤条件定位唯一用户）
        user_list = ots_get_range(
            USERS_TABLE,
            start_pk=[('email', INF_MIN)],
            end_pk=[('email', INF_MAX)],
            column_filter=column_filter,
            limit=1  # 只取第一条结果（user_id唯一）
        )
        if not user_list or len(user_list) == 0:
            logger.warning(f"用户查询失败: user_id不存在（user_id={user_id}）")
            return None
        # 初始化User实例（使用查询到的完整数据）
        return cls(user_list[0])

    def update_profile(self, display_name=None, avatar_url=None, gender=None):
        """更新用户资料（核心修复：强制携带所有核心字段，避免OTS覆盖清空）"""
        # 1. 校验主键：email为空无法定位用户
        if not self.email:
            logger.error("用户资料更新失败: 缺少email主键（无法定位用户）")
            return False, "用户不存在"

        # 2. 关键步骤：更新前先获取当前用户的完整数据（避免使用实例中过时的字段）
        current_user_data = ots_get_row(USERS_TABLE, primary_key=[('email', self.email)])
        if not current_user_data:
            logger.error(f"用户资料更新失败: 无法获取完整数据（email={self.email}）")
            return False, "用户数据已丢失，请重新登录"

        # 3. 组装更新字段：可修改字段 + 所有核心字段（缺一不可）
        update_columns = []
        current_timestamp = int(time.time())

        # 3.1 处理「可修改字段」（用户主动更新的字段）
        # 显示名称：非空才更新（去重空格）
        if display_name is not None and display_name.strip():
            self.display_name = display_name.strip()
            update_columns.append(('display_name', self.display_name))
            logger.debug(f"待更新字段: display_name={self.display_name}")
        # 头像URL：允许为空（但实际场景中应传递有效URL）
        if avatar_url is not None:
            self.avatar_url = avatar_url
            update_columns.append(('avatar_url', self.avatar_url))
            logger.debug(f"待更新字段: avatar_url={self.avatar_url}")
        # 性别：允许为空（用户可取消选择）
        if gender is not None:
            self.gender = gender
            update_columns.append(('gender', self.gender))
            logger.debug(f"待更新字段: gender={self.gender}")

        # 3.2 强制添加「核心不可修改字段」（从数据库读取最新值，避免被清空）
        # 这些字段用户无法修改，但必须传递给OTS，否则会被覆盖删除
        core_unchangeable_fields = [
            ('user_id', current_user_data.get('user_id', '')),  # 登录关键：用户ID
            ('password', current_user_data.get('password', '')),  # 登录关键：密码哈希
            ('role', current_user_data.get('role', 'user')),  # 权限关键：用户角色
            ('is_verified', current_user_data.get('is_verified', False)),  # 验证状态
            ('created_at', current_user_data.get('created_at', current_timestamp)),  # 注册时间（不可改）
            ('updated_at', current_timestamp)  # 更新时间（强制刷新）
        ]
        update_columns.extend(core_unchangeable_fields)  # 合并所有字段

        # 4. 调用OTS执行更新（此时所有核心字段都会被重新写入，不会丢失）
        primary_key = [('email', self.email)]
        success, err = ots_put_row(
            USERS_TABLE,
            primary_key,
            update_columns,
            expect_exist=RowExistenceExpectation.IGNORE  # 兼容用户数据已存在的情况
        )
        if not success:
            logger.error(f"用户资料更新失败: OTS写入异常（email={self.email}, err={err}）")
            return False, str(err)

        # 5. 更新成功后，刷新当前实例的核心字段（确保后续操作使用最新值）
        self.user_id = current_user_data.get('user_id', '')
        self.password = current_user_data.get('password', '')
        self.role = current_user_data.get('role', 'user')
        self.is_verified = current_user_data.get('is_verified', False)
        self.created_at = current_user_data.get('created_at', current_timestamp)
        self.updated_at = current_timestamp

        logger.info(
            f"用户资料更新成功: email={self.email}，"
            f"更新字段={[col[0] for col in update_columns]}（核心字段已完整保留）"
        )
        return True, None

    def update_password(self, new_password):
        """更新用户密码（同步保留其他核心字段，避免丢失）"""
        # 1. 校验主键
        if not self.email:
            logger.error("密码更新失败: 缺少email主键（无法定位用户）")
            return False, "用户不存在"

        # 2. 获取当前用户完整数据（确保其他核心字段不丢失）
        current_user_data = ots_get_row(USERS_TABLE, primary_key=[('email', self.email)])
        if not current_user_data:
            logger.error(f"密码更新失败: 无法获取完整数据（email={self.email}）")
            return False, "用户数据已丢失，请重新登录"

        # 3. 密码哈希处理
        new_hashed_pw = hash_password(new_password)
        if not new_hashed_pw:
            logger.error(f"密码更新失败: 新密码哈希生成异常（email={self.email}）")
            return False, "密码处理异常"

        # 4. 组装更新字段：密码 + 所有核心字段
        current_timestamp = int(time.time())
        update_columns = [
            ('password', new_hashed_pw),  # 新密码哈希
            ('updated_at', current_timestamp),  # 刷新更新时间
            # 强制保留其他核心字段
            ('user_id', current_user_data.get('user_id', '')),
            ('role', current_user_data.get('role', 'user')),
            ('is_verified', current_user_data.get('is_verified', False)),
            ('created_at', current_user_data.get('created_at', current_timestamp)),
            ('display_name', current_user_data.get('display_name', '')),
            ('avatar_url', current_user_data.get('avatar_url', '')),
            ('gender', current_user_data.get('gender', ''))
        ]

        # 5. 写入OTS
        primary_key = [('email', self.email)]
        success, err = ots_put_row(
            USERS_TABLE,
            primary_key,
            update_columns,
            expect_exist=RowExistenceExpectation.IGNORE
        )
        if not success:
            logger.error(f"密码更新失败: OTS写入异常（email={self.email}, err={err}）")
            return False, str(err)

        # 6. 刷新实例密码字段
        self.password = new_hashed_pw
        self.updated_at = current_timestamp

        logger.info(f"密码更新成功: email={self.email}（其他核心字段已保留）")
        return True, None

    @classmethod
    def create_admin(cls):
        """创建默认管理员（确保核心字段完整，用于初始系统管理）"""
        from config import ADMIN_EMAIL, ADMIN_DEFAULT_PASSWORD  # 从配置读取管理员信息
        if not ADMIN_EMAIL or not ADMIN_DEFAULT_PASSWORD:
            logger.error("管理员创建失败: 配置中缺少ADMIN_EMAIL或ADMIN_DEFAULT_PASSWORD")
            return False, "管理员配置缺失"

        # 检查管理员是否已存在
        existing_admin = cls.get_by_email(ADMIN_EMAIL)
        if existing_admin:
            logger.info(f"管理员创建跳过: 已存在（email={ADMIN_EMAIL}）")
            return True, "管理员已存在"

        # 密码哈希处理
        hashed_pw = hash_password(ADMIN_DEFAULT_PASSWORD)
        if not hashed_pw:
            logger.error("管理员创建失败: 密码哈希生成异常")
            return False, "密码处理异常"

        # 组装管理员数据（角色为admin，默认已验证）
        user_id = str(uuid.uuid4())
        current_timestamp = int(time.time())
        admin_data = {
            'email': ADMIN_EMAIL,
            'user_id': user_id,
            'password': hashed_pw,
            'created_at': current_timestamp,
            'updated_at': current_timestamp,
            'role': 'admin',  # 管理员角色
            'is_verified': True,  # 默认已验证
            'display_name': '管理员',
            'avatar_url': "https://api.dicebear.com/7.x/initials/svg?seed=Admin",
            'gender': ''
        }

        # 写入OTS
        primary_key = [('email', ADMIN_EMAIL)]
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
            logger.error(f"管理员创建失败: OTS写入异常（err={err}）")
            return False, str(err)

        logger.info(f"默认管理员创建成功: email={ADMIN_EMAIL}, user_id={user_id}")
        return True, None

    # -------------------------- 用户关联操作（收藏、浏览历史）--------------------------
    def add_favorite(self, book_id):
        """添加图书收藏（依赖user_id，确保非空）"""
        if not self.user_id:
            logger.error(f"收藏添加失败: user_id为空（email={self.email}）")
            return False, "用户ID缺失，无法收藏"
        # 延迟导入避免循环依赖
        from models.favorite import Favorite
        return Favorite.create(self.user_id, book_id)

    def remove_favorite(self, book_id):
        """移除图书收藏（依赖user_id，确保非空）"""
        if not self.user_id:
            logger.error(f"收藏移除失败: user_id为空（email={self.email}）")
            return False, "用户ID缺失，无法取消收藏"
        from models.favorite import Favorite
        return Favorite.delete_by_user_book(self.user_id, book_id)

    def check_favorite(self, book_id):
        """检查图书是否已收藏（依赖user_id，确保非空）"""
        if not self.user_id:
            logger.error(f"收藏检查失败: user_id为空（email={self.email}）")
            return False
        from models.favorite import Favorite
        return Favorite.exists(self.user_id, book_id)

    def get_favorites(self):
        """获取用户收藏列表（依赖user_id，确保非空）"""
        if not self.user_id:
            logger.error(f"收藏列表获取失败: user_id为空（email={self.email}）")
            return []
        from models.favorite import Favorite
        return Favorite.get_by_user_id(self.user_id)

    def add_view_history(self, book_id):
        """添加浏览历史（依赖user_id，确保非空）"""
        if not self.user_id:
            logger.error(f"浏览历史添加失败: user_id为空（email={self.email}）")
            return False, "用户ID缺失，无法记录历史"
        from models.view_history import ViewHistory
        return ViewHistory.create(self.user_id, book_id)

    def get_view_history(self):
        """获取用户浏览历史（依赖user_id，确保非空）"""
        if not self.user_id:
            logger.error(f"浏览历史获取失败: user_id为空（email={self.email}）")
            return []
        from models.view_history import ViewHistory
        return ViewHistory.get_by_user_id(self.user_id)
