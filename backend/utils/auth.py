import hashlib
import time
from tablestore import (  # 补充导入INF_MIN、INF_MAX，解决范围查询的常量引用问题
    SingleColumnCondition, ComparatorType, INF_MIN, INF_MAX
)
from config import logger, USERS_TABLE, ADMIN_CODE
from utils.database import ots_get_row, ots_get_range


def hash_password(password):
    """密码SHA256哈希（与原代码完全一致）"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def get_user_id_by_token(token):
    """通过Token获取用户ID（原代码逻辑：扫描用户表匹配user_id）"""
    try:
        # 条件：user_id等于token
        condition = SingleColumnCondition(
            'user_id',
            token,
            ComparatorType.EQUAL
        )
        # 范围查询用户表（主键email从最小到最大，INF_MIN/INF_MAX已正常导入）
        user_list = ots_get_range(
            USERS_TABLE,
            start_pk=[('email', INF_MIN)],  # 已导入INF_MIN，可正常使用
            end_pk=[('email', INF_MAX)],    # 已导入INF_MAX，可正常使用
            column_filter=condition,
            limit=1
        )
        if user_list:
            user = user_list[0]
            logger.info(f"通过Token找到用户: email={user.get('email')}, user_id={user.get('user_id')}")
            return user.get('user_id')
        logger.warning(f"未找到匹配Token的用户: token={token}")
        return None
    except Exception as e:
        logger.error(f"通过Token获取用户ID失败: {str(e)}", exc_info=True)
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
    """通过用户ID获取用户信息（原代码逻辑：扫描用户表匹配user_id）"""
    try:
        # 条件：user_id等于指定值
        condition = SingleColumnCondition(
            'user_id',
            user_id,
            ComparatorType.EQUAL
        )
        # 范围查询用户表（INF_MIN/INF_MAX已正常导入）
        user_list = ots_get_range(
            USERS_TABLE,
            start_pk=[('email', INF_MIN)],  # 已导入INF_MIN，可正常使用
            end_pk=[('email', INF_MAX)],    # 已导入INF_MAX，可正常使用
            column_filter=condition,
            limit=1
        )
        if user_list:
            user = user_list[0]
            logger.info(f"通过ID找到用户: email={user.get('email')}, role={user.get('role')}")
            # 确保返回字段完整（与原代码一致）
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
        logger.error(f"通过用户ID获取用户信息失败: {str(e)}", exc_info=True)
        return None


def get_user_by_email(email):
    """通过邮箱获取用户信息（原代码get_user函数逻辑）"""
    try:
        user = ots_get_row(USERS_TABLE, primary_key=[('email', email)])
        if not user:
            logger.info(f"用户不存在: email={email}")
            return None
        logger.info(f"通过邮箱获取用户成功: email={email}")
        return user
    except Exception as e:
        logger.error(f"通过邮箱获取用户失败: {str(e)}", exc_info=True)
        return None