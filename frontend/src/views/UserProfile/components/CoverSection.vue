<template>
  <div class="cover-section">
    <div class="cover-container">
      <el-image
        :src="user.background_url || defaultCover"
        fit="cover"
        class="cover-image"
      >
        <template #error>
          <div class="cover-error">
            <el-icon><Picture /></el-icon>
            <span>封面图片</span>
          </div>
        </template>
      </el-image>

      <!-- 封面操作按钮 -->
      <div class="cover-actions">
        <el-button
          type="primary"
          @click="$emit('cover-change')"
          class="cover-btn"
        >
          <el-icon><Camera /></el-icon>
          更换封面
        </el-button>
      </div>

      <!-- 用户头像和信息 -->
      <div class="profile-overlay">
        <div class="avatar-container" @click="$emit('avatar-change')">
          <el-avatar :size="100" :src="user.avatar_url" class="main-avatar">
            <template #error>
              <div class="avatar-error">
                <el-icon><User /></el-icon>
              </div>
            </template>
          </el-avatar>
          <div class="avatar-overlay">
            <el-icon><Camera /></el-icon>
          </div>
        </div>

        <div class="profile-info">
          <h2 class="username">{{ user.display_name || '未知用户' }}</h2>
          <div class="user-id-display">
            <el-tag size="small" type="info" class="user-id-tag">
              <el-icon><User /></el-icon>
              ID: {{ user.user_id || '未知ID' }}
            </el-tag>
            <el-button
              size="small"
              type="text"
              @click="$emit('copy-user-id')"
              class="copy-btn"
            >
              <el-icon><DocumentCopy /></el-icon>
              复制
            </el-button>
          </div>
          <p class="user-signature">{{ user.summary || '这个人很懒，什么都没有写～' }}</p>
          <div class="user-stats">
            <div class="stat-item">
              <span class="stat-number">{{ favoritesCount }}</span>
              <span class="stat-label">收藏</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">{{ viewHistoryCount }}</span>
              <span class="stat-label">浏览</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">{{ formatDays(user.created_at) }}</span>
              <span class="stat-label">加入天数</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Picture, Camera, User, DocumentCopy } from '@element-plus/icons-vue'
import type { UserProfile } from '../composables/useUserProfile'

interface Props {
  user: UserProfile
  favoritesCount: number
  viewHistoryCount: number
  formatDays: (timestamp: number) => number
}

interface Emits {
  (e: 'cover-change'): void
  (e: 'avatar-change'): void
  (e: 'copy-user-id'): void
}

defineProps<Props>()
defineEmits<Emits>()

const defaultCover = 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2340&q=80'
</script>

<style scoped>
.cover-section {
  margin-bottom: 20px;
}

.cover-container {
  position: relative;
  height: 300px;
  overflow: hidden;
}

.cover-image {
  width: 100%;
  height: 100%;
}

.cover-error {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 18px;
}

.cover-actions {
  position: absolute;
  top: 20px;
  right: 20px;
}

.cover-btn {
  background: rgba(255, 255, 255, 0.9);
  border: none;
  color: #333;
}

.cover-btn:hover {
  background: white;
}

.profile-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.6));
  padding: 40px 20px 20px;
  display: flex;
  align-items: flex-end;
  gap: 20px;
}

.avatar-container {
  position: relative;
  cursor: pointer;
}

.main-avatar {
  border: 4px solid white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  opacity: 0;
  transition: opacity 0.3s;
  border: 4px solid white;
}

.avatar-container:hover .avatar-overlay {
  opacity: 1;
}

.avatar-error {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  color: #c0c4cc;
}

.profile-info {
  flex: 1;
  color: white;
}

.username {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 8px 0;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.8);
}

.user-id-display {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.user-id-tag {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  backdrop-filter: blur(10px);
}

.copy-btn {
  color: rgba(255, 255, 255, 0.8);
  padding: 2px 6px;
  height: auto;
}

.copy-btn:hover {
  color: white;
  background: rgba(255, 255, 255, 0.1);
}

.user-signature {
  font-size: 14px;
  margin: 0 0 16px 0;
  opacity: 0.9;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);
}

.user-stats {
  display: flex;
  gap: 24px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  opacity: 0.8;
}

@media (max-width: 768px) {
  .profile-overlay {
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 20px;
  }

  .user-stats {
    justify-content: center;
  }
}
</style>