import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface User {
  id: number
  username: string
  role: 'student' | 'teacher'
  realname?: string
  avatar?: string
}

export const useUserStore = defineStore('user', () => {
  // 状态
  const user = ref<User | null>(null)
  const isLoggedIn = computed(() => user.value !== null)
  const userRole = computed(() => user.value?.role || '')

  // 登录
  function login(userData: User) {
    user.value = userData
    localStorage.setItem('user', JSON.stringify(userData))
  }

  // 登出
  function logout() {
    user.value = null
    localStorage.removeItem('user')
  }

  // 从 localStorage 恢复
  function restoreFromStorage() {
    const stored = localStorage.getItem('user')
    if (stored) {
      try {
        user.value = JSON.parse(stored)
      } catch (e) {
        localStorage.removeItem('user')
      }
    }
  }

  // 更新用户信息
  function updateUser(data: Partial<User>) {
    if (user.value) {
      user.value = { ...user.value, ...data }
      localStorage.setItem('user', JSON.stringify(user.value))
    }
  }

  return {
    user,
    isLoggedIn,
    userRole,
    login,
    logout,
    restoreFromStorage,
    updateUser
  }
})
