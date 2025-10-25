<template>
  <div class="book-list">
    <el-row :gutter="20" v-loading="loading">
      <el-col
        v-for="book in books"
        :key="book.book_id"
        :xs="24"
        :sm="12"
        :md="8"
        :lg="6"
        :xl="6"
      >
        <BookCard
          :book="book"
          @click="$emit('book-click', book.book_id)"
        />
      </el-col>
    </el-row>

    <!-- 空状态 -->
    <div v-if="books.length === 0 && !loading" class="empty-state">
      <el-empty description="暂无图书数据" />
    </div>
  </div>
</template>

<script setup lang="ts">
import BookCard from './BookCard.vue'

interface Props {
  books: any[]
  loading?: boolean
}

defineProps<Props>()
defineEmits(['book-click'])
</script>

<style scoped>
.book-list {
  margin-top: 20px;
  min-height: 400px;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
}
</style>