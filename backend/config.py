import os
import logging

# 配置日志（与原代码一致）
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def get_env(key, default=None):
    """读取环境变量，不存在时打印错误日志"""
    value = os.getenv(key, default)
    if value is None:
        logger.error(f"环境变量 {key} 未设置!")
    return value


# -------------------------- 核心配置项（修正Redis语法+统一规范）--------------------------
# 表格存储（OTS）配置
OTS_INSTANCE_NAME = get_env('OTS_INSTANCE_NAME', 'xxxxxxxxxxxxxxxx')
OTS_ENDPOINT = get_env('OTS_ENDPOINT', 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
OTS_TABLE_NAME = get_env('OTS_TABLE_NAME', 'Books')
USERS_TABLE = get_env('USERS_TABLE', 'Users')
VERIFICATION_CODES_TABLE = get_env('VERIFICATION_CODES_TABLE', 'VerificationCodes')
BORROW_RECORDS_TABLE = get_env('BORROW_RECORDS_TABLE', 'BorrowRecords')
FAVORITES_TABLE = get_env('FAVORITES_TABLE', 'Favorites')
VIEW_HISTORY_TABLE = get_env('VIEW_HISTORY_TABLE', 'ViewHistory')
ANNOUNCEMENTS_TABLE = get_env('ANNOUNCEMENTS_TABLE', 'Announcements')
COMMENTS_TABLE = get_env('COMMENTS_TABLE', 'Comments')
RESERVATIONS_TABLE = get_env('RESERVATIONS_TABLE', 'Reservations')

# 对象存储（OSS）配置
OSS_BUCKET_NAME = get_env('OSS_BUCKET_NAME', 'book-mgmt-images')
OSS_ENDPOINT = get_env('OSS_ENDPOINT', 'xxxxxxxxxxxxxxxxxxxxxxxxxxx').strip()

# Redis缓存配置（核心修正：加字符串引号+统一用get_env读取）
REDIS_HOST = get_env('REDIS_HOST', 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')  # 加引号，修正语法
REDIS_PORT = int(get_env('REDIS_PORT', '6379'))  # 统一用get_env，保持整数类型
REDIS_PASSWORD = get_env('REDIS_PASSWORD', 'FluxLib_Redis_2024')  # 加引号，敏感信息建议通过环境变量传入
REDIS_DB = int(get_env('REDIS_DB', '0'))  # 统一用get_env，保持整数类型

# 阿里云密钥（与原代码一致，含空值校验）
ALIYUN_ACCESS_KEY = get_env('ALIYUN_ACCESS_KEY', 'xxxxxxxxxxxxxxxxxxxxxxxxxx')
ALIYUN_ACCESS_SECRET = get_env('ALIYUN_ACCESS_SECRET', 'xxxxxxxxxxxxxxxxxxxxxxxxxxxx')
ALIYUN_REGION = get_env('ALIYUN_REGION', 'cn-hangzhou')

# 邮箱配置
EMAIL_HOST = get_env('EMAIL_HOST', 'smtp.qq.com')
EMAIL_PORT = int(get_env('EMAIL_PORT', '465'))
EMAIL_USER = get_env('EMAIL_USER', 'xxxxxxxxxxxxxxxxxxxx@qq.com')
EMAIL_PASSWORD = get_env('EMAIL_PASSWORD', 'xxxxxxxxxxxxxxxxxxxxx')

# AI配置（DeepSeek）
DEEPSEEK_API_KEY = get_env('DEEPSEEK_API_KEY', 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxx')

# 管理员配置
ADMIN_CODE = get_env('ADMIN_CODE', '10N086')  # 管理员码
ADMIN_EMAIL = "admin@bookmgmt.com"  # 默认管理员邮箱（原代码create_admin_user函数中）
ADMIN_DEFAULT_PASSWORD = "Admin@1234"  # 默认管理员密码（原代码create_admin_user函数中）

# 应用配置
PORT = int(os.getenv('FC_SERVER_PORT', '9000'))  # 服务端口
CORS_ALLOW_ORIGIN = '*'  # 跨域允许源（与原代码一致）