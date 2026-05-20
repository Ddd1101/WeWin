import { createApiClient } from "./client";

const storeApi = createApiClient("/api/store");

// 平台和分类
export const getPlatforms = () => {
  return storeApi.get("/platforms/");
};

export const getCategories = () => {
  return storeApi.get("/categories/");
};

// 店铺管理
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

// 店铺 API 配置
export const getStoreApiConfig = (storeId) => {
  return storeApi.get(`/${storeId}/api-config/`);
};

export const createOrUpdateStoreApiConfig = (storeId, data) => {
  return storeApi.post(`/${storeId}/api-config/create-or-update/`, data);
};

// 数据拉取
export const triggerDataPull = (storeId, data) => {
  return storeApi.post(`/${storeId}/trigger-pull/`, data, {
    timeout: 600000, // 10分钟超时
  });
};

export const getPullTasks = (storeId) => {
  return storeApi.get(`/${storeId}/pull-tasks/`);
};

// 订单相关
export const getStoreOrders = (storeId, params = {}) => {
  return storeApi.get(`/${storeId}/orders/`, { params });
};

export const getOrderDetail = (storeId, platformOrderId) => {
  return storeApi.get(`/${storeId}/orders/${platformOrderId}/detail/`);
};

// 商品相关
export const getProductTypes = () => {
  return storeApi.get("/products/types/");
};

export const getProducts = (params = {}) => {
  return storeApi.get("/products/", { params });
};

export const createProduct = (data) => {
  // 如果数据包含图片文件，则使用 FormData
  if (data.image) {
    const formData = new FormData();
    for (const key in data) {
      if (data[key] !== undefined && data[key] !== null) {
        if (key === 'beads' || key === 'accessories') {
            formData.append(key, JSON.stringify(data[key]));
        } else {
            formData.append(key, data[key]);
        }
      }
    }
    return storeApi.post("/products/create/", formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }
  return storeApi.post("/products/create/", data);
};

export const updateProduct = (id, data) => {
  // 如果数据包含图片文件或删除图片请求，则使用 FormData
  if (data.image || data.remove_image) {
    const formData = new FormData();
    for (const key in data) {
      if (data[key] !== undefined && data[key] !== null) {
        if (key === 'beads' || key === 'accessories') {
            formData.append(key, JSON.stringify(data[key]));
        } else {
            formData.append(key, data[key]);
        }
      }
    }
    return storeApi.post(`/products/${id}/update/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }
  return storeApi.put(`/products/${id}/update/`, data);
};

export const deleteProduct = (id) => {
  return storeApi.delete(`/products/${id}/delete/`);
};

export const getProductDetail = (id) => {
  return storeApi.get(`/products/${id}/detail/`);
};

export const getAccessories = () => {
  return storeApi.get("/products/accessories/");
};

export const getBeads = () => {
  return storeApi.get("/products/beads/");
};

export default storeApi;
