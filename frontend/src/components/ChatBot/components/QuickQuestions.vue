<template>
  <div class="quick-questions">
    <el-tag
      v-for="(question, index) in questions"
      :key="index"
      size="small"
      @click="$emit('select-question', question)"
      class="question-tag"
    >
      {{ question }}
    </el-tag>
  </div>
</template>

<script setup lang="ts">
interface Props {
  questions: string[]
}

defineProps<Props>()
defineEmits(['select-question'])
</script>

<style scoped>
.quick-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.question-tag {
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  background: #f1f3f4;
  color: #5f6368;
}

.question-tag:hover {
  transform: translateY(-1px);
  background: #667eea;
  color: white;
}
</style>