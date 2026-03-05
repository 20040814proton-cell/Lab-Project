import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref<string | null>(null)
  const userInfo = ref<Record<string, any> | null>(null)

  function decodeTokenPayload(rawToken: string) {
    try {
      const [, payload] = rawToken.split('.')
      if (!payload)
        return null
      const normalized = payload.replace(/-/g, '+').replace(/_/g, '/')
      const padded = normalized.padEnd(normalized.length + (4 - normalized.length % 4) % 4, '=')
      return JSON.parse(atob(padded))
    } catch {
      return null
    }
  }

  function isTokenExpired(rawToken: string | null) {
    if (!rawToken)
      return true
    const payload = decodeTokenPayload(rawToken)
    const exp = payload?.exp
    if (!exp || typeof exp !== 'number')
      return true
    return Date.now() >= exp * 1000
  }

  function isTokenValid() {
    return Boolean(token.value) && !isTokenExpired(token.value)
  }

  const normalizedRole = computed(() => {
    const role = userInfo.value?.user_role ?? userInfo.value?.role ?? ''
    return String(role).toLowerCase()
  })

  function hasRole(...roles: string[]) {
    const target = normalizedRole.value
    return roles.map(r => r.toLowerCase()).includes(target)
  }

  function login(accessToken: string, user: Record<string, any>) {
    token.value = accessToken
    userInfo.value = user
    localStorage.setItem('token', accessToken)
    localStorage.setItem('userInfo', JSON.stringify(user))
  }

  function logout() {
    token.value = null
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
  }

  function setUserInfo(user: Record<string, any>) {
    userInfo.value = user
    localStorage.setItem('userInfo', JSON.stringify(user))
  }

  function init() {
    const storedToken = localStorage.getItem('token')
    const storedUser = localStorage.getItem('userInfo')
    if (storedToken && isTokenExpired(storedToken)) {
      logout()
      return
    }
    if (storedToken) {
      token.value = storedToken
    }
    if (storedUser) {
      try {
        userInfo.value = JSON.parse(storedUser)
      } catch (e) {
        console.error('Failed to parse user info', e)
      }
    }
  }

  return {
    token,
    userInfo,
    normalizedRole,
    hasRole,
    isTokenExpired,
    isTokenValid,
    login,
    logout,
    init,
    setUserInfo,
  }
})
