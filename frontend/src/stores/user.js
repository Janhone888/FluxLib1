import { defineStore } from 'pinia'
import router from '@/router'
import api from '@/utils/api'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    userInfo: JSON.parse(localStorage.getItem('userInfo') || '{}'),
    isAuthenticated: !!localStorage.getItem('token')
  }),

  actions: {
    async login(credentials) {
      try {
        const response = await api.login(credentials)
        this.token = response.data.token
        this.userInfo = {
          user_id: response.data.user_id,
          email: response.data.email,
          role: response.data.role
        }
        this.isAuthenticated = true

        localStorage.setItem('token', this.token)
        localStorage.setItem('userInfo', JSON.stringify(this.userInfo))

        // 触发用户变化事件
        window.dispatchEvent(new CustomEvent('user-changed'))

        return true
      } catch (error) {
        console.error('登录失败:', error)
        throw error
      }
    },

    logout() {
      this.token = ''
      this.userInfo = {}
      this.isAuthenticated = false
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')

      // 触发用户变化事件
      window.dispatchEvent(new CustomEvent('user-changed'))

      router.push('/login')
    }
  }
})