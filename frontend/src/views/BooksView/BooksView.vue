<template>
  <div class="books-view">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <h2>{{ userStore.userInfo.is_admin ? '图书管理' : '图书浏览' }}</h2>
          <SearchAndFilter
            v-model:search-query="searchQuery"
            v-model:selected-category="selectedCategory"
            :categories="categories"
            :show-add-button="userStore.userInfo.is_admin"
            @search="handleSearch"
            @filter="handleFilter"
            @add-book="goToAdd"
          />
        </div>
      </template>

      <!-- 图书列表 -->
      <BookList
        :books="paginatedBooks"
        :loading="loading"
        @book-click="goToDetail"
      />

      <!-- 分页 -->
      <Pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="totalBooks"
        @page-change="handlePageChange"
        @size-change="handleSizeChange"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useBookStore } from '@/stores/books'

import SearchAndFilter from './components/SearchAndFilter.vue'
import BookList from './components/BookList.vue'
import Pagination from './components/Pagination.vue'

import { useBooks } from './composables/useBooks'
import { useSearch } from './composables/useSearch'
import { usePagination } from './composables/usePagination'

const router = useRouter()
const userStore = useUserStore()
const bookStore = useBookStore()

// 使用组合式函数组织逻辑
const {
  categories,
  getCategoryName,
  getCategoryTagType,
  getStatusName,
  getStatusTagType
} = useBooks()

const {
  searchQuery,
  selectedCategory,
  filteredBooks,
  handleSearch,
  handleFilter
} = useSearch(bookStore)

const {
  currentPage,
  pageSize,
  totalBooks,
  paginatedBooks,
  loading,
  handlePageChange,
  handleSizeChange,
  fetchBooks
} = usePagination(bookStore, selectedCategory)

// 导航方法
const goToDetail = (bookId: string) => {
  router.push({ name: 'BookDetail', params: { id: bookId } })
}

const goToAdd = () => {
  router.push('/add')
}

// 添加成功后自动刷新
const handleBookAdded = () => {
  fetchBooks()
}

onMounted(() => {
  fetchBooks()
  // 监听全局事件：当有新书添加时刷新列表
  window.addEventListener('book-added', handleBookAdded)
})

onUnmounted(() => {
  window.removeEventListener('book-added', handleBookAdded)
})
</script>

<style scoped>
.books-view {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.card-header h2 {
  margin: 0;
  flex-shrink: 0;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .books-view {
    padding: 16px;
  }

  .card-header {
    flex-direction: column;
    align-items: stretch;
  }

  .card-header h2 {
    text-align: center;
  }
}
</style>