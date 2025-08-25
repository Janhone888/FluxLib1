<template>
  <div class="user-profile">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card>
          <template #header>
            <h3>个人信息</h3>
          </template>
          <div class="user-info">
            <!-- 头像上传区域 -->
            <div class="avatar-uploader" @click="triggerFileInput">
              <el-avatar :size="100" :src="user.avatar_url" />
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

            <div class="user-name">{{ user.display_name }}</div>
            <div class="user-email">{{ user.email }}</div>
            <div class="user-role">{{ user.is_admin ? '管理员' : '普通用户' }}</div>
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

    <!-- 编辑资料对话框 -->
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
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Camera } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import api from '@/utils/api'

// 路由实例
const router = useRouter()
// 用户状态管理
const userStore = useUserStore()
// 标签页激活状态
const activeTab = ref('favorites')
// 编辑对话框显示状态
const showEditDialog = ref(false)
// 加载状态（上传/更新时）
const updating = ref(false)
// 收藏列表数据
const favorites = ref([])
// 浏览历史数据
const viewHistory = ref([])
// 文件上传输入框引用
const fileInput = ref(null)

// 性别映射
const genderMap = reactive({
  male: '男',
  female: '女',
  other: '其他'
})

// 用户信息（从增加版调整为ref类型，字段改为is_admin）
const user = ref({
  email: '',
  display_name: '',
  avatar_url: '',
  is_admin: false,
  gender: ''
})

// 编辑表单数据
const editForm = ref({
  display_name: '',
  gender: ''
})

// 页面挂载时初始化数据
onMounted(() => {
  fetchUserInfo()
  fetchFavorites()
  fetchViewHistory()
})

// 获取用户信息（整合增加版逻辑，移除原版冗余默认值）
const fetchUserInfo = async () => {
  try {
    const response = await api.getCurrentUser()
    user.value = response.data
    // 初始化编辑表单（与用户信息同步）
    editForm.value = {
      display_name: user.value.display_name,
      gender: user.value.gender || ''  // 添加性别
    }
    // 更新Store中的用户信息（确保全局状态同步）
    userStore.userInfo = {
      ...userStore.userInfo,
      display_name: user.value.display_name,
      avatar_url: user.value.avatar_url,
      is_admin: user.value.is_admin,
      email: user.value.email,
      gender: user.value.gender  // 添加性别
    }
  } catch (error) {
    console.error('获取用户信息失败', error)
    ElMessage.error('获取用户信息失败')
  }
}

// 获取收藏列表（保留原版完整功能）
const fetchFavorites = async () => {
  try {
    const response = await api.getFavorites()
    favorites.value = response.data
  } catch (error) {
    console.error('获取收藏列表失败', error)
    ElMessage.error('获取收藏列表失败')
  }
}

// 获取浏览历史（保留原版完整功能）
const fetchViewHistory = async () => {
  try {
    const response = await api.getViewHistory()
    viewHistory.value = response.data
  } catch (error) {
    console.error('获取浏览历史失败', error)
    ElMessage.error('获取浏览历史失败')
  }
}

// 取消收藏（保留原版完整功能）
const removeFavorite = async (bookId) => {
  try {
    await api.removeFavorite(bookId)
    ElMessage.success('已取消收藏')
    fetchFavorites() // 刷新收藏列表
  } catch (error) {
    ElMessage.error('取消收藏失败')
  }
}

// 跳转到图书详情（保留原版完整功能）
const goToBookDetail = (bookId) => {
  router.push(`/books/${bookId}`)
}

// 日期格式化（保留原版完整功能）
const formatDate = (timestamp) => {
  return new Date(timestamp * 1000).toLocaleString()
}

// 触发文件选择（保留增加版逻辑）
const triggerFileInput = () => {
  fileInput.value.click()
}

// 处理头像上传（整合增加版FormData逻辑，保留文件校验）
const handleAvatarUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  // 检查文件类型和大小
  const isImage = file.type.startsWith('image/')
  const isLt5M = file.size / 1024 / 1024 < 5

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return
  }
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过5MB!')
    return
  }

  try {
    updating.value = true

    // 创建FormData对象（增加版逻辑：携带display_name）
    const formData = new FormData()
    formData.append('avatar', file)
    if (user.value.display_name) {
      formData.append('display_name', user.value.display_name)
    }

    // 上传头像（调用增加版API参数格式）
    const response = await api.updateUserProfile(formData, true)

    if (response.data.success) {
      ElMessage.success('头像更新成功')
      await fetchUserInfo() // 重新拉取用户信息更新视图
    } else {
      ElMessage.error('头像更新失败')
    }
  } catch (error) {
    console.error('头像上传失败', error)
    ElMessage.error('头像上传失败')
  } finally {
    updating.value = false
    event.target.value = '' // 清空文件输入
  }
}

// 更新用户信息（整合增加版FormData逻辑）
const updateProfile = async () => {
  try {
    updating.value = true

    // 创建FormData对象（增加版数据格式）
    const formData = new FormData()
    formData.append('display_name', editForm.value.display_name)
    formData.append('gender', editForm.value.gender)

    // 调用更新接口（增加版API参数格式）
    const response = await api.updateUserProfile(formData, true)

    if (response.data.success) {
      ElMessage.success('资料更新成功')
      showEditDialog.value = false
      await fetchUserInfo() // 重新拉取用户信息更新视图
    } else {
      ElMessage.error('资料更新失败')
    }
  } catch (error) {
    console.error('更新用户资料失败', error)
    ElMessage.error('更新失败')
  } finally {
    updating.value = false
  }
}
</script>

<style scoped>
/* 保留原版完整样式，补充user-profile基础样式 */
.user-profile {
  padding: 20px;
}

.user-info {
  text-align: center;
}

.avatar-uploader {
  position: relative;
  display: inline-block;
  cursor: pointer;
  margin-bottom: 15px;
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.avatar-uploader:hover .avatar-overlay {
  opacity: 1;
}

.avatar-overlay .el-icon {
  font-size: 24px;
  margin-bottom: 5px;
}

.avatar-overlay span {
  font-size: 12px;
}

.user-name {
  font-size: 18px;
  font-weight: bold;
  margin-top: 15px;
}

.user-email {
  color: #666;
  margin-top: 5px;
}

.user-role {
  margin-top: 5px;
  color: #909399;
}

.user-gender {
  margin-top: 5px;
  color: #909399;
}

.edit-btn {
  margin-top: 20px;
}
</style>