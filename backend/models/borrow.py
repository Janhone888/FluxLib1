import uuid
import time
from tablestore import (  # 补充导入INF_MIN、INF_MAX，确保范围查询常量可用
    SingleColumnCondition, ComparatorType, CompositeColumnCondition,
    LogicalOperator, INF_MIN, INF_MAX, RowExistenceExpectation  # 保留原依赖的RowExistenceExpectation
)
from config import logger, BORROW_RECORDS_TABLE, RESERVATIONS_TABLE
from utils.database import ots_put_row, ots_get_row, ots_get_range, ots_delete_row
from models.user import User  # 替换原utils.auth的get_user_by_id，改用User类


class Borrow:
    """借阅记录模型（对应BorrowRecords表）"""
    def __init__(self, data):
        """初始化借阅记录（字段与原代码一致）"""
        self.borrow_id = data.get('borrow_id')  # 主键
        self.book_id = data.get('book_id', '')  # 图书ID
        self.user_id = data.get('user_id', '')  # 用户ID
        self.borrow_date = data.get('borrow_date', int(time.time()))  # 借阅时间
        self.due_date = data.get('due_date', int(time.time()) + 30 * 24 * 3600)  # 应还时间（默认30天）
        self.return_date = data.get('return_date', 0)  # 实际归还时间（0表示未归还）
        self.status = data.get('status', 'borrowed')  # 状态（borrowed/returned）
        self.is_early_return = data.get('is_early_return', False)  # 是否提前归还
        self.created_at = data.get('created_at', int(time.time()))  # 创建时间
        self.updated_at = data.get('updated_at', int(time.time()))  # 更新时间


    @classmethod
    def create_borrow(cls, book_id, user_id, days=30):
        """创建借阅记录（对应原代码borrow_book中的记录创建逻辑）"""
        # 1. 生成borrow_id
        borrow_id = str(uuid.uuid4())
        current_time = int(time.time())
        # 2. 计算应还时间（借阅天数×86400秒）
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

        # 4. 插入OTS（BorrowRecords表）
        primary_key = [('borrow_id', borrow_id)]
        attribute_columns = [
            ('book_id', borrow_data['book_id']),
            ('user_id', borrow_data['user_id']),
            ('borrow_date', borrow_data['borrow_date']),
            ('due_date', borrow_data['due_date']),
            ('status', borrow_data['status']),
            ('created_at', borrow_data['created_at']),
            ('updated_at', borrow_data['updated_at'])
        ]
        success, err = ots_put_row(
            BORROW_RECORDS_TABLE,
            primary_key,
            attribute_columns,
            expect_exist=RowExistenceExpectation.IGNORE
        )
        if not success:
            logger.error(f"创建借阅记录失败: borrow_id={borrow_id}, err={err}")
            return False, str(err)

        logger.info(f"创建借阅记录成功: borrow_id={borrow_id}, user_id={user_id}, book_id={book_id}")
        return True, borrow_id


    @classmethod
    def get_by_id(cls, borrow_id):
        """通过borrow_id获取借阅记录"""
        data = ots_get_row(BORROW_RECORDS_TABLE, primary_key=[('borrow_id', borrow_id)])
        if not data:
            logger.info(f"借阅记录不存在: borrow_id={borrow_id}")
            return None
        return cls(data)


    @classmethod
    def get_by_user_book(cls, user_id, book_id):
        """获取用户的某本图书借阅记录（对应原代码get_borrowing_record逻辑）"""
        # 条件：user_id + book_id + status=borrowed
        condition = CompositeColumnCondition(LogicalOperator.AND)
        condition.add_sub_condition(SingleColumnCondition('user_id', user_id, ComparatorType.EQUAL))
        condition.add_sub_condition(SingleColumnCondition('book_id', book_id, ComparatorType.EQUAL))
        condition.add_sub_condition(SingleColumnCondition('status', 'borrowed', ComparatorType.EQUAL))

        # 范围查询（仅取1条，INF_MIN/INF_MAX已正常导入）
        borrow_list = ots_get_range(
            BORROW_RECORDS_TABLE,
            start_pk=[('borrow_id', INF_MIN)],  # 已导入INF_MIN，可正常使用
            end_pk=[('borrow_id', INF_MAX)],    # 已导入INF_MAX，可正常使用
            column_filter=condition,
            limit=1
        )
        if not borrow_list:
            return None
        return cls(borrow_list[0])


    @classmethod
    def get_by_user_id(cls, user_id):
        """获取用户所有借阅记录（对应原代码get_user_borrows逻辑）"""
        # 条件：user_id匹配
        condition = SingleColumnCondition('user_id', user_id, ComparatorType.EQUAL)
        borrow_list = ots_get_range(
            BORROW_RECORDS_TABLE,
            start_pk=[('borrow_id', INF_MIN)],  # 已导入INF_MIN，可正常使用
            end_pk=[('borrow_id', INF_MAX)],    # 已导入INF_MAX，可正常使用
            column_filter=condition
        )
        return [cls(record) for record in borrow_list]


    @classmethod
    def get_by_book_id(cls, book_id):
        """获取图书的所有借阅记录"""
        condition = SingleColumnCondition('book_id', book_id, ComparatorType.EQUAL)
        borrow_list = ots_get_range(
            BORROW_RECORDS_TABLE,
            start_pk=[('borrow_id', INF_MIN)],  # 已导入INF_MIN，可正常使用
            end_pk=[('borrow_id', INF_MAX)],    # 已导入INF_MAX，可正常使用
            column_filter=condition
        )
        return [cls(record) for record in borrow_list]


    def update_status(self, status, is_early_return=False):
        """更新借阅状态（对应原代码return_book中的状态更新逻辑）"""
        if not self.borrow_id:
            logger.error("更新借阅状态失败: 缺少borrow_id主键")
            return False, "借阅记录不存在"

        # 1. 校验状态合法性
        if status not in ['borrowed', 'returned']:
            return False, "无效状态（仅支持borrowed/returned）"

        # 2. 组装更新字段
        self.status = status
        self.updated_at = int(time.time())
        update_columns = [
            ('status', status),
            ('updated_at', self.updated_at)
        ]

        # 3. 归还时补充字段
        if status == 'returned':
            self.return_date = int(time.time())
            self.is_early_return = is_early_return
            update_columns.extend([
                ('return_date', self.return_date),
                ('is_early_return', is_early_return)
            ])

        # 4. 调用OTS更新
        primary_key = [('borrow_id', self.borrow_id)]
        success, err = ots_put_row(
            BORROW_RECORDS_TABLE,
            primary_key,
            update_columns,
            expect_exist=RowExistenceExpectation.IGNORE
        )
        if not success:
            logger.error(f"更新借阅状态失败: borrow_id={self.borrow_id}, err={err}")
            return False, str(err)

        logger.info(f"更新借阅状态成功: borrow_id={self.borrow_id}, 旧状态={self.status}, 新状态={status}")
        return True, None


class Reservation:
    """预约记录模型（对应Reservations表）"""
    def __init__(self, data):
        """初始化预约记录（字段与原代码一致）"""
        self.reservation_id = data.get('reservation_id')  # 主键
        self.book_id = data.get('book_id', '')  # 图书ID
        self.user_id = data.get('user_id', '')  # 用户ID
        self.reserve_date = data.get('reserve_date', '')  # 预约日期（字符串：YYYY-MM-DD）
        self.time_slot = data.get('time_slot', '')  # 时间段（如08:00-10:00）
        self.days = data.get('days', 30)  # 借阅天数
        self.expected_return_date = data.get('expected_return_date', int(time.time()) + 30 * 24 * 3600)  # 预计归还时间
        self.status = data.get('status', 'reserved')  # 状态（reserved/canceled/completed）
        self.created_at = data.get('created_at', int(time.time()))  # 创建时间
        self.updated_at = data.get('updated_at', int(time.time()))  # 更新时间


    @classmethod
    def create_reservation(cls, book_id, user_id, reserve_date, time_slot, days=30):
        """创建预约记录（对应原代码reserve_book逻辑，替换用户查询方式）"""
        # 1. 生成reservation_id
        reservation_id = str(uuid.uuid4())
        current_time = int(time.time())

        # 2. 计算预计归还时间（预约日期+借阅天数）- 改用User类的get_by_id查询用户
        user = User.get_by_id(user_id)  # 替换原from utils.auth import get_user_by_id
        if not user:
            return False, "用户不存在"

        # 转换预约日期为时间戳（原代码calculate_return_date逻辑）
        try:
            reserve_timestamp = int(time.mktime(time.strptime(reserve_date, '%Y-%m-%d')))
            expected_return_date = reserve_timestamp + days * 24 * 3600
        except Exception as e:
            logger.error(f"计算预约归还日期失败: {str(e)}")
            expected_return_date = int(time.time()) + days * 24 * 3600

        # 3. 组装预约数据
        reservation_data = {
            'reservation_id': reservation_id,
            'book_id': book_id,
            'user_id': user_id,
            'reserve_date': reserve_date,
            'time_slot': time_slot,
            'days': days,
            'expected_return_date': expected_return_date,
            'status': 'reserved',
            'created_at': current_time,
            'updated_at': current_time
        }

        # 4. 插入OTS（Reservations表）
        primary_key = [('reservation_id', reservation_id)]
        attribute_columns = [
            ('book_id', reservation_data['book_id']),
            ('user_id', reservation_data['user_id']),
            ('reserve_date', reservation_data['reserve_date']),
            ('time_slot', reservation_data['time_slot']),
            ('days', reservation_data['days']),
            ('expected_return_date', reservation_data['expected_return_date']),
            ('status', reservation_data['status']),
            ('created_at', reservation_data['created_at']),
            ('updated_at', reservation_data['updated_at'])
        ]
        success, err = ots_put_row(
            RESERVATIONS_TABLE,
            primary_key,
            attribute_columns,
            expect_exist=RowExistenceExpectation.IGNORE
        )
        if not success:
            logger.error(f"创建预约记录失败: reservation_id={reservation_id}, err={err}")
            return False, str(err)

        logger.info(f"创建预约记录成功: reservation_id={reservation_id}, user_id={user_id}, book_id={book_id}")
        return True, reservation_id


    @classmethod
    def get_by_user_id(cls, user_id):
        """获取用户所有预约记录"""
        condition = SingleColumnCondition('user_id', user_id, ComparatorType.EQUAL)
        reserve_list = ots_get_range(
            RESERVATIONS_TABLE,
            start_pk=[('reservation_id', INF_MIN)],  # 已导入INF_MIN，可正常使用
            end_pk=[('reservation_id', INF_MAX)],    # 已导入INF_MAX，可正常使用
            column_filter=condition
        )
        return [cls(record) for record in reserve_list]