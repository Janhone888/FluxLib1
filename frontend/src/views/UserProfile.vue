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
            @click="triggerCoverInput"
            class="cover-btn"
          >
            <el-icon><Camera /></el-icon>
            更换封面
          </el-button>
        </div>

        <!-- 用户头像和信息 -->
        <div class="profile-overlay">
          <div class="avatar-container" @click="triggerAvatarInput">
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
            <!-- 新增：显示 user_id -->
            <div class="user-id-display">
              <el-tag size="small" type="info" class="user-id-tag">
                <el-icon><User /></el-icon>
                ID: {{ user.user_id || '未知ID' }}
              </el-tag>
              <el-button
                size="small"
                type="text"
                @click="copyUserId"
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

    <!-- 主要内容区域 -->
    <div class="main-content">
      <div class="content-container">
        <!-- 左侧导航 -->
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

        <!-- 右侧内容 -->
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
                  <div class="setting-card" @click="showEditDialog = true">
                    <div class="setting-icon">
                      <el-icon><User /></el-icon>
                    </div>
                    <div class="setting-info">
                      <h4>编辑资料</h4>
                      <p>修改个人信息和头像</p>
                    </div>
                    <el-icon class="setting-arrow"><ArrowRight /></el-icon>
                  </div>

                  <div class="setting-card" @click="triggerCoverInput">
                    <div class="setting-icon">
                      <el-icon><Picture /></el-icon>
                    </div>
                    <div class="setting-info">
                      <h4>更换封面</h4>
                      <p>设置个性化封面背景</p>
                    </div>
                    <el-icon class="setting-arrow"><ArrowRight /></el-icon>
                  </div>

                  <div class="setting-card" @click="triggerAvatarInput">
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
    <el-dialog
      v-model="showCropDialog"
      title="裁剪封面图片"
      width="800px"
      :close-on-click-modal="false"
      class="crop-dialog"
    >
      <div class="crop-container">
        <div class="crop-preview">
          <vue-cropper
            ref="cropperRef"
            :src="cropImageSrc"
            :aspect-ratio="3 / 1"
            :view-mode="1"
            :guides="true"
            :background="false"
            :auto-crop-area="0.8"
            class="cropper"
          />
        </div>
        <div class="crop-actions">
          <el-button @click="rotateImage(-90)">
            <el-icon><RefreshLeft /></el-icon>
            向左旋转
          </el-button>
          <el-button @click="rotateImage(90)">
            <el-icon><RefreshRight /></el-icon>
            向右旋转
          </el-button>
          <el-button @click="resetCrop">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
          <el-button type="primary" @click="confirmCrop">
            <el-icon><Check /></el-icon>
            确认裁剪
          </el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 编辑资料对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑个人资料"
      width="500px"
      :close-on-click-modal="false"
      class="edit-dialog"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="editRules"
        label-width="80px"
        class="edit-form"
      >
        <el-form-item label="显示名称" prop="display_name">
          <el-input
            v-model="editForm.display_name"
            placeholder="请输入显示名称"
            maxlength="20"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="性别" prop="gender">
          <el-select
            v-model="editForm.gender"
            placeholder="请选择性别"
            style="width: 100%"
          >
            <el-option label="男" value="male" />
            <el-option label="女" value="female" />
            <el-option label="其他" value="other" />
            <el-option label="不公开" value="" />
          </el-select>
        </el-form-item>

        <el-form-item label="个性签名" prop="summary">
          <el-input
            v-model="editForm.summary"
            type="textarea"
            :rows="3"
            placeholder="请输入个性签名"
            maxlength="50"
            show-word-limit
            resize="none"
          />
        </el-form-item>

        <!-- 头像预览 -->
        <el-form-item label="头像">
          <div class="preview-section">
            <el-image
              :src="editForm.avatar_url || user.avatar_url"
              fit="cover"
              class="preview-avatar"
            >
              <template #error>
                <div class="preview-error">
                  <el-icon><User /></el-icon>
                </div>
              </template>
            </el-image>
            <el-button
              type="text"
              @click="triggerAvatarInput"
              class="change-btn"
            >
              <el-icon><Camera /></el-icon>
              更换头像
            </el-button>
          </div>
        </el-form-item>

        <!-- 封面预览 -->
        <el-form-item label="封面">
          <div class="preview-section">
            <el-image
              :src="editForm.background_url || user.background_url || defaultCover"
              fit="cover"
              class="preview-cover"
            >
              <template #error>
                <div class="preview-error">
                  <el-icon><Picture /></el-icon>
                </div>
              </template>
            </el-image>
            <el-button
              type="text"
              @click="triggerCoverInput"
              class="change-btn"
            >
              <el-icon><Picture /></el-icon>
              更换封面
            </el-button>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button
          type="primary"
          @click="updateProfile"
          :loading="updating"
        >
          {{ updating ? '保存中...' : '保存' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElForm } from 'element-plus'
import {
  Camera,
  User,
  Edit,
  Star,
  Clock,
  Picture,
  ArrowRight,
  Setting,
  DocumentCopy,
  RefreshLeft,
  RefreshRight,
  Refresh,
  Check
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import api from '@/utils/api'

// 导入 Vue Cropper
import 'cropperjs/dist/cropper.css'
import VueCropper from 'vue-cropperjs'

const router = useRouter()
const userStore = useUserStore()

// 响应式数据
const showEditDialog = ref(false)
const showCropDialog = ref(false)
const updating = ref(false)
const avatarInput = ref(null)
const coverInput = ref(null)
const editFormRef = ref(null)
const cropperRef = ref(null)
const activeTab = ref('favorites')
const favoritesPreview = ref([])
const historyPreview = ref([])

// 裁剪相关数据
const cropImageSrc = ref('')
const selectedCoverFile = ref(null)

// 标签页配置
const tabs = [
  { id: 'favorites', name: '我的收藏', icon: Star },
  { id: 'history', name: '浏览历史', icon: Clock },
  { id: 'settings', name: '资料设置', icon: Setting }
]

// 默认封面图
const defaultCover = 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2340&q=80'

// 用户信息
const user = ref({
  user_id: '',
  email: '',
  display_name: '',
  avatar_url: '',
  background_url: '',
  gender: '',
  is_verified: false,
  is_admin: false,
  summary: '',
  created_at: 0,
  ...userStore.userInfo
})

// 编辑表单
const editForm = ref({
  display_name: '',
  gender: '',
  summary: '',
  avatar_url: '',
  background_url: ''
})

// 表单验证规则
const editRules = reactive({
  display_name: [
    { required: true, message: '请输入显示名称', trigger: 'blur' },
    { min: 1, max: 20, message: '显示名称长度需在1-20个字符之间', trigger: 'blur' }
  ]
})

// 计算属性
const favoritesCount = computed(() => favoritesPreview.value.length)
const viewHistoryCount = computed(() => historyPreview.value.length)

// 生命周期
onMounted(() => {
  fetchUserInfo()
  fetchFavoritesPreview()
  fetchHistoryPreview()
})

// 获取用户信息
const fetchUserInfo = async () => {
  try {
    const response = await api.getCurrentUser()
    const newUserData = response.data || {}
    user.value = { ...user.value, ...newUserData }

    // 初始化编辑表单
    editForm.value = {
      display_name: user.value.display_name || '',
      gender: user.value.gender || '',
      summary: user.value.summary || '',
      avatar_url: user.value.avatar_url || '',
      background_url: user.value.background_url || ''
    }

    userStore.userInfo = { ...userStore.userInfo, ...user.value }
  } catch (error) {
    console.error('获取用户信息失败', error)
    ElMessage.error('获取用户信息失败')
  }
}

// 获取收藏预览
const fetchFavoritesPreview = async () => {
  try {
    const response = await api.getFavorites()
    let favoritesData = []

    if (response.data && Array.isArray(response.data)) {
      favoritesData = response.data.slice(0, 6) // 只取前6个作为预览
    } else if (response.data && response.data.items) {
      favoritesData = response.data.items.slice(0, 6)
    }

    favoritesPreview.value = favoritesData
  } catch (error) {
    console.error('获取收藏预览失败', error)
    favoritesPreview.value = []
  }
}

// 获取历史预览
const fetchHistoryPreview = async () => {
  try {
    const response = await api.getViewHistory()
    let historyData = []

    if (response.data && Array.isArray(response.data)) {
      historyData = response.data.slice(0, 6) // 只取前6个作为预览
    } else if (response.data && response.data.items) {
      historyData = response.data.items.slice(0, 6)
    }

    historyPreview.value = historyData
  } catch (error) {
    console.error('获取历史预览失败', error)
    historyPreview.value = []
  }
}

// 触发文件输入
const triggerAvatarInput = () => avatarInput.value?.click()
const triggerCoverInput = () => coverInput.value?.click()

// 头像上传
const handleAvatarUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  await uploadImage(file, 'avatar_url', '头像')
  event.target.value = ''
}

// 封面选择（先进入裁剪）
const handleCoverSelect = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  // 文件校验
  const isImage = file.type.startsWith('image/')
  const isLt5M = file.size / 1024 / 1024 < 5
  if (!isImage) {
    ElMessage.error('只能上传图片文件')
    return
  }
  if (!isLt5M) {
    ElMessage.error('封面大小不能超过5MB')
    return
  }

  // 保存文件引用
  selectedCoverFile.value = file

  // 创建图片URL用于裁剪
  const reader = new FileReader()
  reader.onload = (e) => {
    cropImageSrc.value = e.target.result
    showCropDialog.value = true
  }
  reader.readAsDataURL(file)

  event.target.value = ''
}

// 旋转图片
const rotateImage = (degrees) => {
  if (cropperRef.value) {
    cropperRef.value.rotate(degrees)
  }
}

// 重置裁剪
const resetCrop = () => {
  if (cropperRef.value) {
    cropperRef.value.reset()
  }
}

// 确认裁剪
const confirmCrop = () => {
  if (!cropperRef.value || !selectedCoverFile.value) return

  // 获取裁剪后的canvas
  const canvas = cropperRef.value.getCroppedCanvas({
    width: 1200,
    height: 400,
    imageSmoothingQuality: 'high'
  })

  canvas.toBlob(async (blob) => {
    try {
      // 创建裁剪后的文件
      const croppedFile = new File([blob], selectedCoverFile.value.name, {
        type: selectedCoverFile.value.type,
        lastModified: Date.now()
      })

      // 上传裁剪后的图片
      await uploadImage(croppedFile, 'background_url', '封面')
      showCropDialog.value = false
      cropImageSrc.value = ''
      selectedCoverFile.value = null
    } catch (error) {
      ElMessage.error('裁剪上传失败：' + error.message)
    }
  }, selectedCoverFile.value.type)
}

// 通用图片上传逻辑
const uploadImage = async (file, type, name) => {
  updating.value = true
  try {
    // 获取OSS预签名URL
    const uploadUrlRes = await api.getUploadUrl(file.name, file.type)
    if (!uploadUrlRes.data?.presigned_url) throw new Error('获取上传链接失败')
    const { presigned_url, access_url } = uploadUrlRes.data

    // 上传图片到OSS
    const uploadRes = await fetch(presigned_url, {
      method: 'PUT',
      body: file,
      headers: { 'Content-Type': file.type }
    })
    if (!uploadRes.ok) throw new Error(`上传失败：${uploadRes.status}`)

    // 更新对应字段
    editForm.value[type] = access_url

    // 如果是编辑模式下，直接保存
    if (showEditDialog.value) {
      ElMessage.success(`${name}上传成功，请保存资料`)
    } else {
      // 非编辑模式，直接更新
      await updateUserProfile({ [type]: access_url })
    }
  } catch (error) {
    ElMessage.error(`${name}上传失败：${error.message}`)
  } finally {
    updating.value = false
  }
}

// 更新用户资料
const updateProfile = async () => {
  const formRef = editFormRef.value
  if (!formRef) return

  try {
    await formRef.validate()
    updating.value = true

    const updateData = {
      display_name: editForm.value.display_name.trim(),
      gender: editForm.value.gender,
      summary: editForm.value.summary,
      avatar_url: editForm.value.avatar_url || user.value.avatar_url,
      background_url: editForm.value.background_url || user.value.background_url
    }

    await updateUserProfile(updateData)
    showEditDialog.value = false
    ElMessage.success('资料更新成功')
  } catch (error) {
    if (error instanceof Error) {
      ElMessage.error(`资料更新失败：${error.message}`)
    }
    // 验证失败不显示错误消息
  } finally {
    updating.value = false
  }
}

// 更新用户信息的通用方法
const updateUserProfile = async (updateData) => {
  const response = await api.updateUserProfile(updateData, false)
  const newUserData = response.data?.user
  if (!newUserData) throw new Error('后端返回数据不完整')

  user.value = { ...user.value, ...newUserData }
  userStore.userInfo = { ...userStore.userInfo, ...user.value }
}

// 复制用户ID
const copyUserId = async () => {
  const userId = user.value.user_id
  if (!userId) {
    ElMessage.warning('用户ID不存在')
    return
  }

  try {
    await navigator.clipboard.writeText(userId)
    ElMessage.success('用户ID已复制到剪贴板')
  } catch (error) {
    // 降级方案
    const textArea = document.createElement('textarea')
    textArea.value = userId
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
    ElMessage.success('用户ID已复制到剪贴板')
  }
}

// 导航函数
const goToFavoritesPage = () => {
  router.push('/favorites')
}

const goToHistoryPage = () => {
  router.push('/history')
}

const goToBookDetail = (bookId) => {
  router.push(`/book/${bookId}`)
}

// 工具函数
const formatDays = (timestamp) => {
  if (!timestamp) return 0
  const joinDate = new Date(timestamp * 1000)
  const today = new Date()
  const diffTime = Math.abs(today - joinDate)
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
}

const formatDate = (timestamp) => {
  if (!timestamp) return '未知时间'
  return new Date(timestamp * 1000).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatGender = (gender) => {
  const genderMap = {
    'male': '男',
    'female': '女',
    'other': '其他',
    '': '未设置'
  }
  return genderMap[gender] || '未设置'
}
</script>

<style scoped>
.qqspace-profile {
  min-height: 100vh;
  background-color: #f5f7fa;
}

/* 顶部导航 */
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

/* 封面区域 */
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

/* 个人信息覆盖层 */
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

/* 新增：用户ID显示区域 */
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

/* 主要内容区域 */
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

/* 左侧边栏 */
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

/* 新增：用户ID值的特殊样式 */
.user-id-value {
  font-family: 'Courier New', monospace;
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

/* 右侧内容 */
.right-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

/* 功能导航 */
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

/* 内容区域 */
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

/* 收藏预览 */
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

/* 历史预览 */
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

/* 设置内容 */
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

/* 空状态 */
.empty-preview {
  padding: 40px 0;
  text-align: center;
}

/* 裁剪对话框 */
.crop-dialog {
  border-radius: 12px;
}

.crop-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.crop-preview {
  width: 100%;
  height: 400px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  overflow: hidden;
}

.cropper {
  width: 100%;
  height: 100%;
}

.crop-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}

/* 编辑对话框 */
.edit-dialog {
  border-radius: 12px;
}

.edit-form {
  margin-top: 20px;
}

.preview-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.preview-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  border: 2px solid #f0f0f0;
}

.preview-cover {
  width: 120px;
  height: 80px;
  border-radius: 8px;
  border: 2px solid #f0f0f0;
}

.preview-error {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  color: #c0c4cc;
}

.change-btn {
  color: #1890ff;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .content-container {
    grid-template-columns: 1fr;
  }

  .left-sidebar {
    position: static;
  }

  .profile-overlay {
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 20px;
  }

  .user-stats {
    justify-content: center;
  }

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

  .crop-dialog {
    width: 95% !important;
  }

  .crop-preview {
    height: 300px;
  }

  .crop-actions {
    flex-wrap: wrap;
  }
}
</style>