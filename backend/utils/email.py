import smtplib
import random
import time
from email.mime.text import MIMEText
from config import logger, EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD
from utils.database import ots_put_row, VERIFICATION_CODES_TABLE


def send_verification_code(email):
    """发送注册验证码（完全沿用原代码逻辑）"""
    # 生成6位验证码
    code = str(random.randint(100000, 999999))
    logger.info(f"为 {email} 生成验证码: {code}")
    # 5分钟后过期（300秒）
    expire_time = int(time.time()) + 300
    current_time = int(time.time())

    # 1. 存储验证码到OTS（原代码逻辑）
    primary_key = [('email', email)]
    attribute_columns = [
        ('code', code),
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
        logger.error(f"存储验证码失败: {err}")
        return False

    # 2. 发送邮件（原代码逻辑）
    try:
        message = MIMEText(f"欢迎来到FluxLib泛集库，您的验证码是: {code}，5分钟内有效。")
        message['Subject'] = 'FluxLib泛集库注册验证码'
        message['From'] = EMAIL_USER
        message['To'] = email

        with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT) as server:
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, [email], message.as_string())
        logger.info(f"验证码邮件发送成功: {email}")
        return True
    except Exception as e:
        logger.error(f"发送验证码邮件失败: {str(e)}", exc_info=True)
        return False


def send_reservation_confirmation(email, book_info, reserve_data):
    """发送预约确认邮件（完全沿用原代码逻辑）"""
    try:
        # 格式化归还日期（原代码逻辑：时间戳转字符串）
        expected_return_date = time.strftime(
            '%Y-%m-%d',
            time.localtime(reserve_data['expected_return_date'])
        )

        message = MIMEText(f"""
        您的图书预约已成功创建！
        图书信息:
        书名: {book_info.get('title', '未知')}
        作者: {book_info.get('author', '未知')}
        预约详情:
        预约日期: {reserve_data['reserve_date']}
        时间段: {reserve_data['time_slot']}
        借阅天数: {reserve_data['days']}
        预计归还日期: {expected_return_date}
        请按时到图书馆借阅图书。
        """)
        message['Subject'] = 'FluxLib泛集库图书预约确认'
        message['From'] = EMAIL_USER
        message['To'] = email

        with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT) as server:
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, [email], message.as_string())
        logger.info(f"预约确认邮件发送成功: {email}")
        return True
    except Exception as e:
        logger.error(f"发送预约确认邮件失败: {str(e)}", exc_info=True)
        return False