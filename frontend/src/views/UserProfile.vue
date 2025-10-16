<template>
  <div class="user-profile">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card>
          <template #header>
            <h3>个人信息</h3>
          </template>
          <div class="user-info">
            <!-- 头像上传区域（保留错误 fallback） -->
            <div class="avatar-uploader" @click="triggerFileInput">
              <el-avatar :size="100" :src="user.avatar_url">
                <template #error>
                  <div class="avatar-error">
                    <el-icon><User /></el-icon>
                  </div>
                </template>
              </el-avatar>
              <div class="avatar-overlay">
                <el-icon><Camera /></el-icon>
                <span>更换头像</span>
              </div>
            </div>
            <input
              type="file"
              ref="fileInput"
              style="display: none"
              accept="image/*"
              @change="handleAvatarUpload"
            />

            <!-- 用户信息展示（新增核心字段：邮箱验证状态、角色详情） -->
            <div class="user-name">{{ user.display_name }}</div>
            <div class="user-email">{{ user.email }}</div>
            <div class="user-role">
              {{ user.is_admin ? '管理员' : '普通用户' }}
              <!-- 显式展示is_verified状态，方便调试 -->
              <span class="verify-tag" :class="user.is_verified ? 'verified' : 'unverified'">
                {{ user.is_verified ? '已验证' : '未验证' }}
              </span>
            </div>
            <div class="user-gender" v-if="user.gender">
              {{ genderMap[user.gender] }}
            </div>

            <el-button type="primary" @click="showEditDialog = true" class="edit-btn">
              编辑资料
            </el-button>
          </div>
        </el-card>
      </el-col>

      <el-col :span="18">
        <!-- 收藏/历史标签页（无修改） -->
        <el-tabs v-model="activeTab">
          <el-tab-pane label="我的收藏" name="favorites">
            <el-table :data="favorites" style="width: 100%">
              <el-table-column label="图书封面" width="100">
                <template #default="{ row }">
                  <el-image :src="row.book_cover" fit="cover" style="width: 60px; height: 80px" />
                </template>
              </el-table-column>
              <el-table-column prop="book_title" label="书名" />
              <el-table-column prop="book_author" label="作者" />
              <el-table-column label="操作" width="120">
                <template #default="{ row }">
                  <el-button link @click="goToBookDetail(row.book_id)">查看</el-button>
                  <el-button link @click="removeFavorite(row.book_id)">取消收藏</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
          <el-tab-pane label="浏览历史" name="history">
            <el-table :data="viewHistory" style="width: 100%">
              <el-table-column label="图书封面" width="100">
                <template #default="{ row }">
                  <el-image :src="row.book_cover" fit="cover" style="width: 60px; height: 80px" />
                </template>
              </el-table-column>
              <el-table-column prop="book_title" label="书名" />
              <el-table-column prop="book_author" label="作者" />
              <el-table-column prop="view_time" label="浏览时间">
                <template #default="{ row }">
                  {{ formatDate(row.view_time) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="80">
                <template #default="{ row }">
                  <el-button link @click="goToBookDetail(row.book_id)">查看</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </el-col>
    </el-row>

    <!-- 编辑资料对话框（包含名字和性别） -->
    <el-dialog v-model="showEditDialog" title="编辑资料" width="500px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="显示名称">
          <el-input v-model="editForm.display_name" placeholder="请输入显示名称" />
        </el-form-item>
        <el-form-item label="性别">
          <el-select v-model="editForm.gender" placeholder="请选择性别">
            <el-option label="男" value="male" />
            <el-option label="女" value="female" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="updateProfile" :loading="updating">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElTag } from 'element-plus'
import { Camera, User } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import api from '@/utils/api'

// 基础实例与状态
const router = useRouter()
const userStore = useUserStore()
const activeTab = ref('favorites')
const showEditDialog = ref(false)
const updating = ref(false)
const favorites = ref([])
const viewHistory = ref([])
const fileInput = ref(null)
const genderMap = reactive({ male: '男', female: '女', other: '其他' })

// 核心修复1：初始赋值时显式包含所有核心字段，避免缺失（给默认值兜底）
const user = ref({
  user_id: '',
  email: '',
  display_name: '',
  avatar_url: '',
  gender: '',
  is_verified: false,  // 显式初始化：邮箱验证状态（默认未验证）
  password: '',        // 显式初始化：密码哈希（前端仅存储，不展示）
  role: 'user',        // 显式初始化：角色（默认普通用户）
  created_at: 0,
  updated_at: 0,
  ...userStore.userInfo  // 合并Pinia中的数据（覆盖默认值）
})

// 编辑表单：仅包含可修改字段（名字、性别）
const editForm = ref({
  display_name: user.value.display_name || '',
  gender: user.value.gender || ''
})

// 页面挂载初始化
onMounted(() => {
  fetchUserInfo()
  fetchFavorites()
  fetchViewHistory()
})

// -------------------------- 基础数据拉取函数（修复核心字段同步） --------------------------
const fetchUserInfo = async () => {
  try {
    const response = await api.getCurrentUser()
    const newUserData = response.data || {}

    // 核心修复2：合并数据时显式保留核心字段（避免后端未返回时被清空）
    user.value = {
      // 先保留当前已有的核心字段（防止后端返回缺失）
      ...user.value,
      // 再合并后端返回的新数据（更新可修改字段）
      ...newUserData,
      // 强制兜底：确保核心字段不会为undefined
      is_verified: newUserData.is_verified ?? user.value.is_verified,
      password: newUserData.password ?? user.value.password,
      role: newUserData.role ?? user.value.role,
      is_admin: (newUserData.role ?? user.value.role) === 'admin'  // 基于role重新计算is_admin
    }

    // 同步编辑表单（仅更新可修改字段）
    editForm.value = {
      ...editForm.value,
      display_name: user.value.display_name || '',
      gender: user.value.gender || ''
    }

    // 同步Pinia：确保全局状态包含核心字段
    userStore.userInfo = { ...userStore.userInfo, ...user.value }
  } catch (error) {
    console.error('获取用户信息失败', error)
    ElMessage.error('获取用户信息失败')
  }
}

// -------------------------- 修复：获取收藏列表（添加错误处理与多格式兼容） --------------------------
const fetchFavorites = async () => {
  try {
    console.log('开始获取收藏列表...');
    const response = await api.getFavorites();

    // 调试日志
    console.log('收藏API响应:', response);

    let favoritesData = [];
    if (response.data && Array.isArray(response.data)) {
      favoritesData = response.data;
    } else if (response.data && response.data.items) {
      favoritesData = response.data.items;
    } else if (response.data && response.data.body) {
      // 处理嵌套的body结构
      try {
        favoritesData = JSON.parse(response.data.body);
      } catch (e) {
        console.error('解析收藏数据失败:', e);
      }
    }

    console.log('处理后的收藏数据:', favoritesData);
    favorites.value = favoritesData;

  } catch (error) {
    console.error('获取收藏列表失败', error);
    ElMessage.error('获取收藏列表失败: ' + (error.response?.data?.error || error.message));
    favorites.value = []; // 设置空数组避免渲染错误
  }
};

// -------------------------- 修复：获取浏览历史（添加错误处理与多格式兼容） --------------------------
const fetchViewHistory = async () => {
  try {
    console.log('开始获取浏览历史...');
    const response = await api.getViewHistory();

    // 调试日志
    console.log('浏览历史API响应:', response);

    let historyData = [];
    if (response.data && Array.isArray(response.data)) {
      historyData = response.data;
    } else if (response.data && response.data.items) {
      historyData = response.data.items;
    } else if (response.data && response.data.body) {
      // 处理嵌套的body结构
      try {
        historyData = JSON.parse(response.data.body);
      } catch (e) {
        console.error('解析浏览历史数据失败:', e);
      }
    }

    console.log('处理后的浏览历史数据:', historyData);
    viewHistory.value = historyData;

  } catch (error) {
    console.error('获取浏览历史失败', error);
    ElMessage.error('获取浏览历史失败: ' + (error.response?.data?.error || error.message));
    viewHistory.value = []; // 设置空数组避免渲染错误
  }
};

// -------------------------- 头像上传逻辑（修复：不传递user_id，避免干扰后端） --------------------------
const triggerFileInput = () => { fileInput.value?.click() }
const handleAvatarUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  updating.value = true
  try {
    // 1. 文件校验（保持原有逻辑）
    const isImage = file.type.startsWith('image/')
    const isLt5M = file.size / 1024 / 1024 < 5
    if (!isImage) throw new Error('只能上传图片文件')
    if (!isLt5M) throw new Error('图片大小不能超过5MB')

    // 2. 获取OSS预签名URL（保持原有逻辑）
    const uploadUrlRes = await api.getUploadUrl(file.name, file.type)
    if (!uploadUrlRes.data?.presigned_url) throw new Error('获取上传链接失败')
    const { presigned_url, access_url } = uploadUrlRes.data

    // 3. 上传图片到OSS（保持原有逻辑）
    const uploadRes = await fetch(presigned_url, {
      method: 'PUT',
      body: file,
      headers: { 'Content-Type': file.type },
      timeout: 30000
    })
    if (!uploadRes.ok) throw new Error(`OSS上传失败：${uploadRes.status}`)

    // 核心修复3：更新头像时，仅传递avatar_url（不传递user_id，后端从Token获取）
    // 且明确告诉后端是JSON数据（不是FormData）
    const updateRes = await api.updateUserProfile({ avatar_url: access_url }, false)
    const newUserData = updateRes.data?.user
    if (!newUserData) throw new Error('后端返回数据不完整')

    // 合并数据：保留核心字段，仅更新头像相关
    user.value = { ...user.value, ...newUserData }
    userStore.userInfo = { ...userStore.userInfo, ...user.value }

    ElMessage.success('头像更新成功')
  } catch (error) {
    ElMessage.error(`头像更新失败：${error.message}`)
  } finally {
    updating.value = false
    event.target.value = '' // 清空文件输入
  }
}

// -------------------------- 资料更新逻辑（修复：FormData传递+不传递user_id） --------------------------
const updateProfile = async () => {
  // 表单验证（保持原有逻辑）
  if (!editForm.value.display_name.trim()) {
    ElMessage.warning('显示名称不能为空')
    return
  }

  updating.value = true
  try {
    // 核心修复4：仅传递可修改字段（display_name/gender），不传递user_id
    const formData = new FormData()
    formData.append('display_name', editForm.value.display_name.trim())
    formData.append('gender', editForm.value.gender || '')

    // 明确告诉后端是FormData（is_form_data=true，匹配后端逻辑）
    const updateRes = await api.updateUserProfile(formData, true)
    const newUserData = updateRes.data?.user
    if (!newUserData) throw new Error('后端返回数据不完整')

    // 合并数据：保留核心字段，仅更新名字和性别
    user.value = { ...user.value, ...newUserData }
    userStore.userInfo = { ...userStore.userInfo, ...user.value }

    ElMessage.success('资料更新成功')
    showEditDialog.value = false
  } catch (error) {
    ElMessage.error(`资料更新失败：${error.message}`)
  } finally {
    updating.value = false
  }
}

// -------------------------- 收藏/详情逻辑（无修改） --------------------------
const removeFavorite = async (bookId) => {
  try {
    await api.removeFavorite(bookId)
    ElMessage.success('取消收藏成功')
    fetchFavorites() // 重新拉取收藏列表
  } catch (error) {
    console.error('取消收藏失败', error)
    ElMessage.error('取消收藏失败')
  }
}
const goToBookDetail = (bookId) => {
  router.push(`/book/${bookId}`)
}
const formatDate = (timestamp) => {
  if (!timestamp) return ''
  return new Date(timestamp * 1000).toLocaleString() // 假设时间戳是秒级，转毫秒级
}

// -------------------------- 监听Pinia变化（修复：显式同步核心字段） --------------------------
watch(
  () => userStore.userInfo,
  (newUserInfo) => {
    // 核心修复5：同步时保留核心字段，避免被Pinia空值覆盖
    user.value = {
      ...user.value,
      ...newUserInfo,
      is_verified: newUserInfo.is_verified ?? user.value.is_verified,
      password: newUserInfo.password ?? user.value.password,
      role: newUserInfo.role ?? user.value.role,
      is_admin: (newUserInfo.role ?? user.value.role) === 'admin'
    }
    // 同步编辑表单
    editForm.value = {
      ...editForm.value,
      display_name: user.value.display_name || '',
      gender: user.value.gender || ''
    }
  },
  { deep: true }
)
</script>

<style scoped>
/* 原有样式 + 新增验证状态标签样式 */
.user-profile { padding: 20px; }
.user-info { text-align: center; }
.avatar-uploader { position: relative; display: inline-block; cursor: pointer; margin-bottom: 15px; }
.avatar-overlay {
  position: absolute; inset: 0; background: rgba(0,0,0,0.5); color: #fff;
  display: flex; flex-direction: column; justify-content: center; align-items: center;
  opacity: 0; transition: opacity 0.3s; border-radius: 50%;
}
.avatar-uploader:hover .avatar-overlay { opacity: 1; }
.avatar-overlay .el-icon { font-size: 24px; margin-bottom: 5px; }
.avatar-overlay span { font-size: 12px; }
.avatar-error { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; color: #c0c4cc; }
.user-name { font-size: 18px; font-weight: bold; margin-top: 15px; }
.user-email { color: #666; margin-top: 5px; }
.user-role { color: #909399; margin-top: 5px; display: flex; align-items: center; justify-content: center; gap: 8px; }
.verify-tag.verified { background-color: #f0f9eb; color: #67c23a; }
.verify-tag.unverified { background-color: #fef0f0; color: #f56c6c; }
.user-gender { color: #909399; margin-top: 5px; }
.edit-btn { margin-top: 20px; }
</style>