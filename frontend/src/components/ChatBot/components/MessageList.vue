<template>
  <div class="chat-messages" ref="messagesContainer">
    <MessageItem
      v-for="(msg, index) in messages"
      :key="index"
      :message="msg"
    />

    <!-- 加载状态 -->
    <div v-if="loading" class="message ai">
      <div class="message-avatar">
        <img src="/icons/ai-icon.png" alt="AI助手" class="avatar-img" />
      </div>
      <div class="message-content-wrapper">
        <div class="message-content">
          <div class="ai-name">FluxLib助手</div>
          <div class="text-content">
            <el-icon class="loading"><Loading /></el-icon>
            思考中...
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted, watch } from 'vue'
import { Loading } from '@element-plus/icons-vue'

import MessageItem from './MessageItem.vue'

interface Props {
  messages: any[]
  loading: boolean
}

defineProps<Props>()

// 消息容器引用
const messagesContainer = ref<HTMLElement>()

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// 监听消息变化自动滚动
watch(
  () => props.messages,
  () => {
    scrollToBottom()
  },
  { deep: true }
)

// 暴露方法给父组件
defineExpose({
  scrollToBottom
})
</script>

<style scoped>
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f8f9fa;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message {
  display: flex;
  gap: 12px;
  animation: fadeInUp 0.3s ease;
}

.message.user {
  flex-direction: row-reverse;
}

.message-content-wrapper {
  max-width: 70%;
}

.message-content {
  padding: 12px 16px;
  border-radius: 18px;
  position: relative;
  line-height: 1.5;
  word-wrap: break-word;
}

.user .message-content {
  background: #667eea;
  color: white;
  border-bottom-right-radius: 4px;
}

.ai .message-content {
  background: white;
  color: #333;
  border: 1px solid #e5e5e5;
  border-bottom-left-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.ai-name {
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 4px;
  color: #666;
}

.message-time {
  font-size: 11px;
  color: #999;
  margin-top: 4px;
  text-align: right;
}

.user .message-time {
  text-align: left;
  color: rgba(255, 255, 255, 0.7);
}

.avatar-img {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.loading {
  animation: rotating 2s linear infinite;
  margin-right: 8px;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes rotating {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .message-content-wrapper {
    max-width: 85%;
  }
}
</style>