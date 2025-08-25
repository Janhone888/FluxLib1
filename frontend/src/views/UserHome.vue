<template>
  <div class="user-home">
    <el-row :gutter="20">
      <!-- 公告区域 -->
      <el-col :span="16">
        <el-card>
          <template #header>
            <h3>图书馆公告</h3>
          </template>
          <div v-if="announcements.length > 0">
            <el-timeline>
              <el-timeline-item
                v-for="announcement in announcements"
                :key="announcement.announcement_id"
                :timestamp="formatDate(announcement.publish_time)"
                placement="top"
              >
                <el-card>
                  <h4>{{ announcement.title }}</h4>
                  <p>{{ announcement.content }}</p>
                </el-card>
              </el-timeline-item>
            </el-timeline>
          </div>
          <div v-else class="empty-state">
            <el-empty description="暂无公告" />
          </div>
        </el-card>
      </el-col>

      <!-- 我的借阅记录 -->
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="flex-between">
              <h3>我的借阅记录</h3>
              <el-link type="primary" :underline="false" @click="$router.push('/borrows')">查看全部</el-link>
            </div>
          </template>

          <el-table :data="myBorrows" v-if="myBorrows.length > 0" style="width: 100%">
            <el-table-column prop="book_title" label="图书名称" />
            <el-table-column label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.status === 'returned' ? 'success' : 'warning'" size="small">
                  {{ row.status === 'returned' ? '已归还' : '借阅中' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="due_date" label="应还日期" width="100">
              <template #default="{ row }">
                {{ formatDate(row.due_date) }}
              </template>
            </el-table-column>
          </el-table>

          <div v-else class="empty-tip">
            <p>您还没有借过书</p>
            <el-button type="text" @click="$router.push('/books')">去借书</el-button>
          </div>
        </el-card>

        <!-- 推荐图书 -->
        <el-card class="mt-20">
          <template #header>
            <h3>推荐图书</h3>
          </template>
          <div v-if="recommendedBooks.length > 0">
            <div v-for="book in recommendedBooks" :key="book.book_id" class="book-item" @click="goToBookDetail(book.book_id)">
              <el-image :src="book.cover" fit="cover" class="book-cover" />
              <div class="book-info">
                <div class="book-title">{{ book.title }}</div>
                <div class="book-author">{{ book.author }}</div>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">
            <el-empty description="暂无推荐" />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/utils/api'

const router = useRouter()
const announcements = ref([])
const myBorrows = ref([])
const recommendedBooks = ref([])

onMounted(() => {
  fetchAnnouncements()
  fetchMyBorrows()
  fetchRecommendedBooks()
})

const fetchAnnouncements = async () => {
  try {
    const response = await api.getAnnouncements()
    announcements.value = response.data
  } catch (error) {
    console.error('获取公告失败', error)
  }
}

const fetchMyBorrows = async () => {
  try {
    const response = await api.getUserBorrows()
    myBorrows.value = (response.data.items || []).slice(0, 5)
  } catch (error) {
    console.error('获取借阅记录失败', error)
  }
}

const fetchRecommendedBooks = async () => {
  try {
    // 获取热门图书作为推荐
    const response = await api.getBooks(1, 4)
    recommendedBooks.value = response.data.items || []
  } catch (error) {
    console.error('获取推荐图书失败', error)
  }
}

const formatDate = (timestamp) => {
  if (!timestamp) return '未知'
  return new Date(timestamp * 1000).toLocaleDateString()
}

const goToBookDetail = (bookId) => {
  router.push(`/books/${bookId}`)
}
</script>

<style scoped>
.user-home {
  padding: 20px;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
}

.empty-tip {
  text-align: center;
  padding: 20px;
  color: #999;
}

.mt-20 {
  margin-top: 20px;
}

.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.book-item {
  display: flex;
  margin-bottom: 15px;
  cursor: pointer;
  padding: 10px;
  border-radius: 6px;
  transition: background-color 0.3s;
}

.book-item:hover {
  background-color: #f5f7fa;
}

.book-cover {
  width: 60px;
  height: 80px;
  border-radius: 4px;
  margin-right: 15px;
}

.book-info {
  flex: 1;
}

.book-title {
  font-weight: bold;
  margin-bottom: 5px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-author {
  font-size: 12px;
  color: #666;
}
</style>