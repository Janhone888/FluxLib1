<template>
  <div class="chatbot-container">
    <!-- 最小化状态 -->
    <MinimizedChat
      v-if="isMinimized"
      :has-new-message="hasNewMessage"
      @toggle="toggleMinimize"
    />

    <!-- 聊天窗口 -->
    <ChatWindow
      v-else
      :position="windowPosition"
      :size="windowSize"
      :is-dragging="isDragging"
      :messages="messages"
      :loading="loading"
      :input-message="inputMessage"
      :quick-questions="quickQuestions"
      @start-drag="startDrag"
      @start-resize="startResize"
      @toggle-minimize="toggleMinimize"
      @close="closeChat"
      @send-message="sendMessage"
      @select-question="selectQuickQuestion"
      @update:input-message="inputMessage = $event"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, watch } from 'vue'

import MinimizedChat from './components/MinimizedChat.vue'
import ChatWindow from './components/ChatWindow.vue'

import { useChatMessages } from './composables/useChatMessages'
import { useChatWindow } from './composables/useChatWindow'
import { useDragAndDrop } from './composables/useDragAndDrop'
import { useResize } from './composables/useResize'

// 使用组合式函数组织逻辑
const {
  messages,
  loading,
  inputMessage,
  hasNewMessage,
  quickQuestions,
  sendMessage,
  selectQuickQuestion,
  loadMessages,
  saveMessages,
  scrollToBottom
} = useChatMessages()

const {
  isMinimized,
  toggleMinimize,
  closeChat
} = useChatWindow(messages, hasNewMessage, scrollToBottom)

const {
  windowPosition,
  windowSize,
  isDragging,
  startDrag,
  stopDrag,
  onDrag
} = useDragAndDrop()

const {
  isResizing,
  startResize,
  stopResize,
  onResize
} = useResize(windowSize)

// 快捷问题
const quickQuestionsList = [
  "推荐几本计算机类的书",
  "图书馆的营业时间是什么？",
  "如何借阅图书？",
  "有哪些文学类图书？"
]

// 页面挂载时加载消息
onMounted(() => {
  loadMessages()
  window.addEventListener('user-changed', handleUserChange)
})

onUnmounted(() => {
  window.removeEventListener('user-changed', handleUserChange)
})

// 处理用户变化
const handleUserChange = () => {
  messages.value = []
  loadMessages()
}
</script>

<style scoped>
.chatbot-container {
  position: fixed;
  z-index: 10000;
  right: 0;
  bottom: 0;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .chatbot-container {
    padding: 10px;
  }
}
</style>