<template>
  <el-card
    :body-style="{ padding: '0px' }"
    shadow="hover"
    class="book-card"
    @click="$emit('click')"
  >
    <div class="book-cover-container">
      <el-image :src="book.cover" fit="cover" class="book-cover" v-if="book.cover">
        <template #error>
          <div class="book-cover-placeholder">
            <el-icon><Picture /></el-icon>
          </div>
        </template>
      </el-image>
      <div class="book-cover-placeholder" v-else>
        <el-icon><Picture /></el-icon>
      </div>
    </div>

    <div class="book-info">
      <div class="book-title">{{ book.title }}</div>
      <div class="book-author">{{ book.author }}</div>

      <div class="book-meta">
        <div class="book-category">
          <el-tag :type="getCategoryTagType(book.category)" size="small">
            {{ getCategoryName(book.category) }}
          </el-tag>
        </div>

        <div class="book-status">
          <el-tag :type="getStatusTagType(book.status)" size="small">
            {{ getStatusName(book.status) }}
          </el-tag>
          <span class="stock-text">库存: {{ book.stock }}</span>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { Picture } from '@element-plus/icons-vue'

interface Props {
  book: any
}

defineProps<Props>()
defineEmits(['click'])

// 工具方法 - 这些可以从主组件传入，但为了组件独立性，先放在这里
const getCategoryTagType = (category: string) => {
  const types: Record<string, string> = {
    computer: '',
    literature: 'success',
    economy: 'warning',
    history: 'danger',
    science: 'info',
    art: 'primary',
    management: 'success',
    education: 'warning'
  }
  return types[category] || ''
}

const getCategoryName = (category: string) => {
  const names: Record<string, string> = {
    computer: '计算机',
    literature: '文学',
    economy: '经济',
    history: '历史',
    science: '科学',
    art: '艺术',
    management: '管理',
    education: '教育'
  }
  return names[category] || category
}

const getStatusTagType = (status: string) => {
  const types: Record<string, string> = {
    available: 'success',
    borrowed: 'warning',
    maintenance: 'danger'
  }
  return types[status] || 'info'
}

const getStatusName = (status: string) => {
  const names: Record<string, string> = {
    available: '可借阅',
    borrowed: '已借出',
    maintenance: '维护中'
  }
  return names[status] || status
}
</script>

<style scoped>
.book-card {
  margin-bottom: 20px;
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  height: 100%;
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
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.book-info {
  padding: 15px;
}

.book-title {
  font-weight: bold;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 16px;
  color: #1f2937;
}

.book-author {
  color: #6b7280;
  margin-bottom: 12px;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.book-category {
  margin-bottom: 8px;
}

.book-status {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stock-text {
  font-size: 12px;
  color: #6b7280;
}
</style>