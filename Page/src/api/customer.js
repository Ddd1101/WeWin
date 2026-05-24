import { createApiClient } from "./client";

const customerApi = createApiClient("/api/customer");

// 获取客户列表
export const getCustomers = (params = {}) => {
  return customerApi.get("/", { params });
};

// 创建客户
export const createCustomer = (data) => {
  return customerApi.post("/create/", data);
};

// 更新客户
export const updateCustomer = (customerId, data) => {
  return customerApi.put(`/${customerId}/update/`, data);
};

// 删除客户
export const deleteCustomer = (customerId) => {
  return customerApi.delete(`/${customerId}/delete/`);
};

// 获取客户详情
export const getCustomerDetail = (customerId) => {
  return customerApi.get(`/${customerId}/detail/`);
};

// 获取客户商品关联列表
export const getCustomerProducts = (customerId) => {
  return customerApi.get(`/${customerId}/products/`);
};

// 创建或更新客户商品关联
export const createOrUpdateCustomerProduct = (customerId, data) => {
  return customerApi.post(`/${customerId}/products/create-or-update/`, data);
};

// 获取客户商品报价历史
export const getCustomerPriceHistory = (customerId, productId, params = {}) => {
  return customerApi.get(
    `/${customerId}/products/${productId}/price-history/`,
    { params },
  );
};

// 获取客户可见性配置
export const getCustomerVisibility = (customerId) => {
  return customerApi.get(`/${customerId}/visibility/`);
};

// 设置客户可见性
export const setCustomerVisibility = (customerId, data) => {
  return customerApi.post(`/${customerId}/visibility/set/`, data);
};

// 删除客户可见性配置
export const removeCustomerVisibility = (customerId, visibilityId) => {
  return customerApi.delete(
    `/${customerId}/visibility/${visibilityId}/delete/`,
  );
};

export default customerApi;
