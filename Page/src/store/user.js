import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || '{}'))
  const currentStore = ref(JSON.parse(localStorage.getItem('currentStore') || '{}'))
  const pageConfig = ref(JSON.parse(localStorage.getItem('pageConfig') || '[]'))

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

  const setPageConfig = (config) => {
    pageConfig.value = config
    localStorage.setItem('pageConfig', JSON.stringify(config))
  }

  const logout = () => {
    token.value = ''
    userInfo.value = {}
    currentStore.value = {}
    pageConfig.value = []
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
    localStorage.removeItem('currentStore')
    localStorage.removeItem('pageConfig')
  }

  return {
    token,
    userInfo,
    currentStore,
    pageConfig,
    setToken,
    setUserInfo,
    setCurrentStore,
    setPageConfig,
    logout
  }
})