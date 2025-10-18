<template>
  <div class="history-page">
    <div class="page-header">
      <el-button icon="ArrowLeft" @click="router.back()" class="back-btn">返回</el-button>
      <h1>浏览历史</h1>
    </div>

    <div class="history-container">
      <el-table :data="viewHistory" style="width: 100%">
        <el-table-column label="图书封面" width="100">
          <template #default="{ row }">
            <el-image :src="row.book_cover" fit="cover" style="width: 60px; height: 80px" />
          </template>
        </el-table-column>
        <el-table-column prop="book_title" label="书名" />
        <el-table-column prop="book_author" label="作者" />
        <el-table-column prop="view_time" label="浏览时间">
          <template #default="{ row }">
            {{ formatDate(row.view_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-button link @click="goToBookDetail(row.book_id)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'

const router = useRouter()
const viewHistory = ref([])

onMounted(() => {
  fetchViewHistory()
})

const fetchViewHistory = async () => {
  try {
    const response = await api.getViewHistory()
    let historyData = []

    if (response.data && Array.isArray(response.data)) {
      historyData = response.data
    } else if (response.data && response.data.items) {
      historyData = response.data.items
    }

    viewHistory.value = historyData
  } catch (error) {
    console.error('获取浏览历史失败', error)
    ElMessage.error('获取浏览历史失败')
  }
}

const goToBookDetail = (bookId) => {
  router.push(`/book/${bookId}`)
}

const formatDate = (timestamp) => {
  if (!timestamp) return ''
  return new Date(timestamp * 1000).toLocaleString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.history-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.back-btn {
  margin-right: auto;
}

.history-container {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
</style>