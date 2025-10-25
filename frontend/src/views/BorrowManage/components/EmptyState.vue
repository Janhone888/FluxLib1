<template>
  <div class="empty-state">
    <el-empty description="您还没有借阅记录">
      <el-button type="primary" @click="$emit('go-to-books')">
        去借书
      </el-button>
    </el-empty>
  </div>
</template>

<script setup lang="ts">
defineEmits(['go-to-books'])
</script>

<style scoped>
.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
}
</style>