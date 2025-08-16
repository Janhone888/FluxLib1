<template>
  <div class="search-bar">
    <el-input
      v-model="query"
      placeholder="搜索图书..."
      clearable
      @input="onSearch"
      @clear="onClear"
    >
      <template #prefix>
        <el-icon><Search /></el-icon>
      </template>
    </el-input>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Search } from '@element-plus/icons-vue'

const emit = defineEmits(['search'])
const query = ref('')

const onSearch = () => {
  emit('search', query.value)
}

const onClear = () => {
  emit('search', '')
}
</script>

<style scoped>
.search-bar {
  margin-bottom: 20px;
}
</style>