import uuid
import time
from typing import List, Tuple, Optional, Dict, Any
from config import logger
from models.borrow import Borrow
from repositories.book_repository import BookRepository


class Book:
    """图书数据模型（使用仓储层进行数据访问）"""

    def __init__(self, data: Dict[str, Any]):
        """初始化图书对象"""
        self.book_id = data.get('book_id')
        self.title = data.get('title', '')
        self.author = data.get('author', '')
        self.publisher = data.get('publisher', '')
        self.isbn = data.get('isbn', '')
        self.price = float(data.get('price', 0.0)) if 'price' in data else 0.0
        self.category = data.get('category', '')
        self.description = data.get('description', '')
        self.cover = data.get('cover', '')
        self.summary = data.get('summary', '')
        self.status = data.get('status', 'available')
        self.stock = int(data.get('stock', 0)) if 'stock' in data else 0
        self.created_at = data.get('created_at', int(time.time()))
        self.updated_at = data.get('updated_at', int(time.time()))

        # 初始化仓储
        self._repository = BookRepository()

    @classmethod
    def create_book(cls, book_data: Dict[str, Any]) -> Tuple[bool, str]:
        """创建图书"""
        # 1. 校验必填字段
        if not book_data.get('title'):
            logger.error("创建图书失败: 缺少书名（title）")
            return False, "书名是必填项"

        # 2. 组装图书数据
        book_id = str(uuid.uuid4())
        current_time = int(time.time())
        price = float(book_data.get('price', 0.0)) if 'price' in book_data else 0.0
        stock = int(book_data.get('stock', 0)) if 'stock' in book_data else 0

        book_entity_data = {
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

        # 3. 通过仓储层插入数据
        repository = BookRepository()
        result = repository.create(book_entity_data)

        if not result:
            logger.error(f"创建图书失败: book_id={book_id}")
            return False, "创建图书失败"

        logger.info(f"创建图书成功: book_id={book_id}, title={book_entity_data['title']}")
        return True, book_id

    @classmethod
    def get_by_id(cls, book_id: str) -> Optional['Book']:
        """通过book_id获取图书"""
        repository = BookRepository()
        data = repository.get_by_id(book_id)

        if not data:
            return None

        return cls(data)

    @classmethod
    def get_list(cls, page: int = 1, size: int = 10, category: str = '') -> Tuple[List['Book'], int]:
        """获取图书列表"""
        try:
            logger.info(f"📚 Book.get_list() 开始: page={page}, size={size}, category='{category}'")

            # 计算分页偏移
            offset = (page - 1) * size

            # 通过仓储层获取数据
            repository = BookRepository()
            filters = {'category': category} if category else None
            all_books_data = repository.get_all(filters)

            logger.info(f"📊 查询到总记录数: {len(all_books_data)}")

            if not all_books_data:
                logger.info("📭 无图书数据")
                return [], 0

            # 按创建时间倒序
            all_books_data.sort(key=lambda x: x.get('created_at', 0), reverse=True)

            # 内存分页
            start_index = offset
            end_index = offset + size
            paged_books_data = all_books_data[start_index:end_index]

            logger.info(f"📄 分页结果: 起始索引={start_index}, 结束索引={end_index}, 本页数量={len(paged_books_data)}")

            # 转换为Book对象
            book_list = []
            for i, book_data in enumerate(paged_books_data):
                try:
                    book_obj = cls(book_data)
                    book_list.append(book_obj)
                    logger.info(f"✅ 转换成功 {i + 1}: {book_obj.title} (ID: {book_obj.book_id})")
                except Exception as e:
                    logger.error(f"❌ 转换图书数据失败: {book_data}, 错误: {str(e)}")

            # 获取总数
            total = len(all_books_data)
            logger.info(f"📊 最终返回: {len(book_list)} 本书, 总数: {total}")

            return book_list, total

        except Exception as e:
            logger.error(f"💥 Book.get_list() 异常: {str(e)}", exc_info=True)
            return [], 0

    @classmethod
    def get_total(cls, category: str = '') -> int:
        """获取图书总数"""
        repository = BookRepository()
        filters = {'category': category} if category else None
        return repository.count(filters)

    @classmethod
    def check_table_data(cls) -> bool:
        """检查图书表数据状态"""
        repository = BookRepository()
        return repository.check_table_data()

    def update_book(self, book_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """更新图书"""
        if not self.book_id:
            logger.error("更新图书失败: 缺少book_id主键")
            return False, "图书不存在"

        # 组装更新字段
        update_columns = {}

        # 处理各字段更新
        if 'title' in book_data and book_data['title']:
            self.title = book_data['title']
            update_columns['title'] = self.title

        if 'author' in book_data:
            self.author = book_data['author']
            update_columns['author'] = self.author

        if 'publisher' in book_data:
            self.publisher = book_data['publisher']
            update_columns['publisher'] = self.publisher

        if 'isbn' in book_data:
            self.isbn = book_data['isbn']
            update_columns['isbn'] = self.isbn

        if 'price' in book_data:
            try:
                self.price = float(book_data['price'])
                update_columns['price'] = self.price
            except ValueError:
                logger.error(f"更新图书失败: 价格格式错误（{book_data['price']}）")
                return False, "价格必须为数字"

        if 'category' in book_data:
            self.category = book_data['category']
            update_columns['category'] = self.category

        if 'description' in book_data:
            self.description = book_data['description']
            update_columns['description'] = self.description

        if 'cover' in book_data:
            self.cover = book_data['cover']
            update_columns['cover'] = self.cover

        if 'summary' in book_data:
            self.summary = book_data['summary']
            update_columns['summary'] = self.summary

        if 'status' in book_data and book_data['status'] in ['available', 'borrowed', 'maintenance']:
            self.status = book_data['status']
            update_columns['status'] = self.status

        if 'stock' in book_data:
            try:
                self.stock = int(book_data['stock'])
                update_columns['stock'] = self.stock
            except ValueError:
                logger.error(f"更新图书失败: 库存格式错误（{book_data['stock']}）")
                return False, "库存必须为整数"

        # 强制更新updated_at
        self.updated_at = int(time.time())
        update_columns['updated_at'] = self.updated_at

        # 无更新字段校验
        if not update_columns:
            return False, "没有提供有效更新字段"

        # 通过仓储层更新数据
        success = self._repository.update(self.book_id, update_columns)

        if not success:
            logger.error(f"更新图书失败: book_id={self.book_id}")
            return False, "更新图书失败"

        logger.info(f"更新图书成功: book_id={self.book_id}")
        return True, None

    def delete_book(self) -> Tuple[bool, Optional[str]]:
        """删除图书"""
        if not self.book_id:
            logger.error("删除图书失败: 缺少book_id主键")
            return False, "图书不存在"

        # 通过仓储层删除数据
        success = self._repository.delete(self.book_id)

        if not success:
            logger.error(f"删除图书失败: book_id={self.book_id}")
            return False, "删除图书失败"

        logger.info(f"删除图书成功: book_id={self.book_id}")
        return True, None

    def update_stock(self, change: int) -> Tuple[bool, Optional[str]]:
        """更新库存"""
        # 1. 计算新库存
        new_stock = self.stock + change
        if new_stock < 0:
            logger.error(f"库存更新失败: book_id={self.book_id}, 新库存为负（{new_stock}）")
            return False, "库存不足"

        # 2. 更新库存和状态
        self.stock = new_stock
        self.status = 'borrowed' if new_stock == 0 else 'available'
        self.updated_at = int(time.time())

        # 3. 通过仓储层更新数据
        update_data = {
            'stock': self.stock,
            'status': self.status,
            'updated_at': self.updated_at
        }

        success = self._repository.update(self.book_id, update_data)

        if not success:
            logger.error(f"库存更新失败: book_id={self.book_id}")
            return False, "库存更新失败"

        logger.info(f"库存更新成功: book_id={self.book_id}, 原库存={self.stock - change}, 新库存={self.stock}")
        return True, None

    def get_borrow_history(self) -> List['Borrow']:
        """获取图书借阅历史"""
        logger.info(f"获取图书借阅历史: book_id={self.book_id}")
        return Borrow.get_by_book_id(self.book_id)

    def get_earliest_return_date(self) -> str:
        """获取最早归还日期"""
        from tablestore import (
            CompositeColumnCondition, LogicalOperator, SingleColumnCondition,
            ComparatorType, INF_MIN, INF_MAX
        )
        from utils.database import ots_get_range
        from config import BORROW_RECORDS_TABLE

        # 1. 构建条件
        condition = CompositeColumnCondition(LogicalOperator.AND)
        condition.add_sub_condition(SingleColumnCondition('book_id', self.book_id, ComparatorType.EQUAL))
        condition.add_sub_condition(SingleColumnCondition('status', 'borrowed', ComparatorType.EQUAL))

        # 2. OTS范围查询
        borrow_records = ots_get_range(
            BORROW_RECORDS_TABLE,
            start_pk=[('borrow_id', INF_MIN)],
            end_pk=[('borrow_id', INF_MAX)],
            column_filter=condition
        )

        # 3. 查找最早due_date
        earliest_date = None
        for record in borrow_records:
            due_date = record.get('due_date')
            if due_date and (earliest_date is None or due_date < earliest_date):
                earliest_date = due_date

        # 4. 格式转换
        if earliest_date:
            return time.strftime('%Y-%m-%d', time.localtime(earliest_date))
        return "未知日期"