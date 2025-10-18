<template>
  <div class="favorites-page">
    <div class="page-header">
      <el-button icon="ArrowLeft" @click="router.back()" class="back-btn">返回</el-button>
      <h1>我的收藏</h1>
    </div>

    <div class="favorites-container">
      <div v-if="favorites.length === 0" class="empty-state">
        <el-empty description="您还没有收藏任何图书" />
        <el-button type="primary" @click="router.push('/books')" class="mt-4">去收藏图书</el-button>
      </div>
      <el-table :data="favorites" style="width: 100%" v-else>
        <el-table-column label="图书封面" width="100">
          <template #default="{ row }">
            <el-image :src="row.book_cover" fit="cover" style="width: 60px; height: 80px" />
          </template>
        </el-table-column>
        <el-table-column prop="book_title" label="书名" />
        <el-table-column prop="book_author" label="作者" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button link @click="goToBookDetail(row.book_id)">查看</el-button>
            <el-button link @click="removeFavorite(row.book_id)">取消收藏</el-button>
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
const favorites = ref([])

onMounted(() => {
  fetchFavorites()
})

const fetchFavorites = async () => {
  try {
    const response = await api.getFavorites()
    let favoritesData = []

    if (response.data && Array.isArray(response.data)) {
      favoritesData = response.data
    } else if (response.data && response.data.items) {
      favoritesData = response.data.items
    }

    favorites.value = favoritesData
  } catch (error) {
    console.error('获取收藏列表失败', error)
    ElMessage.error('获取收藏列表失败')
  }
}

const removeFavorite = async (bookId) => {
  try {
    await api.removeFavorite(bookId)
    ElMessage.success('取消收藏成功')
    fetchFavorites()
  } catch (error) {
    ElMessage.error('取消收藏失败')
  }
}

const goToBookDetail = (bookId) => {
  router.push(`/book/${bookId}`)
}
</script>

<style scoped>
.favorites-page {
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

.favorites-container {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.empty-state {
  text-align: center;
  padding: 40px 0;
}

.mt-4 {
  margin-top: 16px;
}
</style>