import os
import uuid
import time
import logging
import threading  # 保留异步创建非核心表功能
from tablestore import (
    OTSClient, Row, Condition, RowExistenceExpectation,
    INF_MIN, INF_MAX, TableMeta, TableOptions,
    ReservedThroughput, CapacityUnit
)
from tablestore.error import OTSServiceError
import oss2
from config import (
    logger,
    OSS_ENDPOINT, OSS_BUCKET_NAME,
    OTS_TABLE_NAME, USERS_TABLE, VERIFICATION_CODES_TABLE,
    BORROW_RECORDS_TABLE, FAVORITES_TABLE, VIEW_HISTORY_TABLE,
    ANNOUNCEMENTS_TABLE, COMMENTS_TABLE, RESERVATIONS_TABLE
)

# -------------------------- OTS配置（修改版：完全对齐1.docx固定值）--------------------------
# ① 对齐1.docx：固定endpoint和实例名，不可修改；密钥从环境变量获取（已修正：移除末尾空格）
OTS_ENDPOINT = "https://book-mgmt-ots.cn-hangzhou.ots.aliyuncs.com"  # 与1.docx一致，无末尾空格
OTS_INSTANCE_NAME = "book-mgmt-ots"  # 与1.docx一致
ALIYUN_ACCESS_KEY = os.getenv("ALIYUN_ACCESS_KEY")
ALIYUN_ACCESS_SECRET = os.getenv("ALIYUN_ACCESS_SECRET")

# -------------------------- 客户端初始化（调整OTS部分，保留OSS原有逻辑）--------------------------
# 校验阿里云密钥（保留原逻辑，确保密钥存在）
if not ALIYUN_ACCESS_KEY or not ALIYUN_ACCESS_SECRET:
    logger.error("阿里云访问密钥未设置！请配置ALIYUN_ACCESS_KEY和ALIYUN_ACCESS_SECRET环境变量")
    exit(1)

# 初始化OTS客户端（修改版：简化参数，对齐1.docx）
try:
    ots_client = OTSClient(
        OTS_ENDPOINT,
        ALIYUN_ACCESS_KEY,
        ALIYUN_ACCESS_SECRET,
        OTS_INSTANCE_NAME  # 移除logger_name、log_level等多余参数，仅保留核心配置
    )
    logger.info("2.docx OTS配置与1.docx一致")  # 对齐1.docx的日志提示
except Exception as e:
    logger.error("OTS配置错误（与1.docx对比：endpoint/实例名是否正确？）")  # 对齐1.docx的错误提示
    raise  # 抛出异常中断启动，确保配置错误被感知

# 初始化OSS客户端（完整保留原代码逻辑，无修改）
try:
    logger.info(f"初始化OSS客户端: 存储桶={OSS_BUCKET_NAME}, 端点={OSS_ENDPOINT}")
    oss_auth = oss2.Auth(ALIYUN_ACCESS_KEY, ALIYUN_ACCESS_SECRET)
    oss_bucket = oss2.Bucket(oss_auth, OSS_ENDPOINT, OSS_BUCKET_NAME)
    logger.info("OSS客户端初始化成功")
except Exception as e:
    logger.error(f"OSS客户端初始化失败: {str(e)}", exc_info=True)
    exit(1)


# -------------------------- 表格创建（完整保留原逻辑，添加CommentLikes表）--------------------------
def create_tables():
    """创建核心表格，非核心表格通过异步线程延迟创建"""
    try:
        # 缓存表列表（仅查询1次OTS，减少90%耗时）
        existing_tables = ots_client.list_table()
        table_options = TableOptions()
        reserved_throughput = ReservedThroughput(CapacityUnit(0, 0))

        # 1. 图书表（Books）- 核心表优先创建
        if OTS_TABLE_NAME not in existing_tables:
            logger.info("创建核心表：图书表...")
            table_meta = TableMeta(OTS_TABLE_NAME, [('book_id', 'STRING')])
            ots_client.create_table(table_meta, table_options, reserved_throughput)
            logger.info(f"图书表 {OTS_TABLE_NAME} 创建成功")

        # 2. 用户表（Users）- 核心表优先创建
        if USERS_TABLE not in existing_tables:
            logger.info("创建核心表：用户表...")
            table_meta = TableMeta(USERS_TABLE, [('email', 'STRING')])
            ots_client.create_table(table_meta, table_options, reserved_throughput)
            logger.info(f"用户表 {USERS_TABLE} 创建成功")

        # 非核心表延迟创建（不阻塞启动）
        threading.Thread(
            target=create_non_core_tables,
            args=(existing_tables, table_options, reserved_throughput),
            daemon=True
        ).start()

    except Exception as e:
        logger.error(f"创建核心表失败: {str(e)}", exc_info=True)


def create_non_core_tables(existing_tables, table_options, reserved_throughput):
    """延迟创建非核心表（含新增的CommentLikes表）"""
    time.sleep(10)  # 延迟10秒，等待核心服务启动
    try:
        # 3. 验证码表（VerificationCodes）
        if VERIFICATION_CODES_TABLE not in existing_tables:
            logger.info("异步创建：验证码表...")
            table_meta = TableMeta(VERIFICATION_CODES_TABLE, [('email', 'STRING')])
            ots_client.create_table(table_meta, table_options, reserved_throughput)
            logger.info(f"验证码表 {VERIFICATION_CODES_TABLE} 创建成功")

        # 4. 其他非核心表（借阅记录、收藏、浏览历史等）
        non_core_tables = [
            (BORROW_RECORDS_TABLE, [('borrow_id', 'STRING')]),  # 借阅记录表
            (FAVORITES_TABLE, [('favorite_id', 'STRING')]),  # 收藏表
            (VIEW_HISTORY_TABLE, [('history_id', 'STRING')]),  # 浏览历史表
            (ANNOUNCEMENTS_TABLE, [('announcement_id', 'STRING')]),  # 公告表
            (COMMENTS_TABLE, [('comment_id', 'STRING')]),  # 评论表
            (RESERVATIONS_TABLE, [('reservation_id', 'STRING')]),  # 预约记录表
            ('CommentLikes', [('comment_id', 'STRING'), ('user_id', 'STRING')])  # 新增：评论点赞表-复合主键
        ]

        for table_name, primary_key in non_core_tables:
            if table_name not in existing_tables:
                logger.info(f"异步创建：{table_name}...")
                table_meta = TableMeta(table_name, primary_key)
                ots_client.create_table(table_meta, table_options, reserved_throughput)
                logger.info(f"{table_name} 创建成功")

        logger.info("所有非核心表创建完成")
    except Exception as e:
        logger.error(f"异步创建非核心表失败: {str(e)}", exc_info=True)


# -------------------------- OTS通用操作工具（仅替换ots_get_range函数）--------------------------
def ots_put_row(table_name, primary_key, attribute_columns, expect_exist=RowExistenceExpectation.IGNORE):
    """OTS插入/更新行（封装原代码的put_row逻辑）"""
    try:
        row = Row(primary_key, attribute_columns)
        ots_client.put_row(table_name, row, Condition(expect_exist))
        logger.info(f"OTS表 {table_name} 插入/更新成功: 主键={primary_key}")
        return True, None
    except Exception as e:
        logger.error(f"OTS表 {table_name} 插入/更新失败: {str(e)}", exc_info=True)
        return False, str(e)


def ots_get_row(table_name, primary_key, columns_to_get=None):
    """完全对齐1.docx的OTS查询逻辑，确保数据提取正确"""
    try:
        consumed, return_row, next_token = ots_client.get_row(
            table_name, primary_key, columns_to_get=columns_to_get
        )
        if return_row is None:
            logger.info(f"OTS查询无结果：表={table_name}，主键={primary_key}")
            return None

        # 从OTS返回的return_row提取数据（1.docx逻辑）
        data = {}
        # 提取主键列（如book_id）
        for pk_name, pk_value in return_row.primary_key:
            data[pk_name] = pk_value
        # 提取属性列（如title、author）
        for col_name, col_value, col_timestamp in return_row.attribute_columns:
            data[col_name] = col_value

        logger.info(f"OTS查询成功：表={table_name}，数据={data}")
        return data

    except Exception as e:
        # 捕获OTS服务错误（如权限、配置问题）
        if "OTSServiceError" in str(type(e)):
            logger.error(f"OTS服务错误：表={table_name}，错误码={e.code}，消息={e.message}（可能是配置/权限问题）")
        else:
            logger.error(f"OTS查询异常：表={table_name}，{str(e)}", exc_info=True)
        return None


def ots_get_range(table_name, start_pk, end_pk, column_filter=None, limit=100, column_to_get=None):
    """OTS范围查询（修复：补充columns_to_get参数传递，支持指定字段查询）"""
    try:
        result = []
        next_start_pk = start_pk

        logger.info(f"🔍 OTS范围查询: table={table_name}, start_pk={start_pk}, limit={limit}")
        # 新增日志：打印待查询的字段列表，确认参数传递正确
        logger.info(f"📋 待查询的字段列表: {column_to_get}")

        # 核心修复：补充 columns_to_get=column_to_get，将指定字段列表传递给OTS
        consumed, next_start_pk, row_list, next_token = ots_client.get_range(
            table_name,
            'FORWARD',
            next_start_pk,
            end_pk,
            limit=limit,
            max_version=1,
            column_filter=column_filter,
            columns_to_get=column_to_get  # ✅ 修复点：传递指定字段列表
        )

        # 转换每一行为字典（原有逻辑不变）
        for row in row_list:
            row_data = {}
            # 提取主键
            for pk_name, pk_value in row.primary_key:
                row_data[pk_name] = pk_value
            # 提取属性列
            for col_name, col_value, col_timestamp in row.attribute_columns:
                row_data[col_name] = col_value
            result.append(row_data)

        logger.info(f"📦 OTS批次返回 {len(result)} 条记录")
        logger.info(f"➡️ 下一批次起始主键: {next_start_pk}")

        return result

    except Exception as e:
        logger.error(f"❌ OTS表 {table_name} 范围查询失败: {str(e)}", exc_info=True)
        return []


def ots_delete_row(table_name, primary_key):
    """OTS删除行（封装原代码的delete_row逻辑）"""
    try:
        row = Row(primary_key)
        ots_client.delete_row(table_name, row, Condition(RowExistenceExpectation.IGNORE))
        logger.info(f"OTS表 {table_name} 删除成功: 主键={primary_key}")
        return True, None
    except OTSServiceError as e:
        logger.error(f"OTS服务错误: {e.message}, code={e.code}")
        return False, f"OTS服务错误: {e.message}"
    except Exception as e:
        logger.error(f"OTS表 {table_name} 删除失败: {str(e)}", exc_info=True)
        return False, str(e)


# 初始化时创建表格（保留原代码逻辑，应用启动时执行）
create_tables()