# WeWin 电商 ERP 管理系统

WeWin 是一套面向多企业的电商运营管理系统，围绕**手串（串珠 / 配件 / 成品）与童装**两条商品线，提供企业隔离、店铺管理、1688 订单拉取、商品 BOM 与成本核算、客户报价、销售利润统计，并配套 Web 后台与 Android 客户端。

---

## 功能特性

| 模块 | 能力 |
| --- | --- |
| 企业与权限 | 多企业数据隔离；6 类用户角色；页面可见性配置；JWT 登录认证 |
| 店铺管理 | 多平台店铺维护（1688 已接入）；平台 API 凭证配置；手动/定时拉单；拉单任务记录 |
| 订单管理 | 1688 订单列表与详情同步；收货人、商品项、物流、评价等完整明细；保留平台原始 JSON |
| 商品管理 | 串珠、手串配件、手串成品、童装四类商品；SKU 管理；商品图片上传 |
| 成本核算 | 成品 BOM（串珠 + 配件）成本自动重算；成本变更历史快照；利润与利润率展示 |
| 童装成本表 | 类 Excel 成本矩阵（行=货号、列=尺码），支持筛选、搜索、排序、冻结列与批量保存 |
| 客户与报价 | 客户档案；客户可见商品配置；客户专属报价与报价历史 |
| 数据看板 | 商品统计概览 |
| 移动端 | Android 原生客户端，复用后端 API，支持登录与商品管理 |
| 辅助工具 | 1688 订单/利润汇算脚本；企业微信销售日报推送 |

> 说明：Web 端「库存管理」「销售数据」目前为占位页面，功能尚未实现。

---

## 技术栈

### 后端

- Python 3.10+（当前环境 3.12）
- Django 4.2.30（未使用 Django REST Framework）
- PyJWT 2.8.0（HS256，手写认证装饰器）
- SQLite（默认数据库）
- django-cors-headers、python-dotenv、Pillow、APScheduler、openpyxl

### Web 前端

- Vue 3.5 + Vite 4
- Element Plus 2.13 + @element-plus/icons-vue
- Pinia（状态管理）、vue-router（history 模式）
- Axios（统一封装）、ECharts、Handsontable、xlsx + file-saver

### Android

- Kotlin + Jetpack Compose（Material3）
- Retrofit + OkHttp + kotlinx-serialization
- DataStore（Token 持久化）、Coil、Navigation Compose

### 独立脚本

- Python + requests 直连 1688 OpenAPI
- openpyxl 处理成本与利润 Excel
- 企业微信机器人 Webhook 推送

---

## 系统架构

```
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│  Page (Vue 3)   │   │ Android (Kotlin)│   │ AliData (脚本)  │
│  Web 管理后台   │   │  移动端客户端   │   │ 1688 拉单/汇算  │
└────────┬────────┘   └────────┬────────┘   └────────┬────────┘
         │  HTTP + JWT         │                     │ 1688 OpenAPI
         └──────────┬──────────┘                     │
                    ▼                                ▼
        ┌───────────────────────┐          ┌──────────────────┐
        │  Server (Django)      │          │  1688 开放平台   │
        │  /api/<app>/  :8003   │          └──────────────────┘
        └───────────┬───────────┘
                    │
     ┌──────────────┼───────────────┬──────────────┐
     ▼              ▼               ▼              ▼
  account        company          store         customer
  用户/权限      企业隔离      店铺/商品/订单    客户/报价
                    │
                    ▼
              SQLite (db.sqlite3)
```

- 所有业务表通过 `company` 外键实现企业级数据隔离。
- 认证为自定义 JWT：请求头 `Authorization: Bearer <token>`，Token 有效期 7 天。
- 定时任务由 APScheduler 在 Django 进程内启动（每分钟检查一次自动拉单配置）。

---

## 目录结构

```
WeWin/
├── Server/                       # Django 后端（:8003）
│   ├── wewin/                    # 项目配置（settings / urls / wsgi）
│   ├── account/                  # 用户、认证、角色、页面配置
│   ├── company/                  # 企业管理
│   ├── customer/                 # 客户、报价、可见性
│   ├── store/                    # 店铺 / 商品 / 订单 / 拉单
│   │   ├── models/               # store / product / order / data_pull
│   │   ├── views/                # helpers / store_views / product_views / order_views
│   │   ├── services/             # 拉单服务基类与 1688 实现
│   │   ├── management/commands/  # 商品导入、成本历史初始化
│   │   ├── tasks.py              # 自动拉单任务
│   │   └── apps.py               # APScheduler 启动入口
│   ├── utils/decorators.py       # jwt_required / permission_required 等
│   ├── manage.py
│   └── requirements.txt
├── Page/                         # Vue 3 前端
│   ├── src/
│   │   ├── api/                  # 模块化 API 客户端
│   │   ├── views/                # 页面（products / stores / components）
│   │   ├── layout/               # 主布局（侧边栏 + 顶栏）
│   │   ├── router/               # 路由与登录/权限守卫
│   │   └── store/                # Pinia 状态
│   ├── serve_spa.py              # 生产环境 SPA 静态服务（:8080）
│   └── vite.config.js
├── Android/                      # Kotlin + Compose 原生客户端
├── AliData/                      # 1688 独立脚本（拉单、利润汇算、企微推送）
├── docs/                         # CODE_WIKI.md、提交日志 log.txt
├── document/                     # 业务与 1688 API 相关文档
├── .trae/                        # 规划文档与 specs
├── start.sh / stop.sh            # 一键启停脚本
├── start_backend.sh              # 后端启动脚本
├── start_frontend.sh             # 前端启动脚本（Nginx）
├── start_wxwork.sh               # 企微定时任务启动脚本
└── Makefile
```

---

## 快速开始

### 环境要求

| 依赖 | 版本建议 |
| --- | --- |
| Python | 3.10+（推荐 3.12） |
| Node.js | 18+ |
| npm | 9+ |
| Android Studio / JDK | 仅开发 Android 端时需要（compileSdk 34，minSdk 24） |

### 1. 启动后端

```bash
cd Server

# 创建并激活虚拟环境
python3 -m venv venv
source venv/bin/activate          # Windows: .\venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt

# 准备环境变量
cp .env.example .env              # 按需修改

# 初始化数据库
python manage.py migrate

# 创建默认超级管理员（superadmin / superadmin123，首次登录后请修改密码）
python manage.py create_superadmin

# 初始化页面可见性配置
python manage.py init_page_config

# 启动服务
python manage.py runserver 0.0.0.0:8003
```

后端本地地址：`http://127.0.0.1:8003`，公网地址：`http://47.250.165.79:8003`，API 前缀：`/api/`。

### 2. 启动 Web 前端

```bash
cd Page
npm install

# 配置后端地址（代码默认 http://47.250.165.79:8003；本地开发可覆盖为 127.0.0.1）
echo "VITE_API_BASE_URL=http://47.250.165.79:8003" > .env.local

npm run dev                       # 开发环境，默认 http://localhost:5173
```

生产构建与本地预览：

```bash
npm run build                     # 产物输出到 Page/dist
python3 serve_spa.py              # SPA 静态服务，http://localhost:8080
```

### 3. 启动 Android 客户端（可选）

```bash
cd Android
cp app/local.properties.example app/local.properties
# 修改 API_BASE_URL：
#   模拟器  -> http://10.0.2.2:8003
#   真机    -> http://<后端局域网IP>:8003

./gradlew assembleDebug
```

APK 输出：`app/build/outputs/apk/debug/app-debug.apk`。

### 4. 使用启动脚本（Linux 服务器）

```bash
./start.sh          # 同时启动后端（:8003）与前端（:8080，serve_spa.py）
./stop.sh           # 停止两个服务

./start_backend.sh  # 仅启动后端
./start_frontend.sh # 仅启动前端（使用系统 Nginx + nginx_system.conf）
./stop_backend.sh
./stop_frontend.sh

./start_wxwork.sh   # 启动企微定时推送服务
./stop_wxwork.sh
```

日志：`backend.log`、`frontend.log`、`wxwork.log`。

---

## 配置说明

### 后端环境变量（`Server/.env`）

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `SECRET_KEY` | 内置开发值 | Django 与 JWT 签名密钥，生产环境必须修改 |
| `DEBUG` | `True` | 调试模式；为 `True` 时 CORS 允许所有来源 |
| `ALLOWED_HOSTS` | `*` | 逗号分隔的允许域名 |
| `CORS_ALLOWED_ORIGINS` | 空 | 非 DEBUG 时生效的跨域白名单，逗号分隔 |
| `DB_ENGINE` / `DB_NAME` / `DB_USER` / `DB_PASSWORD` / `DB_HOST` / `DB_PORT` | - | 示例中预留，当前 `settings.py` 固定使用 SQLite，暂未读取 |

### 前端环境变量（`Page/.env.local`）

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `VITE_API_BASE_URL` | `http://47.250.165.79:8003` | 后端 API 基址（本地开发可覆盖为 `http://127.0.0.1:8003`） |

### Android（`Android/app/local.properties`）

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `API_BASE_URL` | `http://10.0.2.2:8003` | 模拟器访问宿主机后端；真机改为局域网地址 |

---

## 常用命令

### Django 管理命令

| 命令 | 说明 |
| --- | --- |
| `python manage.py create_superadmin` | 创建默认网站超级管理员 |
| `python manage.py init_page_config` | 初始化各用户类型的页面可见性 |
| `python manage.py update_enterprise_admin_to_leader` | 将历史企业管理员数据迁移为企业负责人 |
| `python manage.py import_children_clothing` | 从 Excel 导入童装商品 |
| `python manage.py init_finished_cost_history` | 为现有成品初始化成本历史记录 |
| `python manage.py migrate` | 执行数据库迁移 |

### 数据库备份

```bash
cd Server
python backup_db.py --keep 10     # 备份并保留最近 10 份
```

### 服装利润汇算（AliData）

```bash
cd AliData
python profit_counting.py \
  --start 2026-11-01 --end 2026-11-30 \
  --shops "店铺名" \
  --send --export-profit --export-summary
```

| 参数 | 说明 |
| --- | --- |
| `--start` / `--end` | 统计起止日期（`YYYY-MM-DD`） |
| `--shops` | 指定店铺名，多个可用逗号分隔 |
| `--send` | 推送汇总到企业微信 |
| `--export-profit` | 导出每单利润明细 |
| `--export-summary` | 导出总账汇总 |

---

## API 约定

统一前缀：`/api/<app>/`，返回格式为 `JsonResponse`。

| 前缀 | 说明 |
| --- | --- |
| `/api/account/` | 登录、注册、当前用户、改密、用户管理、页面配置 |
| `/api/company/` | 企业 CRUD、企业用户、批量状态 |
| `/api/store/` | 店铺、API 配置、拉单、订单、商品、SKU、成本历史、童装成本 |
| `/api/customer/` | 客户 CRUD、客户商品与报价、可见性配置 |

约定：

- 业务接口统一使用 `@jwt_required` 校验登录，必要时叠加 `@permission_required` / `@admin_required`。
- 请求头携带 `Authorization: Bearer <token>`。
- 成功返回业务数据对象，失败返回 `{"error": "错误信息"}`。
- 所有查询按 `request.user.company` 过滤，禁止跨企业访问。
- 前端统一通过 `src/api/` 下的模块调用，不直接使用 Axios。

示例：

```
POST /api/account/login/
GET  /api/store/products/?product_type=finished
GET  /api/store/products/12/cost-history/
GET  /api/store/3/orders/?page=1
```

---

## 核心数据模型

```
Company
├── User（super_admin / site_admin / enterprise_leader /
│         enterprise_admin / enterprise_user / temporary）
├── Store
│   ├── PlatformApiConfig
│   ├── StoreDataConfig
│   ├── DataPullTask
│   ├── StoreData
│   └── Order
│       ├── OrderItem / OrderReceiver / OrderContact
│       ├── OrderStep / OrderTradeTerm
│       ├── OrderRateInfo / OrderBizInfo
│       └── OrderLogistics → OrderLogisticsItem
├── Product（product_type: bead / accessory / finished / children_clothing）
│   ├── ProductSku
│   ├── Bead / Accessory / FinishedProduct / ChildrenClothing
│   ├── FinishedProductBead / FinishedProductAccessory（BOM）
│   └── FinishedProductCostHistory（成本快照）
└── Customer
    ├── CustomerVisibility
    ├── CustomerProduct
    └── CustomerPriceHistory
```

要点：

- 商品采用「基础表 + 类型扩展表」：`Product` 存通用字段，四类详情各用 OneToOne 扩展。
- 成品通过 `FinishedProductBead` / `FinishedProductAccessory` 记录组成与数量，成本变动时自动重算并写入历史快照。
- 订单采用「主表 + 扩展表」，并在 `platform_raw_data` 中保留平台原始数据。
- 表名通过 `Meta.db_table` 显式指定，且均为单数形式（如 `product`、`order`）。

---

## 支持的平台

| 平台 | 状态 |
| --- | --- |
| 1688 | 已实现订单拉取 |
| 淘宝 / 天猫 / 京东 / 拼多多 / 抖音 / 快手 / 小红书 / 微信小店 | 模型已预留，拉单服务待实现 |

新增平台：在 `Server/store/services/` 继承 `BaseDataPullService`，实现 `pull_orders`、`pull_order_detail`、`save_order`，并在 `get_service_class` 中注册。

---

## 定时任务

| 任务 | 触发方式 | 说明 |
| --- | --- | --- |
| 店铺自动拉单 | APScheduler，每 1 分钟检查 | 读取 `StoreDataConfig.auto_pull_enabled` 与 `pull_interval_hours` 决定是否拉取 |
| 企微销售推送 | 独立进程，每日 00:03 | 由 `start_wxwork.sh` 启动 `AliData/hooks/wxwork.py` |

> 自动拉单调度随 Django 进程启动。生产环境如使用多 worker（如 gunicorn 多进程），需改为单独进程或分布式调度，避免重复执行。

---

## 部署

### 开发环境

- 后端：`python manage.py runserver 0.0.0.0:8003`
- 前端：`npm run dev`（5173）

### 生产环境

```bash
# 前端构建
cd Page
npm run build

# 方式一：内置 SPA 服务（:8080）
python3 serve_spa.py

# 方式二：系统 Nginx（仓库提供 nginx_system.conf / wewin-nginx.conf）
./start_frontend.sh
```

```bash
# 后端：Django 开发服务器（脚本默认方式）
./start_backend.sh

# 或 gunicorn
cd Server
source venv/bin/activate
gunicorn wewin.wsgi:application -b 0.0.0.0:8003
```

### 端口约定

| 服务 | 端口 |
| --- | --- |
| 后端 API | 8003 |
| 前端开发 | 5173 |
| 前端生产 | 8080 |

---

## 项目文档

- [AGENTS.md](AGENTS.md)：面向开发者的仓库导航、约定与常见任务指引
- [docs/CODE_WIKI.md](docs/CODE_WIKI.md)：逐模块代码导读
- [docs/log.txt](docs/log.txt)：提交日志（倒序）
- [DEPLOYMENT.md](DEPLOYMENT.md)：部署与启停脚本说明
- [document/](document/)：数据库设计、1688 API、业务模块等原始文档
- [.trae/specs/](.trae/specs/)：各功能模块的需求与实现规格

---

## 安全与注意事项

1. **生产环境必须修改 `SECRET_KEY`**，并将 `DEBUG` 设为 `False`、收敛 `ALLOWED_HOSTS` 与 CORS 白名单。
2. `AliData/global_params.py` 含 1688 店铺凭证，`Server/.env`、`Page/.env.local` 含敏感配置，禁止提交到公开仓库。
3. 数据库当前为 SQLite；高并发或多人协作场景建议迁移到 PostgreSQL / MySQL。
4. 仓库中的 `Server/db.sqlite3` 及备份文件可能包含真实业务数据，请勿随代码分发。
5. 业务代码暂无自动化测试；`Server/` 下的 `check_*.py`、`create_*.py`、`test_*.py` 多为一次性运维脚本，请勿当作测试套件执行。
6. 提交代码后需按约定更新 `docs/log.txt`（倒序，每个 commit 一条），详见 [AGENTS.md](AGENTS.md)。
