# AGENT.md

本文件为 AI 代理（如 Trae / Claude Code 等）在本仓库中工作时的导航指南，帮助快速理解项目结构、约定与常用操作。

---

## 项目概述

**WeWin** 是一套面向多企业的电商 ERP 管理系统，支持多店铺、多平台订单拉取、商品（串珠/配件/成品）管理、客户报价与权限隔离。

- **业务领域**：电商运营管理（店铺、商品、订单、客户、库存、销售数据）
- **核心商品类型**：串珠（bead）、手串配件（accessory）、手串成品（finished，由串珠+配件组成）
- **支持平台**：1688（已实现）、淘宝/天猫/京东/拼多多/抖音/快手/小红书/微信小店（模型已预留，服务待实现）

---

## 仓库结构

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
│   │   ├── api/                # 按模块拆分的 API 客户端（account/company/store/customer）
│   │   ├── views/              # 页面组件
│   │   ├── layout/             # 主布局（侧边栏+顶栏）
│   │   ├── router/             # 路由配置（含登录守卫）
│   │   ├── store/              # Pinia 状态（user）
│   │   └── components/         # 通用组件
│   ├── vite.config.js
│   ├── package.json
│   └── serve_spa.py            # 简易 SPA 静态服务器（生产部署用）
├── AliData/                    # 独立的 1688 数据拉取脚本（遗留/参考实现，非 Django 部分）
│   ├── global_params.py        # 店铺 AppKey/AppSecret/AccessToken（硬编码，敏感）
│   ├── manager/                # OrderManager 等业务逻辑
│   ├── utils/                  # 工具函数
│   └── hooks/                  # 企业微信通知等钩子
├── .trae/                      # Trae 规划文档与 specs
│   ├── documents/              # 分析与计划文档
│   └── specs/                  # 各模块 PRD（customer_module / deployment 等）
├── Makefile                    # 常用命令入口
├── DEPLOYMENT.md               # 部署说明
└── OPTIMIZATION.md             # 已完成优化与后续建议
```

> 注意：`Server/venv2/` 为虚拟环境，`Server/staticfiles/` 为 Django 收集的静态文件，均不应手动修改。

---

## 技术栈

### 后端（Server/）
- **框架**：Django 4.2.30（项目配置写法兼容 5.2）
- **认证**：PyJWT 手写 JWT（非 DRF），通过 `utils/decorators.py` 中的装饰器校验
- **数据库**：SQLite（`Server/db.sqlite3`），表名通过 `db_table` 显式指定
- **CORS**：django-cors-headers，开发环境 `CORS_ALLOW_ALL_ORIGINS=True`
- **配置**：python-dotenv 读取 `Server/.env`
- **关键依赖**：见 `Server/requirements.txt`（Django / PyJWT / requests / corsheaders / dotenv）

### 前端（Page/）
- **框架**：Vue 3.5 + Vite 4
- **UI**：Element Plus 2.13 + @element-plus/icons-vue
- **状态**：Pinia
- **路由**：vue-router 5（history 模式，带登录守卫）
- **HTTP**：axios（封装于 `src/api/client.js` 的 `createApiClient` 工厂）
- **其他**：echarts（图表）、xlsx + file-saver（导出 Excel）

### 遗留脚本（AliData/）
- 独立 Python 脚本，直连 1688 OpenAPI，用于参考与离线数据拉取
- `global_params.py` 中含硬编码的店铺凭证，属敏感信息

---

## 核心数据模型关系

```
Company（企业）
  ├── User（用户，account.User，自定义 AbstractUser）
  │     └── UserType: super_admin / site_admin / enterprise_leader /
  │                    enterprise_admin / enterprise_user / temporary
  ├── Store（店铺）
  │     ├── PlatformApiConfig（平台 API 凭证）
  │     ├── StoreDataConfig（自动拉取配置）
  │     ├── DataPullTask（拉取任务记录）
  │     ├── StoreData（按日聚合数据）
  │     └── Order（订单）
  │           ├── OrderItem（订单商品）
  │           ├── OrderReceiver（收货人）
  │           ├── OrderContact / OrderStep / OrderTradeTerm
  │           ├── OrderRateInfo / OrderBizInfo
  │           └── OrderLogistics → OrderLogisticsItem（物流）
  ├── Product（商品，按 product_type 区分）
  │     ├── ProductSku（SKU）
  │     ├── Bead（串珠详情，OneToOne）
  │     ├── Accessory（配件详情，OneToOne）
  │     └── FinishedProduct（成品详情）
  │           ├── FinishedProductBead（成品-串珠组成）
  │           └── FinishedProductAccessory（成品-配件组成）
  └── Customer（客户）
        ├── CustomerVisibility（可见用户配置）
        ├── CustomerProduct（客户专属商品+报价）
        └── CustomerPriceHistory（报价历史）
```

- 所有业务表均通过 `company` 外键实现**企业级数据隔离**
- `created_by` 字段记录创建人，`is_active` 控制启用状态
- 订单相关表大量使用 `JSONField` 保存平台原始数据（`platform_raw_data`）

---

## 后端开发约定

### 认证与权限
- 所有业务 API 必须使用 `@jwt_required` 装饰器校验登录
- 权限控制使用 `@permission_required([...])` / `@admin_required` / `@enterprise_leader_required`
- 装饰器位于 [Server/utils/decorators.py](file:///d:/workplace_shop/WeWin/Server/utils/decorators.py)
- JWT payload 中含 `user_id`，装饰器会将 `User` 对象挂到 `request.user`

### URL 路由
- 总路由：[Server/wewin/urls.py](file:///d:/workplace_shop/WeWin/Server/wewin/urls.py)，统一前缀 `/api/<app>/`
- 各 app 的 `urls.py` 定义具体路由，命名风格：`<action>-<resource>`（如 `create-store`）
- 视图函数风格：函数视图 + `@csrf_exempt` + `@require_http_methods`，返回 `JsonResponse`

### 数据库
- 默认 SQLite，表名通过模型 `Meta.db_table` 显式指定（如 `product`、`order`、`user`）
- 迁移文件位于各 app 的 `migrations/` 目录
- 自定义用户模型：`AUTH_USER_MODEL = 'account.User'`

### 平台数据拉取
- 抽象基类：[Server/store/services/base.py](file:///d:/workplace_shop/WeWin/Server/store/services/base.py) `BaseDataPullService`
- 1688 实现：[Server/store/services/ali1688.py](file:///d:/workplace_shop/WeWin/Server/store/services/ali1688.py)
- 新增平台需继承基类并实现 `pull_orders` / `pull_order_detail` / `save_order`，在 `get_service_class` 中注册

### 管理命令
- `python manage.py create_superadmin` — 创建超级管理员
- `python manage.py init_page_config` — 初始化各用户类型的页面可见性配置

---

## 前端开发约定

### API 调用
- 统一通过 `src/api/` 下的模块化客户端调用，**不要**直接使用 axios
- 工厂函数：[Page/src/api/client.js](file:///d:/workplace_shop/WeWin/Page/src/api/client.js) `createApiClient(basePath)`
- 拦截器自动注入 `Authorization: Bearer <token>`，401 时自动跳转登录
- API 基址由 `VITE_API_BASE_URL` 环境变量配置，默认 `http://127.0.0.1:8003`

### 路由与权限
- 路由配置：[Page/src/router/index.js](file:///d:/workplace_shop/WeWin/Page/src/router/index.js)
- 登录守卫：未登录访问受保护页面跳转 `/login`；已登录访问登录页跳转 `/`
- 菜单由路由 `meta.title` / `meta.icon` / `meta.requiresAdmin` 驱动，`meta.hidden` 控制是否在菜单显示
- Token 与用户信息存于 `localStorage`，Pinia store 同步状态（[Page/src/store/user.js](file:///d:/workplace_shop/WeWin/Page/src/store/user.js)）

### 页面结构
- 主布局：[Page/src/layout/index.vue](file:///d:/workplace_shop/WeWin/Page/src/layout/index.vue)（可折叠侧边栏 + 顶栏用户下拉）
- 主要页面：Dashboard / Customers / Stores / Products / Inventory / Sales / Users / Companies / Profile
- 子路由示例：`/customers/:id/products`（客户商品管理）

---

## 常用命令

### 环境准备
```bash
# 后端
cd Server
pip install -r requirements.txt
cp .env.example .env        # 按需修改
python manage.py migrate
python manage.py create_superadmin
python manage.py init_page_config

# 前端
cd Page
npm install
cp .env.example .env.local  # 按需修改 VITE_API_BASE_URL
```

### 本地开发
```bash
# 后端（默认 8003 端口）
cd Server
python manage.py runserver 0.0.0.0:8003

# 前端（默认 5173 端口）
cd Page
npm run dev

# 或通过 Makefile
make install-backend install-frontend
make run-backend run-frontend
```

### 构建与部署
```bash
# 前端构建
cd Page
npm run build               # 产物在 Page/dist

# 生产环境 SPA 服务（端口 8080）
cd Page
python serve_spa.py
```

### 部署端口约定
- 前端：`8080`（生产）/ `5173`（开发）
- 后端：`8003`
- 部署脚本：`start_frontend.sh` / `stop_frontend.sh` / `start_backend.sh` / `stop_backend.sh`（见 [DEPLOYMENT.md](file:///d:/workplace_shop/WeWin/DEPLOYMENT.md)）

---

## 重要约定与注意事项

1. **企业数据隔离**：所有业务查询必须按 `request.user.company` 过滤，禁止跨企业访问。参考各 app 的 `views.py` 实现。
2. **敏感信息**：`Server/.env`、`Page/.env.local`、`AliData/global_params.py`、`Server/token.txt`、`db.sqlite3*` 均含敏感数据，已被 `.gitignore` 忽略，不得提交。
3. **遗留代码**：`AliData/` 为独立脚本，与 Django 后端无直接依赖；`Server/` 下大量 `check_*.py` / `create_*.py` / `test_*.py` 为一次性运维脚本，非测试套件。
4. **未使用 DRF**：项目未引入 Django REST Framework，API 为手写函数视图；`OPTIMIZATION.md` 中有引入 DRF 的后续建议。
5. **前端向后兼容**：`src/api/index.js` 同时支持命名导出与默认导出，修改 API 模块时保持两种导出方式均可用。
6. **数据库表名**：模型 `Meta.db_table` 显式指定表名（如 `product` 而非 `store_product`），新增模型需遵循此约定。
7. **时区**：`TIME_ZONE = "Asia/Shanghai"`，`USE_TZ = True`，时间字段统一使用 UTC 存储、前端按需转换。
8. **文件上传**：商品图片上传至 `products/%Y/%m/%d/`，`MEDIA_ROOT = Server/media`，单文件上限 100MB。
9. **规划文档**：`.trae/specs/` 下为各模块 PRD，`.trae/documents/` 下为分析与计划文档，开发新功能前应先查阅对应 spec。

---

## 常见任务指引

### 新增一个后端 API
1. 在对应 app 的 `views.py` 编写函数视图，加 `@jwt_required` 与权限装饰器
2. 在 app 的 `urls.py` 注册路由
3. 涉及新模型时，修改 `models.py` 后执行 `makemigrations` + `migrate`
4. 返回统一使用 `JsonResponse`，错误信息放在 `{'error': '...'}`

### 新增一个前端页面
1. 在 `Page/src/views/` 创建 `.vue` 组件
2. 在 `Page/src/router/index.js` 注册路由，填写 `meta.title` / `meta.icon`
3. 如需菜单展示，确保父路由 `meta` 不含 `hidden`
4. API 调用通过 `src/api/` 对应模块，必要时新增导出

### 接入新的电商平台
1. 在 `Server/store/services/` 新建 `<platform>.py`，继承 `BaseDataPullService`
2. 实现 `pull_orders` / `pull_order_detail` / `save_order` 三个抽象方法
3. 在 `base.py` 的 `get_service_class` 中注册平台映射
4. 平台枚举已在 `store.models.Platform` 中预留，直接选用即可

### 调试 1688 数据拉取
- 后端实现：[Server/store/services/ali1688.py](file:///d:/workplace_shop/WeWin/Server/store/services/ali1688.py)
- 参考实现：[AliData/manager/OrderManager.py](file:///d:/workplace_shop/WeWin/AliData/manager/OrderManager.py)
- 签名算法：HMAC-SHA1，详见 `_calculate_signature` 方法
- 凭证配置：通过店铺的 `PlatformApiConfig` 管理，前端在店铺详情页配置
