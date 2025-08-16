<template>
  <div class="book-detail">
    <el-card class="book-card">
      <div class="book-header">
        <el-button icon="el-icon-arrow-left" @click="goBack">返回</el-button>
        <h2>{{ book.title }}</h2>
        <div class="book-actions" v-if="userStore.userInfo.role === 'admin'">
          <el-button type="primary" @click="editBook">编辑</el-button>
          <el-button type="danger" @click="deleteBook">删除</el-button>
        </div>
      </div>

      <div class="book-content">
        <div class="book-cover">
          <el-image :src="book.cover" fit="contain" style="height: 300px" v-if="book.cover">
            <template #error>
              <div class="image-error">
                <el-icon><Picture /></el-icon>
                <span>图片加载失败</span>
              </div>
            </template>
          </el-image>
          <div class="no-cover" v-else>
            无封面
          </div>
        </div>

        <div class="book-info">
          <div class="info-row">
            <span class="label">作者：</span>
            <span>{{ book.author }}</span>
          </div>
          <div class="info-row">
            <span class="label">出版社：</span>
            <span>{{ book.publisher }}</span>
          </div>
          <div class="info-row">
            <span class="label">ISBN：</span>
            <span>{{ book.isbn }}</span>
          </div>
          <div class="info-row">
            <span class="label">分类：</span>
            <el-tag :type="getCategoryTagType(book.category)">
              {{ getCategoryName(book.category) }}
            </el-tag>
          </div>
          <div class="info-row">
            <span class="label">价格：</span>
            <span>¥{{ book.price.toFixed(2) }}</span>
          </div>
          <div class="info-row">
            <span class="label">库存：</span>
            <el-tag :type="book.stock > 0 ? 'success' : 'danger'">
              {{ book.stock }} 本
            </el-tag>
          </div>
          <div class="info-row">
            <span class="label">状态：</span>
            <el-tag :type="getStatusTagType(book.status)">
              {{ getStatusName(book.status) }}
            </el-tag>
          </div>
          <div class="info-row">
            <span class="label">描述：</span>
            <p>{{ book.description }}</p>
          </div>
        </div>
      </div>

      <div class="book-borrow-actions">
        <!-- 添加借阅期限选择 -->
        <el-select v-model="selectedDays" placeholder="选择借阅期限" v-if="book.stock > 0 && !hasBorrowed">
          <el-option label="7天" :value="7" />
          <el-option label="15天" :value="15" />
          <el-option label="30天" :value="30" />
        </el-select>

        <el-button
          type="primary"
          :disabled="book.stock <= 0 || hasBorrowed"
          @click="borrowBook"
          v-if="!hasBorrowed"
        >
          借阅本书
        </el-button>
        <el-button
          type="success"
          v-if="hasBorrowed"
          @click="returnBook"
        >
          归还本书
        </el-button>
      </div>

      <div class="borrow-history" v-if="borrowRecords.length > 0">
        <h3>借阅历史</h3>
        <el-table :data="borrowRecords" style="width: 100%">
          <el-table-column prop="borrower" label="借阅人" />
          <el-table-column prop="borrow_date" label="借阅日期">
            <template #default="{ row }">
              {{ formatDate(row.borrow_date) }}
            </template>
          </el-table-column>
          <el-table-column prop="return_date" label="归还日期">
            <template #default="{ row }">
              {{ row.return_date ? formatDate(row.return_date) : '未归还' }}
            </template>
          </el-table-column>
          <el-table-column label="状态">
            <template #default="{ row }">
              <el-tag :type="row.status === 'returned' ? 'success' : 'warning'">
                {{ row.status === 'returned' ? '已归还' : '借阅中' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Picture } from '@element-plus/icons-vue'
import { useBookStore } from '@/stores/books'
import { useUserStore } from '@/stores/user'
import api from '@/utils/api'

const route = useRoute()
const router = useRouter()
const bookStore = useBookStore()
const userStore = useUserStore()

const bookId = route.params.id
const book = ref({})
const borrowRecords = ref([])
const hasBorrowed = ref(false)
const loading = ref(false)
const selectedDays = ref(30)

// 状态和分类映射函数
const statusMap = {
  available: { name: '可借阅', type: 'success' },
  borrowed: { name: '已借出', type: 'warning' },
  maintenance: { name: '维护中', type: 'danger' }
}

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

const getStatusName = (status) => statusMap[status]?.name || status
const getStatusTagType = (status) => statusMap[status]?.type || ''
const getCategoryName = (category) => categoryMap[category]?.name || category
const getCategoryTagType = (category) => categoryMap[category]?.type || ''

const fetchBookDetail = async () => {
  try {
    loading.value = true
    await bookStore.fetchBook(bookId)
    book.value = bookStore.currentBook

    // 获取借阅记录
    // 这里需要根据实际API调整
    // const response = await api.getBorrowHistory(bookId)
    // borrowRecords.value = response.data

    // 检查当前用户是否借阅了此书
    // 暂时模拟
    hasBorrowed.value = false
  } catch (error) {
    ElMessage.error('获取图书详情失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 修改borrowBook方法，传入selectedDays
const borrowBook = async () => {
  try {
    await bookStore.borrowBook(bookId, selectedDays.value)
    ElMessage.success('借阅成功')
    fetchBookDetail() // 刷新数据
  } catch (error) {
    // 添加详细的错误提示
    const errorMessage = error.response?.data?.error || error.message
    ElMessage.error(`借阅失败: ${errorMessage}`)

    // 如果是认证问题，提示用户重新登录
    if (error.response?.status === 401) {
      ElMessage.warning('认证已过期，请重新登录')
      router.push('/login')
    }
  }
}

const returnBook = async () => {
  try {
    await bookStore.returnBook(bookId)
    ElMessage.success('归还成功')
    fetchBookDetail() // 刷新数据
  } catch (error) {
    const errorMessage = error.response?.data?.error || error.message
    ElMessage.error(`归还失败: ${errorMessage}`)

    if (error.response?.status === 401) {
      ElMessage.warning('认证已过期，请重新登录')
      router.push('/login')
    }
  }
}

const editBook = () => {
  router.push({ name: 'EditBook', params: { id: bookId } })
}

const deleteBook = () => {
  ElMessageBox.confirm('确定要删除这本书吗？删除后无法恢复', '删除确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await bookStore.deleteBook(bookId)
      ElMessage.success('删除成功')
      router.push('/books')
    } catch (error) {
      ElMessage.error('删除失败: ' + error.message)
    }
  }).catch(() => {})
}

const goBack = () => {
  router.go(-1)
}

const formatDate = (timestamp) => {
  return new Date(timestamp * 1000).toLocaleDateString()
}

onMounted(() => {
  fetchBookDetail()
})
</script>

<style scoped>
.book-detail {
  padding: 20px;
}

.book-card {
  max-width: 1000px;
  margin: 0 auto;
}

.book-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.book-header h2 {
  margin-left: 15px;
  flex-grow: 1;
}

.book-content {
  display: flex;
  gap: 30px;
  margin-bottom: 30px;
}

@media (max-width: 768px) {
  .book-content {
    flex-direction: column;
  }
}

.book-cover {
  flex: 0 0 300px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
  border-radius: 8px;
  overflow: hidden;
}

.no-cover {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
  font-size: 14px;
}

.image-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #c0c4cc;
  background-color: #f5f7fa;
}

.book-info {
  flex: 1;
}

.info-row {
  margin-bottom: 15px;
  display: flex;
}

.info-row .label {
  font-weight: bold;
  min-width: 80px;
}

.book-borrow-actions {
  margin: 20px 0;
  display: flex;
  gap: 15px;
  align-items: center;
}

.borrow-history {
  margin-top: 30px;
  border-top: 1px solid #eee;
  padding-top: 20px;
}
</style>