import time
from typing import List, Dict, Any, Optional
from tablestore import (
    SingleColumnCondition, ComparatorType, CompositeColumnCondition,
    LogicalOperator, INF_MIN, INF_MAX, RowExistenceExpectation
)
from config import logger, OTS_TABLE_NAME
from utils.database import ots_put_row, ots_get_row, ots_get_range, ots_delete_row
from repositories.base_repository import BaseRepository


class BookRepository(BaseRepository):
    """图书数据仓储层，负责所有图书数据的OTS访问操作"""

    def __init__(self):
        self.table_name = OTS_TABLE_NAME

    def get_by_id(self, book_id: str) -> Optional[Dict[str, Any]]:
        """根据book_id获取图书数据"""
        logger.info(f"查询Books表: 表名={self.table_name}, 主键=book_id, 查询值={book_id}")

        data = ots_get_row(self.table_name, primary_key=[('book_id', book_id)])
        if not data:
            logger.info(f"图书不存在: book_id={book_id}（OTS表无记录）")
            return None

        # 字段类型校准
        if 'stock' in data:
            data['stock'] = int(data['stock'])
        if 'price' in data:
            data['price'] = float(data['price'])

        logger.info(f"获取图书成功: book_id={book_id}, title={data.get('title')}")
        return data

    def get_all(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """获取所有图书数据，支持过滤条件"""
        column_filter = None

        # 处理过滤条件
        if filters and 'category' in filters and filters['category']:
            column_filter = SingleColumnCondition('category', filters['category'], ComparatorType.EQUAL)
            logger.info(f"分类过滤: {filters['category']}")

        # 查询所有数据
        all_books = ots_get_range(
            self.table_name,
            start_pk=[('book_id', INF_MIN)],
            end_pk=[('book_id', INF_MAX)],
            column_filter=column_filter
        )

        logger.info(f"查询到总记录数: {len(all_books)}")

        # 类型转换
        for book in all_books:
            if 'stock' in book:
                book['stock'] = int(book['stock'])
            if 'price' in book:
                book['price'] = float(book['price'])

        return all_books

    def create(self, entity_data: Dict[str, Any]) -> Optional[str]:
        """创建新图书"""
        book_id = entity_data.get('book_id')
        if not book_id:
            logger.error("创建图书失败: 缺少book_id")
            return None

        primary_key = [('book_id', book_id)]
        attribute_columns = [
            ('title', entity_data['title']),
            ('author', entity_data['author']),
            ('publisher', entity_data['publisher']),
            ('isbn', entity_data['isbn']),
            ('price', entity_data['price']),
            ('category', entity_data['category']),
            ('description', entity_data['description']),
            ('cover', entity_data['cover']),
            ('summary', entity_data['summary']),
            ('status', entity_data['status']),
            ('stock', entity_data['stock']),
            ('created_at', entity_data['created_at']),
            ('updated_at', entity_data['updated_at'])
        ]

        success, err = ots_put_row(
            self.table_name,
            primary_key,
            attribute_columns,
            expect_exist=RowExistenceExpectation.IGNORE
        )

        if not success:
            logger.error(f"创建图书失败: book_id={book_id}, err={err}")
            return None

        logger.info(f"创建图书成功: book_id={book_id}, title={entity_data['title']}")
        return book_id

    def update(self, book_id: str, update_data: Dict[str, Any]) -> bool:
        """更新图书数据"""
        if not book_id:
            logger.error("更新图书失败: 缺少book_id")
            return False

        primary_key = [('book_id', book_id)]
        update_columns = [(key, value) for key, value in update_data.items()]

        success, err = ots_put_row(
            self.table_name,
            primary_key,
            update_columns,
            expect_exist=RowExistenceExpectation.IGNORE
        )

        if not success:
            logger.error(f"更新图书失败: book_id={book_id}, err={err}")
            return False

        logger.info(f"更新图书成功: book_id={book_id}")
        return True

    def delete(self, book_id: str) -> bool:
        """删除图书（单主键：book_id，适配基类*args签名）"""
        success, err = ots_delete_row(
            self.table_name,
            primary_key=[('book_id', book_id)]
        )

        if not success:
            logger.error(f"删除图书失败: book_id={book_id}, err={err}")
            return False

        logger.info(f"删除图书成功: book_id={book_id}")
        return True

    def count(self, filters: Dict[str, Any] = None) -> int:
        """统计图书数量"""
        column_filter = None

        if filters and 'category' in filters and filters['category']:
            column_filter = SingleColumnCondition('category', filters['category'], ComparatorType.EQUAL)

        count = 0
        next_start_pk = [('book_id', INF_MIN)]
        max_batches = 100

        batch_count = 0
        while next_start_pk and batch_count < max_batches:
            batch_count += 1
            logger.info(f"总数统计第 {batch_count} 批次, next_start_pk={next_start_pk}")

            batch = ots_get_range(
                self.table_name,
                start_pk=next_start_pk,
                end_pk=[('book_id', INF_MAX)],
                column_filter=column_filter,
                limit=1000
            )

            logger.info(f"总数统计批次 {batch_count} 获取到 {len(batch)} 条记录")

            if not batch:
                break

            count += len(batch)

            # 更新下一批次起始主键
            if len(batch) > 0:
                next_start_pk = [('book_id', batch[-1]['book_id'])]
            else:
                next_start_pk = None

        logger.info(f"图书总数统计完成: {count} 条记录")
        return count

    def check_table_data(self) -> bool:
        """检查图书表数据状态"""
        try:
            logger.info("检查图书表数据状态...")

            books = ots_get_range(
                self.table_name,
                start_pk=[('book_id', INF_MIN)],
                end_pk=[('book_id', INF_MAX)],
                limit=5
            )

            logger.info(f"图书表共有 {len(books)} 条记录")

            for i, book in enumerate(books):
                logger.info(f"图书 {i + 1}: ID={book.get('book_id')}, 标题={book.get('title')}")

            return len(books) > 0
        except Exception as e:
            logger.error(f"检查图书表数据失败: {str(e)}")
            return False