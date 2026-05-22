import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || '{}'))
  const currentStore = ref(JSON.parse(localStorage.getItem('currentStore') || '{}'))

  const setToken = (newToken) => {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  const setUserInfo = (info) => {
    userInfo.value = info
    localStorage.setItem('userInfo', JSON.stringify(info))
  }

  const setCurrentStore = (store) => {
    currentStore.value = store
    localStorage.setItem('currentStore', JSON.stringify(store))
  }

  const logout = () => {
    token.value = ''
    userInfo.value = {}
    currentStore.value = {}
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
    localStorage.removeItem('currentStore')
  }

  return {
    token,
    userInfo,
    currentStore,
    setToken,
    setUserInfo,
    setCurrentStore,
    logout
  }
})