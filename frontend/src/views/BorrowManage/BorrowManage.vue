<template>
  <div class="borrow-manage">
    <el-card>
      <template #header>
        <div class="header-content">
          <h2>借阅管理</h2>
          <div class="header-actions">
            <SortControls
              @sort-by-status="handleSortByStatus"
              @sort-by-date="handleSortByDate"
            />
            <BatchActions
              :selected-count="selectedBorrows.length"
              @batch-return="handleBatchReturn"
            />
          </div>
        </div>
      </template>

      <!-- 借阅记录表格 -->
      <BorrowTable
        :records="borrowRecords"
        :loading="loading"
        @selection-change="handleSelectionChange"
        @return-book="handleReturnBook"
      />

      <!-- 空状态 -->
      <EmptyState
        v-if="borrowRecords.length === 0 && !loading"
        @go-to-books="goToBooks"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

import SortControls from './components/SortControls.vue'
import BatchActions from './components/BatchActions.vue'
import BorrowTable from './components/BorrowTable.vue'
import EmptyState from './components/EmptyState.vue'

import { useBorrowRecords } from './composables/useBorrowRecords'
import { useBorrowActions } from './composables/useBorrowActions'
import { useBorrowSort } from './composables/useBorrowSort'

const router = useRouter()

// 使用组合式函数组织逻辑
const {
  borrowRecords,
  loading,
  selectedBorrows,
  fetchBorrowRecords,
  handleSelectionChange
} = useBorrowRecords()

const {
  returnBook,
  batchReturn
} = useBorrowActions(fetchBorrowRecords)

const {
  sortByStatus,
  sortByDate
} = useBorrowSort(borrowRecords)

// 处理单个归还
const handleReturnBook = (borrowId: string) => {
  returnBook(borrowId)
}

// 处理批量归还
const handleBatchReturn = () => {
  const borrowIds = selectedBorrows.value.map(item => item.borrow_id)
  batchReturn(borrowIds)
}

// 处理排序
const handleSortByStatus = () => {
  sortByStatus()
}

const handleSortByDate = () => {
  sortByDate()
}

// 跳转到图书列表
const goToBooks = () => {
  router.push('/books')
}

// 页面挂载时加载数据
onMounted(() => {
  fetchBorrowRecords()
})
</script>

<style scoped>
.borrow-manage {
  padding: 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .borrow-manage {
    padding: 16px;
  }

  .header-content {
    flex-direction: column;
    align-items: stretch;
  }

  .header-actions {
    justify-content: space-between;
  }
}

@media (max-width: 480px) {
  .header-actions {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>