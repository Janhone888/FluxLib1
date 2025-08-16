<template>
  <div class="app-container">
    <TopNav v-if="showNav" />
    <router-view />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import TopNav from '@/components/TopNav.vue'

const route = useRoute()

const showNav = computed(() => {
  return !route.meta.hideNav
})
</script>

<style>
.app-container {
  min-height: 100vh;
  background-color: #f5f7fa;
}

/* 全局样式调整 */
.el-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.el-button {
  border-radius: 4px;
}

.el-table {
  border-radius: 8px;
  overflow: hidden;
}
</style>