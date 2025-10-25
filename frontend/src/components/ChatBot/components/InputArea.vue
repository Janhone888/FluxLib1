<template>
  <div class="chat-input-area">
    <!-- 快捷问题 -->
    <QuickQuestions
      :questions="quickQuestions"
      @select-question="$emit('select-question', $event)"
    />

    <div class="input-wrapper">
      <el-input
        v-model="inputMessage"
        placeholder="输入您的问题..."
        @keyup.enter="$emit('send-message')"
        :disabled="loading"
        class="message-input"
        resize="none"
        type="textarea"
        :autosize="{ minRows: 1, maxRows: 4 }"
      >
        <template #append>
          <el-button
            :icon="Search"
            @click="$emit('send-message')"
            :loading="loading"
            class="send-btn"
          />
        </template>
      </el-input>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Search } from '@element-plus/icons-vue'

import QuickQuestions from './QuickQuestions.vue'

interface Props {
  inputMessage: string
  loading: boolean
  quickQuestions: string[]
}

interface Emits {
  (e: 'update:inputMessage', value: string): void
  (e: 'send-message'): void
  (e: 'select-question', value: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 计算属性用于双向绑定
const inputMessage = computed({
  get: () => props.inputMessage,
  set: (value) => emit('update:inputMessage', value)
})
</script>

<style scoped>
.chat-input-area {
  padding: 16px 20px;
  border-top: 1px solid #e5e5e5;
  background: white;
}

.input-wrapper {
  display: flex;
  gap: 8px;
}

.message-input {
  flex: 1;
}

:deep(.el-textarea__inner) {
  border: 1px solid #e1e5e9;
  border-radius: 12px;
  resize: none;
  padding: 12px 16px;
  font-size: 14px;
}

:deep(.el-textarea__inner:focus) {
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
}

.send-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.send-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}
</style>