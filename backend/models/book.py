import uuid
import time
from tablestore import (
    SingleColumnCondition, ComparatorType, CompositeColumnCondition, LogicalOperator,
    INF_MIN, INF_MAX, RowExistenceExpectation
)
from config import logger, OTS_TABLE_NAME, BORROW_RECORDS_TABLE
from utils.database import ots_put_row, ots_get_row, ots_get_range, ots_delete_row
from models.borrow import Borrow  # 确保借阅模型关联正确


class Book:
    """图书数据模型（对应Books表，与原版字段、逻辑完全对齐）"""

    def __init__(self, data):
        """初始化图书对象（严格保留原版所有字段及默认值）"""
        self.book_id = data.get('book_id')  # 主键（必传）
        self.title = data.get('title', '')  # 书名（必填）
        self.author = data.get('author', '')  # 作者（默认空）
        self.publisher = data.get('publisher', '')  # 出版社（默认空）
        self.isbn = data.get('isbn', '')  # ISBN（默认空）
        # 价格：原版逻辑——存在则转float，不存在默认0.0
        self.price = float(data.get('price', 0.0)) if 'price' in data else 0.0
        self.category = data.get('category', '')  # 分类（默认空）
        self.description = data.get('description', '')  # 描述（默认空）
        self.cover = data.get('cover', '')  # 封面URL（默认空）
        self.summary = data.get('summary', '')  # 图书概述（默认空）
        self.status = data.get('status', 'available')  # 状态（默认available）
        # 库存：原版逻辑——存在则转int，不存在默认0
        self.stock = int(data.get('stock', 0)) if 'stock' in data else 0
        self.created_at = data.get('created_at', int(time.time()))  # 创建时间（默认当前时间）
        self.updated_at = data.get('updated_at', int(time.time()))  # 更新时间（默认当前时间）

    @classmethod
    def create_book(cls, book_data):
        """创建图书（完全复刻原版create_book逻辑，含字段校验）"""
        # 1. 校验必填字段（书名）
        if not book_data.get('title'):
            logger.error("创建图书失败: 缺少书名（title）")
            return False, "书名是必填项"

        # 2. 组装图书数据（与原版字段、类型转换完全一致）
        book_id = str(uuid.uuid4())
        current_time = int(time.time())
        # 价格处理：原版逻辑——存在则转float，不存在默认0.0
        price = float(book_data.get('price', 0.0)) if 'price' in book_data else 0.0
        # 库存处理：原版逻辑——存在则转int，不存在默认0
        stock = int(book_data.get('stock', 0)) if 'stock' in book_data else 0

        book_data = {
            'book_id': book_id,
            'title': book_data['title'],
            'author': book_data.get('author', ''),
            'publisher': book_data.get('publisher', ''),
            'isbn': book_data.get('isbn', ''),
            'price': price,
            'category': book_data.get('category', ''),
            'description': book_data.get('description', ''),
            'cover': book_data.get('cover', ''),
            'summary': book_data.get('summary', ''),
            'status': book_data.get('status', 'available'),
            'stock': stock,
            'created_at': current_time,
            'updated_at': current_time
        }

        # 3. 插入OTS（Books表，与原版存储逻辑一致）
        primary_key = [('book_id', book_id)]
        attribute_columns = [
            ('title', book_data['title']),
            ('author', book_data['author']),
            ('publisher', book_data['publisher']),
            ('isbn', book_data['isbn']),
            ('price', book_data['price']),
            ('category', book_data['category']),
            ('description', book_data['description']),
            ('cover', book_data['cover']),
            ('summary', book_data['summary']),
            ('status', book_data['status']),
            ('stock', book_data['stock']),
            ('created_at', book_data['created_at']),
            ('updated_at', book_data['updated_at'])
        ]
        success, err = ots_put_row(
            OTS_TABLE_NAME,
            primary_key,
            attribute_columns,
            expect_exist=RowExistenceExpectation.IGNORE
        )
        if not success:
            logger.error(f"创建图书失败: book_id={book_id}, err={err}")
            return False, str(err)

        logger.info(f"创建图书成功: book_id={book_id}, title={book_data['title']}")
        return True, book_id

    @classmethod
    def get_by_id(cls, book_id):
        """通过book_id获取图书（复刻原版get_book逻辑，含详细日志）"""
        logger.info(
            f"查询Books表: 表名={OTS_TABLE_NAME}, "
            f"主键=book_id, 查询值={book_id}, 类型={type(book_id).__name__}"
        )
        # 调用OTS查询（与原版get_row逻辑一致）
        data = ots_get_row(OTS_TABLE_NAME, primary_key=[('book_id', book_id)])
        if not data:
            logger.info(f"图书不存在: book_id={book_id}（OTS表无记录）")
            return None

        # 字段类型校准（与原版一致：stock转int，price转float）
        if 'stock' in data:
            data['stock'] = int(data['stock'])
        if 'price' in data:
            data['price'] = float(data['price'])

        logger.info(f"获取图书成功: book_id={book_id}, title={data.get('title')}")
        return cls(data)

    @classmethod
    def get_list(cls, page=1, size=10, category=''):
        """获取图书列表（修复起始主键问题）"""
        try:
            logger.info(f"📚 Book.get_list() 开始: page={page}, size={size}, category='{category}'")

            # 1. 计算分页偏移
            offset = (page - 1) * size
            result = []
            # 重要修复：始终从 INF_MIN 开始查询
            next_start_pk = [('book_id', INF_MIN)]

            logger.info(f"📐 分页参数: offset={offset}, limit={size}")
            logger.info(f"📍 起始主键: {next_start_pk}")

            # 2. 分类过滤条件
            column_filter = None
            if category:
                column_filter = SingleColumnCondition('category', category, ComparatorType.EQUAL)
                logger.info(f"🎯 分类过滤: {category}")

            # 3. 循环获取数据
            batch_count = 0
            total_scanned = 0

            while next_start_pk and len(result) < size:
                batch_count += 1
                logger.info(f"🔄 第 {batch_count} 批次查询, next_start_pk={next_start_pk}")

                # 调用OTS范围查询
                batch = ots_get_range(
                    OTS_TABLE_NAME,
                    start_pk=next_start_pk,
                    end_pk=[('book_id', INF_MAX)],
                    column_filter=column_filter,
                    limit=size * 3  # 多取一些数据来处理偏移
                )

                logger.info(f"📦 批次 {batch_count} 获取到 {len(batch)} 条记录")
                total_scanned += len(batch)

                if not batch:
                    logger.info("📭 无更多数据，终止循环")
                    break

                # 处理偏移：跳过前offset条
                if offset > 0:
                    logger.info(f"⏩ 需要跳过 {offset} 条记录，当前批次有 {len(batch)} 条")
                    if len(batch) <= offset:
                        offset -= len(batch)
                        # 更新下一批次起始主键
                        if batch:
                            next_start_pk = [('book_id', batch[-1]['book_id'])]
                        else:
                            next_start_pk = None
                        logger.info(f"⏭️ 跳过整个批次，剩余offset={offset}")
                        continue
                    else:
                        # 截取偏移后的部分
                        batch = batch[offset:]
                        offset = 0  # 偏移处理完成
                        logger.info(f"✅ 偏移处理完成，剩余批次长度: {len(batch)}")

                # 收集结果（确保不超过size）
                take = min(size - len(result), len(batch))
                if take > 0:
                    result.extend(batch[:take])
                    logger.info(f"📥 收集 {take} 条记录，当前总数: {len(result)}")
                else:
                    logger.info("📥 无需收集更多记录")

                # 更新下一批次起始主键
                if batch and len(result) < size:
                    next_start_pk = [('book_id', batch[-1]['book_id'])]
                    logger.info(f"➡️ 下一批次起始主键: {next_start_pk}")
                else:
                    next_start_pk = None
                    logger.info("🏁 无下一批次")

            # 4. 转换为Book对象并校准字段类型
            book_list = []
            logger.info(f"🔄 开始转换 {len(result)} 条记录为Book对象")

            for i, book_data in enumerate(result):
                try:
                    # 校准stock和price类型
                    if 'stock' in book_data:
                        book_data['stock'] = int(book_data['stock'])
                    if 'price' in book_data:
                        book_data['price'] = float(book_data['price'])

                    book_obj = cls(book_data)
                    book_list.append(book_obj)

                    logger.info(f"✅ 转换成功: {book_obj.title} (ID: {book_obj.book_id})")

                except Exception as e:
                    logger.error(f"❌ 转换图书数据失败: {book_data}, 错误: {str(e)}")

            # 5. 获取总数
            logger.info("🔢 开始获取图书总数...")
            total = cls.get_total(category)
            logger.info(f"📊 图书总数: {total}")

            logger.info(f"🎉 最终返回: {len(book_list)} 本书, 总数: {total}, 扫描了 {total_scanned} 条记录")
            return book_list, total

        except Exception as e:
            logger.error(f"💥 Book.get_list() 异常: {str(e)}", exc_info=True)
            return [], 0

    @classmethod
    def get_total(cls, category=''):
        """获取图书总数（修复无限循环问题）"""
        count = 0
        next_start_pk = [('book_id', INF_MIN)]
        column_filter = None

        # 分类过滤
        if category:
            column_filter = SingleColumnCondition('category', category, ComparatorType.EQUAL)

        # 循环统计总数
        batch_count = 0
        max_batches = 100  # 防止无限循环

        while next_start_pk and batch_count < max_batches:
            batch_count += 1
            logger.info(f"🔄 总数统计第 {batch_count} 批次, next_start_pk={next_start_pk}")

            batch = ots_get_range(
                OTS_TABLE_NAME,
                start_pk=next_start_pk,
                end_pk=[('book_id', INF_MAX)],
                column_filter=column_filter,
                limit=1000
            )

            logger.info(f"📦 总数统计批次 {batch_count} 获取到 {len(batch)} 条记录")

            if not batch:
                logger.info("📭 总数统计无更多数据")
                break

            count += len(batch)

            # 更新下一批次起始主键
            if len(batch) > 0:
                next_start_pk = [('book_id', batch[-1]['book_id'])]
                logger.info(f"➡️ 总数统计下一批次起始主键: {next_start_pk}")
            else:
                next_start_pk = None
                logger.info("🏁 总数统计无下一批次")

        if batch_count >= max_batches:
            logger.warning(f"⚠️ 总数统计达到最大批次限制 {max_batches}，可能数据量过大")

        logger.info(f"📊 图书总数统计完成: {count} 条记录")
        return count

    @classmethod
    def check_table_data(cls):
        """检查图书表数据状态"""
        try:
            logger.info("🔍 检查图书表数据状态...")

            # 直接查询前几条记录
            books = ots_get_range(
                OTS_TABLE_NAME,
                start_pk=[('book_id', INF_MIN)],
                end_pk=[('book_id', INF_MAX)],
                limit=5
            )

            logger.info(f"📊 图书表共有 {len(books)} 条记录")

            for i, book in enumerate(books):
                logger.info(f"📖 图书 {i + 1}: ID={book.get('book_id')}, 标题={book.get('title')}")

            return len(books) > 0
        except Exception as e:
            logger.error(f"❌ 检查图书表数据失败: {str(e)}")
            return False

    def update_book(self, book_data):
        """更新图书（复刻原版update_book逻辑，含字段校验与类型转换）"""
        if not self.book_id:
            logger.error("更新图书失败: 缺少book_id主键")
            return False, "图书不存在"

        # 1. 组装更新字段（仅更新传入字段，保留原版字段校验）
        update_columns = []
        # 处理书名
        if 'title' in book_data and book_data['title']:
            self.title = book_data['title']
            update_columns.append(('title', self.title))
        # 处理作者
        if 'author' in book_data:
            self.author = book_data['author']
            update_columns.append(('author', self.author))
        # 处理出版社
        if 'publisher' in book_data:
            self.publisher = book_data['publisher']
            update_columns.append(('publisher', self.publisher))
        # 处理ISBN
        if 'isbn' in book_data:
            self.isbn = book_data['isbn']
            update_columns.append(('isbn', self.isbn))
        # 处理价格（原版逻辑：转float）
        if 'price' in book_data:
            try:
                self.price = float(book_data['price'])
                update_columns.append(('price', self.price))
            except ValueError:
                logger.error(f"更新图书失败: 价格格式错误（{book_data['price']}）")
                return False, "价格必须为数字"
        # 处理分类
        if 'category' in book_data:
            self.category = book_data['category']
            update_columns.append(('category', self.category))
        # 处理描述
        if 'description' in book_data:
            self.description = book_data['description']
            update_columns.append(('description', self.description))
        # 处理封面
        if 'cover' in book_data:
            self.cover = book_data['cover']
            update_columns.append(('cover', self.cover))
        # 处理概述
        if 'summary' in book_data:
            self.summary = book_data['summary']
            update_columns.append(('summary', self.summary))
        # 处理状态（校验合法性）
        if 'status' in book_data and book_data['status'] in ['available', 'borrowed', 'maintenance']:
            self.status = book_data['status']
            update_columns.append(('status', self.status))
        # 处理库存（原版逻辑：转int）
        if 'stock' in book_data:
            try:
                self.stock = int(book_data['stock'])
                update_columns.append(('stock', self.stock))
            except ValueError:
                logger.error(f"更新图书失败: 库存格式错误（{book_data['stock']}）")
                return False, "库存必须为整数"

        # 强制更新updated_at（与原版一致）
        self.updated_at = int(time.time())
        update_columns.append(('updated_at', self.updated_at))

        # 无更新字段校验
        if not update_columns:
            return False, "没有提供有效更新字段"

        # 2. 调用OTS更新（与原版update_row逻辑一致）
        primary_key = [('book_id', self.book_id)]
        success, err = ots_put_row(
            OTS_TABLE_NAME,
            primary_key,
            update_columns,
            expect_exist=RowExistenceExpectation.IGNORE
        )
        if not success:
            logger.error(f"更新图书失败: book_id={self.book_id}, err={err}")
            return False, str(err)

        logger.info(f"更新图书成功: book_id={self.book_id}")
        return True, None

    def delete_book(self):
        """删除图书（复刻原版delete_book逻辑，含OTS删除校验）"""
        if not self.book_id:
            logger.error("删除图书失败: 缺少book_id主键")
            return False, "图书不存在"

        # 调用OTS删除（与原版delete_row逻辑一致）
        success, err = ots_delete_row(OTS_TABLE_NAME, primary_key=[('book_id', self.book_id)])
        if not success:
            logger.error(f"删除图书失败: book_id={self.book_id}, err={err}")
            return False, str(err)

        logger.info(f"删除图书成功: book_id={self.book_id}")
        return True, None

    def update_stock(self, change):
        """更新库存（±1，复刻原版借阅/归还库存处理逻辑）"""
        # 1. 计算新库存（确保非负，与原版一致）
        new_stock = self.stock + change
        if new_stock < 0:
            logger.error(f"库存更新失败: book_id={self.book_id}, 新库存为负（{new_stock}）")
            return False, "库存不足"

        # 2. 更新库存和状态（库存为0时改状态为borrowed，与原版一致）
        self.stock = new_stock
        self.status = 'borrowed' if new_stock == 0 else 'available'
        self.updated_at = int(time.time())

        # 3. 调用OTS更新（仅更新库存、状态、更新时间）
        primary_key = [('book_id', self.book_id)]
        update_columns = [
            ('stock', self.stock),
            ('status', self.status),
            ('updated_at', self.updated_at)
        ]
        success, err = ots_put_row(
            OTS_TABLE_NAME,
            primary_key,
            update_columns,
            expect_exist=RowExistenceExpectation.IGNORE
        )
        if not success:
            logger.error(f"库存更新失败: book_id={self.book_id}, err={err}")
            return False, str(err)

        logger.info(f"库存更新成功: book_id={self.book_id}, 原库存={self.stock - change}, 新库存={self.stock}")
        return True, None

    def get_borrow_history(self):
        """获取图书借阅历史（完全复刻原版get_borrow_history逻辑）"""
        logger.info(f"获取图书借阅历史: book_id={self.book_id}")
        # 调用Borrow模型获取记录（与原版全表扫描+内存过滤逻辑一致）
        return Borrow.get_by_book_id(self.book_id)

    def get_earliest_return_date(self):
        """获取最早归还日期（复刻原版同名逻辑，含条件过滤）"""
        # 1. 构建条件：book_id匹配 + 状态为borrowed（与原版一致）
        condition = CompositeColumnCondition(LogicalOperator.AND)
        condition.add_sub_condition(SingleColumnCondition('book_id', self.book_id, ComparatorType.EQUAL))
        condition.add_sub_condition(SingleColumnCondition('status', 'borrowed', ComparatorType.EQUAL))

        # 2. OTS范围查询（与原版一致）
        borrow_records = ots_get_range(
            BORROW_RECORDS_TABLE,
            start_pk=[('borrow_id', INF_MIN)],
            end_pk=[('borrow_id', INF_MAX)],
            column_filter=condition
        )

        # 3. 查找最早due_date（与原版一致）
        earliest_date = None
        for record in borrow_records:
            due_date = record.get('due_date')
            if due_date and (earliest_date is None or due_date < earliest_date):
                earliest_date = due_date

        # 4. 格式转换（时间戳转字符串，与原版一致）
        if earliest_date:
            return time.strftime('%Y-%m-%d', time.localtime(earliest_date))
        return "未知日期"