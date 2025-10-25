<template>
  <div class="sort-controls">
    <el-button-group>
      <el-button @click="$emit('sort-by-status')">
        <el-icon><Sort /></el-icon>
        按状态排序
      </el-button>
      <el-button @click="$emit('sort-by-date')">
        <el-icon><Sort /></el-icon>
        按时间排序
      </el-button>
    </el-button-group>
  </div>
</template>

<script setup lang="ts">
import { Sort } from '@element-plus/icons-vue'

defineEmits(['sort-by-status', 'sort-by-date'])
</script>

<style scoped>
.sort-controls {
  display: flex;
  margin-right: 10px;
}
</style>