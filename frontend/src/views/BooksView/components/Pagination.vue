<template>
  <div class="pagination-container">
    <el-pagination
      background
      layout="prev, pager, next, sizes, total"
      :total="total"
      :page-size="pageSize"
      :current-page="currentPage"
      :page-sizes="[12, 24, 48, 96]"
      @current-change="$emit('page-change', $event)"
      @size-change="$emit('size-change', $event)"
    />
  </div>
</template>

<script setup lang="ts">
interface Props {
  currentPage: number
  pageSize: number
  total: number
}

interface Emits {
  (e: 'update:currentPage', value: number): void
  (e: 'update:pageSize', value: number): void
  (e: 'page-change', value: number): void
  (e: 'size-change', value: number): void
}

defineProps<Props>()
defineEmits<Emits>()
</script>

<style scoped>
.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .pagination-container {
    justify-content: center;
  }
}
</style>