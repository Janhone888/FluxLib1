<template>
  <div class="book-filter">
    <div class="filter-group">
      <el-select
        v-model="category"
        placeholder="全部分类"
        clearable
        @change="emitFilterChange"
        class="filter-select"
      >
        <el-option label="全部分类" value="" />
        <el-option
          v-for="cat in categories"
          :key="cat.value"
          :label="cat.label"
          :value="cat.value"
        />
      </el-select>
    </div>

    <div class="filter-group">
      <el-select
        v-model="status"
        placeholder="全部状态"
        clearable
        @change="emitFilterChange"
        class="filter-select"
      >
        <el-option label="全部状态" value="" />
        <el-option label="可借阅" value="available" />
        <el-option label="已借出" value="borrowed" />
        <el-option label="维护中" value="maintenance" />
      </el-select>
    </div>

    <div class="filter-group">
      <el-select
        v-model="sort"
        placeholder="排序方式"
        @change="emitFilterChange"
        class="filter-select"
      >
        <el-option label="最新上架" value="newest" />
        <el-option label="最受欢迎" value="popular" />
        <el-option label="价格从低到高" value="price_asc" />
        <el-option label="价格从高到低" value="price_desc" />
      </el-select>
    </div>

    <el-button
      type="default"
      icon="el-icon-refresh"
      @click="resetFilters"
      class="reset-btn"
    >
      重置
    </el-button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['update:category', 'update:status', 'update:sort', 'filter-change'])

const props = defineProps({
  category: {
    type: String,
    default: ''
  },
  status: {
    type: String,
    default: ''
  },
  sort: {
    type: String,
    default: 'newest'
  }
})

const category = ref(props.category)
const status = ref(props.status)
const sort = ref(props.sort)

const categories = [
  { value: 'computer', label: '计算机' },
  { value: 'literature', label: '文学' },
  { value: 'economy', label: '经济' },
  { value: 'history', label: '历史' },
  { value: 'science', label: '科学' },
  { value: 'art', label: '艺术' },
  { value: 'management', label: '管理' },
  { value: 'education', label: '教育' }
]

const emitFilterChange = () => {
  emit('update:category', category.value)
  emit('update:status', status.value)
  emit('update:sort', sort.value)
  emit('filter-change')
}

const resetFilters = () => {
  category.value = ''
  status.value = ''
  sort.value = 'newest'
  emitFilterChange()
}
</script>

<style scoped>
.book-filter {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
}

.filter-select {
  width: 140px;
}

.filter-select:deep(.el-input__wrapper) {
  border-radius: 8px;
}

.reset-btn {
  border-radius: 8px;
  padding: 10px 16px;
}

@media (max-width: 768px) {
  .book-filter {
    justify-content: space-between;
  }

  .filter-select {
    width: 120px;
  }
}

@media (max-width: 480px) {
  .book-filter {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-select {
    width: 100%;
  }
}
</style>