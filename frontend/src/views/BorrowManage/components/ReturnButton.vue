<template>
  <el-button
    v-if="record.status !== 'returned'"
    type="text"
    @click="$emit('click')"
    :disabled="record.returning"
    :loading="record.returning"
    class="return-btn"
  >
    归还
  </el-button>
  <span v-else class="returned-text">已归还</span>
</template>

<script setup lang="ts">
interface Props {
  record: any
}

defineProps<Props>()
defineEmits(['click'])
</script>

<style scoped>
.return-btn {
  color: #409EFF;
}

.returned-text {
  color: #67C23A;
  font-size: 14px;
}
</style>