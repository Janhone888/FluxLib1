/* 功能特性卡片组件 */
<template>
  <div class="feature-card" @mouseenter="isHovered = true" @mouseleave="isHovered = false">
    <div class="feature-icon">
      <i :class="icon"></i>
    </div>
    <div class="feature-content">
      <h3>{{ title }}</h3>
      <p>{{ description }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  icon: {
    type: String,
    required: true
  },
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  }
})

const isHovered = ref(false)
</script>

<style scoped>
.feature-card {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 20px;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.1);
  cursor: default;
}

.feature-card:hover {
  transform: translateY(-5px);
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.2);
}

.feature-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  flex-shrink: 0;
}

.feature-icon i {
  font-size: 24px;
  color: white;
}

.feature-content h3 {
  margin: 0 0 5px 0;
  font-size: 16px;
  font-weight: 600;
}

.feature-content p {
  margin: 0;
  font-size: 14px;
  opacity: 0.8;
}
</style>