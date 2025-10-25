<template>
  <div class="right-content">
    <!-- 功能导航 -->
    <div class="function-nav">
      <div class="nav-tabs">
        <div
          v-for="tab in tabs"
          :key="tab.id"
          :class="['nav-tab', { active: activeTab === tab.id }]"
          @click="activeTab = tab.id"
        >
          <el-icon class="tab-icon"><component :is="tab.icon" /></el-icon>
          <span class="tab-text">{{ tab.name }}</span>
        </div>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="content-area">
      <!-- 收藏内容 -->
      <div v-if="activeTab === 'favorites'" class="tab-content">
        <div class="content-header">
          <h3>我的收藏</h3>
          <el-button type="primary" @click="goToFavoritesPage">
            查看全部
          </el-button>
        </div>
        <div class="favorites-preview">
          <div v-if="favoritesPreview.length === 0" class="empty-preview">
            <el-empty description="暂无收藏的图书" :image-size="100" />
          </div>
          <div v-else class="preview-grid">
            <div
              v-for="item in favoritesPreview"
              :key="item.book_id"
              class="preview-item"
              @click="goToBookDetail(item.book_id)"
            >
              <el-image
                :src="item.book_cover"
                fit="cover"
                class="item-cover"
              >
                <template #error>
                  <div class="cover-error-small">
                    <el-icon><Picture /></el-icon>
                  </div>
                </template>
              </el-image>
              <div class="item-info">
                <h4 class="item-title">{{ item.book_title }}</h4>
                <p class="item-author">{{ item.book_author || '未知作者' }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 浏览历史 -->
      <div v-else-if="activeTab === 'history'" class="tab-content">
        <div class="content-header">
          <h3>浏览历史</h3>
          <el-button type="primary" @click="goToHistoryPage">
            查看全部
          </el-button>
        </div>
        <div class="history-preview">
          <div v-if="historyPreview.length === 0" class="empty-preview">
            <el-empty description="暂无浏览历史" :image-size="100" />
          </div>
          <div v-else class="preview-list">
            <div
              v-for="item in historyPreview"
              :key="item.history_id"
              class="history-item"
              @click="goToBookDetail(item.book_id)"
            >
              <el-image
                :src="item.book_cover"
                fit="cover"
                class="history-cover"
              >
                <template #error>
                  <div class="cover-error-small">
                    <el-icon><Picture /></el-icon>
                  </div>
                </template>
              </el-image>
              <div class="history-info">
                <h4 class="history-title">{{ item.book_title }}</h4>
                <p class="history-time">{{ formatDate(item.view_time) }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 资料设置 -->
      <div v-else-if="activeTab === 'settings'" class="tab-content">
        <div class="settings-content">
          <h3>资料设置</h3>
          <div class="settings-grid">
            <div class="setting-card" @click="$emit('edit-profile')">
              <div class="setting-icon">
                <el-icon><User /></el-icon>
              </div>
              <div class="setting-info">
                <h4>编辑资料</h4>
                <p>修改个人信息和头像</p>
              </div>
              <el-icon class="setting-arrow"><ArrowRight /></el-icon>
            </div>

            <div class="setting-card" @click="$emit('change-cover')">
              <div class="setting-icon">
                <el-icon><Picture /></el-icon>
              </div>
              <div class="setting-info">
                <h4>更换封面</h4>
                <p>设置个性化封面背景</p>
              </div>
              <el-icon class="setting-arrow"><ArrowRight /></el-icon>
            </div>

            <div class="setting-card" @click="$emit('change-avatar')">
              <div class="setting-icon">
                <el-icon><Camera /></el-icon>
              </div>
              <div class="setting-info">
                <h4>更换头像</h4>
                <p>上传新的头像图片</p>
              </div>
              <el-icon class="setting-arrow"><ArrowRight /></el-icon>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Picture, User, Camera, ArrowRight } from '@element-plus/icons-vue'
import type { FavoriteItem, HistoryItem } from '../composables/useProfileTabs'

interface Props {
  activeTab: string
  tabs: Array<{ id: string; name: string; icon: any }>
  favoritesPreview: FavoriteItem[]
  historyPreview: HistoryItem[]
  formatDate: (timestamp: number) => string
}

interface Emits {
  (e: 'update:activeTab', value: string): void
  (e: 'edit-profile'): void
  (e: 'change-cover'): void
  (e: 'change-avatar'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const router = useRouter()

const activeTab = computed({
  get: () => props.activeTab,
  set: (value) => emit('update:activeTab', value)
})

const goToFavoritesPage = () => {
  router.push('/favorites')
}

const goToHistoryPage = () => {
  router.push('/history')
}

const goToBookDetail = (bookId: string) => {
  router.push(`/book/${bookId}`)
}
</script>

<style scoped>
.right-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.function-nav {
  border-bottom: 1px solid #f0f0f0;
}

.nav-tabs {
  display: flex;
  padding: 0 20px;
}

.nav-tab {
  display: flex;
  align-items: center;
  padding: 16px 24px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.3s ease;
  gap: 8px;
}

.nav-tab:hover {
  color: #1890ff;
}

.nav-tab.active {
  color: #1890ff;
  border-bottom-color: #1890ff;
}

.tab-icon {
  font-size: 18px;
}

.tab-text {
  font-size: 14px;
  font-weight: 500;
}

.content-area {
  padding: 24px;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.content-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
}

.preview-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.preview-item {
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

.preview-item:hover {
  border-color: #1890ff;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.1);
  transform: translateY(-2px);
}

.item-cover {
  width: 100%;
  height: 120px;
}

.cover-error-small {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  color: #c0c4cc;
}

.item-info {
  padding: 12px;
}

.item-title {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 4px 0;
  color: #1a1a1a;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-author {
  font-size: 12px;
  color: #666;
  margin: 0;
}

.preview-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  gap: 12px;
}

.history-item:hover {
  border-color: #1890ff;
  background: #f5f7fa;
}

.history-cover {
  width: 60px;
  height: 80px;
  border-radius: 4px;
}

.history-info {
  flex: 1;
}

.history-title {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 4px 0;
  color: #1a1a1a;
}

.history-time {
  font-size: 12px;
  color: #999;
  margin: 0;
}

.settings-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.setting-card {
  display: flex;
  align-items: center;
  padding: 16px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  gap: 12px;
}

.setting-card:hover {
  border-color: #1890ff;
  background: #f5f7fa;
}

.setting-icon {
  width: 40px;
  height: 40px;
  border-radius: 6px;
  background: #1890ff;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
}

.setting-info {
  flex: 1;
}

.setting-info h4 {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 4px 0;
  color: #1a1a1a;
}

.setting-info p {
  font-size: 12px;
  color: #666;
  margin: 0;
}

.setting-arrow {
  color: #999;
}

.empty-preview {
  padding: 40px 0;
  text-align: center;
}

@media (max-width: 768px) {
  .preview-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .nav-tabs {
    overflow-x: auto;
    padding: 0 16px;
  }

  .nav-tab {
    padding: 12px 16px;
    white-space: nowrap;
  }
}
</style>