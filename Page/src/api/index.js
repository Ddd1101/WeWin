import axios from "axios";

// 后端服务地址
const API_BASE_URL = "http://192.168.1.14:8000";

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/account`,
  timeout: 10000,
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // 只有当状态码为401（未授权）时才重定向到登录页面
      // 403（禁止访问，如账户被禁用）不重定向，让错误信息传递给前端组件处理
      localStorage.removeItem("token");
      localStorage.removeItem("userInfo");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  },
);

export const login = (username, password) => {
  // 登录请求不使用拦截器添加的Authorization头
  return axios
    .post(`${API_BASE_URL}/api/account/login/`, { username, password })
    .then((response) => {
      console.log("Login API response:", response);
      return response;
    })
    .catch((error) => {
      console.log("Login API error:", error);
      throw error;
    });
};

export const logout = () => {
  return api.post("/logout/");
};

export const getUsers = () => {
  return api.get("/users/");
};

export const getPageConfig = () => {
  return api.get("/page-config/");
};

export const createEnterpriseAdmin = (data) => {
  return api.post("/create-enterprise-admin/", data);
};

export const createEnterpriseUser = (data) => {
  return api.post("/create-enterprise-user/", data);
};

export const getCurrentUser = () => {
  return api.get("/current-user/");
};

export const updateProfile = (data) => {
  return api.put("/profile/update/", data);
};

export const changePassword = (data) => {
  return api.post("/password/change/", data);
};

// 企业管理相关API

const companyApi = axios.create({
  baseURL: `${API_BASE_URL}/api/company`,
  timeout: 10000,
});

const storeApi = axios.create({
  baseURL: `${API_BASE_URL}/api/store`,
  timeout: 10000,
});

companyApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

storeApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

companyApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("userInfo");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  },
);

storeApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("userInfo");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  },
);

export const getCompanies = () => {
  return companyApi.get("/");
};

export const createCompany = (data) => {
  return companyApi.post("/create/", data);
};

export const updateCompany = (data) => {
  return companyApi.put(`/${data.id}/update/`, data);
};

export const deleteCompany = (id) => {
  return companyApi.delete(`/${id}/delete/`);
};

export const getCompanyUsers = (companyId) => {
  return companyApi.get(`/${companyId}/users/`);
};

export const batchUpdateCompanyStatus = (companyIds, isActive) => {
  return companyApi.post("/batch-status/", {
    company_ids: companyIds,
    is_active: isActive,
  });
};

export const getPlatforms = () => {
  return storeApi.get("/platforms/");
};

export const getCategories = () => {
  return storeApi.get("/categories/");
};

export const getStores = () => {
  return storeApi.get("/");
};

export const createStore = (data) => {
  return storeApi.post("/create/", data);
};

export const updateStore = (data) => {
  return storeApi.put(`/${data.id}/update/`, data);
};

export const deleteStore = (id) => {
  return storeApi.delete(`/${id}/delete/`);
};

export const getStoreApiConfig = (storeId) => {
  return storeApi.get(`/${storeId}/api-config/`);
};

export const createOrUpdateStoreApiConfig = (storeId, data) => {
  return storeApi.post(`/${storeId}/api-config/create-or-update/`, data);
};

export const triggerDataPull = (storeId, data) => {
  return storeApi.post(`/${storeId}/trigger-pull/`, data);
};

export const getStoreOrders = (storeId, params = {}) => {
  return storeApi.get(`/${storeId}/orders/`, { params });
};

export const getPullTasks = (storeId) => {
  return storeApi.get(`/${storeId}/pull-tasks/`);
};

export const getOrderDetail = (storeId, platformOrderId) => {
  return storeApi.get(`/${storeId}/orders/${platformOrderId}/detail/`);
};

export default api;
