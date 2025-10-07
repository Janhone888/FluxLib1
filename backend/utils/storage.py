import uuid
from config import logger, OSS_BUCKET_NAME, OSS_ENDPOINT
from utils.database import oss_bucket


def generate_presigned_url(file_name, file_type):
    """生成OSS预签名URL（完全沿用原代码逻辑）"""
    try:
        if not file_name or not file_type:
            logger.error("生成预签名URL失败：缺少file_name或file_type")
            return {
                'statusCode': 400,
                'body': {'error': 'Missing file_name or file_type'}
            }

        # 生成唯一文件名（原代码逻辑：uuid+原始文件名）
        unique_name = f"{uuid.uuid4()}-{file_name}"
        object_path = f"book-covers/{unique_name}"  # 存储路径与原代码一致
        headers = {'Content-Type': file_type}

        # 生成3600秒有效期的PUT预签名URL
        presigned_url = oss_bucket.sign_url('PUT', object_path, 3600, headers=headers)

        # 生成访问URL（原代码格式：https://bucket.endpoint/path）
        endpoint = OSS_ENDPOINT.replace('https://', '').replace('http://', '')
        access_url = f"https://{OSS_BUCKET_NAME}.{endpoint}/{object_path}"

        logger.info(f"生成预签名URL成功: object_path={object_path}, access_url={access_url}")
        return {
            'statusCode': 200,
            'body': {
                'presigned_url': presigned_url,
                'access_url': access_url
            }
        }
    except Exception as e:
        logger.error(f"生成预签名URL失败: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': {
                'error': '生成预签名URL失败',
                'detail': str(e)
            }
        }