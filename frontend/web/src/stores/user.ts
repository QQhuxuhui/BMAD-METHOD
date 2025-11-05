import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface UserInfo {
  id: string
  name: string
  email: string
  avatar?: string
}

export const useUserStore = defineStore('user', () => {
  const userInfo = ref<UserInfo | null>(null)
  const token = ref<string>('')

  function setUserInfo(info: UserInfo) {
    userInfo.value = info
  }

  function setToken(newToken: string) {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  function logout() {
    userInfo.value = null
    token.value = ''
    localStorage.removeItem('token')
  }

  // 从localStorage恢复token
  function initToken() {
    const savedToken = localStorage.getItem('token')
    if (savedToken) {
      token.value = savedToken
    }
  }

  return {
    userInfo,
    token,
    setUserInfo,
    setToken,
    logout,
    initToken,
  }
})
