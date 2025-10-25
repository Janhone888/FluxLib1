import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'

export function useBorrowRecords() {
  const borrowRecords = ref<any[]>([])
  const loading = ref(false)
  const selectedBorrows = ref<any[]>([])

  const fetchBorrowRecords = async () => {
    try {
      loading.value = true
      const response = await api.getUserBorrows()

      // 确保使用正确的数据结构
      if (response.data && response.data.items) {
        // 添加returning状态用于控制按钮
        borrowRecords.value = response.data.items.map((item: any) => ({
          ...item,
          returning: false
        }))
      } else {
        borrowRecords.value = []
      }
    } catch (error: any) {
      ElMessage.error('获取借阅记录失败: ' + error.message)
    } finally {
      loading.value = false
    }
  }

  const handleSelectionChange = (selection: any[]) => {
    selectedBorrows.value = selection
  }

  return {
    borrowRecords,
    loading,
    selectedBorrows,
    fetchBorrowRecords,
    handleSelectionChange
  }
}