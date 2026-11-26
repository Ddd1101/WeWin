# WeWin 电商 ERP 系统 — Code Wiki

> 本文档为 WeWin 项目仓库的结构化代码知识库，涵盖项目整体架构、主要模块职责、关键类与函数说明、依赖关系及运行方式。
>
> 生成日期：2026-07-06 · 仓库根目录：`d:\workplace_shop\WeWin`

---

## 目录

- [1. 项目概述](#1-项目概述)
- [2. 整体架构](#2-整体架构)
- [3. 仓库目录结构](#3-仓库目录结构)
- [4. 技术栈与依赖](#4-技术栈与依赖)
- [5. 后端 Server（Django）](#5-后端-serverdjango)
  - [5.1 项目配置 wewin/](#51-项目配置-wewin)
  - [5.2 account 应用（用户与认证）](#52-account-应用用户与认证)
  - [5.3 company 应用（企业管理）](#53-company-应用企业管理)
  - [5.4 store 应用（店铺/商品/订单）](#54-store-应用店铺商品订单)
  - [5.5 customer 应用（客户管理）](#55-customer-应用客户管理)
  - [5.6 utils 模块（装饰器）](#56-utils-模块装饰器)
  - [5.7 平台数据拉取服务](#57-平台数据拉取服务)
- [6. 前端 Page（Vue 3）](#6-前端-pagevue-3)
  - [6.1 项目配置](#61-项目配置)
  - [6.2 入口与路由](#62-入口与路由)
  - [6.3 API 层](#63-api-层)
  - [6.4 状态管理 Pinia](#64-状态管理-pinia)
  - [6.5 页面视图](#65-页面视图)
- [7. Android 原生应用](#7-android-原生应用)
  - [7.1 项目配置](#71-项目配置)
  - [7.2 架构模式](#72-架构模式)
  - [7.3 数据层](#73-数据层)
  - [7.4 UI 层](#74-ui-层)
- [8. AliData 遗留模块](#8-alidata-遗留模块)
- [9. 核心数据模型关系](#9-核心数据模型关系)
- [10. 认证与权限体系](#10-认证与权限体系)
- [11. 项目运行方式](#11-项目运行方式)
- [12. 已知问题与注意事项](#12-已知问题与注意事项)

---

## 1. 项目概述

**WeWin** 是一套面向多企业的电商 ERP 管理系统，支持多店铺、多平台订单拉取、商品（串珠 / 配件 / 成品）管理、客户报价与权限隔离。

- **业务领域**：电商运营管理（店铺、商品、订单、客户、库存、销售数据）
- **核心商品类型**：串珠（bead）、手串配件（accessory）、手串成品（finished，由串珠 + 配件组成）
- **支持平台**：1688（已实现）、淘宝 / 天猫 / 京东 / 拼多多 / 抖音 / 快手 / 小红书 / 微信小店（模型已预留，服务待实现）
- **部署形态**：Django 后端 + Vue 3 前端 + Android 原生 App + 遗留 1688 数据拉取脚本

---

## 2. 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         客户端层                                  │
│  ┌──────────────┐   ┌──────────────┐                            │
│  │  Vue 3 Web   │   │  Android App │                            │
│  │  (Page/)     │   │  (Android/)  │                            │
│  │  端口 5173/  │   │  Jetpack     │                            │
│  │      8080    │   │  Compose     │                            │
│  └──────┬───────┘   └──────┬───────┘                            │
│         │                  │                                     │
│         │  HTTP/JSON (JWT) │                                     │
│         ▼                  ▼                                     │
├─────────────────────────────────────────────────────────────────┤
│                       后端服务层                                  │
│  ┌──────────────────────────────────────────────────┐           │
│  │  Django 4.2 (Server/)                            │           │
│  │  端口 8003                                        │           │
│  │  ┌────────┬────────┬────────┬────────┐           │           │
│  │  │account │company │ store  │customer│           │           │
│  │  └────────┴────────┴────────┴────────┘           │           │
│  │  SQLite (db.sqlite3)                              │           │
│  │  平台服务：BaseDataPullService / Ali1688           │           │
│  └──────────────────────┬───────────────────────────┘           │
│                         │                                        │
│         1688 OpenAPI    │                                        │
│         (HMAC-SHA1)     │                                        │
│                         ▼                                        │
├─────────────────────────────────────────────────────────────────┤
│                   外部平台与遗留系统                              │
│  ┌──────────────┐   ┌──────────────┐                            │
│  │  1688 开放平台│   │  AliData/    │                            │
│  │  gw.open.1688│   │  遗留脚本     │                            │
│  │  .com        │   │  (独立运行)   │                            │
│  └──────────────┘   └──────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
```

**关键架构特征**：

1. **多租户隔离**：所有业务表通过 `company` 外键实现企业级数据隔离，在视图层过滤而非数据库层。
2. **无状态 JWT 认证**：PyJWT 手写 JWT（HS256，7 天有效期），不使用 DRF，函数视图 + `@csrf_exempt`。
3. **平台服务抽象**：`BaseDataPullService` 抽象基类 + `Ali1688DataPullService` 实现，可扩展接入更多平台。
4. **三端共用同一后端**：Web、Android、遗留脚本均通过 `/api/*` 接口访问 Django 后端。

---

## 3. 仓库目录结构

```
WeWin/
├── Server/                     # Django 后端（主后端服务）
│   ├── wewin/                  # Django 项目配置（settings/urls/wsgi）
│   ├── account/                # 用户、认证、页面配置
│   ├── company/                # 企业管理
│   ├── store/                  # 店铺、商品、订单、平台数据拉取
│   │   └── services/           # 平台数据拉取服务（base.py 基类，ali1688.py 实现）
│   ├── customer/               # 客户、客户商品、报价历史、可见性
│   ├── utils/                  # 共享装饰器（jwt_required / permission_required 等）
│   ├── manage.py
│   ├── requirements.txt
│   └── .env.example
├── Page/                       # Vue 3 前端
│   ├── src/
│   │   ├── api/                # 按模块拆分的 API 客户端
│   │   ├── views/              # 页面组件
│   │   ├── layout/             # 主布局（侧边栏 + 顶栏）
│   │   ├── router/             # 路由配置（含登录守卫）
│   │   ├── store/              # Pinia 状态（user）
│   │   └── components/         # 通用组件
│   ├── vite.config.js
│   ├── package.json
│   └── serve_spa.py            # 简易 SPA 静态服务器（生产部署用）
├── Android/                    # Android 原生应用（Kotlin + Jetpack Compose）
│   ├── app/
│   │   ├── src/main/java/com/wewin/app/
│   │   │   ├── data/           # 数据层（local/remote/dto）
│   │   │   ├── ui/             # UI 层（navigation/login/products/profile/theme）
│   │   │   ├── WeWinApp.kt
│   │   │   └── MainActivity.kt
│   │   ├── build.gradle.kts
│   │   └── proguard-rules.pro
│   └── settings.gradle.kts
├── AliData/                    # 独立的 1688 数据拉取脚本（遗留/参考实现）
│   ├── global_params.py        # 店铺凭证（硬编码，敏感）
│   ├── manager/                # OrderManager / ClothTradeManager
│   ├── utils/                  # 工具函数（ali_api/utils/cloth_worksheet）
│   ├── common/                 # settings / order_amount
│   └── hooks/                  # 企业微信通知等钩子
├── .trae/                      # Trae 规划文档与 specs
│   ├── documents/              # 分析与计划文档
│   └── specs/                  # 各模块 PRD
├── Makefile                    # 常用命令入口
├── DEPLOYMENT.md               # 部署说明
├── OPTIMIZATION.md             # 已完成优化与后续建议
├── AGENT.md                    # AI 代理导航指南
└── README.md                   # 项目运行说明
```

---

## 4. 技术栈与依赖

### 4.1 后端 Server（Django）

| 组件 | 版本 | 说明 |
|---|---|---|
| Django | 4.2.30 (LTS) | 主框架（注：`settings.py` 注释写 5.2.11，以 requirements.txt 为准）|
| PyJWT | 2.8.0 | 手写 JWT 认证 |
| requests | 2.32.4 | 调用 1688 OpenAPI |
| django-cors-headers | 4.3.1 | 跨域支持 |
| python-dotenv | 1.0.0 | 加载 `.env` 配置 |
| Pillow | 未声明（实际需要） | `ImageField` 依赖，**未列入 requirements.txt** |
| SQLite | 内置 | 默认数据库 |

依赖文件：[Server/requirements.txt](file:///d:/workplace_shop/WeWin/Server/requirements.txt)

### 4.2 前端 Page（Vue 3）

| 组件 | 版本 | 说明 |
|---|---|---|
| vue | ^3.5.25 | 核心框架 |
| vue-router | ^5.0.3 | 路由（history 模式）|
| pinia | ^3.0.4 | 状态管理 |
| element-plus | ^2.13.2 | UI 组件库 |
| @element-plus/icons-vue | ^2.3.2 | 图标 |
| axios | ^1.13.6 | HTTP 客户端 |
| echarts | ^6.0.0 | 图表 |
| xlsx | ^0.18.5 | Excel 导出 |
| file-saver | ^2.0.5 | 文件下载 |
| vite | ^4.5.3 | 构建工具 |

依赖文件：[Page/package.json](file:///d:/workplace_shop/WeWin/Page/package.json)

### 4.3 Android 原生应用

| 组件 | 版本 | 说明 |
|---|---|---|
| Kotlin | 1.9.22 | 编程语言 |
| Android Gradle Plugin | 8.2.2 | 构建插件 |
| Gradle | 8.5 | 构建工具 |
| compileSdk / targetSdk | 34 | SDK 版本 |
| minSdk | 24 | 最低支持版本 |
| Compose BOM | 2024.02.00 | Jetpack Compose |
| Retrofit | 2.9.0 | 网络请求 |
| OkHttp | 4.12.0 | HTTP 客户端 |
| kotlinx-serialization | 1.6.3 | JSON 序列化 |
| Coil | 2.5.0 | 图片加载 |
| DataStore Preferences | 1.0.0 | 持久化存储 |
| Navigation Compose | 2.7.7 | 导航 |

依赖文件：[Android/app/build.gradle.kts](file:///d:/workplace_shop/WeWin/Android/app/build.gradle.kts)

### 4.4 AliData 遗留模块

| 组件 | 说明 |
|---|---|
| requests | HTTP 请求 |
| hmac / hashlib | 1688 签名算法 |
| xlrd | 读取 price.xlsx |
| xlsxwriter | 生成备货单 Excel |
| schedule | 定时任务（每日 00:03 推送企业微信）|

---

## 5. 后端 Server（Django）

### 5.1 项目配置 wewin/

**[settings.py](file:///d:/workplace_shop/WeWin/Server/wewin/settings.py)**

- `BASE_DIR`：`Server/` 目录
- `load_dotenv(BASE_DIR / '.env')`：模块加载时自动读取 `.env`
- `SECRET_KEY`：从环境变量读取，有硬编码 fallback
- `DEBUG`：默认 True
- `INSTALLED_APPS`：admin / auth / contenttypes / sessions / messages / staticfiles / corsheaders / account / company / store / customer
- `AUTH_USER_MODEL = 'account.User'`（自定义用户模型）
- `MIDDLEWARE`：CORS 中间件置于首位
- `DATABASES`：硬编码 SQLite（`.env.example` 暴露 DB_* 变量但 settings.py 未消费）
- `TIME_ZONE = "Asia/Shanghai"`，`USE_TZ = True`
- `STATIC_ROOT = BASE_DIR / "staticfiles"`，`MEDIA_ROOT = BASE_DIR / "media"`
- `DATA_UPLOAD_MAX_MEMORY_SIZE = 100 MB`，`FILE_UPLOAD_MAX_MEMORY_SIZE = 100 MB`
- `CORS_ALLOW_ALL_ORIGINS = DEBUG`（开发环境放开所有来源）
- JWT 配置：无专门配置块，复用 Django `SECRET_KEY`，HS256，7 天有效期（硬编码于 `account/views.py`）

**[urls.py](file:///d:/workplace_shop/WeWin/Server/wewin/urls.py)**

```
admin/                  -> admin.site.urls
api/account/            -> account.urls
api/company/            -> company.urls
api/store/              -> store.urls
api/customer/           -> customer.urls
```

DEBUG 模式下额外提供 `media/` 静态服务。

### 5.2 account 应用（用户与认证）

**[models.py](file:///d:/workplace_shop/WeWin/Server/account/models.py)**

#### `UserType` 枚举（TextChoices）

| 常量 | 值 | 中文显示 |
|---|---|---|
| `SUPER_ADMIN` | `super_admin` | 网站超级管理员 |
| `SITE_ADMIN` | `site_admin` | 网站管理员 |
| `ENTERPRISE_LEADER` | `enterprise_leader` | 企业负责人 |
| `ENTERPRISE_ADMIN` | `enterprise_admin` | 企业用户管理员 |
| `ENTERPRISE_USER` | `enterprise_user` | 企业用户普通账户 |
| `TEMPORARY` | `temporary` | 临时账户 |

#### `User` 模型（继承 `AbstractUser`，表名 `user`）

| 字段 | 类型 | 说明 |
|---|---|---|
| `uid` | UUIDField | 自动生成，唯一 |
| `user_type` | CharField(20) | UserType 枚举，默认 TEMPORARY |
| `company` | FK → Company | CASCADE，related_name=`users` |
| `created_by` | FK → self | SET_NULL，记录创建人 |
| `phone` | CharField(50) | 手机号 |
| `real_name` | CharField(100) | 真实姓名 |

`save()` 重写自动填充 `uid`。

#### `PageConfig` 模型（表名 `page_config`）

按用户类型配置页面可见性。字段：`user_type` / `page_name` / `page_route` / `is_visible` / `order`。`unique_together = ('user_type', 'page_route')`。

**[views.py](file:///d:/workplace_shop/WeWin/Server/account/views.py)** 关键函数：

| 函数 | HTTP | 路径 | 用途 |
|---|---|---|---|
| `login_view` | POST | `/api/account/login/` | 用户名密码登录，返回 JWT |
| `logout_view` | POST | `/api/account/logout/` | 登出（无状态，token 仍有效）|
| `simple_register` | POST | `/api/account/register/` | 公开注册（创建 TEMPORARY 用户）|
| `get_current_user` | GET | `/api/account/current-user/` | 获取当前用户信息 |
| `update_profile` | PUT | `/api/account/profile/update/` | 更新个人资料 |
| `change_password` | POST | `/api/account/password/change/` | 修改密码 |
| `create_enterprise_admin` | POST | `/api/account/create-enterprise-admin/` | 创建企业 + 企业负责人（事务）|
| `create_enterprise_user` | POST | `/api/account/create-enterprise-user/` | 创建企业用户 |
| `create_and_bind_company` | POST | `/api/account/create-and-bind-company/` | 已登录用户创建并绑定企业 |
| `bind_existing_company` | POST | `/api/account/bind-existing-company/` | 通过企业码加入已有企业 |
| `get_users` | GET | `/api/account/users/` | 按角色范围列出用户 |
| `create_user` | POST | `/api/account/users/create/` | 创建用户（权限校验）|
| `update_user_status` | PUT | `/api/account/users/<id>/status/` | 启用/禁用用户 |
| `delete_user` | DELETE | `/api/account/users/<id>/delete/` | 删除用户 |
| `update_user_type` | PUT | `/api/account/users/<id>/update-type/` | 修改用户类型（基于 `USER_TYPE_RANK` 规则）|
| `get_page_config` | GET | `/api/account/page-config/` | 获取当前用户类型可见页面 |

辅助函数：
- `generate_token(user)`：构造 `{user_id, username, user_type, exp=now+7d}`，HS256 编码
- `generate_company_code()`：生成 8 位顺序企业码（从 10000001 递增）
- `USER_TYPE_RANK`：权限层级（0=最强，5=最弱）

**管理命令**：
- `python manage.py create_superadmin` — 创建默认超管（`superadmin / superadmin123`）
- `python manage.py init_page_config` — 初始化各用户类型的页面可见性配置
- `python manage.py update_enterprise_admin_to_leader` — 迁移企业管理员角色

### 5.3 company 应用（企业管理）

**[models.py](file:///d:/workplace_shop/WeWin/Server/company/models.py)**

#### `Company` 模型（表名 `company`）

| 字段 | 类型 | 说明 |
|---|---|---|
| `name` | CharField(200) | 企业名称，唯一 |
| `code` | CharField(50) | 企业码，唯一 |
| `address` | CharField(500) | 地址 |
| `contact_name` | CharField(100) | 联系人 |
| `contact_phone` | CharField(50) | 联系电话 |
| `is_active` | BooleanField | 是否启用 |

反向关系：`users`、`stores`、`products`、`customers`。

**[views.py](file:///d:/workplace_shop/WeWin/Server/company/views.py)**

| 函数 | HTTP | 路径 | 用途 |
|---|---|---|---|
| `get_companies` | GET | `/api/company/` | 列出企业（仅超管/站点管理员）|
| `create_company` | POST | `/api/company/create/` | 创建企业（自动生成 8 位码）|
| `update_company` | PUT | `/api/company/<id>/update/` | 更新企业（禁用时连带禁用企业用户）|
| `delete_company` | DELETE | `/api/company/<id>/delete/` | 删除企业（有用户时拒绝）|
| `get_company_users` | GET | `/api/company/<id>/users/` | 列出企业用户 |
| `batch_update_company_status` | POST | `/api/company/batch-status/` | 批量启用/禁用 |

### 5.4 store 应用（店铺/商品/订单）

**[models.py](file:///d:/workplace_shop/WeWin/Server/store/models.py)**

#### 枚举

- **`ProductType`**：`bead`（串珠）/ `accessory`（配件）/ `finished`（成品）
- **`Platform`**：10 个平台（`1688` 已实现，其余预留）
- **`Category`**：14 个商品分类
- **`OrderStatus`**：20 种订单状态
- **`RefundStatus`**：`no_refund` / `wait_seller_agree` / `refund_success`
- **`DataPullStatus`**：`pending` / `pulling` / `success` / `failed`

#### 商品体系模型

| 模型 | 表名 | 关系 | 说明 |
|---|---|---|---|
| `Product` | `product` | FK→Company | 商品主表（code/name/type/prices/image）|
| `ProductSku` | `product_sku` | FK→Product | SKU（material/size/color/weight/quality/prices）|
| `Bead` | `bead` | OneToOne→Product | 串珠详情 |
| `Accessory` | `accessory` | OneToOne→Product | 配件详情 |
| `FinishedProduct` | `finished_product` | OneToOne→Product | 成品详情（labor_cost/elastic_cost）|
| `FinishedProductBead` | `finished_product_bead` | M2M 中间表 | 成品-串珠组成（含 sku/quantity）|
| `FinishedProductAccessory` | `finished_product_accessory` | M2M 中间表 | 成品-配件组成（含 sku/quantity）|

**关键成本计算**（[views.py](file:///d:/workplace_shop/WeWin/Server/store/views.py) 中的 `calculate_finished_product_cost`）：
```
成品总成本 = Σ(串珠 cost_price × quantity) + Σ(配件 cost_price × quantity) + labor_cost + elastic_cost
```
对于串珠类型，若无显式 `cost_price`，则 `cost_price = purchase_cost × weight`。

#### 店铺与订单体系模型

| 模型 | 表名 | 说明 |
|---|---|---|
| `Store` | `store` | 店铺（name/platform/category/managers M2M）|
| `PlatformApiConfig` | `platform_api_config` | 平台 API 凭证（OneToOne→Store）|
| `StoreDataConfig` | `store_data_config` | 自动拉取配置（OneToOne→Store）|
| `DataPullTask` | `data_pull_task` | 拉取任务记录 |
| `StoreData` | `store_data` | 按日聚合数据 |
| `Order` | `order` | 订单主表（镜像 1688 交易 schema，含 `platform_raw_data` JSON）|
| `OrderItem` | `order_item` | 订单商品项 |
| `OrderReceiver` | `order_receiver` | 收货人信息（OneToOne→Order）|
| `OrderContact` | `order_contact` | 联系人（买家/卖家）|
| `OrderStep` | `order_step` | 交易步骤 |
| `OrderTradeTerm` | `order_trade_term` | 分期付款 |
| `OrderRateInfo` | `order_rate_info` | 评价信息 |
| `OrderBizInfo` | `order_biz_info` | 业务信息 |
| `OrderLogistics` | `order_logistics` | 卖家发货地址 |
| `OrderLogisticsItem` | `order_logistics_item` | 物流明细 |

#### URL 路由（`/api/store/` 前缀）

完整路由见 [store/urls.py](file:///d:/workplace_shop/WeWin/Server/store/urls.py)，主要分组：

**店铺管理**：
| 路径 | 函数 | HTTP |
|---|---|---|
| `` | `get_stores` | GET |
| `create/` | `create_store` | POST |
| `<id>/update/` | `update_store` | PUT |
| `<id>/delete/` | `delete_store` | DELETE |
| `<id>/api-config/` | `get_store_api_config` | GET |
| `<id>/api-config/create-or-update/` | `create_or_update_api_config` | POST |
| `<id>/trigger-pull/` | `trigger_data_pull` | POST |
| `<id>/orders/` | `get_orders` | GET |
| `<id>/orders/<platform_order_id>/detail/` | `get_order_detail` | GET |
| `<id>/pull-tasks/` | `get_pull_tasks` | GET |

**商品管理**：
| 路径 | 函数 | HTTP |
|---|---|---|
| `products/types/` | `get_product_types` | GET |
| `products/stats/` | `get_product_stats` | GET |
| `products/` | `get_products` | GET |
| `products/create/` | `create_product` | POST |
| `products/<id>/update/` | `update_product` | PUT, POST |
| `products/<id>/delete/` | `delete_product` | DELETE |
| `products/<id>/detail/` | `get_product_detail` | GET |
| `products/accessories/` | `get_accessories` | GET |
| `products/beads/` | `get_beads` | GET |
| `products/<id>/skus/` | `get_product_skus` | GET |

**关键视图函数说明**：
- `update_product`：**PUT 请求手动解析 multipart/form-data**（使用 `MultiPartParser`），因为 Django 默认只自动解析 POST 的 multipart
- `trigger_data_pull`：通过 `BaseDataPullService.get_service_class(platform)` 解析服务类，创建 `DataPullTask`，执行 `pull_orders`
- `get_products`：分页（50/页），支持 `product_type` / `is_active` / `ordering` 过滤，内嵌类型特定数据，成品计算总成本
- `get_orders`：分页（50/页），支持 `status` / `start_date` / `end_date` 过滤

**辅助函数**：
- `calculate_finished_product_cost(finished)`：计算成品总成本
- `sync_skus(product, sku_items, ...)`：SKU 全量同步（删除缺失/更新已有/确保唯一默认）
- `sku_schema_ready()`：内省数据库 schema，向后兼容 pre-SKU 表结构
- `product_skus_payload(product)`：返回 SKU 列表

### 5.5 customer 应用（客户管理）

**[models.py](file:///d:/workplace_shop/WeWin/Server/customer/models.py)**

| 模型 | 表名 | 说明 |
|---|---|---|
| `Customer` | `customer` | 客户主表（name/phone/email/company FK）|
| `CustomerVisibility` | `customer_visibility` | 客户可见用户配置（customer + visible_user + configured_by）|
| `CustomerProduct` | `customer_product` | 客户专属商品（customer + product + price，`unique_together`）|
| `CustomerPriceHistory` | `customer_price_history` | 报价历史（customer + product + price）|

**URL 路由（`/api/customer/` 前缀）**：

| 函数 | HTTP | 路径 | 用途 |
|---|---|---|---|
| `get_customers` | GET | `/` | 分页客户列表（search/is_active 过滤）|
| `create_customer` | POST | `/create/` | 创建客户（支持 `visible_user_ids`）|
| `update_customer` | PUT | `/<id>/update/` | 更新客户 |
| `delete_customer` | DELETE | `/<id>/delete/` | 删除客户 |
| `get_customer_detail` | GET | `/<id>/detail/` | 客户详情（含 visible_users）|
| `get_customer_products` | GET | `/<id>/products/` | 客户商品列表 |
| `create_or_update_customer_product` | POST | `/<id>/products/create-or-update/` | 上架/更新客户商品（价格变动写历史）|
| `get_customer_price_history` | GET | `/<id>/products/<product_id>/price-history/` | 报价历史 |
| `get_customer_visibility` | GET | `/<id>/visibility/` | 可见性配置 |
| `set_customer_visibility` | POST | `/<id>/visibility/set/` | 替换可见性配置 |
| `remove_customer_visibility` | DELETE | `/<id>/visibility/<vid>/delete/` | 删除单条可见性 |

**可见性规则**（`get_visible_customers`）：
- `SUPER_ADMIN` / `SITE_ADMIN`：全部客户
- `ENTERPRISE_LEADER`：本企业全部客户
- `ENTERPRISE_ADMIN`：自己创建的 + 对自己可见的（本企业内）
- `ENTERPRISE_USER`：仅对自己可见的（本企业内）

### 5.6 utils 模块（装饰器）

**[utils/decorators.py](file:///d:/workplace_shop/WeWin/Server/utils/decorators.py)**

| 装饰器 | 行为 |
|---|---|
| `jwt_required(view_func)` | 校验 `Authorization: Bearer <token>`，解码 JWT，加载 User 到 `request.user` |
| `permission_required(allowed_user_types)` | 工厂函数，校验 `request.user.user_type` 是否在允许列表 |
| `admin_required(view_func)` | `permission_required([SUPER_ADMIN, SITE_ADMIN])` |
| `enterprise_leader_required(view_func)` | `permission_required([SUPER_ADMIN, SITE_ADMIN, ENTERPRISE_LEADER])` |

> **注意**：这些装饰器已定义但**实际未被任何视图使用**。各视图模块（account/company/store/customer 的 `views.py`）内联了自己的 JWT 解码与权限校验逻辑，存在代码重复。`customer/views.py` 使用本地 `authenticate_jwt(request)` 辅助函数。

### 5.7 平台数据拉取服务

**架构**：抽象基类 + 实现类，通过工厂方法注册。

```
BaseDataPullService (ABC)                  [store/services/base.py]
    └── Ali1688DataPullService             [store/services/ali1688.py]
```

#### `BaseDataPullService`（[base.py](file:///d:/workplace_shop/WeWin/Server/store/services/base.py)）

构造函数：接收 `Store`，初始化 `self.api_config`。

**抽象方法**（子类必须实现）：
1. `pull_orders(start_time, end_time, task=None) -> Dict` — 按时间窗口拉取订单
2. `pull_order_detail(platform_order_id) -> Optional[Dict]` — 拉取单个订单详情
3. `save_order(order_data) -> bool` — 持久化订单，返回是否新建

**具体方法**：
- `create_pull_task(task_type, start_time, end_time, params)` — 创建 `DataPullTask`
- `update_task_status(task, status, ...)` — 更新任务状态
- `get_service_class(platform)` — 工厂方法，返回平台对应服务类（目前仅 `'1688' -> Ali1688DataPullService`）

#### `Ali1688DataPullService`（[ali1688.py](file:///d:/workplace_shop/WeWin/Server/store/services/ali1688.py)）

**常量**：
- `BASE_URL = "https://gw.open.1688.com/openapi/"`
- `REQUEST_TYPE_TRADE = "param2/1/com.alibaba.trade/"`

**1688 签名算法**（`_calculate_signature`）：

1. 对 `data` 中每个 key，构造字符串 `key + str(value)`
2. 对字符串列表**字典序排序**
3. 拼接为 `assembled_params`
4. 前置 URL 路径：`merged_params = url_path + assembled_params`（UTF-8 编码）
5. `hmac.new(app_secret, merged_params, digestmod="sha1").hexdigest()`
6. 转大写返回，作为 `_aop_signature`

**关键方法**：
- `_get_trade_data(data)`：调用 `alibaba.trade.getSellerOrderList/{app_key}`，分页拉取（pageSize=20）
- `_get_single_trade_detail(order_id)`：调用 `alibaba.trade.get.sellerView/{app_key}`
- `_format_date(dt)`：`strftime("%Y%m%d") + "000000000+0800"`
- `_de_format_time(date_str)`：解析 `%Y%m%d%H%M%S%f`（去除 `+0800` 后缀）
- `pull_orders`：分页拉取，调用 `save_order` 保存，返回 `{stats, request_logs}`
- `save_order`（`@transaction.atomic`）：`get_or_create` 订单，更新字段，调用 `_save_order_items` / `_save_order_receiver`
- `_save_order_items`：同步订单商品项，删除上游已消失的项
- `_save_order_receiver`：保存收货人信息

---

## 6. 前端 Page（Vue 3）

### 6.1 项目配置

**[package.json](file:///d:/workplace_shop/WeWin/Page/package.json)**：Vue 3.5 + Vite 4 + Element Plus 2.13 + Pinia 3 + axios + echarts + xlsx + file-saver。

**[vite.config.js](file:///d:/workplace_shop/WeWin/Page/vite.config.js)**：
- 插件：`@vitejs/plugin-vue`
- 别名：`@` → `src`
- 未配置 server 端口/代理（开发端口默认 5173）

**[serve_spa.py](file:///d:/workplace_shop/WeWin/Page/serve_spa.py)**：基于 Python stdlib 的生产 SPA 服务器，端口 8080，支持 history 模式路由重写（未匹配文件路径回退到 `index.html`）。

**环境变量**：仅 `VITE_API_BASE_URL`，默认 `http://127.0.0.1:8003`（在 [src/api/config.js](file:///d:/workplace_shop/WeWin/Page/src/api/config.js) 读取）。**注意：`Page/` 目录无 `.env.example` 文件**。

### 6.2 入口与路由

**[main.js](file:///d:/workplace_shop/WeWin/Page/src/main.js)**：
1. `createApp(App)`
2. 注册 Pinia、Element Plus（含全部图标全局注册）、Router
3. `mount('#app')`

**[router/index.js](file:///d:/workplace_shop/WeWin/Page/src/router/index.js)**：`createWebHistory` 模式，含登录守卫。

| 路径 | 名称 | 组件 | meta |
|---|---|---|---|
| `/login` | Login | Login.vue | 公开 |
| `/register` | Register | Register.vue | 公开 |
| `/bind-company` | BindCompany | BindCompany.vue | 公开 |
| `/` | Layout | layout/index.vue | redirect → /dashboard |
| └ `dashboard` | Dashboard | Dashboard.vue | 数据概览 |
| └ `customers` | Customers | — | 客户管理（父）|
| └─ `list` | CustomerList | Customers.vue | 客户列表 |
| └─ `:id/products` | CustomerProducts | CustomerProducts.vue | 客户商品（hidden）|
| └ `stores` | Stores | — | 店铺管理（父）|
| └─ `list` | StoreList | Stores.vue | 店铺列表 |
| └─ `test` | StoreTest | StoreTest.vue | 订单总览 |
| └ `products` | Products | Products.vue | 商品管理 |
| └ `inventory` | Inventory | Inventory.vue | 库存管理（占位）|
| └ `sales` | Sales | Sales.vue | 销售数据（占位）|
| └ `users` | Users | Users.vue | 用户管理 |
| └ `profile` | Profile | Profile.vue | 个人信息 |
| └ `companies` | Companies | Companies.vue | 企业管理（requiresAdmin）|

**登录守卫**：未登录访问受保护页面跳 `/login`；已登录访问登录页跳 `/`。`requiresAdmin` **仅在菜单生成时校验，路由本身未守卫**。

### 6.3 API 层

**工厂模式**：[src/api/client.js](file:///d:/workplace_shop/WeWin/Page/src/api/client.js) 的 `createApiClient(basePath)`：
- `axios.create({ baseURL: API_BASE_URL + basePath, timeout: 10000 })`
- 请求拦截器：注入 `Authorization: Bearer <token>`
- 响应拦截器：401 时清空 localStorage 并硬跳转 `/login`

**模块化客户端**（统一通过 `src/api/` 调用，不直接用 axios）：

| 文件 | basePath | 主要导出 |
|---|---|---|
| [account.js](file:///d:/workplace_shop/WeWin/Page/src/api/account.js) | `/api/account` | `login`, `logout`, `getUsers`, `createUser`, `updateUserStatus`, `updateUserType`, `getPageConfig`, `getCurrentUser`, `updateProfile`, `changePassword`, `simpleRegister`, `createEnterpriseAdmin`, `createEnterpriseUser`, `createAndBindCompany`, `bindExistingCompany`, `deleteUser` |
| [company.js](file:///d:/workplace_shop/WeWin/Page/src/api/company.js) | `/api/company` | `getCompanies`, `createCompany`, `updateCompany`, `deleteCompany`, `getCompanyUsers`, `batchUpdateCompanyStatus` |
| [customer.js](file:///d:/workplace_shop/WeWin/Page/src/api/customer.js) | `/api/customer` | `getCustomers`, `createCustomer`, `updateCustomer`, `deleteCustomer`, `getCustomerDetail`, `getCustomerProducts`, `createOrUpdateCustomerProduct`, `getCustomerPriceHistory`, `getCustomerVisibility`, `setCustomerVisibility`, `removeCustomerVisibility` |
| [store.js](file:///d:/workplace_shop/WeWin/Page/src/api/store.js) | `/api/store` | `getPlatforms`, `getCategories`, `getStores`, `createStore`, `updateStore`, `deleteStore`, `getStoreApiConfig`, `createOrUpdateStoreApiConfig`, `triggerDataPull`（10 分钟超时）, `getPullTasks`, `getStoreOrders`, `getOrderDetail`, `getProductTypes`, `getProducts`, `getProductStats`, `createProduct`（FormData）, `updateProduct`, `deleteProduct`, `getProductDetail`, `getAccessories`, `getBeads`, `getProductSkus` |

**[index.js](file:///d:/workplace_shop/WeWin/Page/src/api/index.js)**：barrel 导出，同时支持命名导出与默认导出（向后兼容）。

### 6.4 状态管理 Pinia

**[store/user.js](file:///d:/workplace_shop/WeWin/Page/src/store/user.js)**（Composition API 风格）：

| State | 来源 |
|---|---|
| `token` | `localStorage.getItem('token')` |
| `userInfo` | `JSON.parse(localStorage.getItem('userInfo') \|\| '{}')` |
| `currentStore` | `JSON.parse(localStorage.getItem('currentStore') \|\| '{}')` |

| Action | 行为 |
|---|---|
| `setToken(newToken)` | 设 ref + localStorage |
| `setUserInfo(info)` | 设 ref + localStorage |
| `setCurrentStore(store)` | 设 ref + localStorage |
| `logout()` | 清空三个 ref + 移除 localStorage |

### 6.5 页面视图

| 视图 | 路由 | 主要功能 |
|---|---|---|
| [Dashboard.vue](file:///d:/workplace_shop/WeWin/Page/src/views/Dashboard.vue) | /dashboard | 4 统计卡片 + ECharts 销售趋势线柱图 + 分类饼图（部分数据硬编码）|
| [Login.vue](file:///d:/workplace_shop/WeWin/Page/src/views/Login.vue) | /login | 登录表单，用户名记忆（localStorage loginHistory）|
| [Register.vue](file:///d:/workplace_shop/WeWin/Page/src/views/Register.vue) | /register | 注册表单（使用原生 fetch）|
| [Customers.vue](file:///d:/workplace_shop/WeWin/Page/src/views/Customers.vue) | /customers/list | 客户 CRUD + 统计卡片 + 搜索 + 分页 |
| [CustomerProducts.vue](file:///d:/workplace_shop/WeWin/Page/src/views/CustomerProducts.vue) | /customers/:id/products | 客户商品关联管理 + 报价历史时间线 + 价格趋势图 |
| [Stores.vue](file:///d:/workplace_shop/WeWin/Page/src/views/Stores.vue) | /stores/list | 店铺 CRUD + API 配置弹窗 + 管理员多选 |
| [Products.vue](file:///d:/workplace_shop/WeWin/Page/src/views/Products.vue) | /products | 商品管理（按类型分页）+ 图片上传 + SKU 管理 + 成品组成 + Excel 导出 |
| [components/ProductTable.vue](file:///d:/workplace_shop/WeWin/Page/src/views/components/ProductTable.vue) | — | 商品表格（桌面/移动双布局）+ 图片预览 + 克价模拟弹窗 |
| [Inventory.vue](file:///d:/workplace_shop/WeWin/Page/src/views/Inventory.vue) | /inventory | 占位页面 |
| [Sales.vue](file:///d:/workplace_shop/WeWin/Page/src/views/Sales.vue) | /sales | 占位页面 |
| [Users.vue](file:///d:/workplace_shop/WeWin/Page/src/views/Users.vue) | /users | 用户管理 + 内联角色修改 + 批量启停（使用原生 fetch）|
| [Companies.vue](file:///d:/workplace_shop/WeWin/Page/src/views/Companies.vue) | /companies | 企业 CRUD + 批量启停 + 内联启停开关 |
| [BindCompany.vue](file:///d:/workplace_shop/WeWin/Page/src/views/BindCompany.vue) | /bind-company | 创建/加入企业（双 Tab）|
| [Profile.vue](file:///d:/workplace_shop/WeWin/Page/src/views/Profile.vue) | /profile | 个人资料编辑 + 修改密码 |
| [StoreTest.vue](file:///d:/workplace_shop/WeWin/Page/src/views/StoreTest.vue) | /stores/test | 订单拉取测试控制台 + 请求日志展示 + 订单详情弹窗 |

**[utils/exportProducts.js](file:///d:/workplace_shop/WeWin/Page/src/utils/exportProducts.js)**：`exportFinishedProducts(products)` 导出成品明细 Excel（成品行 + 串珠/配件组成行）。

**[layout/index.vue](file:///d:/workplace_shop/WeWin/Page/src/layout/index.vue)**：可折叠侧边栏（200px/64px）+ 顶栏用户下拉 + 移动端响应式。

---

## 7. Android 原生应用

### 7.1 项目配置

**[build.gradle.kts](file:///d:/workplace_shop/WeWin/Android/app/build.gradle.kts)**：

| 配置项 | 值 |
|---|---|
| applicationId | `com.wewin.app` |
| compileSdk / targetSdk | 34 |
| minSdk | 24 |
| versionCode / versionName | 1 / "1.0" |
| Java / JVM target | 17 |
| Compose | 启用（kotlinCompilerExtensionVersion = "1.5.8"）|
| BuildConfig | `API_BASE_URL` 从 `local.properties` 读取，默认 `http://10.0.2.2:8003` |

**[AndroidManifest.xml](file:///d:/workplace_shop/WeWin/Android/app/src/main/AndroidManifest.xml)**：
- 权限：仅 `INTERNET`
- Application：`WeWinApp`，`networkSecurityConfig` 引用 `@xml/network_security_config`
- 单 Activity：`MainActivity`（启动入口）

**[network_security_config.xml](file:///d:/workplace_shop/WeWin/Android/app/src/main/res/xml/network_security_config.xml)**：允许明文 HTTP 的域名：`10.0.2.2`、`192.168.1.6`、`localhost`、`127.0.0.1`、`www.wanying.asia`。

### 7.2 架构模式

**MVVM + 单向数据流 + Jetpack Compose**：

- **View 层**：`@Composable` 屏幕组件，通过 `collectAsState()` 观察 `StateFlow<UiState>`
- **ViewModel 层**：每个屏幕一个 ViewModel，`MutableStateFlow` 持有状态，`asStateFlow()` 暴露
- **Model 层**：`data/local`（DataStore 持久化）+ `data/remote`（Retrofit + DTO），无 Repository 抽象（ViewModel 直接调 `RetrofitClient.apiService`）
- **导航**：Jetpack Navigation Compose，两层 NavHost（顶层 AppNavGraph + 内嵌 MainScaffold 的底部 Tab）
- **依赖注入**：手动（无 Hilt/Dagger），`RetrofitClient` 单例在 `WeWinApp.onCreate()` 初始化

### 7.3 数据层

#### 本地存储

**[TokenStore.kt](file:///d:/workplace_shop/WeWin/Android/app/src/main/java/com/wewin/app/data/local/TokenStore.kt)**：
- 基于 Jetpack DataStore Preferences
- `tokenFlow: Flow<String?>` + `userFlow: Flow<UserInfo?>`
- `saveAuth(token, user)` / `clear()`

**[AuthEventBus.kt](file:///d:/workplace_shop/WeWin/Android/app/src/main/java/com/wewin/app/data/local/AuthEventBus.kt)**：
- `object` 单例，`SharedFlow<Unit>` 事件总线
- `emitLogout()`：401 时触发，`AppNavGraph` 收到后跳转登录

#### 网络层

**[RetrofitClient.kt](file:///d:/workplace_shop/WeWin/Android/app/src/main/java/com/wewin/app/data/remote/RetrofitClient.kt)**：
- 单例 `object`，双重检查锁初始化
- `init(context)`：构建 TokenStore + OkHttp（拦截器链：AuthInterceptor → Global401Interceptor → HttpLoggingInterceptor）+ Retrofit（kotlinx-serialization 转换器）
- Base URL：`BuildConfig.API_BASE_URL`（强制尾斜杠）
- 超时：30s

**[AuthInterceptor.kt](file:///d:/workplace_shop/WeWin/Android/app/src/main/java/com/wewin/app/data/remote/AuthInterceptor.kt)**：
- 每个请求注入 `Authorization: Bearer <token>`（通过 `runBlocking` 读取 TokenStore）

**[Global401Interceptor.kt](file:///d:/workplace_shop/WeWin/Android/app/src/main/java/com/wewin/app/data/remote/Global401Interceptor.kt)**：
- 响应 401 时清空凭证 + `AuthEventBus.emitLogout()`

**[ApiService.kt](file:///d:/workplace_shop/WeWin/Android/app/src/main/java/com/wewin/app/data/remote/ApiService.kt)**（Retrofit 接口）：

| 函数 | HTTP | 路径 |
|---|---|---|
| `login` | POST | `api/account/login/` |
| `getProductTypes` | GET | `api/store/products/types/` |
| `getProductStats` | GET | `api/store/products/stats/` |
| `getProducts` | GET | `api/store/products/` |
| `getProductDetail` | GET | `api/store/products/{id}/detail/` |
| `getBeads` | GET | `api/store/products/beads/` |
| `getAccessories` | GET | `api/store/products/accessories/` |
| `getProductSkus` | GET | `api/store/products/{id}/skus/` |
| `createProductMultipart` | POST (multipart) | `api/store/products/create/` |
| `updateProductMultipart` | PUT (multipart) | `api/store/products/{id}/update/` |
| `deleteProduct` | DELETE | `api/store/products/{id}/delete/` |

#### DTO（18 个 `@Serializable data class`）

位于 [data/remote/dto/](file:///d:/workplace_shop/WeWin/Android/app/src/main/java/com/wewin/app/data/remote/dto/)，主要：
- `LoginRequest` / `LoginResponse` / `UserInfo`
- `ProductDto`（含 `BeadDto` / `AccessoryDto` / `FinishedDto` / `SkuDto`）
- `ProductListResponse` / `ProductStatsDto` / `ProductTypesDto`
- `BeadListDto` / `AccessoryListDto` / `SkuListResponse`
- `FinishedBeadItemDto` / `FinishedAccessoryItemDto` / `FinishedComponentRequest`
- `ErrorResponse` / `MessageResponse`

### 7.4 UI 层

#### 导航

**[Screen.kt](file:///d:/workplace_shop/WeWin/Android/app/src/main/java/com/wewin/app/ui/navigation/Screen.kt)**：`sealed class Screen`，定义路由：`Login` / `Main` / `ProductList` / `ProductDetail/{productId}` / `ProductEdit?productId={productId}` / `Profile`。

**[AppNavGraph.kt](file:///d:/workplace_shop/WeWin/Android/app/src/main/java/com/wewin/app/ui/navigation/AppNavGraph.kt)**：顶层 NavHost，根据 token 存在与否决定起始目的地（Main 或 Login），订阅 `AuthEventBus` 强制登出。

**[MainScaffold.kt](file:///d:/workplace_shop/WeWin/Android/app/src/main/java/com/wewin/app/ui/navigation/MainScaffold.kt)**：底部双 Tab（商品 / 我的）。

#### 屏幕

| 屏幕 | 文件 | ViewModel | 主要功能 |
|---|---|---|---|
| 登录 | [LoginScreen.kt](file:///d:/workplace_shop/WeWin/Android/app/src/main/java/com/wewin/app/ui/login/LoginScreen.kt) | `LoginViewModel` | 用户名/密码登录，错误信息中文化 |
| 商品列表 | [ProductListScreen.kt](file:///d:/workplace_shop/WeWin/Android/app/src/main/java/com/wewin/app/ui/products/ProductListScreen.kt) | `ProductListViewModel` | 统计卡片 + 类型过滤 + 搜索 + 无限滚动 + SKU 懒加载 |
| 商品详情 | [ProductDetailScreen.kt](file:///d:/workplace_shop/WeWin/Android/app/src/main/java/com/wewin/app/ui/products/ProductDetailScreen.kt) | `ProductDetailViewModel` | 详情展示 + **ON_RESUME 自动刷新** + 克价模拟弹窗（成本/利润/利润率实时计算）|
| 商品编辑 | [ProductEditScreen.kt](file:///d:/workplace_shop/WeWin/Android/app/src/main/java/com/wewin/app/ui/products/ProductEditScreen.kt) | `ProductEditViewModel` | 图片选择 + 表单 + multipart 提交 |
| 个人中心 | [ProfileScreen.kt](file:///d:/workplace_shop/WeWin/Android/app/src/main/java/com/wewin/app/ui/profile/ProfileScreen.kt) | — | 用户信息展示 + 退出登录 |

**关键 ViewModel**：
- `ProductListViewModel`：`loadInitial()` 并行加载商品+统计；`loadMore()` 分页；`loadSkusIfNeeded()` 懒加载 SKU
- `ProductDetailViewModel`：`loadDetail()` 加载详情
- `ProductEditViewModel`（继承 `AndroidViewModel`）：`submit()` 构建 multipart 提交；`loadFinishedOptions()` 并行加载串珠/配件选项

---

## 8. AliData 遗留模块

**位置**：[AliData/](file:///d:/workplace_shop/WeWin/AliData)  
**性质**：独立 Python 脚本，非 Django 部分，用于参考与离线数据拉取。

### 8.1 模块结构

| 路径 | 说明 |
|---|---|
| [global_params.py](file:///d:/workplace_shop/WeWin/AliData/global_params.py) | 7 个店铺的 AppKey/AppSecret/AccessToken（**硬编码，敏感**），全局配置 |
| [main.py](file:///d:/workplace_shop/WeWin/AliData/main.py) | 空文件 |
| [api.py](file:///d:/workplace_shop/WeWin/AliData/api.py) | 空文件（实际 API 在 utils/ali_api.py）|
| [every_counting.py](file:///d:/workplace_shop/WeWin/AliData/every_counting.py) | 手动销售汇算入口脚本 |
| [tmp.py](file:///d:/workplace_shop/WeWin/AliData/tmp.py) | 遗留备货单生成（mixin 风格，未启用）|
| [tmp2.py](file:///d:/workplace_shop/WeWin/AliData/tmp2.py) | 遗留备货单 Excel 生成（mixin 风格，未启用）|
| [manager/OrderManager.py](file:///d:/workplace_shop/WeWin/AliData/manager/OrderManager.py) | 旧版订单管理（含死代码）|
| [manager/cloth_trade_manager.py](file:///d:/workplace_shop/WeWin/AliData/manager/cloth_trade_manager.py) | **活跃的销售汇算引擎** |
| [utils/ali_api.py](file:///d:/workplace_shop/WeWin/AliData/utils/ali_api.py) | 1688 API 调用 + 签名算法 |
| [utils/utils.py](file:///d:/workplace_shop/WeWin/AliData/utils/utils.py) | 通用工具（分页/尺寸格式化）|
| [utils/cloth_worksheet.py](file:///d:/workplace_shop/WeWin/AliData/utils/cloth_worksheet.py) | price.xlsx 价格查询 |
| [common/settings.py](file:///d:/workplace_shop/WeWin/AliData/common/settings.py) | Settings 类（含 3 天回溯）|
| [common/order_amount.py](file:///d:/workplace_shop/WeWin/AliData/common/order_amount.py) | OrderAmount 累加器 DTO |
| [hooks/wxwork.py](file:///d:/workplace_shop/WeWin/AliData/hooks/wxwork.py) | 企业微信定时通知 |

### 8.2 ClothTradeManager 核心逻辑

**[manager/cloth_trade_manager.py](file:///d:/workplace_shop/WeWin/AliData/manager/cloth_trade_manager.py)**：

- `set_params(start_time, end_time, shop_names, order_status, filter_tags, ...)`：配置参数
- `get_all_origin_order_list()`：拉取所有订单，**过滤刷单**（`sellerRemarkIcon` 为 2/3 即蓝/绿标签的分到 `shuadan_orders`）
- `get_sales_amount()`：拉取 + 按店铺聚合销售金额
- `get_single_order_amount(order)`：按订单状态分发计算
  - **支付时间门控**：`payTime` 必须在 `[order_start_time, end_time)` 区间
  - `success`：直接取 baseInfo 金额
  - `cancel`：跳过 `alipayTradeId == "UNCREATED"`（未支付主动取消）或有 `closeReason`（被动取消未支付）
  - `waitsellersend` / `waitbuyerreceive`：若 `refundStatus == "waitselleragree"`，累加退款中商品 itemAmount
- `get_refund_amount_info_by_product_items(product_items)`：区分正常/退款金额

### 8.3 1688 签名算法

**[utils/ali_api.py::CalculateSignature](file:///d:/workplace_shop/WeWin/AliData/utils/ali_api.py)**：

1. 对 `data` 每个 key 构造 `key + str(value)`
2. 字典序排序
3. 拼接为 `assembedParams`
4. `mergedParams = urlPath + assembedParams`
5. `hmac.new(AppSecret[shopName], mergedParams, digestmod="sha1").hexdigest()`
6. 转大写返回

与 Django 后端 `ali1688.py::_calculate_signature` **算法完全一致**。

### 8.4 企业微信通知

**[hooks/wxwork.py](file:///d:/workplace_shop/WeWin/AliData/hooks/wxwork.py)**：

- 使用 `schedule` 库，每日 00:03 执行
- `start()`：拉取纺织类店铺（万盈饰品厂等 5 家）销售汇算，推送 markdown 到企业微信群机器人
- `compare()`：拉取饰品类店铺（4 家），推送另一群机器人
- 消息格式：`formate_single_message` 按店铺生成绿色（销售额）/橙色（总计）markdown 块

### 8.5 与 Django 后端的关系

| 维度 | AliData（遗留）| Django `ali1688.py`（现代）|
|---|---|---|
| 框架 | 独立脚本 | Django 服务，ORM 持久化 |
| 凭证 | 硬编码 | 数据库 `PlatformApiConfig` |
| 签名算法 | `CalculateSignature` | `_calculate_signature`（一致）|
| 分页 | `CalPageNum`（pageSize=20）| 内联计算（一致）|
| 持久化 | 无 | `Order`/`OrderItem`/`OrderReceiver` 全量入库 |
| 销售汇算 | `get_sales_amount` + 按状态退款计算 | **未实现** |
| 刷单过滤 | BLUE/GREEN 标签分流 | **未实现** |
| 3 天回溯 | `Settings` 应用 | **未实现** |
| Excel 备货单 | `tmp.py`/`tmp2.py` 生成 | **未实现** |
| 企业微信通知 | `hooks/wxwork.py` 定时推送 | **未实现** |
| 物流接口 | `GetDeliveryData`（未用）| 未实现 |
| 任务跟踪 | 无 | `DataPullTask` 状态机 |

**结论**：Django 后端是 AliData 拉取逻辑的现代化精简重构，仅实现了数据入库；销售汇算、退款计算、刷单过滤、Excel、企业微信等业务功能**仍仅存在于 AliData**，尚未迁移。

---

## 9. 核心数据模型关系

```
Company（企业）
  ├── User（用户，account.User，自定义 AbstractUser）
  │     └── UserType: super_admin / site_admin / enterprise_leader /
  │                    enterprise_admin / enterprise_user / temporary
  ├── Store（店铺）
  │     ├── PlatformApiConfig（平台 API 凭证，OneToOne）
  │     ├── StoreDataConfig（自动拉取配置，OneToOne）
  │     ├── DataPullTask（拉取任务记录）
  │     ├── StoreData（按日聚合数据）
  │     └── Order（订单）
  │           ├── OrderItem（订单商品）
  │           ├── OrderReceiver（收货人，OneToOne）
  │           ├── OrderContact / OrderStep / OrderTradeTerm
  │           ├── OrderRateInfo / OrderBizInfo
  │           └── OrderLogistics → OrderLogisticsItem（物流）
  ├── Product（商品，按 product_type 区分）
  │     ├── ProductSku（SKU）
  │     ├── Bead（串珠详情，OneToOne）
  │     ├── Accessory（配件详情，OneToOne）
  │     └── FinishedProduct（成品详情，OneToOne）
  │           ├── FinishedProductBead（成品-串珠组成）
  │           └── FinishedProductAccessory（成品-配件组成）
  └── Customer（客户）
        ├── CustomerVisibility（可见用户配置）
        ├── CustomerProduct（客户专属商品 + 报价）
        └── CustomerPriceHistory（报价历史）
```

**关键约定**：
- 所有业务表通过 `company` 外键实现**企业级数据隔离**
- `created_by` 字段记录创建人，`is_active` 控制启用状态
- 订单相关表大量使用 `JSONField` 保存平台原始数据（`platform_raw_data`）
- 表名通过 `Meta.db_table` 显式指定（如 `product` 而非 `store_product`）

---

## 10. 认证与权限体系

### 10.1 JWT 认证流程

```
客户端                      后端
  │                          │
  │  POST /api/account/login/│
  │  {username, password}    │
  │ ────────────────────────>│
  │                          │ 验证密码
  │                          │ 生成 JWT (HS256, 7天)
  │  {token, user}           │
  │<──────────────────────── │
  │                          │
  │  GET /api/xxx            │
  │  Authorization: Bearer xxx
  │ ────────────────────────>│
  │                          │ 解码 JWT
  │                          │ 加载 User 到 request.user
  │                          │ 业务处理
  │  Response                │
  │<──────────────────────── │
```

- **算法**：HS256
- **密钥**：复用 Django `SECRET_KEY`
- **有效期**：7 天（硬编码）
- **无 refresh token**，无服务端黑名单
- **登出**：仅前端清除 token（后端 `logout_view` 调用 Django `logout()` 但对无状态 JWT 无实际效果）

### 10.2 权限层级

`USER_TYPE_RANK`（数字越小权限越高）：

| Rank | UserType | 说明 |
|---|---|---|
| 0 | super_admin | 网站超级管理员 |
| 1 | site_admin | 网站管理员 |
| 2 | enterprise_leader | 企业负责人 |
| 3 | enterprise_admin | 企业用户管理员 |
| 4 | enterprise_user | 企业用户普通账户 |
| 5 | temporary | 临时账户 |

**修改用户类型规则**：调用者只能修改 rank 严格大于自己的用户，且只能改为 rank 严格大于自己的类型。

### 10.3 数据可见性

| 用户类型 | 可见数据范围 |
|---|---|
| super_admin / site_admin | 全部 |
| enterprise_leader | 本企业全部 |
| enterprise_admin | 本企业内自己创建的 + 对自己可见的 |
| enterprise_user | 本企业内对自己可见的 |
| temporary | 无企业数据 |

---

## 11. 项目运行方式

### 11.1 环境准备

#### 后端

```bash
cd Server
python -m venv venv
source venv/bin/activate        # Linux
# 或 .\venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
cp .env.example .env            # 按需修改 SECRET_KEY 等
python manage.py migrate
python manage.py create_superadmin   # 创建超管 (superadmin / superadmin123)
python manage.py init_page_config    # 初始化页面配置
```

**环境变量**（[Server/.env.example](file:///d:/workplace_shop/WeWin/Server/.env.example)）：

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,*
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
# 以下变量在 .env.example 中暴露，但 settings.py 未消费（数据库硬编码 SQLite）
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
```

#### 前端

```bash
cd Page
npm install
# 创建 .env.local（注意：仓库未提供 .env.example）
# 内容：VITE_API_BASE_URL=http://127.0.0.1:8003
npm run dev
```

#### Android

```bash
cd Android
# 创建 app/local.properties 或根 local.properties
# 内容：API_BASE_URL=http://10.0.2.2:8003（模拟器）
# 或：API_BASE_URL=http://192.168.x.x:8003（真机，需配置 adb reverse）
./gradlew assembleRelease      # 构建 release APK
# 产物：app/build/outputs/apk/release/app-release.apk
adb install -r app/build/outputs/apk/release/app-release.apk
```

**真机调试**（来自项目记忆）：
- Windows 防火墙默认阻止手机访问本机 Django（端口 8003）
- 解决方案：配置防火墙规则 或 `adb reverse tcp:8003 tcp:8003`

### 11.2 本地开发

```bash
# 后端（端口 8003）
cd Server
python manage.py runserver 0.0.0.0:8003

# 前端（端口 5173）
cd Page
npm run dev

# 或通过 Makefile
make install-backend install-frontend
make run-backend run-frontend
```

### 11.3 生产部署

参考 [DEPLOYMENT.md](file:///d:/workplace_shop/WeWin/DEPLOYMENT.md)：

| 服务 | 端口 | 启动方式 |
|---|---|---|
| 后端 | 8003 | `gunicorn wewin.wsgi:application -b 0.0.0.0:8003` |
| 前端 | 8080 | `npm run build` 后 `python serve_spa.py`（serve dist）|

**生产服务器**：`http://10.0.8.11:8080`（前端）/ `http://10.0.8.11:8003`（后端）

**后台运行**：

```bash
# 后端
cd Server
nohup gunicorn wewin.wsgi:application -b 127.0.0.1:8003 > gunicorn.log 2>&1 &

# 前端
cd Page
npm run build
nohup serve -s dist -l 5173 > serve.log 2>&1 &
# 或 python serve_spa.py（端口 8080）
```

### 11.4 管理命令汇总

| 命令 | 用途 |
|---|---|
| `python manage.py create_superadmin` | 创建超级管理员 |
| `python manage.py init_page_config` | 初始化页面可见性配置 |
| `python manage.py update_enterprise_admin_to_leader` | 迁移企业管理员角色 |
| `python manage.py createsuperuser` | Django 标准超管创建 |
| `python manage.py makemigrations` | 生成迁移文件 |
| `python manage.py migrate` | 执行迁移 |

### 11.5 端口约定

| 端口 | 服务 | 环境 |
|---|---|---|
| 8003 | Django 后端 | 开发 + 生产 |
| 5173 | Vue 前端 | 开发 |
| 8080 | Vue 前端（SPA 服务器）| 生产 |

---

## 12. 已知问题与注意事项

### 12.1 安全相关

1. **敏感信息泄露**：`Server/.env`、`Page/.env.local`、`AliData/global_params.py`（硬编码 7 个店铺凭证）、`Server/token.txt`、`db.sqlite3*` 含敏感数据，已被 `.gitignore` 忽略，不得提交。
2. **CORS 开放**：开发环境 `CORS_ALLOW_ALL_ORIGINS=True`，生产环境需确保 `DEBUG=False`。
3. **JWT 无失效机制**：无 refresh token、无黑名单，token 泄露后只能等待过期（7 天）。
4. **明文 HTTP**：Android `network_security_config.xml` 允许 `www.wanying.asia` 明文 HTTP，存在安全风险。

### 12.2 代码质量

1. **装饰器未使用**：[utils/decorators.py](file:///d:/workplace_shop/WeWin/Server/utils/decorators.py) 定义了 `jwt_required` / `permission_required` 等装饰器，但各视图内联了自己的 JWT 校验，存在代码重复。
2. **Django 版本不一致**：`settings.py` 注释写 5.2.11，`requirements.txt` 写 4.2.30，实际 venv 可能是 5.x。
3. **Pillow 未声明**：`ImageField` 依赖 Pillow，但未列入 `requirements.txt`。
4. **数据库配置未消费 env**：`.env.example` 暴露 `DB_*` 变量，但 `settings.py` 硬编码 SQLite。
5. **`get_service_class` 缺少 `@staticmethod`**：[base.py](file:///d:/workplace_shop/WeWin/Server/store/services/base.py) 中的方法未加装饰器。
6. **`generate_company_code` 重复**：在 `account/views.py` 和 `company/views.py` 中重复定义。

### 12.3 前端问题

1. **`requiresAdmin` 未在路由守卫强制**：`/companies` 路由仅菜单过滤，直接输入 URL 可绕过。
2. **部分页面使用原生 fetch**：`Login.vue` / `Register.vue` / `BindCompany.vue` / `Users.vue` 使用 `fetch()` 而非封装的 axios 客户端，绕过统一 401 处理。
3. **占位页面**：`Inventory.vue` 和 `Sales.vue` 未实现。
4. **`BindCompany.vue` Bug**：`onMounted` 读取 `userStore.user` 但 store 暴露的是 `userInfo`。
5. **`Companies.vue` Bug**：`updateUserStatus` 本地函数遮蔽导入，调用未导入的 `updateUserStatusApi`。

### 12.4 Android 问题

1. **`ProductEditScreen` 表单未完整实现**：ViewModel 有完整状态，但屏幕仅渲染图片选择 + 错误条 + 保存按钮，字段输入未接入。
2. **`deleteProduct` 无 UI 调用**：`ApiService` 声明了删除接口，但无界面调用。
3. **`getProductTypes` 未使用**：声明但未被任何 ViewModel 调用。

### 12.5 AliData 遗留代码

1. **路径 CWD 相对**：`global_params.py` 使用 `os.path.realpath(os.curdir)`，必须从 `AliData/` 目录运行。
2. **多个 Bug**：
   - `utils/utils.py::SplitChineseAndPinyin` 使用内置 `str` 而非参数
   - `utils/cloth_worksheet.py::GetCost` 作用域错误 + 缺参数
   - `utils/ali_api.py::GetDeliveryTraceData` 死代码（计算错误签名后覆盖）
   - `manager/OrderManager.py::ProcessByOrderStatus` 引用未定义名称

### 12.6 开发约定

1. **企业数据隔离**：所有业务查询必须按 `request.user.company` 过滤。
2. **数据库表名**：模型 `Meta.db_table` 显式指定（如 `product` 而非 `store_product`）。
3. **时区**：`TIME_ZONE = "Asia/Shanghai"`，`USE_TZ = True`，时间字段 UTC 存储。
4. **文件上传**：商品图片上传至 `products/%Y/%m/%d/`，`MEDIA_ROOT = Server/media`，单文件上限 100MB。
5. **PUT multipart 处理**：Django PUT 请求需手动用 `MultiPartParser` 解析 multipart/form-data。
6. **规划文档**：`.trae/specs/` 下为各模块 PRD，开发新功能前应先查阅对应 spec。

---

## 附录：关键文件索引

### 后端核心

| 文件 | 说明 |
|---|---|
| [Server/wewin/settings.py](file:///d:/workplace_shop/WeWin/Server/wewin/settings.py) | Django 配置 |
| [Server/wewin/urls.py](file:///d:/workplace_shop/WeWin/Server/wewin/urls.py) | 总路由 |
| [Server/account/models.py](file:///d:/workplace_shop/WeWin/Server/account/models.py) | User / PageConfig 模型 |
| [Server/account/views.py](file:///d:/workplace_shop/WeWin/Server/account/views.py) | 认证与用户管理视图 |
| [Server/company/models.py](file:///d:/workplace_shop/WeWin/Server/company/models.py) | Company 模型 |
| [Server/store/models.py](file:///d:/workplace_shop/WeWin/Server/store/models.py) | 店铺/商品/订单模型 |
| [Server/store/views.py](file:///d:/workplace_shop/WeWin/Server/store/views.py) | 店铺与商品管理视图 |
| [Server/store/services/base.py](file:///d:/workplace_shop/WeWin/Server/store/services/base.py) | 数据拉取抽象基类 |
| [Server/store/services/ali1688.py](file:///d:/workplace_shop/WeWin/Server/store/services/ali1688.py) | 1688 平台实现 |
| [Server/customer/models.py](file:///d:/workplace_shop/WeWin/Server/customer/models.py) | 客户管理模型 |
| [Server/utils/decorators.py](file:///d:/workplace_shop/WeWin/Server/utils/decorators.py) | 认证装饰器 |

### 前端核心

| 文件 | 说明 |
|---|---|
| [Page/src/main.js](file:///d:/workplace_shop/WeWin/Page/src/main.js) | 应用入口 |
| [Page/src/router/index.js](file:///d:/workplace_shop/WeWin/Page/src/router/index.js) | 路由配置 |
| [Page/src/api/client.js](file:///d:/workplace_shop/WeWin/Page/src/api/client.js) | axios 工厂 |
| [Page/src/store/user.js](file:///d:/workplace_shop/WeWin/Page/src/store/user.js) | Pinia 用户状态 |
| [Page/src/layout/index.vue](file:///d:/workplace_shop/WeWin/Page/src/layout/index.vue) | 主布局 |
| [Page/src/views/Products.vue](file:///d:/workplace_shop/WeWin/Page/src/views/Products.vue) | 商品管理（最复杂）|

### Android 核心

| 文件 | 说明 |
|---|---|
| [Android/app/build.gradle.kts](file:///d:/workplace_shop/WeWin/Android/app/build.gradle.kts) | 构建配置 |
| [Android/app/src/main/java/com/wewin/app/WeWinApp.kt](file:///d:/workplace_shop/WeWin/Android/app/src/main/java/com/wewin/app/WeWinApp.kt) | Application 入口 |
| [Android/app/src/main/java/com/wewin/app/data/remote/RetrofitClient.kt](file:///d:/workplace_shop/WeWin/Android/app/src/main/java/com/wewin/app/data/remote/RetrofitClient.kt) | 网络客户端 |
| [Android/app/src/main/java/com/wewin/app/data/remote/ApiService.kt](file:///d:/workplace_shop/WeWin/Android/app/src/main/java/com/wewin/app/data/remote/ApiService.kt) | API 接口定义 |
| [Android/app/src/main/java/com/wewin/app/ui/navigation/AppNavGraph.kt](file:///d:/workplace_shop/WeWin/Android/app/src/main/java/com/wewin/app/ui/navigation/AppNavGraph.kt) | 导航图 |

### 文档

| 文件 | 说明 |
|---|---|
| [AGENT.md](file:///d:/workplace_shop/WeWin/AGENT.md) | AI 代理导航指南 |
| [DEPLOYMENT.md](file:///d:/workplace_shop/WeWin/DEPLOYMENT.md) | 部署说明 |
| [OPTIMIZATION.md](file:///d:/workplace_shop/WeWin/OPTIMIZATION.md) | 优化总结与建议 |
| [README.md](file:///d:/workplace_shop/WeWin/README.md) | 项目运行说明 |
| [Makefile](file:///d:/workplace_shop/WeWin/Makefile) | 常用命令入口 |

---

*本文档基于代码库静态分析生成，反映生成日期时的仓库状态。*
