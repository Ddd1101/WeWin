import { createRouter, createWebHistory } from "vue-router";

const routes = [
  {
    path: "/login",
    name: "Login",
    component: () => import("../views/Login.vue"),
  },
  {
    path: "/register",
    name: "Register",
    component: () => import("../views/Register.vue"),
  },
  {
    path: "/bind-company",
    name: "BindCompany",
    component: () => import("../views/BindCompany.vue"),
  },
  {
    path: "/",
    name: "Layout",
    component: () => import("../layout/index.vue"),
    redirect: "/dashboard",
    children: [
      {
        path: "dashboard",
        name: "Dashboard",
        component: () => import("../views/Dashboard.vue"),
        meta: { title: "数据概览", icon: "DataAnalysis" },
      },
      {
        path: "stores",
        name: "Stores",
        meta: { title: "店铺管理", icon: "Shop" },
        redirect: "/stores/list",
        children: [
          {
            path: "list",
            name: "StoreList",
            component: () => import("../views/Stores.vue"),
            meta: { title: "店铺列表", icon: "List" },
          },
          {
            path: "test",
            name: "StoreTest",
            component: () => import("../views/StoreTest.vue"),
            meta: { title: "测试页面", icon: "Document" },
          },
        ],
      },
      {
        path: "products",
        name: "Products",
        component: () => import("../views/Products.vue"),
        meta: { title: "商品管理", icon: "Goods" },
      },
      {
        path: "inventory",
        name: "Inventory",
        component: () => import("../views/Inventory.vue"),
        meta: { title: "库存管理", icon: "Box" },
      },
      {
        path: "sales",
        name: "Sales",
        component: () => import("../views/Sales.vue"),
        meta: { title: "销售数据", icon: "TrendCharts" },
      },
      {
        path: "users",
        name: "Users",
        component: () => import("../views/Users.vue"),
        meta: { title: "用户管理", icon: "User" },
      },
      {
        path: "profile",
        name: "Profile",
        component: () => import("../views/Profile.vue"),
        meta: { title: "个人信息", icon: "UserFilled" },
      },
      {
        path: "companies",
        name: "Companies",
        component: () => import("../views/Companies.vue"),
        meta: {
          title: "企业管理",
          icon: "OfficeBuilding",
          requiresAdmin: true,
        },
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem("token");
  if (
    to.path !== "/login" &&
    to.path !== "/register" &&
    to.path !== "/bind-company" &&
    !token
  ) {
    next("/login");
  } else if ((to.path === "/login" || to.path === "/register") && token) {
    next("/");
  } else {
    next();
  }
});

export default router;
