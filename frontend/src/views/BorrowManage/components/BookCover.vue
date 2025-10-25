<template>
  <el-image
    :src="cover"
    fit="cover"
    style="width: 60px; height: 80px"
    v-if="cover"
  >
    <template #error>
      <div class="image-error">
        <el-icon><Picture /></el-icon>
      </div>
    </template>
  </el-image>
  <div class="no-cover" v-else>
    无封面
  </div>
</template>

<script setup lang="ts">
import { Picture } from '@element-plus/icons-vue'

interface Props {
  cover?: string
}

defineProps<Props>()
</script>

<style scoped>
.image-error {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 80px;
  background-color: #f5f7fa;
  color: #c0c4cc;
}

.no-cover {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 80px;
  background-color: #f5f7fa;
  color: #909399;
  font-size: 12px;
}
</style>