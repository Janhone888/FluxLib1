<template>
  <div
    class="chatbot-window"
    :class="{ 'is-dragging': isDragging }"
    :style="windowStyle"
    ref="chatWindow"
  >
    <!-- 标题栏 -->
    <div class="chat-header" @mousedown="$emit('start-drag', $event)">
      <div class="header-left">
        <img src="/icons/ai-icon.png" alt="AI助手" class="ai-avatar" />
        <div class="header-info">
          <h3>FluxLib AI助手</h3>
          <span class="status">在线</span>
        </div>
      </div>
      <div class="header-actions">
        <el-button link @click="$emit('toggle-minimize')" class="action-btn">
          <el-icon><Minus /></el-icon>
        </el-button>
        <el-button link @click="$emit('close')" class="action-btn">
          <el-icon><Close /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- 消息区域 -->
    <MessageList
      :messages="messages"
      :loading="loading"
      ref="messagesContainer"
    />

    <!-- 输入区域 -->
    <InputArea
      :input-message="inputMessage"
      :loading="loading"
      :quick-questions="quickQuestions"
      @send-message="$emit('send-message')"
      @select-question="$emit('select-question', $event)"
      @update:input-message="$emit('update:input-message', $event)"
    />

    <!-- 调整大小手柄 -->
    <ResizeHandle @mousedown="$emit('start-resize', $event)" />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { Minus, Close } from '@element-plus/icons-vue'

import MessageList from './MessageList.vue'
import InputArea from './InputArea.vue'
import ResizeHandle from './ResizeHandle.vue'

interface Props {
  position: { x: number; y: number }
  size: { width: number; height: number }
  isDragging: boolean
  messages: any[]
  loading: boolean
  inputMessage: string
  quickQuestions: string[]
}

defineProps<Props>()

defineEmits([
  'start-drag',
  'start-resize',
  'toggle-minimize',
  'close',
  'send-message',
  'select-question',
  'update:input-message'
])

// 计算窗口样式
const windowStyle = computed(() => ({
  left: `${props.position.x}px`,
  top: `${props.position.y}px`,
  width: `${props.size.width}px`,
  height: `${props.size.height}px`
}))

// 聊天窗口引用
const chatWindow = ref<HTMLElement>()
const messagesContainer = ref()
</script>

<style scoped>
.chatbot-window {
  position: fixed;
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid #e1e5e9;
  transition: box-shadow 0.3s ease;
}

.chatbot-window:hover {
  box-shadow: 0 15px 50px rgba(0, 0, 0, 0.2);
}

.chatbot-window.is-dragging {
  cursor: grabbing;
  user-select: none;
}

/* 标题栏 */
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  cursor: grab;
  user-select: none;
}

.chat-header:active {
  cursor: grabbing;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-info h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.status {
  font-size: 12px;
  color: #a8e6a8;
}

.ai-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.header-actions {
  display: flex;
  gap: 4px;
}

.action-btn {
  color: white;
  padding: 6px;
  border-radius: 6px;
  transition: background-color 0.2s;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chatbot-window {
    width: 100vw !important;
    height: 100vh !important;
    left: 0 !important;
    top: 0 !important;
    border-radius: 0;
  }
}
</style>