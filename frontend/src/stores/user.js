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
        // 补充background_url、summary等新字段，确保与UserProfile.vue使用字段匹配
        this.userInfo = {
          user_id: response.data.user_id,
          email: response.data.email,
          role: response.data.role,
          is_admin: response.data.is_admin, // 补充管理员标识字段
          display_name: response.data.display_name || '', // 补充显示名称字段（默认空字符串）
          avatar_url: response.data.avatar_url || '', // 补充头像链接字段（默认空字符串）
          background_url: response.data.background_url || '', // 补充背景图链接字段（默认空字符串）
          summary: response.data.summary || '', // 补充个人简介字段（默认空字符串）
          created_at: response.data.created_at || 0 // 补充注册时间字段（默认0）
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