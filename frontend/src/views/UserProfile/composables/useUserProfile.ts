import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import api from '@/utils/api'

export interface UserProfile {
  user_id: string
  email: string
  display_name: string
  avatar_url: string
  background_url: string
  gender: string
  is_verified: boolean
  is_admin: boolean
  summary: string
  created_at: number
}

export function useUserProfile() {
  const userStore = useUserStore()

  const user = ref<UserProfile>({
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

  const updating = ref(false)

  const fetchUserInfo = async () => {
    try {
      const response = await api.getCurrentUser()
      const newUserData = response.data || {}
      user.value = { ...user.value, ...newUserData }
      userStore.userInfo = { ...userStore.userInfo, ...user.value }
      return user.value
    } catch (error) {
      console.error('获取用户信息失败', error)
      ElMessage.error('获取用户信息失败')
      throw error
    }
  }

  const updateUserProfile = async (updateData: Partial<UserProfile>) => {
    updating.value = true
    try {
      const response = await api.updateUserProfile(updateData, false)
      const newUserData = response.data?.user
      if (!newUserData) throw new Error('后端返回数据不完整')

      user.value = { ...user.value, ...newUserData }
      userStore.userInfo = { ...userStore.userInfo, ...user.value }
      return newUserData
    } catch (error) {
      console.error('更新用户信息失败', error)
      throw error
    } finally {
      updating.value = false
    }
  }

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

  const formatDays = (timestamp: number) => {
    if (!timestamp) return 0
    const joinDate = new Date(timestamp * 1000)
    const today = new Date()
    const diffTime = Math.abs(today - joinDate)
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  }

  const formatDate = (timestamp: number) => {
    if (!timestamp) return '未知时间'
    return new Date(timestamp * 1000).toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const formatGender = (gender: string) => {
    const genderMap: Record<string, string> = {
      'male': '男',
      'female': '女',
      'other': '其他',
      '': '未设置'
    }
    return genderMap[gender] || '未设置'
  }

  return {
    user,
    updating,
    fetchUserInfo,
    updateUserProfile,
    copyUserId,
    formatDays,
    formatDate,
    formatGender
  }
}