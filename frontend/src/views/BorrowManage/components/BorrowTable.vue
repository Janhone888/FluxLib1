<template>
  <el-table
    :data="records"
    @selection-change="$emit('selection-change', $event)"
    v-loading="loading"
    class="borrow-table"
  >
    <el-table-column type="selection" width="55" />

    <el-table-column prop="book_title" label="图书名称" min-width="200">
      <template #default="{ row }">
        <div class="book-info">
          <span class="book-title">{{ row.book_title }}</span>
          <span class="book-author" v-if="row.book_author"> - {{ row.book_author }}</span>
        </div>
      </template>
    </el-table-column>

    <el-table-column label="封面" width="120">
      <template #default="{ row }">
        <BookCover :cover="row.book_cover" />
      </template>
    </el-table-column>

    <el-table-column prop="borrow_date" label="借阅日期" width="180">
      <template #default="{ row }">
        {{ formatDate(row.borrow_date) }}
      </template>
    </el-table-column>

    <el-table-column prop="due_date" label="应还日期" width="180">
      <template #default="{ row }">
        {{ formatDate(row.due_date) }}
      </template>
    </el-table-column>

    <el-table-column label="状态" width="120">
      <template #default="{ row }">
        <StatusTag :status="row.status" />
      </template>
    </el-table-column>

    <el-table-column label="操作" width="120" fixed="right">
      <template #default="{ row }">
        <ReturnButton
          :record="row"
          @click="$emit('return-book', row.borrow_id)"
        />
      </template>
    </el-table-column>
  </el-table>
</template>

<script setup lang="ts">
import BookCover from './BookCover.vue'
import StatusTag from './StatusTag.vue'
import ReturnButton from './ReturnButton.vue'

interface Props {
  records: any[]
  loading?: boolean
}

withDefaults(defineProps<Props>(), {
  loading: false
})

defineEmits(['selection-change', 'return-book'])

const formatDate = (timestamp: number) => {
  return new Date(timestamp * 1000).toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.borrow-table {
  width: 100%;
}

.book-info {
  display: flex;
  flex-direction: column;
}

.book-title {
  font-weight: 500;
  margin-bottom: 4px;
}

.book-author {
  font-size: 12px;
  color: #909399;
}
</style>