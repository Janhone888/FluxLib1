<template>
  <div :class="['message', message.role]">
    <div class="message-avatar">
      <img
        v-if="message.role === 'ai'"
        src="/icons/ai-icon.png"
        alt="AI助手"
        class="avatar-img"
      />
      <img
        v-else
        src="/icons/user-icon.png"
        alt="用户"
        class="avatar-img"
      />
    </div>
    <div class="message-content-wrapper">
      <div class="message-content">
        <div v-if="message.role === 'ai'" class="ai-name">FluxLib助手</div>
        <div class="text-content">{{ message.content }}</div>
      </div>
      <div class="message-time">
        {{ formatTime(message.timestamp) }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  message: {
    role: string
    content: string
    timestamp: number
  }
}

defineProps<Props>()

const formatTime = (timestamp: number) => {
  return new Date(timestamp).toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.message {
  display: flex;
  gap: 12px;
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

.text-content {
  white-space: pre-wrap;
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

/* 响应式设计 */
@media (max-width: 768px) {
  .message-content-wrapper {
    max-width: 85%;
  }
}
</style>