<template>
  <div class="book-management">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <h2>图书管理</h2>
          <div class="header-actions">
            <el-button type="primary" icon="el-icon-circle-plus" @click="goToAdd">添加新书</el-button>
            <el-input
              v-model="searchQuery"
              placeholder="搜索图书..."
              prefix-icon="el-icon-search"
              style="width: 300px; margin-left: 15px;"
              @input="searchBooks"
            />
            <el-select v-model="selectedCategory" placeholder="全部类别" style="width: 150px; margin-left: 15px;" @change="filterByCategory">
              <el-option label="全部" value=""></el-option>
              <el-option v-for="category in categories" :key="category.value" :label="category.label" :value="category.value"></el-option>
            </el-select>
          </div>
        </div>
      </template>

      <!-- 图书卡片展示 -->
      <div class="book-list">
        <el-row :gutter="20">
          <el-col :span="6" v-for="book in paginatedBooks" :key="book.book_id">
            <el-card :body-style="{ padding: '0px' }" shadow="hover" class="book-card" @click="goToDetail(book.book_id)">
              <div class="book-cover-container">
                <el-image :src="book.cover" fit="cover" class="book-cover" v-if="book.cover" />
                <div class="book-cover-placeholder" v-else>
                  <el-icon><Picture /></el-icon>
                </div>
              </div>
              <div class="book-info">
                <div class="book-title">{{ book.title }}</div>
                <div class="book-category">
                  <el-tag :type="getCategoryTagType(book.category)">{{ getCategoryName(book.category) }}</el-tag>
                </div>
                <div class="book-status">
                  <el-tag :type="getStatusTagType(book.status)">{{ getStatusName(book.status) }}</el-tag>
                  <span>库存: {{ book.stock }}</span>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <div class="pagination-container">
        <el-pagination
          background
          layout="prev, pager, next, sizes, total"
          :total="totalBooks"
          :page-size="pageSize"
          :current-page="currentPage"
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        ></el-pagination>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Picture } from '@element-plus/icons-vue'
import { useBookStore } from '@/stores/books'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const bookStore = useBookStore()
const userStore = useUserStore()

const books = ref([])
const filteredBooks = ref([])
const loading = ref(true)
const searchQuery = ref('')
const totalBooks = ref(0)
const currentPage = ref(1)
const pageSize = ref(12)
const selectedCategory = ref('')

// 图书状态映射
const statusMap = {
  available: { name: '可借阅', type: 'success' },
  borrowed: { name: '已借出', type: 'warning' },
  maintenance: { name: '维护中', type: 'danger' }
}

// 图书分类映射
const categoryMap = {
  computer: { name: '计算机', type: '' },
  literature: { name: '文学', type: 'success' },
  economy: { name: '经济', type: 'warning' },
  history: { name: '历史', type: 'danger' },
  science: { name: '科学', type: 'info' },
  art: { name: '艺术', type: 'primary' },
  management: { name: '管理', type: 'success' },
  education: { name: '教育', type: 'warning' }
}

const categories = ref([
  { value: 'computer', label: '计算机' },
  { value: 'literature', label: '文学' },
  { value: 'economy', label: '经济' },
  { value: 'history', label: '历史' },
  { value: 'science', label: '科学' },
  { value: 'art', label: '艺术' },
  { value: 'management', label: '管理' },
  { value: 'education', label: '教育' }
])

const getStatusName = (status) => statusMap[status]?.name || status
const getStatusTagType = (status) => statusMap[status]?.type || ''
const getCategoryName = (category) => categoryMap[category]?.name || category
const getCategoryTagType = (category) => categoryMap[category]?.type || ''

const fetchBooks = async () => {
  try {
    loading.value = true
    const response = await bookStore.fetchBooks(currentPage.value, pageSize.value, selectedCategory.value)
    books.value = response.items
    filteredBooks.value = [...books.value]
    totalBooks.value = response.total
  } catch (error) {
    ElMessage.error('获取图书数据失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

const searchBooks = () => {
  if (!searchQuery.value) {
    filteredBooks.value = [...books.value]
    return
  }

  const query = searchQuery.value.toLowerCase()
  filteredBooks.value = books.value.filter(book =>
    book.title.toLowerCase().includes(query) ||
    book.author.toLowerCase().includes(query) ||
    book.publisher.toLowerCase().includes(query)
  )
}

const filterByCategory = () => {
  if (!selectedCategory.value) {
    filteredBooks.value = [...books.value]
    return
  }

  filteredBooks.value = books.value.filter(book => book.category === selectedCategory.value)
}

const handlePageChange = (page) => {
  currentPage.value = page
  fetchBooks()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  fetchBooks()
}

const paginatedBooks = computed(() => {
  return filteredBooks.value
})

const goToDetail = (bookId) => {
  router.push({ name: 'BookDetail', params: { id: bookId } })
}

const goToAdd = () => {
  router.push('/add')
}

// 监听图书库变化
watch(
  () => bookStore.books,
  (newBooks) => {
    books.value = newBooks
    filteredBooks.value = [...newBooks]
    totalBooks.value = bookStore.total
  },
  { deep: true }
)

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
.book-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.book-list {
  margin-top: 20px;
}

.book-card {
  margin-bottom: 20px;
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.book-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.book-cover-container {
  height: 200px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa;
}

.book-cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.book-cover-placeholder {
  font-size: 60px;
  color: #c0c4cc;
}

.book-info {
  padding: 15px;
}

.book-title {
  font-weight: bold;
  margin-bottom: 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-category {
  margin-bottom: 10px;
}

.book-status {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>