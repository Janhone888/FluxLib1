<template>
  <div class="book-detail-container">
    <!-- 面包屑导航 -->
    <div class="breadcrumb">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/books' }">
          图书{{ userStore.userInfo.is_admin ? '管理' : '浏览' }}
        </el-breadcrumb-item>
        <el-breadcrumb-item>图书详情</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <div class="book-detail">
      <!-- 主要内容区域 -->
      <div class="main-content">
        <!-- 图书基础信息卡片 -->
        <BookInfoSection
          :book="book"
          :is-favorited="isFavorited"
          :has-borrowed="hasBorrowed"
          @toggle-favorite="toggleFavorite"
          @edit-book="editBook"
          @delete-book="deleteBook"
          @go-back="goBack"
        />

        <!-- 借阅操作区域 -->
        <BorrowActions
          :book="book"
          :has-borrowed="hasBorrowed"
          :user-is-admin="userStore.userInfo.is_admin"
          @borrow="borrowBook"
          @return="confirmReturn"
          @reserve="showReserveDialog"
        />
      </div>

      <!-- 借阅历史 -->
      <BorrowHistoryCard
        v-if="borrowRecords.length > 0"
        :records="borrowRecords"
      />

      <!-- 评论区 -->
      <CommentSection
        :book-id="bookId"
        :comments="comments"
        :total-comments-count="totalCommentsCount"
        @submit-comment="submitComment"
        @like-comment="likeComment"
        @reply-comment="handleReply"
      />
    </div>

    <!-- 预约对话框 -->
    <ReservationDialog
      v-model:visible="reserveDialogVisible"
      @submit="submitReservation"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

import { useUserStore } from '@/stores/user'
import { useBookStore } from '@/stores/books'

import BookInfoSection from './components/BookInfoSection.vue'
import BorrowActions from './components/BorrowActions.vue'
import BorrowHistoryCard from './components/BorrowHistoryCard.vue'
import CommentSection from './components/CommentSection.vue'
import ReservationDialog from './components/ReservationDialog.vue'

import { useBookDetail } from './composables/useBookDetail'
import { useBorrowActions } from './composables/useBorrowActions'
import { useComments } from './composables/useComments'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const bookStore = useBookStore()

// 获取图书ID
const bookId = computed(() => {
  const id = route.params.id
  if (!id) {
    ElMessage.error('图书ID缺失，无法加载详情')
    router.push('/books')
    return ''
  }
  return id as string
})

// 使用组合式函数组织逻辑
const {
  book,
  loading,
  isFavorited,
  hasBorrowed,
  borrowRecords,
  fetchBookDetail,
  toggleFavorite,
  editBook,
  deleteBook,
  goBack
} = useBookDetail(bookId, userStore, bookStore, router)

const {
  reserveDialogVisible,
  borrowBook,
  confirmReturn,
  showReserveDialog,
  submitReservation
} = useBorrowActions(bookId, bookStore, fetchBookDetail)

const {
  comments,
  totalCommentsCount,
  fetchComments,
  submitComment,
  likeComment,
  handleReply
} = useComments(bookId)

// 页面挂载时加载数据
onMounted(() => {
  fetchBookDetail()
  fetchComments()
})
</script>

<style scoped>
.book-detail-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  background: #f5f7fa;
  min-height: 100vh;
}

.breadcrumb {
  margin-bottom: 20px;
}

.book-detail {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.main-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .book-detail-container {
    padding: 16px;
  }

  .main-content {
    gap: 16px;
  }
}
</style>