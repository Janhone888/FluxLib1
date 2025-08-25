<template>
  <el-menu
    mode="horizontal"
    :default-active="activeIndex"
    background-color="#2c3e50"
    text-color="#fff"
    active-text-color="#ffd04b"
    router
  >
    <!-- 普通用户菜单 -->
    <template v-if="!userStore.userInfo.is_admin">
      <el-menu-item index="/home">
        <el-icon><House /></el-icon>
        <span>首页</span>
      </el-menu-item>

      <el-menu-item index="/books">
        <el-icon><Notebook /></el-icon>
        <span>图书浏览</span>
      </el-menu-item>

      <el-menu-item index="/borrows">
        <el-icon><Collection /></el-icon>
        <span>我的借阅</span>
      </el-menu-item>

      <el-menu-item index="/profile">
        <el-icon><User /></el-icon>
        <span>个人中心</span>
      </el-menu-item>
    </template>

    <!-- 管理员菜单 -->
    <template v-else>
      <el-menu-item index="/dashboard">
        <el-icon><House /></el-icon>
        <span>仪表盘</span>
      </el-menu-item>

      <el-menu-item index="/books">
        <el-icon><Notebook /></el-icon>
        <span>图书管理</span>
      </el-menu-item>

      <el-menu-item index="/borrows">
        <el-icon><Collection /></el-icon>
        <span>借阅管理</span>
      </el-menu-item>

      <el-menu-item index="/analytics">
        <el-icon><DataAnalysis /></el-icon>
        <span>数据分析</span>
      </el-menu-item>

      <el-menu-item index="/settings">
        <el-icon><Setting /></el-icon>
        <span>系统设置</span>
      </el-menu-item>
    </template>

    <div class="user-info">
      <el-dropdown>
        <span class="user-dropdown">
          <el-avatar :size="32" :src="avatarUrl" />
          <span class="user-name">{{ userStore.userInfo.email }}</span>
          <span class="user-role">{{ userStore.userInfo.is_admin ? '(管理员)' : '(用户)' }}</span>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item v-if="!userStore.userInfo.is_admin" @click="goToProfile">
              <el-icon><User /></el-icon> 个人中心
            </el-dropdown-item>
            <el-dropdown-item @click="logout">
              <el-icon><SwitchButton /></el-icon> 退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </el-menu>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import {
  House, Notebook, Collection, DataAnalysis, Setting, SwitchButton, User
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const activeIndex = ref(route.path)

const avatarUrl = computed(() => {
  return `https://api.dicebear.com/7.x/initials/svg?seed=${userStore.userInfo.email}`
})

const logout = () => {
  userStore.logout()
  router.push('/login')
}

const goToProfile = () => {
  router.push('/profile')
}
</script>

<style scoped>
.user-info {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
}

.user-dropdown {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: white;
}

.user-name {
  margin-left: 8px;
  font-size: 14px;
}

.user-role {
  margin-left: 4px;
  font-size: 12px;
  color: #ccc;
}
</style>