<template>
  <div class="search-and-filter">
    <el-button
      v-if="showAddButton"
      type="primary"
      icon="el-icon-circle-plus"
      @click="$emit('add-book')"
      class="add-button"
    >
      添加新书
    </el-button>

    <div class="filter-controls">
      <el-input
        v-model="searchQuery"
        placeholder="搜索图书..."
        prefix-icon="el-icon-search"
        @input="$emit('search', searchQuery)"
        class="search-input"
        clearable
      />

      <el-select
        v-model="selectedCategory"
        placeholder="全部类别"
        @change="$emit('filter', selectedCategory)"
        class="category-select"
      >
        <el-option label="全部" value=""></el-option>
        <el-option
          v-for="category in categories"
          :key="category.value"
          :label="category.label"
          :value="category.value"
        />
      </el-select>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

interface Props {
  searchQuery: string
  selectedCategory: string
  categories: any[]
  showAddButton?: boolean
}

interface Emits {
  (e: 'update:searchQuery', value: string): void
  (e: 'update:selectedCategory', value: string): void
  (e: 'search', value: string): void
  (e: 'filter', value: string): void
  (e: 'add-book'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 创建本地ref用于v-model
const searchQuery = ref(props.searchQuery)
const selectedCategory = ref(props.selectedCategory)

// 监听变化并触发emit
watch(searchQuery, (value) => {
  emit('update:searchQuery', value)
})

watch(selectedCategory, (value) => {
  emit('update:selectedCategory', value)
})
</script>

<style scoped>
.search-and-filter {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
}

.filter-controls {
  display: flex;
  align-items: center;
  gap: 15px;
  flex: 1;
  min-width: 300px;
}

.search-input {
  width: 300px;
}

.category-select {
  width: 150px;
}

.add-button {
  flex-shrink: 0;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .search-and-filter {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-controls {
    min-width: auto;
    flex-direction: column;
  }

  .search-input,
  .category-select {
    width: 100%;
  }
}
</style>