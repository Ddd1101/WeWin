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
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const login = (username, password) => {
  return api.post('/login/', { username, password })
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

export default api
