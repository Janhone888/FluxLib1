<template>
  <el-tag :type="getTagType(status)" size="small">
    {{ getStatusText(status) }}
  </el-tag>
</template>

<script setup lang="ts">
interface Props {
  status: string
}

defineProps<Props>()

const getTagType = (status: string) => {
  return status === 'returned' ? 'success' : 'warning'
}

const getStatusText = (status: string) => {
  return status === 'returned' ? '已归还' : '借阅中'
}
</script>