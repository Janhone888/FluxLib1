<template>
  <el-form-item>
    <el-button
      type="primary"
      @click="$emit('submit')"
      :loading="submitting"
      class="submit-btn"
    >
      <el-icon><Check /></el-icon>
      <span>{{ isEdit ? '保存更改' : '提交' }}</span>
    </el-button>

    <el-button @click="$emit('reset')" class="reset-btn">
      <el-icon><Refresh /></el-icon>
      <span>重置</span>
    </el-button>

    <el-button @click="$emit('cancel')" class="cancel-btn">
      <el-icon><Close /></el-icon>
      <span>取消</span>
    </el-button>
  </el-form-item>
</template>

<script setup lang="ts">
import { Check, Refresh, Close } from '@element-plus/icons-vue'

interface Props {
  isEdit?: boolean
  submitting?: boolean
}

withDefaults(defineProps<Props>(), {
  isEdit: false,
  submitting: false
})

defineEmits(['submit', 'reset', 'cancel'])
</script>

<style scoped>
.submit-btn,
.reset-btn,
.cancel-btn {
  margin-right: 12px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .submit-btn,
  .reset-btn,
  .cancel-btn {
    width: 100%;
    margin-bottom: 8px;
    margin-right: 0;
  }
}
</style>