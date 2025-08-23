<template>
  <div class="app-container">
    <TopNav v-if="showNav" />
    <router-view />
    <!-- 添加AI聊天机器人 -->
    <ChatBot v-if="userStore.isAuthenticated" />
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import TopNav from '@/components/TopNav.vue'
import ChatBot from '@/components/ChatBot.vue'

const route = useRoute()
const userStore = useUserStore()

const showNav = computed(() => {
  return !route.meta.hideNav
})

// 初始化用户状态
onMounted(() => {
  // 从localStorage恢复用户状态
  const token = localStorage.getItem('token')
  const userInfo = localStorage.getItem('userInfo')

  if (token && userInfo) {
    userStore.token = token
    userStore.userInfo = JSON.parse(userInfo)
    userStore.isAuthenticated = true
  }
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

/* 全局加载样式 */
.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}

/* 全局空状态样式 */
.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #909399;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .app-container {
    padding: 0 10px;
  }
}
</style>