import axios from "axios";
import { createApiClient } from "./client";
import { API_BASE_URL } from "./config";

const accountApi = createApiClient("/api/account");

// 登录是特殊的，不需要 token
export const login = (username, password) => {
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
  return accountApi.post("/logout/");
};

export const getUsers = () => {
  return accountApi.get("/users/");
};

export const getPageConfig = () => {
  return accountApi.get("/page-config/");
};

export const createEnterpriseAdmin = (data) => {
  return accountApi.post("/create-enterprise-admin/", data);
};

export const createEnterpriseUser = (data) => {
  return accountApi.post("/create-enterprise-user/", data);
};

export const getCurrentUser = () => {
  return accountApi.get("/current-user/");
};

export const updateProfile = (data) => {
  return accountApi.put("/profile/update/", data);
};

export const changePassword = (data) => {
  return accountApi.post("/password/change/", data);
};

export const simpleRegister = (data) => {
  return axios.post(`${API_BASE_URL}/api/account/simple-register/`, data);
};

export const createAndBindCompany = (data) => {
  return accountApi.post("/create-and-bind-company/", data);
};

export const bindExistingCompany = (data) => {
  return accountApi.post("/bind-existing-company/", data);
};

export const updateUserStatus = (userId, data) => {
  return accountApi.put(`/users/${userId}/status/`, data);
};

export const deleteUser = (userId) => {
  return accountApi.delete(`/users/${userId}/delete/`);
};

export const updateUserType = (userId, data) => {
  return accountApi.put(`/users/${userId}/type/`, data);
};

export const createUser = (data) => {
  return accountApi.post("/users/create/", data);
};

export default accountApi;
