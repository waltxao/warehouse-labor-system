import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import client from '../api/client'

export interface UserInfo {
  id: number
  username: string
  role: string
  is_active: boolean
  warehouse_ids?: number[]
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('access_token') || '')
  const user = ref<UserInfo | null>(null)
  const isAuthenticated = computed(() => !!token.value)

  async function login(username: string, password: string) {
    const resp: any = await client.post('/auth/login', { username, password })
    token.value = resp.data.access_token
    localStorage.setItem('access_token', resp.data.access_token)
    localStorage.setItem('refresh_token', resp.data.refresh_token)
    await fetchUser()
  }

  async function fetchUser() {
    const resp: any = await client.get('/auth/me')
    user.value = resp.data
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  function hasRole(...roles: string[]) {
    return !!(user.value && roles.includes(user.value.role))
  }

  return { token, user, isAuthenticated, login, fetchUser, logout, hasRole }
})
