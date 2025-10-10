import time
from config import logger, VERIFICATION_CODES_TABLE
from utils.email import send_verification_code
from utils.auth import verify_admin_code, hash_password
from utils.database import ots_get_row
from models.user import User


def send_verification_email(email):
    """发送注册验证码（对应原代码handle_send_verification_code逻辑）"""
    if not email:
        logger.error("发送验证码失败: 缺少邮箱")
        return False, "邮箱是必填项"

    # 调用邮件工具发送注册验证码（默认类型为register）
    success = send_verification_code(email)
    if not success:
        return False, "发送验证码失败"
    return True, "验证码已发送至邮箱"


def verify_registration_code(email, code):
    """验证注册验证码（兼容原有逻辑，内部调用新的验证函数）"""
    return verify_code_with_type(email, code, 'register')


def verify_reset_code(email, code):
    """验证重置密码验证码（独立验证，不涉及密码重置）"""
    return verify_code_with_type(email, code, 'reset_password')


def verify_code_with_type(email, code, code_type='register'):
    """验证验证码（支持不同类型：register/reset_password）"""
    if not email or not code:
        logger.error("验证验证码失败: 邮箱或验证码为空")
        return False, "邮箱和验证码是必填项"

    # 从OTS获取验证码（包含类型字段）
    code_data = ots_get_row(
        VERIFICATION_CODES_TABLE,
        primary_key=[('email', email)],
        columns_to_get=['code', 'type', 'expire_time']  # 获取类型字段用于校验
    )
    if not code_data:
        logger.warning(f"验证码记录不存在: email={email}, type={code_type}")
        return False, "验证码错误或已过期"

    # 校验验证码类型是否匹配
    stored_type = code_data.get('type', 'register')  # 默认register保持向后兼容
    if stored_type != code_type:
        logger.warning(f"验证码类型不匹配: email={email}, 期望={code_type}, 实际={stored_type}")
        return False, "验证码类型错误"

    # 校验验证码内容和有效期
    stored_code = code_data.get('code')
    expire_time = code_data.get('expire_time', 0)
    current_time = int(time.time())

    if stored_code != code:
        logger.warning(f"验证码不匹配: email={email}, 输入={code}, 存储={stored_code}")
        return False, "验证码错误"

    if expire_time <= current_time:
        logger.warning(f"验证码已过期: email={email}, 过期时间={expire_time}, 当前时间={current_time}")
        return False, "验证码已过期"

    logger.info(f"验证码验证成功: email={email}, type={code_type}")
    return True, "验证码验证成功"


def register_user(email, password, code, gender=None):
    """用户注册（对应原代码register_user逻辑）"""
    # 1. 验证注册验证码（复用类型验证函数）
    verify_success, verify_msg = verify_code_with_type(email, code, 'register')
    if not verify_success:
        return False, verify_msg

    # 2. 检查用户是否已注册
    existing_user = User.get_by_email(email)
    if existing_user:
        return False, "该邮箱已注册"

    # 3. 创建用户（调用User模型）
    create_success, user_id = User.create_user(email, password, gender)
    if not create_success:
        return False, user_id  # user_id此时为错误信息

    return True, user_id


def login_user(email, password, admin_code=None):
    """用户登录（对应原代码login_user逻辑，含临时管理员权限）"""
    logger.info(f"登录请求: email={email}, 管理员码={admin_code}")

    # 1. 检查用户是否存在
    user = User.get_by_email(email)
    if not user:
        logger.warning(f"用户不存在: email={email}")
        return False, "用户不存在"

    # 2. 校验密码
    hashed_pw = hash_password(password)
    if user.password != hashed_pw:
        logger.warning(f"密码错误: email={email}")
        return False, "密码错误"

    # 3. 校验管理员码（临时管理员权限）
    is_temporary_admin = False
    if admin_code:
        if not verify_admin_code(admin_code):
            logger.warning(f"管理员码错误: email={email}, 输入={admin_code}")
            return False, "管理员码错误"
        is_temporary_admin = True
        logger.info(f"用户获取临时管理员权限: email={email}")

    # 4. 组装返回数据（与原代码一致）
    login_data = {
        'user_id': user.user_id,
        'email': email,
        'role': 'admin' if is_temporary_admin else user.role,
        'is_admin': is_temporary_admin,
        'is_temporary_admin': is_temporary_admin
    }
    logger.info(f"用户登录成功: email={email}, 角色={login_data['role']}")
    return True, login_data


def send_reset_password_code(email):
    """发送重置密码验证码（指定类型为reset_password）"""
    if not email:
        logger.error("发送重置密码验证码失败: 缺少邮箱")
        return False, "邮箱是必填项"

    # 检查邮箱是否已注册
    user = User.get_by_email(email)
    if not user:
        return False, "该邮箱未注册，请先注册账号"

    # 调用邮件工具发送验证码（明确指定类型为reset_password）
    success = send_verification_code(email, 'reset_password')
    if not success:
        return False, "发送验证码失败"
    return True, "验证码已发送至邮箱"


def reset_password(email, code, new_password):
    """重置密码（使用类型验证确保安全性）"""
    if not email or not code or not new_password:
        logger.error("重置密码失败: 邮箱、验证码或新密码为空")
        return False, "邮箱、验证码和新密码是必填项"

    # 验证验证码（明确指定类型为reset_password）
    verify_success, verify_msg = verify_code_with_type(email, code, 'reset_password')
    if not verify_success:
        return False, verify_msg

    # 获取用户并更新密码
    user = User.get_by_email(email)
    if not user:
        return False, "用户不存在"

    success, err = user.update_password(new_password)
    if not success:
        return False, err

    logger.info(f"重置密码成功: email={email}")
    return True, "密码重置成功"