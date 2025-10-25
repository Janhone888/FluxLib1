<template>
  <div class="chatbot-minimized" @click="$emit('toggle')">
    <div class="minimized-content">
      <img src="/icons/ai-icon.png" alt="AI助手" class="minimized-icon" />
      <span class="notification-dot" v-if="hasNewMessage"></span>
      <div class="minimized-tooltip">AI助手</div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  hasNewMessage: boolean
}

defineProps<Props>()
defineEmits(['toggle'])
</script>

<style scoped>
.chatbot-minimized {
  position: relative;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

.chatbot-minimized:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 25px rgba(0, 0, 0, 0.2);
}

.minimized-content {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.minimized-icon {
  width: 32px;
  height: 32px;
  object-fit: contain;
}

.minimized-tooltip {
  position: absolute;
  bottom: -40px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  white-space: nowrap;
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.chatbot-minimized:hover .minimized-tooltip {
  opacity: 1;
}

.notification-dot {
  position: absolute;
  top: -2px;
  right: -2px;
  width: 12px;
  height: 12px;
  background-color: #ff4757;
  border-radius: 50%;
  border: 2px solid white;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(255, 71, 87, 0.7);
  }
  70% {
    transform: scale(1);
    box-shadow: 0 0 0 6px rgba(255, 71, 87, 0);
  }
  100% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(255, 71, 87, 0);
  }
}
</style>