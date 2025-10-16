# 10.12.docx 中修复后的完整 utils/storage.py（仅改 sign_url 参数名，其他逻辑不变）
import uuid
from config import logger, OSS_BUCKET_NAME, OSS_ENDPOINT, ALIYUN_ACCESS_KEY, ALIYUN_ACCESS_SECRET
import oss2
import urllib.parse  # 用于中文/特殊字符 URL 编码

# -------------------------- OSS 客户端初始化（兼容旧版 oss2，无 exists() 方法）--------------------------
try:
    logger.info(f"📦 初始化 OSS 客户端: 存储桶={OSS_BUCKET_NAME}, 端点={OSS_ENDPOINT}")

    # 1. 校验阿里云密钥有效性
    if not ALIYUN_ACCESS_KEY or not ALIYUN_ACCESS_SECRET:
        raise ValueError("阿里云密钥未配置（ALIYUN_ACCESS_KEY/ALIYUN_ACCESS_SECRET 为空）")

    # 2. 初始化 OSS Auth 实例（旧版 oss2 兼容）
    oss_auth = oss2.Auth(ALIYUN_ACCESS_KEY, ALIYUN_ACCESS_SECRET)

    # 3. 初始化 Bucket 实例（旧版 oss2 无 exists() 方法，直接创建）
    oss_bucket = oss2.Bucket(oss_auth, OSS_ENDPOINT, OSS_BUCKET_NAME)
    logger.info(f"✅ OSS 客户端初始化成功（存储桶: {OSS_BUCKET_NAME}）")

except Exception as e:
    logger.error(f"❌ OSS 客户端初始化失败: {str(e)}", exc_info=True)
    raise  # 初始化失败终止，避免后续隐性错误


def generate_presigned_url(file_name, file_type):
    """
    生成 OSS 预签名 URL（修复 sign_url 参数名，兼容旧版 oss2）
    参数:
        file_name: 原始文件名（支持中文/特殊字符）
        file_type: 文件 MIME 类型（如 image/jpeg、image/png）
    返回:
        包含预签名上传 URL、访问 URL 的字典
    """
    try:
        # 1. 参数校验
        if not file_name or not file_type:
            logger.error("❌ 生成预签名 URL 失败: 缺少 file_name 或 file_type")
            return {
                'statusCode': 400,
                'body': {
                    'error': 'Missing file_name or file_type',
                    'detail': 'file_name（文件名）和 file_type（文件类型）为必填项'
                }
            }

        # 2. 处理中文/特殊字符文件名（核心修复：URL 编码）
        encoded_file_name = urllib.parse.quote(file_name, safe='')  # 编码所有特殊字符（如"熊猫.jpg"→"%E7%86%8A%E7%8C%AB.jpg"）
        unique_name = f"{uuid.uuid4()}-{encoded_file_name}"  # 生成唯一文件名，避免重复
        object_path = f"book-covers/{unique_name}"  # OSS 存储路径（固定 book-covers 目录）
        logger.info(f"📂 生成 OSS 存储路径: {object_path}")

        # 3. 设置文件 Content-Type（确保与上传文件一致）
        headers = {'Content-Type': file_type}
        logger.info(f"📄 文件 Content-Type: {file_type}")

        # 4. 生成预签名 PUT URL（关键修复：expire → expires，适配旧版 oss2）
        presigned_url = oss_bucket.sign_url(
            method='PUT',
            key=object_path,
            expires=3600,  # 旧版 oss2 用 expires（带 s），有效期 3600 秒
            headers=headers
        )
        logger.info(f"✅ 预签名上传 URL: {presigned_url}")

        # 5. 生成 OSS 图片访问 URL（用于前端渲染）
        # 处理端点格式：去除 http/https 前缀
        endpoint = OSS_ENDPOINT.replace('https://', '').replace('http://', '').strip()
        # 编码存储路径，确保 URL 合法性
        encoded_object_path = urllib.parse.quote(object_path, safe='')
        # 拼接标准 OSS 访问 URL（格式：https://BucketName.Endpoint/ObjectPath）
        access_url = f"https://{OSS_BUCKET_NAME}.{endpoint}/{encoded_object_path}"
        logger.info(f"✅ 图片访问 URL: {access_url}")

        # 6. 返回结果（兼容前端原有调用逻辑）
        return {
            'statusCode': 200,
            'body': {
                'presigned_url': presigned_url,
                'access_url': access_url,
                'object_path': object_path,  # 新增：便于后端排查 OSS 路径
                'encoded_file_name': encoded_file_name  # 新增：编码后的文件名
            }
        }

    # OSS 服务端错误处理（如权限不足、Bucket 不存在等，旧版 oss2 兼容）
    except oss2.exceptions.OssError as e:
        logger.error(
            f"❌ OSS 服务错误: 错误码={e.code}, 信息={e.message}, "
            f"RequestId={e.request_id}, HostId={e.host_id}",
            exc_info=True
        )
        return {
            'statusCode': 500,
            'body': {
                'error': 'OSS Service Error',
                'detail': f"错误码: {e.code}, 详情: {e.message}",
                'request_id': e.request_id  # 用于阿里云工单排查
            }
        }
    # 通用异常处理
    except Exception as e:
        logger.error(f"❌ 生成预签名 URL 失败: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': {
                'error': 'Failed to generate presigned URL',
                'detail': str(e)
            }
        }