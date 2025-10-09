import hashlib
import time
from tablestore import (
    SingleColumnCondition, ComparatorType, INF_MIN, INF_MAX
)
from config import logger, USERS_TABLE, ADMIN_CODE
from utils.database import ots_get_row, ots_get_range
from utils.redis_client import redis_client  # 导入Redis客户端


def hash_password(password):
    """密码SHA256哈希（与原代码完全一致）"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def get_user_id_by_token(token):
    """通过Token获取用户ID - Redis优化版"""
    try:
        # 1. 先查Redis缓存
        cached_user_id = redis_client.get_user_by_token(token)
        if cached_user_id:
            logger.info(f"✅ Redis缓存命中: token={token}")
            return cached_user_id

        # 2. 缓存未命中，查询OTS
        condition = SingleColumnCondition('user_id', token, ComparatorType.EQUAL)
        user_list = ots_get_range(
            USERS_TABLE,
            start_pk=[('email', INF_MIN)],
            end_pk=[('email', INF_MAX)],
            column_filter=condition,
            limit=1
        )

        if user_list:
            user = user_list[0]
            user_id = user.get('user_id')

            # 3. 写入Redis缓存
            redis_client.set_token_user(token, user_id)
            redis_client.set_user(user_id, user)

            logger.info(f"✅ OTS查询成功并缓存: user_id={user_id}")
            return user_id

        logger.warning(f"未找到匹配Token的用户: token={token}")
        return None
    except Exception as e:
        logger.error(f"❌ 获取用户ID失败: {str(e)}", exc_info=True)
        return None


def get_current_user_id(headers):
    """从请求头获取当前用户ID（原代码逻辑：解析Bearer Token）"""
    auth_header = headers.get('Authorization', '')
    logger.info(f"Authorization header: '{auth_header}'")
    if auth_header.startswith('Bearer '):
        token = auth_header[7:]  # 提取Token（去掉"Bearer "前缀）
        logger.info(f"提取Token: {token}")
        user_id = get_user_id_by_token(token)
        if user_id:
            return user_id
        logger.warning("无效或过期的Token")
        return None
    logger.warning("Authorization头缺失或格式错误（需Bearer Token）")
    return None


def verify_admin_code(input_code):
    """验证管理员码（与原代码一致）"""
    if input_code == ADMIN_CODE:
        logger.info("管理员码验证成功")
        return True
    logger.warning(f"管理员码验证失败: 输入={input_code}, 正确={ADMIN_CODE}")
    return False


def get_user_by_id(user_id):
    """通过用户ID获取用户信息 - 增加Redis缓存优化"""
    try:
        # 1. 先查Redis缓存
        cached_user = redis_client.get_user(user_id)
        if cached_user:
            logger.info(f"✅ Redis缓存命中: user_id={user_id}")
            return {
                'email': cached_user.get('email'),
                'user_id': cached_user.get('user_id'),
                'password': cached_user.get('password'),
                'role': cached_user.get('role', 'user'),
                'display_name': cached_user.get('display_name'),
                'avatar_url': cached_user.get('avatar_url'),
                'gender': cached_user.get('gender', ''),
                'created_at': cached_user.get('created_at'),
                'updated_at': cached_user.get('updated_at')
            }

        # 2. 缓存未命中，查询OTS
        condition = SingleColumnCondition(
            'user_id',
            user_id,
            ComparatorType.EQUAL
        )
        user_list = ots_get_range(
            USERS_TABLE,
            start_pk=[('email', INF_MIN)],
            end_pk=[('email', INF_MAX)],
            column_filter=condition,
            limit=1
        )

        if user_list:
            user = user_list[0]

            # 3. 写入Redis缓存
            redis_client.set_user(user_id, user)

            logger.info(f"✅ OTS查询成功并缓存: user_id={user_id}")
            return {
                'email': user.get('email'),
                'user_id': user.get('user_id'),
                'password': user.get('password'),
                'role': user.get('role', 'user'),
                'display_name': user.get('display_name'),
                'avatar_url': user.get('avatar_url'),
                'gender': user.get('gender', ''),
                'created_at': user.get('created_at'),
                'updated_at': user.get('updated_at')
            }

        logger.warning(f"未找到用户: user_id={user_id}")
        return None
    except Exception as e:
        logger.error(f"❌ 通过用户ID获取用户信息失败: {str(e)}", exc_info=True)
        return None


def get_user_by_email(email):
    """通过邮箱获取用户信息 - 增加Redis缓存优化"""
    try:
        # 1. 先查Redis缓存
        cached_user = redis_client.get_user_by_email(email)
        if cached_user:
            logger.info(f"✅ Redis缓存命中: email={email}")
            return cached_user

        # 2. 缓存未命中，查询OTS
        user = ots_get_row(USERS_TABLE, primary_key=[('email', email)])

        if not user:
            logger.info(f"用户不存在: email={email}")
            return None

        # 3. 写入Redis缓存
        user_id = user.get('user_id')
        if user_id:
            redis_client.set_user(user_id, user)
            redis_client.set_user_by_email(email, user)

        logger.info(f"✅ OTS查询成功并缓存: email={email}")
        return user
    except Exception as e:
        logger.error(f"❌ 通过邮箱获取用户失败: {str(e)}", exc_info=True)
        return None