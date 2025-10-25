<template>
  <div class="left-sidebar">
    <div class="sidebar-card">
      <h3>个人资料</h3>
      <div class="profile-details">
        <div class="detail-item">
          <span class="detail-label">用户ID：</span>
          <span class="detail-value user-id-value">{{ user.user_id || '未知ID' }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">用户名：</span>
          <span class="detail-value">{{ user.display_name || '未知用户' }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">邮箱：</span>
          <span class="detail-value">{{ user.email || '未绑定邮箱' }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">性别：</span>
          <span class="detail-value">{{ formatGender(user.gender) }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">角色：</span>
          <el-tag
            size="small"
            :type="user.is_admin ? 'danger' : 'primary'"
          >
            {{ user.is_admin ? '管理员' : '普通用户' }}
          </el-tag>
        </div>
        <div class="detail-item">
          <span class="detail-label">注册时间：</span>
          <span class="detail-value">{{ formatDate(user.created_at) }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">账号状态：</span>
          <el-tag
            size="small"
            :type="user.is_verified ? 'success' : 'warning'"
          >
            {{ user.is_verified ? '已验证' : '未验证' }}
          </el-tag>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { UserProfile } from '../composables/useUserProfile'

interface Props {
  user: UserProfile
  formatGender: (gender: string) => string
  formatDate: (timestamp: number) => string
}

defineProps<Props>()
</script>

<style scoped>
.left-sidebar {
  position: sticky;
  top: 80px;
  height: fit-content;
}

.sidebar-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.sidebar-card h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 16px 0;
  color: #1a1a1a;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.profile-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-label {
  font-size: 14px;
  color: #666;
}

.detail-value {
  font-size: 14px;
  color: #1a1a1a;
  font-weight: 500;
}

.user-id-value {
  font-family: 'Courier New', monospace;
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

@media (max-width: 768px) {
  .left-sidebar {
    position: static;
  }
}
</style>