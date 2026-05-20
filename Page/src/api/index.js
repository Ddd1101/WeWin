// API 模块统一导出
import accountApi, * as account from "./account";
import companyApi, * as company from "./company";
import storeApi, * as store from "./store";
import { API_BASE_URL } from "./config";

export { API_BASE_URL };

// 导出所有 API 函数
export {
  account,
  company,
  store,
};

// 导出默认实例
export { accountApi, companyApi, storeApi };

// 保持向后兼容，也可以直接导出常用函数
export * from "./account";
export * from "./company";
export * from "./store";

// 默认导出 accountApi（保持兼容性）
export default accountApi;
