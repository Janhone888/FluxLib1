import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'

export function useBorrowActions(bookId: any, bookStore: any, fetchBookDetail: Function) {
  const reserveDialogVisible = ref(false)
  const hasBorrowed = ref(false)

  const borrowBook = async () => {
    try {
      await api.post('/borrow', { book_id: bookId.value })
      ElMessage.success('借阅成功')
      hasBorrowed.value = true
      fetchBookDetail()
    } catch (error) {
      ElMessage.error('借阅失败')
    }
  }

  const confirmReturn = (isEarly: boolean) => {
    ElMessageBox.confirm(
      `确定要${isEarly ? '提前' : ''}归还这本书吗？`,
      '归还确认',
      {
        type: 'warning'
      }
    ).then(() => {
      returnBook(isEarly)
    })
  }

  const returnBook = async (isEarly: boolean) => {
    try {
      await api.post('/return', {
        book_id: bookId.value,
        is_early: isEarly
      })
      ElMessage.success('归还成功')
      hasBorrowed.value = false
      fetchBookDetail()
    } catch (error) {
      ElMessage.error('归还失败')
    }
  }

  const showReserveDialog = () => {
    reserveDialogVisible.value = true
  }

  const submitReservation = async (reserveData: any) => {
    try {
      await api.post('/reservations', {
        book_id: bookId.value,
        ...reserveData
      })
      ElMessage.success('预约成功')
      reserveDialogVisible.value = false
    } catch (error) {
      ElMessage.error('预约失败')
    }
  }

  return {
    reserveDialogVisible,
    hasBorrowed,
    borrowBook,
    confirmReturn,
    showReserveDialog,
    submitReservation
  }
}