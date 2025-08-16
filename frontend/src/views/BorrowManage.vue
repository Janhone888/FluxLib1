<template>
  <div class="borrow-manage">
    <el-card>
      <template #header>
        <h2>借阅管理</h2>
        <div class="header-actions">
          <div class="sort-controls">
            <el-button-group>
              <el-button @click="sortByStatus">
                <el-icon><Sort /></el-icon> 按状态排序
              </el-button>
              <el-button @click="sortByDate">
                <el-icon><Sort /></el-icon> 按时间排序
              </el-button>
            </el-button-group>
          </div>
          <el-button
            type="primary"
            :disabled="selectedBorrows.length === 0"
            @click="batchReturn"
          >
            批量归还
          </el-button>
        </div>
      </template>

      <el-table
        :data="borrowRecords"
        @selection-change="handleSelectionChange"
        v-loading="loading"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="book_title" label="图书名称" />
        <el-table-column label="封面" width="120">
          <template #default="{ row }">
            <el-image :src="row.book_cover" fit="cover" style="width: 60px; height: 80px" v-if="row.book_cover">
              <template #error>
                <div class="image-error">
                  <el-icon><Picture /></el-icon>
                </div>
              </template>
            </el-image>
            <div class="no-cover" v-else>
              无封面
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="borrow_date" label="借阅日期" width="180">
          <template #default="{ row }">
            {{ formatDate(row.borrow_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="due_date" label="应还日期" width="180">
          <template #default="{ row }">
            {{ formatDate(row.due_date) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.status === 'returned' ? 'success' : 'warning'">
              {{ row.status === 'returned' ? '已归还' : '借阅中' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button
              v-if="row.status !== 'returned'"
              type="text"
              @click="returnBook(row.borrow_id)"
              :disabled="row.returning"
              :loading="row.returning"
            >
              归还
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="borrowRecords.length === 0 && !loading" class="empty-state">
        <el-empty description="您还没有借阅记录">
          <el-button type="primary" @click="goToBooks">去借书</el-button>
        </el-empty>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Picture, Sort } from '@element-plus/icons-vue'
import { useBookStore } from '@/stores/books'
import { useUserStore } from '@/stores/user'
import api from '@/utils/api'

const router = useRouter()
const bookStore = useBookStore()
const userStore = useUserStore()

const borrowRecords = ref([])
const loading = ref(false)
const selectedBorrows = ref([])

// 获取用户借阅记录
const fetchBorrowRecords = async () => {
  try {
    loading.value = true
    const response = await api.getUserBorrows()
    // 确保使用正确的数据结构
    if (response.data && response.data.items) {
      // 添加returning状态用于控制按钮
      borrowRecords.value = response.data.items.map(item => ({
        ...item,
        returning: false
      }))
    } else {
      borrowRecords.value = []
    }
  } catch (error) {
    ElMessage.error('获取借阅记录失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 格式化日期
const formatDate = (timestamp) => {
  return new Date(timestamp * 1000).toLocaleDateString()
}

// 处理选择
const handleSelectionChange = (selection) => {
  selectedBorrows.value = selection
}

// 单本归还
const returnBook = async (borrowId) => {
  try {
    // 设置归还中状态
    const record = borrowRecords.value.find(r => r.borrow_id === borrowId)
    if (record) record.returning = true

    const response = await api.returnBookByBorrowId(borrowId)

    // 确保解析正确的数据结构
    const result = response.data?.body ? JSON.parse(response.data.body) : response.data

    if (result && result.success) {
      // 更新本地记录状态
      const record = borrowRecords.value.find(r => r.borrow_id === borrowId)
      if (record) {
        record.status = 'returned'
        record.return_date = Math.floor(Date.now() / 1000) // 设置归还时间
      }

      ElMessage.success('归还成功')
    } else {
      ElMessage.error('归还失败: ' + (result?.error || '未知错误'))
    }
  } catch (error) {
    ElMessage.error('归还失败: ' + error.message)
  } finally {
    // 重置归还状态
    const record = borrowRecords.value.find(r => r.borrow_id === borrowId)
    if (record) record.returning = false
  }
}

// 批量归还
const batchReturn = async () => {
  ElMessageBox.confirm('确定要归还选中的图书吗？', '确认归还', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const borrowIds = selectedBorrows.value.map(item => item.borrow_id)

      // 设置归还中状态
      borrowRecords.value.forEach(record => {
        if (borrowIds.includes(record.borrow_id)) {
          record.returning = true
        }
      })

      const response = await api.batchReturnBooks({ borrow_ids: borrowIds })

      // 确保解析正确的数据结构
      const result = response.data?.body ? JSON.parse(response.data.body) : response.data

      if (result && result.success) {
        // 更新本地记录状态
        borrowRecords.value.forEach(record => {
          if (borrowIds.includes(record.borrow_id)) {
            record.status = 'returned'
            record.return_date = Math.floor(Date.now() / 1000)
          }
        })

        ElMessage.success(`成功归还 ${result.returned_count || borrowIds.length} 本书`)
        selectedBorrows.value = []
      } else {
        ElMessage.error('批量归还失败: ' + (result?.error || '未知错误'))
      }
    } catch (error) {
      ElMessage.error('批量归还失败: ' + error.message)
    } finally {
      // 重置归还状态
      borrowRecords.value.forEach(record => {
        if (borrowIds.includes(record.borrow_id)) {
          record.returning = false
        }
      })
    }
  }).catch(() => {})
}

// 添加排序方法
const sortByStatus = () => {
  borrowRecords.value.sort((a, b) => {
    if (a.status === b.status) return 0
    return a.status === 'returned' ? 1 : -1
  })
}

const sortByDate = () => {
  borrowRecords.value.sort((a, b) => {
    return b.borrow_date - a.borrow_date
  })
}

// 跳转到图书列表
const goToBooks = () => {
  router.push('/books')
}

onMounted(() => {
  fetchBorrowRecords()
})
</script>

<style scoped>
.borrow-manage {
  padding: 20px;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}

.sort-controls {
  display: flex;
  margin-right: 10px;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
}

.image-error {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 80px;
  background-color: #f5f7fa;
  color: #c0c4cc;
}

.no-cover {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 80px;
  background-color: #f5f7fa;
  color: #909399;
  font-size: 12px;
}
</style>