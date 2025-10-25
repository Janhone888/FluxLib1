<template>
  <div class="resize-handle" @mousedown="$emit('mousedown', $event)"></div>
</template>

<script setup lang="ts">
defineEmits(['mousedown'])
</script>

<style scoped>
.resize-handle {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 20px;
  height: 20px;
  cursor: nwse-resize;
  background: linear-gradient(135deg, transparent 50%, #667eea 50%);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .resize-handle {
    display: none;
  }
}
</style>