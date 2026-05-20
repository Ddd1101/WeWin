import { createApiClient } from "./client";

const companyApi = createApiClient("/api/company");

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

export default companyApi;
