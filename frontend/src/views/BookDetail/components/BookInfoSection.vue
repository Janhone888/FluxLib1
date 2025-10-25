<template>
  <el-card class="book-info-card" shadow="hover">
    <div class="book-header">
      <div class="back-action">
        <el-button icon="ArrowLeft" @click="$emit('go-back')">返回</el-button>
      </div>
      <div class="title-section">
        <h1 class="book-title">{{ book.title }}</h1>
        <div class="book-subtitle">
          <span class="author">{{ book.author }}</span>
          <el-divider direction="vertical" />
          <span class="publisher">{{ book.publisher }}</span>
        </div>
      </div>
      <div class="header-actions" v-if="userIsAdmin">
        <el-button type="primary" @click="$emit('edit-book')" icon="Edit">编辑</el-button>
        <el-button type="danger" @click="$emit('delete-book')" icon="Delete">删除</el-button>
      </div>
    </div>

    <div class="book-content">
      <!-- 左侧封面区域 -->
      <div class="cover-section">
        <div class="cover-container">
          <el-image
            :src="book.cover"
            fit="contain"
            class="book-cover-image"
            :preview-src-list="[book.cover]"
          >
            <template #error>
              <div class="cover-error">
                <el-icon size="48"><Picture /></el-icon>
                <span>封面加载失败</span>
              </div>
            </template>
            <template #placeholder>
              <div class="cover-loading">
                <el-icon class="loading-icon"><Loading /></el-icon>
                <span>加载中...</span>
              </div>
            </template>
          </el-image>

          <!-- 收藏按钮 -->
          <div class="cover-actions">
            <el-button
              :type="isFavorited ? 'warning' : 'default'"
              @click="$emit('toggle-favorite')"
              :icon="isFavorited ? 'StarFilled' : 'Star'"
              class="favorite-btn"
              round
            >
              {{ isFavorited ? '已收藏' : '收藏' }}
            </el-button>
          </div>
        </div>
      </div>

      <!-- 右侧详细信息 -->
      <div class="info-section">
        <!-- 基础信息网格 -->
        <div class="info-grid">
          <div class="info-item">
            <label class="info-label">ISBN</label>
            <span class="info-value">{{ book.isbn || '暂无' }}</span>
          </div>
          <div class="info-item">
            <label class="info-label">分类</label>
            <el-tag :type="getCategoryTagType(book.category)" effect="light">
              {{ getCategoryName(book.category) }}
            </el-tag>
          </div>
          <div class="info-item">
            <label class="info-label">价格</label>
            <span class="info-value price">¥{{ book.price?.toFixed(2) || '0.00' }}</span>
          </div>
          <div class="info-item">
            <label class="info-label">库存状态</label>
            <div class="stock-info">
              <el-tag :type="book.stock > 0 ? 'success' : 'danger'" effect="light">
                {{ book.stock > 0 ? `${book.stock} 本可借` : '暂无库存' }}
              </el-tag>
              <el-tag :type="getStatusTagType(book.status)" class="status-tag">
                {{ getStatusName(book.status) }}
              </el-tag>
            </div>
          </div>
        </div>

        <!-- 图书概述 -->
        <div class="summary-section" v-if="book.summary">
          <h3 class="section-title">图书概述</h3>
          <p class="summary-text">{{ book.summary }}</p>
        </div>

        <!-- 详细描述 -->
        <div class="description-section" v-if="book.description">
          <h3 class="section-title">内容简介</h3>
          <p class="description-text">{{ book.description }}</p>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { Picture, Loading, Star, StarFilled, Edit, Delete, ArrowLeft } from '@element-plus/icons-vue'

interface Props {
  book: any
  isFavorited: boolean
  hasBorrowed: boolean
  userIsAdmin?: boolean
}

defineProps<Props>()
defineEmits(['toggle-favorite', 'edit-book', 'delete-book', 'go-back'])

// 工具方法
const getCategoryTagType = (category: string) => {
  const types: Record<string, string> = {
    literature: '',
    technology: 'success',
    art: 'warning',
    history: 'info',
    science: 'danger'
  }
  return types[category] || ''
}

const getCategoryName = (category: string) => {
  const names: Record<string, string> = {
    literature: '文学',
    technology: '科技',
    art: '艺术',
    history: '历史',
    science: '科学'
  }
  return names[category] || '未知'
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
  return names[status] || '未知'
}
</script>

<style scoped>
.book-info-card {
  border-radius: 12px;
  overflow: hidden;
}

.book-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.back-action {
  flex-shrink: 0;
}

.title-section {
  flex: 1;
  margin: 0 24px;
}

.book-title {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 8px 0;
  line-height: 1.3;
}

.book-subtitle {
  display: flex;
  align-items: center;
  color: #6b7280;
  font-size: 16px;
}

.header-actions {
  flex-shrink: 0;
  display: flex;
  gap: 8px;
}

/* 图书内容布局 */
.book-content {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 32px;
  align-items: start;
}

/* 封面区域 */
.cover-section {
  position: sticky;
  top: 20px;
}

.cover-container {
  text-align: center;
}

.book-cover-image {
  width: 100%;
  height: 400px;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
  margin-bottom: 16px;
}

.book-cover-image:hover {
  transform: translateY(-4px);
}

.cover-error,
.cover-loading {
  width: 100%;
  height: 400px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
  border-radius: 12px;
  color: #9ca3af;
}

.loading-icon {
  animation: rotating 2s linear infinite;
}

.cover-actions {
  margin-top: 16px;
}

.favorite-btn {
  width: 100%;
}

/* 信息区域 */
.info-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  padding: 20px;
  background: #f8fafc;
  border-radius: 8px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
}

.info-value {
  font-size: 16px;
  color: #1f2937;
  font-weight: 600;
}

.price {
  color: #f59e0b;
  font-size: 18px;
}

.stock-info {
  display: flex;
  gap: 8px;
  align-items: center;
}

.status-tag {
  margin-left: 8px;
}

/* 文本内容区域 */
.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 12px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid #e5e7eb;
}

.summary-text,
.description-text {
  line-height: 1.6;
  color: #4b5563;
  margin: 0;
  font-size: 15px;
}

/* 动画 */
@keyframes rotating {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 响应式调整 */
@media (max-width: 768px) {
  .book-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .title-section {
    margin: 0;
    text-align: center;
  }

  .header-actions {
    justify-content: center;
  }

  .book-content {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .cover-section {
    position: static;
  }

  .book-cover-image {
    height: 300px;
  }

  .info-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
}

@media (max-width: 480px) {
  .book-title {
    font-size: 24px;
  }

  .book-cover-image {
    height: 250px;
  }
}
</style>