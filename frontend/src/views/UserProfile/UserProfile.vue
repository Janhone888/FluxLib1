<template>
  <div class="qqspace-profile">
    <!-- 顶部导航 -->
    <div class="nav-header">
      <div class="nav-container">
        <div class="nav-left">
          <h1>个人中心</h1>
        </div>
        <div class="nav-right">
          <el-button type="primary" @click="showEditDialog = true">
            <el-icon><Edit /></el-icon>
            编辑资料
          </el-button>
        </div>
      </div>
    </div>

    <!-- 封面区域 -->
    <CoverSection
      :user="user"
      :favorites-count="favoritesCount"
      :view-history-count="viewHistoryCount"
      :format-days="formatDays"
      @cover-change="triggerCoverInput"
      @avatar-change="triggerAvatarInput"
      @copy-user-id="copyUserId"
    />

    <!-- 主要内容区域 -->
    <div class="main-content">
      <div class="content-container">
        <!-- 左侧导航 -->
        <ProfileSidebar
          :user="user"
          :format-gender="formatGender"
          :format-date="formatDate"
        />

        <!-- 右侧内容 -->
        <ProfileTabs
          v-model:active-tab="activeTab"
          :tabs="tabs"
          :favorites-preview="favoritesPreview"
          :history-preview="historyPreview"
          :format-date="formatDate"
          @edit-profile="showEditDialog = true"
          @change-cover="triggerCoverInput"
          @change-avatar="triggerAvatarInput"
        />
      </div>
    </div>

    <!-- 文件输入 -->
    <input
      type="file"
      ref="avatarInput"
      style="display: none"
      accept="image/*"
      @change="handleAvatarUpload"
    />
    <input
      type="file"
      ref="coverInput"
      style="display: none"
      accept="image/*"
      @change="handleCoverSelect"
    />

    <!-- 图片裁剪对话框 -->
    <ImageCropDialog
      v-model="showCropDialog"
      :crop-image-src="cropImageSrc"
      @confirm="handleCroppedCover"
    />

    <!-- 编辑资料对话框 -->
    <EditProfileDialog
      v-model="showEditDialog"
      :user="user"
      :updating="updating"
      @save="updateProfile"
      @change-avatar="triggerAvatarInput"
      @change-cover="triggerCoverInput"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Edit } from '@element-plus/icons-vue'

// Components
import CoverSection from './components/CoverSection.vue'
import ProfileSidebar from './components/ProfileSidebar.vue'
import ProfileTabs from './components/ProfileTabs.vue'
import EditProfileDialog from './components/EditProfileDialog.vue'
import ImageCropDialog from './components/ImageCropDialog.vue'

// Composables
import { useUserProfile } from './composables/useUserProfile'
import { useImageUpload } from './composables/useImageUpload'
import { useProfileTabs } from './composables/useProfileTabs'

// 用户资料逻辑
const {
  user,
  updating,
  fetchUserInfo,
  updateUserProfile,
  copyUserId,
  formatDays,
  formatDate,
  formatGender
} = useUserProfile()

// 图片上传逻辑
const {
  uploadImage,
  validateImageFile
} = useImageUpload()

// 标签页逻辑
const {
  activeTab,
  tabs,
  favoritesPreview,
  historyPreview,
  favoritesCount,
  viewHistoryCount,
  fetchFavoritesPreview,
  fetchHistoryPreview
} = useProfileTabs()

// 组件状态
const showEditDialog = ref(false)
const showCropDialog = ref(false)
const avatarInput = ref<HTMLInputElement>()
const coverInput = ref<HTMLInputElement>()

// 裁剪相关
const cropImageSrc = ref('')
const selectedCoverFile = ref<File>()

// 初始化
onMounted(() => {
  initializeProfile()
})

const initializeProfile = async () => {
  await fetchUserInfo()
  await fetchFavoritesPreview()
  await fetchHistoryPreview()
}

// 文件处理
const triggerAvatarInput = () => avatarInput.value?.click()
const triggerCoverInput = () => coverInput.value?.click()

const handleAvatarUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  try {
    const avatarUrl = await uploadImage(file, 'avatar_url', '头像')

    // 如果在编辑模式下，更新表单中的头像URL
    if (showEditDialog.value) {
      // 这里可以通过事件传递给编辑对话框，或者直接更新用户信息
      await updateUserProfile({ avatar_url: avatarUrl })
    } else {
      await updateUserProfile({ avatar_url: avatarUrl })
    }
  } catch (error) {
    console.error('头像上传失败:', error)
  } finally {
    target.value = ''
  }
}

const handleCoverSelect = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  if (!validateImageFile(file)) {
    target.value = ''
    return
  }

  selectedCoverFile.value = file

  // 创建图片URL用于裁剪
  const reader = new FileReader()
  reader.onload = (e) => {
    cropImageSrc.value = e.target?.result as string
    showCropDialog.value = true
  }
  reader.readAsDataURL(file)

  target.value = ''
}

const handleCroppedCover = async (file: File) => {
  try {
    const backgroundUrl = await uploadImage(file, 'background_url', '封面')

    if (showEditDialog.value) {
      // 在编辑模式下，可能需要更新表单
      await updateUserProfile({ background_url: backgroundUrl })
    } else {
      await updateUserProfile({ background_url: backgroundUrl })
    }
  } catch (error) {
    console.error('封面上传失败:', error)
  }
}

// 资料更新
const updateProfile = async (updateData: any) => {
  try {
    await updateUserProfile(updateData)
    showEditDialog.value = false
  } catch (error) {
    console.error('资料更新失败:', error)
  }
}
</script>

<style scoped>
.qqspace-profile {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.nav-header {
  background: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-left h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px 40px;
}

.content-container {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 20px;
}

@media (max-width: 768px) {
  .content-container {
    grid-template-columns: 1fr;
  }
}
</style>