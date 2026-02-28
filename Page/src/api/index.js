import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api/account',
  timeout: 10000
})

api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      // 只有当状态码为401（未授权）时才重定向到登录页面
      // 403（禁止访问，如账户被禁用）不重定向，让错误信息传递给前端组件处理
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const login = (username, password) => {
  // 登录请求不使用拦截器添加的Authorization头
  return axios.post('http://localhost:8000/api/account/login/', { username, password })
}

export const logout = () => {
  return api.post('/logout/')
}

export const getUsers = () => {
  return api.get('/users/')
}

export const getPageConfig = () => {
  return api.get('/page-config/')
}

export const createEnterpriseAdmin = (data) => {
  return api.post('/create-enterprise-admin/', data)
}

export const createEnterpriseUser = (data) => {
  return api.post('/create-enterprise-user/', data)
}

export const getCurrentUser = () => {
  return api.get('/current-user/')
}

export const updateProfile = (data) => {
  return api.put('/profile/update/', data)
}

export const changePassword = (data) => {
  return api.post('/password/change/', data)
}

export default api
