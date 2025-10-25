<template>
  <div class="batch-actions">
    <el-button
      type="primary"
      :disabled="selectedCount === 0"
      @click="$emit('batch-return')"
      class="batch-return-btn"
    >
      批量归还 ({{ selectedCount }})
    </el-button>
  </div>
</template>

<script setup lang="ts">
interface Props {
  selectedCount: number
}

defineProps<Props>()
defineEmits(['batch-return'])
</script>

<style scoped>
.batch-actions {
  display: flex;
}

.batch-return-btn {
  min-width: 120px;
}
</style>