import uuid
import time
from typing import List, Optional, Dict, Any
from tablestore import RowExistenceExpectation
from config import logger
from repositories.borrow_repository import BorrowRepository


class Borrow:
    """借阅记录模型（使用仓储层进行数据访问）"""

    def __init__(self, data: Dict[str, Any]):
        """初始化借阅记录"""
        self.borrow_id = data.get('borrow_id')
        self.book_id = data.get('book_id', '')
        self.user_id = data.get('user_id', '')
        self.borrow_date = data.get('borrow_date', int(time.time()))
        self.due_date = data.get('due_date', int(time.time()) + 30 * 24 * 3600)
        self.return_date = data.get('return_date', 0)
        self.status = data.get('status', 'borrowed')
        self.is_early_return = data.get('is_early_return', False)
        self.created_at = data.get('created_at', int(time.time()))
        self.updated_at = data.get('updated_at', int(time.time()))

        # 初始化仓储
        self._repository = BorrowRepository()

    @classmethod
    def create_borrow(cls, book_id: str, user_id: str, days: int = 30) -> tuple:
        """创建借阅记录"""
        # 1. 生成borrow_id
        borrow_id = str(uuid.uuid4())
        current_time = int(time.time())

        # 2. 计算应还时间
        due_date = current_time + days * 24 * 3600

        # 3. 组装借阅数据
        borrow_data = {
            'borrow_id': borrow_id,
            'book_id': book_id,
            'user_id': user_id,
            'borrow_date': current_time,
            'due_date': due_date,
            'status': 'borrowed',
            'created_at': current_time,
            'updated_at': current_time
        }

        # 4. 通过仓储层插入数据
        repository = BorrowRepository()
        result = repository.create(borrow_data)

        if not result:
            logger.error(f"创建借阅记录失败: borrow_id={borrow_id}")
            return False, "创建借阅记录失败"

        logger.info(f"创建借阅记录成功: borrow_id={borrow_id}, user_id={user_id}, book_id={book_id}")
        return True, borrow_id

    @classmethod
    def get_by_id(cls, borrow_id: str) -> Optional['Borrow']:
        """通过borrow_id获取借阅记录"""
        repository = BorrowRepository()
        data = repository.get_by_id(borrow_id)

        if not data:
            return None

        return cls(data)

    @classmethod
    def get_by_user_book(cls, user_id: str, book_id: str) -> Optional['Borrow']:
        """获取用户的某本图书借阅记录"""
        repository = BorrowRepository()
        data = repository.get_by_user_book(user_id, book_id)

        if not data:
            return None

        return cls(data)

    @classmethod
    def get_by_user_id(cls, user_id: str) -> List['Borrow']:
        """获取用户所有借阅记录"""
        repository = BorrowRepository()
        data_list = repository.get_by_user_id(user_id)

        return [cls(data) for data in data_list]

    @classmethod
    def get_by_book_id(cls, book_id: str) -> List['Borrow']:
        """获取图书的所有借阅记录"""
        repository = BorrowRepository()
        data_list = repository.get_by_book_id(book_id)

        return [cls(data) for data in data_list]

    def update_status(self, status: str, is_early_return: bool = False) -> tuple:
        """更新借阅状态"""
        if not self.borrow_id:
            logger.error("更新借阅状态失败: 缺少borrow_id主键")
            return False, "借阅记录不存在"

        # 1. 校验状态合法性
        if status not in ['borrowed', 'returned']:
            return False, "无效状态（仅支持borrowed/returned）"

        # 2. 组装更新字段
        update_columns = {
            'status': status,
            'updated_at': int(time.time())
        }

        # 3. 归还时补充字段
        if status == 'returned':
            self.return_date = int(time.time())
            self.is_early_return = is_early_return
            update_columns['return_date'] = self.return_date
            update_columns['is_early_return'] = self.is_early_return

        # 4. 通过仓储层更新数据
        success = self._repository.update(self.borrow_id, update_columns)

        if not success:
            logger.error(f"更新借阅状态失败: borrow_id={self.borrow_id}")
            return False, "更新借阅状态失败"

        # 更新实例状态
        self.status = status
        self.updated_at = int(time.time())

        logger.info(f"更新借阅状态成功: borrow_id={self.borrow_id}, 新状态={status}")
        return True, None