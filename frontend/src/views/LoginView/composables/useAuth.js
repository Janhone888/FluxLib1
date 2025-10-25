/* 认证逻辑组合式函数 */
import { useUserStore } from '@/stores/user'
import api from '@/utils/api'

export function useAuth() {
  const userStore = useUserStore()

  const login = async (loginData) => {
    const response = await api.login(loginData)

    userStore.token = response.data.token
    userStore.userInfo = {
      user_id: response.data.user_id,
      email: response.data.email,
      role: response.data.role,
      is_admin: response.data.is_admin,
      is_temporary_admin: response.data.is_temporary_admin
    }
    userStore.isAuthenticated = true

    localStorage.setItem('token', userStore.token)
    localStorage.setItem('userInfo', JSON.stringify(userStore.userInfo))

    return userStore.userInfo
  }

  const register = async (registerData) => {
    const response = await api.register(registerData)
    return response.data
  }

  const sendVerificationCode = async (email) => {
    const response = await api.sendVerificationCode(email)
    return response.data
  }

  return {
    login,
    register,
    sendVerificationCode
  }
}