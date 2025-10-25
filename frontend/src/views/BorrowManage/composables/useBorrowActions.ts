import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'

export function useBorrowActions(fetchBorrowRecords: Function) {
  const returning = ref(false)

  const returnBook = async (borrowId: string) => {
    try {
      // 设置归还中状态
      const record = getRecordById(borrowId)
      if (record) record.returning = true

      const response = await api.returnBookByBorrowId(borrowId)

      // 确保解析正确的数据结构
      const result = response.data?.body ? JSON.parse(response.data.body) : response.data

      if (result && result.success) {
        // 更新本地记录状态
        const record = getRecordById(borrowId)
        if (record) {
          record.status = 'returned'
          record.return_date = Math.floor(Date.now() / 1000) // 设置归还时间
        }

        ElMessage.success('归还成功')
      } else {
        ElMessage.error('归还失败: ' + (result?.error || '未知错误'))
      }
    } catch (error: any) {
      ElMessage.error('归还失败: ' + error.message)
    } finally {
      // 重置归还状态
      const record = getRecordById(borrowId)
      if (record) record.returning = false
    }
  }

  const batchReturn = async (borrowIds: string[]) => {
    try {
      await ElMessageBox.confirm('确定要归还选中的图书吗？', '确认归还', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })

      // 设置归还中状态
      borrowIds.forEach(borrowId => {
        const record = getRecordById(borrowId)
        if (record) record.returning = true
      })

      const response = await api.batchReturnBooks({ borrow_ids: borrowIds })

      // 确保解析正确的数据结构
      const result = response.data?.body ? JSON.parse(response.data.body) : response.data

      if (result && result.success) {
        // 更新本地记录状态
        borrowIds.forEach(borrowId => {
          const record = getRecordById(borrowId)
          if (record) {
            record.status = 'returned'
            record.return_date = Math.floor(Date.now() / 1000)
          }
        })

        ElMessage.success(`成功归还 ${result.returned_count || borrowIds.length} 本书`)
        selectedBorrows.value = []
      } else {
        ElMessage.error('批量归还失败: ' + (result?.error || '未知错误'))
      }
    } catch (error: any) {
      if (error !== 'cancel') {
        ElMessage.error('批量归还失败: ' + error.message)
      }
    } finally {
      // 重置归还状态
      borrowIds.forEach(borrowId => {
        const record = getRecordById(borrowId)
        if (record) record.returning = false
      })
    }
  }

  // 辅助函数：根据ID获取记录
  const getRecordById = (borrowId: string) => {
    // 这里需要访问borrowRecords，可以通过参数传递或从store获取
    // 暂时返回null，实际使用时需要修改
    return null
  }

  // 辅助函数：选中的借阅记录
  const selectedBorrows = ref<any[]>([])

  return {
    returning,
    returnBook,
    batchReturn,
    selectedBorrows
  }
}