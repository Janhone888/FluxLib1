import smtplib
import random
import time
from email.mime.text import MIMEText
from tablestore import RowExistenceExpectation  # 显式导入枚举，确保ots_put_row正常使用
from config import logger, EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD
from utils.database import ots_put_row, VERIFICATION_CODES_TABLE


def send_verification_code(email, code_type='register'):
    """发送验证码（支持不同类型：register-注册、reset_password-密码重置）"""
    # 生成6位数字验证码
    code = str(random.randint(100000, 999999))
    logger.info(f"🔐 开始发送{code_type}类型验证码: email={email}, code={code}")

    # 验证码有效期：5分钟（300秒），计算过期时间戳
    expire_time = int(time.time()) + 300
    current_time = int(time.time())

    # 1. 存储验证码到OTS
    primary_key = [('email', email)]
    attribute_columns = [
        ('code', code),
        ('type', code_type),
        ('expire_time', expire_time),
        ('created_at', current_time),
        ('updated_at', current_time)
    ]
    success, err = ots_put_row(
        VERIFICATION_CODES_TABLE,
        primary_key,
        attribute_columns,
        expect_exist=RowExistenceExpectation.IGNORE
    )
    if not success:
        logger.error(f"❌ 存储{code_type}类型验证码失败: {err}")
        return False

    logger.info(f"✅ 验证码存储成功，开始发送邮件...")

    # 2. 根据验证码类型，组装不同的邮件主题和内容
    if code_type == 'reset_password':
        email_subject = 'FluxLib泛集库密码重置验证码'
        email_content = f"您正在执行FluxLib泛集库的密码重置操作，您的验证码是: {code}\n验证码5分钟内有效，请勿向他人泄露。"
    else:  # 默认register类型
        email_subject = 'FluxLib泛集库注册验证码'
        email_content = f"欢迎注册FluxLib泛集库，您的注册验证码是: {code}\n验证码5分钟内有效，请尽快完成注册验证。"

    # 3. 发送邮件
    try:
        logger.info(f"📧 准备发送邮件: 发件人={EMAIL_USER}, 收件人={email}")
        logger.info(f"📧 SMTP配置: host={EMAIL_HOST}, port={EMAIL_PORT}")

        # 构造MIMEText邮件对象
        message = MIMEText(email_content, 'plain', 'utf-8')
        message['Subject'] = email_subject
        message['From'] = EMAIL_USER
        message['To'] = email

        # 建立SMTP连接
        logger.info("🔌 尝试建立SMTP连接...")
        if EMAIL_PORT == 465:
            # SSL连接
            smtp_server = smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT, timeout=30)
        else:
            # TLS连接
            smtp_server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=30)
            smtp_server.starttls()

        logger.info("✅ SMTP连接建立成功，开始登录...")

        # 登录SMTP服务器
        smtp_server.login(EMAIL_USER, EMAIL_PASSWORD)
        logger.info("✅ SMTP登录成功，开始发送邮件...")

        # 发送邮件
        smtp_server.sendmail(EMAIL_USER, [email], message.as_string())
        logger.info("✅ 邮件发送成功！")

        # 关闭连接
        smtp_server.quit()
        logger.info(f"🎉 {code_type}类型验证码邮件发送完成: 收件人={email}")

        return True

    except smtplib.SMTPException as e:
        logger.error(f"❌ SMTP协议错误: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ 发送邮件时发生未知错误: {str(e)}", exc_info=True)
        return False


def send_reservation_confirmation(email, book_info, reserve_data):
    """发送图书预约确认邮件（完全沿用原代码逻辑，无修改）"""
    try:
        # 格式化预计归还日期（时间戳转成"YYYY-MM-DD"格式）
        expected_return_date = time.strftime(
            '%Y-%m-%d',
            time.localtime(reserve_data['expected_return_date'])
        )

        # 组装预约确认邮件内容
        email_content = f"""
        您好！您的FluxLib泛集库图书预约已成功创建，详情如下：

        【图书信息】
        书名：{book_info.get('title', '未知书名')}
        作者：{book_info.get('author', '未知作者')}
        ISBN：{book_info.get('isbn', '未知ISBN')}（如存在）

        【预约详情】
        预约提交时间：{reserve_data.get('reserve_date', '未知时间')}
        预约时间段：{reserve_data.get('time_slot', '未知时段')}
        计划借阅天数：{reserve_data.get('days', '未知天数')}天
        预计归还日期：{expected_return_date}

        【温馨提示】
        1. 请在预约时间段内到图书馆服务台领取图书，逾期未领将自动取消预约；
        2. 领取时请携带有效证件（如身份证/学生证），以便核对身份；
        3. 若无法按时领取，请提前在系统中取消预约，避免影响您的预约权限。

        感谢您使用FluxLib泛集库的服务！
        """

        # 构造邮件对象
        message = MIMEText(email_content, 'plain', 'utf-8')
        message['Subject'] = 'FluxLib泛集库图书预约确认通知'
        message['From'] = EMAIL_USER
        message['To'] = email

        # 发送邮件
        with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT) as smtp_server:
            smtp_server.login(EMAIL_USER, EMAIL_PASSWORD)
            smtp_server.sendmail(EMAIL_USER, [email], message.as_string())

        logger.info(f"图书预约确认邮件发送成功: 收件人={email}, 预约图书={book_info.get('title')}")
        return True
    except Exception as e:
        logger.error(
            f"发送图书预约确认邮件失败: 收件人={email}, 错误信息={str(e)}",
            exc_info=True
        )
        return False