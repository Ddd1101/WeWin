import axios from "axios";
import { API_BASE_URL } from "./config";

// 创建基础 axios 实例的工厂函数
function createApiClient(basePath) {
  const client = axios.create({
    baseURL: `${API_BASE_URL}${basePath}`,
    timeout: 10000,
  });

  // 请求拦截器
  client.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem("token");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // 响应拦截器
  client.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response && error.response.status === 401) {
        localStorage.removeItem("token");
        localStorage.removeItem("userInfo");
        window.location.href = "/login";
      }
      return Promise.reject(error);
    }
  );

  return client;
}

export { createApiClient };
