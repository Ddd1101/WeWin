# AGENTS.md

本文件为 AI 编码代理在本仓库中工作的导航指南，帮助快速理解项目结构、约定与常用操作。

---

## 项目概述

**WeWin** 是一套面向多企业的电商 ERP 管理系统，支持多店铺、多平台订单拉取、商品（串珠/配件/成品）管理、客户报价与权限隔离。

- **业务领域**：电商运营管理（店铺、商品、订单、客户、库存、销售数据）
- **核心商品类型**：串珠（bead）、手串配件（accessory）、手串成品（finished，由串珠+配件组成）、童装（children_clothing）
- **支持平台**：1688（已实现）、淘宝/天猫/京东/拼多多/抖音/快手/小红书/微信小店（模型已预留，服务待实现）

---

## 技术栈

### 后端（Server/）
- **框架**：Django 5.2.19
- **认证**：PyJWT 手写 JWT（非 DRF），通过 `utils/decorators.py` 的 `@jwt_required` 装饰器校验
- **数据库**：SQLite（开发为 `Server/db.sqlite3`，生产为 `/var/lib/wewin/db.sqlite3`），表名通过 `Meta.db_table` 显式指定
- **CORS**：django-cors-headers，开发环境 `CORS_ALLOW_ALL_ORIGINS=True`
- **定时任务**：APScheduler（店铺自动拉单）
- **关键依赖**：Django / PyJWT / requests / corsheaders / dotenv / Pillow / APScheduler

### 前端（Page/）
- **框架**：Vue 3.5 + Vite 4
- **UI**：Element Plus 2.13 + @element-plus/icons-vue
- **状态**：Pinia
- **路由**：vue-router（history 模式，带登录守卫 + requiresAdmin 校验）
- **HTTP**：axios（封装于 `src/api/client.js` 的 `createApiClient` 工厂）
- **其他**：echarts（图表）、xlsx + file-saver（导出 Excel）

### Android（Android/）
- **实现**：Kotlin + Jetpack Compose（Material3），Retrofit/OkHttp、kotlinx-serialization
- **状态与认证**：ViewModel/StateFlow、DataStore Token 与用户信息持久化
- **图片**：Coil + 系统 Photo Picker，上传使用 IO 线程有界临时文件
- **当前范围**：登录、四类商品与 SKU、童装尺码成本/售价、成品 BOM 和克价模拟、图片操作、个人信息与退出登录
- **构建**：JDK17、Android SDK34、Gradle Wrapper8.5；生产默认 HTTPS，参数见 `Android/README.md`
- **验收**：P0110 / Android17 已完成指定企业负责人账号真机验证；正式签名发布及其他版本/角色另行验证

### N1 媒体服务（media-service/）
- **实现**：Go 标准库，构建工具链 Go 1.27.4，部署为 ARM64 独立程序
- **职责**：图片原文件读写、哈希校验、原子发布、空间保护、回收区和媒体清单
- **链路**：N1 主动连接阿里云 SSH22，反向映射 Ali `127.0.0.1:10080` → N1 `127.0.0.1:18080`
- **数据位置**：N1 `~/Documents/workplace_shop/wewin-media/objects`；数据库仍在阿里云
- **运行监督**：`deploy/n1/run_media.py` 管理媒体进程和专用隧道，独占锁防止重复实例

### 部署与运维（deploy/）
- Nginx、systemd 服务与 timer 配置，前端构建、运行代码同步及统一启停入口
- 数据库/媒体清单备份、校验传输、联合恢复，以及 N1 安装与监督脚本
- `deploy/` 维护配置和运维工具，图片实际读写逻辑位于 `media-service/`
- 完整指引见 `DEPLOYMENT.md`、`deploy/N1-MEDIA.md`

### 独立脚本（AliData/）
- 独立 Python 脚本，直连 1688 OpenAPI，含销售/利润汇算与服装利润命令行入口
- `global_params.py` 中含硬编码的店铺凭证，属敏感信息

---

## 目录结构

```
WeWin/
├── Server/                     # Django 后端（主服务，端口 8003）
│   ├── wewin/                  # 项目配置（settings/urls/wsgi）
│   ├── account/                # 用户、认证、页面配置
│   ├── company/                # 企业管理
│   ├── store/                  # 店铺/商品/订单/拉单
│   │   ├── models/             # 按领域拆分为 product/store/order/data_pull 子包
│   │   ├── views/              # 按领域拆分为 helpers/store_views/order_views/product_views
│   │   ├── services/           # base.py 基类 + ali1688.py 实现
│   │   ├── tasks.py            # auto_pull_orders 自动拉单任务
│   │   └── apps.py             # 应用注册，不启动调度
│   ├── customer/               # 客户、报价、可见性
│   ├── utils/                  # 认证装饰器、media.py 上传事务/清理队列、remote_media.py N1 存储适配
│   ├── backup_db.py            # 数据库备份脚本
│   ├── manage.py
│   ├── requirements.txt
│   └── .env.example
├── Page/                       # Vue 3 前端（端口 5173 开发 / HTTPS 443 生产）
│   └── src/
│       ├── api/                # 按模块拆分的 API 客户端（account/company/store/customer）
│       ├── views/              # 页面（products/ stores/ 已拆分，components/ 复用组件）
│       ├── layout/             # 主布局（侧边栏+顶栏）
│       ├── router/             # 路由（含登录守卫 + requiresAdmin）
│       ├── store/              # Pinia 状态（user）
│       └── components/         # 通用组件
├── AliData/                    # 独立 1688 脚本（拉单 + 销售/利润汇算）
│   ├── manager/cloth_trade_manager.py
│   ├── hooks/wxwork.py         # 企业微信推送（销售/利润 markdown）
│   ├── profit_counting.py      # 服装利润汇算命令行入口
│   ├── utils/                  # ali_api / cloth_worksheet / utils
│   └── global_params.py        # 店铺凭证（硬编码，敏感）
├── Android/                    # Kotlin + Compose 原生客户端
│   ├── app/src/main/java/com/wewin/app/
│   │   ├── data/local/         # TokenStore 与认证事件
│   │   ├── data/remote/        # ApiService、网络/认证拦截器、DTO
│   │   └── ui/                # login / products / profile / navigation
│   └── README.md               # SDK、API配置、安装和真机验证入口
├── media-service/              # N1 图片读写程序：main.go、main_test.go、go.mod
├── deploy/                     # Nginx/systemd 配置、发布/备份/恢复工具
│   ├── n1/                    # N1 媒体监督与备份安装脚本
│   ├── backup.py / backup_exchange.py / restore_backup.py
│   └── N1-MEDIA.md             # 图片存储、缓存、迁移及恢复指引
├── ShopManager/                # 独立第三方工程（已 gitignore，不纳入本仓库）
├── docs/log.txt                # 提交日志
├── AGENTS.md                   # 本文件
├── Makefile / DEPLOYMENT.md / OPTIMIZATION.md
└── .trae/                      # Trae 规划文档与 specs
```

> 注意：`Server/venv2/` 为虚拟环境，`Server/staticfiles/` 为 Django 收集的静态文件，均不应手动修改。

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
  │     ├── ChildrenClothing（童装详情）
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
- 装饰器位于 `Server/utils/decorators.py`
- JWT payload 中含 `user_id`，装饰器会将 `User` 对象挂到 `request.user`

### URL 路由
- 总路由：`Server/wewin/urls.py`，统一前缀 `/api/<app>/`
- 各 app 的 `urls.py` 定义具体路由，命名风格：`<action>-<resource>`（如 `create-store`）
- 视图函数风格：函数视图 + `@csrf_exempt` + `@require_http_methods`，返回 `JsonResponse`

### 数据库
- 默认 SQLite，表名通过模型 `Meta.db_table` 显式指定（如 `product` 而非 `store_product`）
- 迁移文件位于各 app 的 `migrations/` 目录
- 自定义用户模型：`AUTH_USER_MODEL = 'account.User'`

### 平台数据拉取
- 抽象基类：`Server/store/services/base.py` 的 `BaseDataPullService`
- 1688 实现：`Server/store/services/ali1688.py`
- 新增平台需继承基类并实现 `pull_orders` / `pull_order_detail` / `save_order`，在 `get_service_class` 中注册
- 自动拉单：`store/tasks.py` 的 `auto_pull_orders`，由 `python manage.py run_scheduler` 的独立 APScheduler 进程每分钟调度，按 `StoreDataConfig` 的 `auto_pull_enabled` + `pull_interval_hours` 触发

### 管理命令
- `python manage.py create_superadmin` — 创建超级管理员
- `python manage.py init_page_config` — 初始化各用户类型的页面可见性配置

---

## 前端开发约定

### API 调用
- 统一通过 `src/api/` 下的模块化客户端调用，**不要**直接使用 axios
- 工厂函数：`Page/src/api/client.js` 的 `createApiClient(basePath)`
- 拦截器自动注入 `Authorization: Bearer <token>`，401 时自动跳转登录
- API 基址由 `VITE_API_BASE_URL` 环境变量配置，生产默认同源 HTTPS，本地开发默认 `http://127.0.0.1:8003`

### 路由与权限
- 路由配置：`Page/src/router/index.js`
- 登录守卫：未登录访问受保护页面跳转 `/login`；已登录访问登录页跳转 `/`
- `requiresAdmin` 路由会校验 `user_type` 是否为 `super_admin` / `site_admin`
- 菜单由路由 `meta.title` / `meta.icon` / `meta.requiresAdmin` 驱动，`meta.hidden` 控制是否在菜单显示
- Token 与用户信息存于 `localStorage`，Pinia store 同步状态

### 页面结构
- 主布局：`Page/src/layout/index.vue`（可折叠侧边栏 + 顶栏用户下拉）
- 主要页面：Dashboard / Customers / Stores / Products / Inventory / Sales / Users / Companies / Profile
- 子路由示例：`/customers/:id/products`（客户商品管理）

---

## 手串成品成本约定

- `FinishedProduct.cost_mode` 区分auto组成核算与manual独立整件定价；manual_cost为包含整件费用的采用成本，不再叠加工费。
- 组成始终可维护，reference_cost只用于参考测算。材料变价不能覆盖manual采用成本，利润使用顶层cost_price。
- 保存、重算、详情/列表共用 `store/views/helpers.py` 成本入口；客户端传入cost_price不得覆盖成品采用成本。
- 模式切换/独立成本调整要求cost_note；快照保存模式、采用成本、参考测算、原因及BOM。旧历史金额不重算，模式切换金额不变也留记录。
- 验证：`python manage.py test store.test_finished_cost_modes --noinput`；两端行为与API约定见 `docs/finished-cost-modes.md`。

---

## 重要约定与注意事项

1. **企业数据隔离**：所有业务查询必须按 `request.user.company` 过滤，禁止跨企业访问。
2. **敏感信息**：`Server/.env`、`Page/.env.local`、`AliData/global_params.py`、`Server/token.txt` 均含敏感数据，已被 `.gitignore` 忽略，不得提交。
3. **遗留代码**：`AliData/` 为独立脚本，与 Django 后端无直接依赖；`Server/` 下大量 `check_*.py` / `create_*.py` / `test_*.py` 为一次性运维脚本，非测试套件。
4. **未使用 DRF**：项目未引入 Django REST Framework，API 为手写函数视图。
5. **前端向后兼容**：`src/api/index.js` 同时支持命名导出与默认导出，修改 API 模块时保持两种导出方式均可用。
6. **数据库表名**：模型 `Meta.db_table` 显式指定表名（如 `product` 而非 `store_product`），新增模型需遵循此约定。
7. **时区**：`TIME_ZONE = "Asia/Shanghai"`，`USE_TZ = True`，时间字段统一 UTC 存储、前端按需转换。
8. **文件上传**：商品图片上传至 `products/%Y/%m/%d/`，开发 `MEDIA_ROOT = Server/media`，生产在线原文件使用N1 `wewin-media/objects`，阿里云缓存仅2GB，单文件上限 100MB。
9. **规划文档**：`.trae/specs/` 下为各模块 PRD，`.trae/documents/` 下为分析与计划文档，开发新功能前应先查阅对应 spec。
10. **提交日志**：每次 `git commit` 后必须在 `docs/log.txt` 追加一条记录，按提交时间**倒序**排列（最新在最上面），格式与步骤见「常见任务指引 → 提交代码与更新日志」。

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
```

### 本地开发
```bash
# 后端（默认 8003 端口）
cd Server
python manage.py runserver 0.0.0.0:8003

# 前端（默认 5173 端口）
cd Page
npm run dev
```

### 构建与部署
```bash
# 前端构建
cd Page
npm run build               # 产物在 Page/dist

# 生产环境（仓库根目录，systemd 单元已安装）
bash start.sh
python3 deploy/service_control.py all status
```

### 数据库备份
```bash
systemctl start wewin-backup    # 生产：数据库快照 + N1 媒体清单，不包含图片内容
# 开发SQLite备份：cd Server && python backup_db.py --keep 10
```

### 服装利润汇算（AliData 命令行）
```bash
cd AliData
python profit_counting.py [--start YYYY-MM-DD] [--end YYYY-MM-DD] [--shops 店名] [--send] [--export-profit] [--export-summary]
```

### 部署端口约定
- 前端：`443`（生产 HTTPS，80 跳转/证书验证）/ `5173`（开发）
- 后端：`8003`（生产仅监听 127.0.0.1）
- N1 媒体映射：Ali `127.0.0.1:10080` → N1 `127.0.0.1:18080`，不开放公网
- SSH22 用于管理、媒体隧道和受限备份传输；FRP7000/6000 为独立管理链路，按来源限制

---

## 生产部署与数据端代码入口

当前线上图片原文件存放N1，阿里云SQLite保留本地，图片缓存硬上限2GB。媒体模块为 `media-service/` 和 `Server/utils/remote_media.py`，部署指引 `deploy/N1-MEDIA.md`。新增图片写入不得回落到阿里云原文件目录，数据库备份不得包含全量图片。

- `Page/` 为前端源码，`Server/` 为后端源码，`deploy/` 为服务配置、联合备份与恢复代码。
- 统一启停使用 `start.sh` / `stop.sh` 或 `deploy/service_control.py`，支持 `--dry-run`，不恢复旧 runserver/8080 启动方式。
- `deploy/sync_runtime.py` 仅复制 Git 跟踪的源码与示例；生产库、媒体、密钥、环境文件和构建产物保留在仓库外。
- N1安装入口为 `deploy/n1/install_backup.py`，遵循 `deploy/n1/README.md`，保留既有FRP与其他cron任务。
- 开发、生产配置与服务安装步骤见 `DEPLOYMENT.md`、`deploy/README.md`；上线验收和整合记录在 `docs/`。

---

## Android 开发与真机验证约定

- 通过 `data/remote/ApiService.kt` 定义接口，由 ViewModel 管理请求和状态；DTO保持与后端 JSON 兼容。
- API地址优先顺序为 `-PAPI_BASE_URL`、`WEWIN_API_BASE_URL`、Android根目录 `local.properties`，默认 `https://47.250.165.79`。SDK路径使用实际 `ANDROID_HOME` 或根目录 `sdk.dir`。
- 搜索应查询后端企业可见范围，先筛选再分页；切换筛选取消旧请求，过期响应不得覆盖新结果。返回页面时刷新，分页失败提供重试。
- 编辑已有商品固定货号与类型；修改默认SKU时保留其他SKU的ID和数据。童装按尺码行保存，成品组成使用明确的材料/SKU和正整数数量。
- 图片选择使用Photo Picker；不得在UI线程读取全部大文件，临时文件需限制大小并在完成/失败后清理。图片读取失败应提示，不可静默当作无图提交。
- 错误密码留在登录页并展示反馈；业务401清除本地会话。Debug网络日志仅BASIC、Release关闭，禁止记录密码、Token或登录正文。
- 真机写入验证只操作专门创建的验证商品；先核对账号企业和权限，测试结束清理商品/SKU/图片引用并恢复网络设置。
- 变更按范围执行 `assembleDebug`、`lintDebug` 及真机复验。Lint Warning与Error分开报告；单设备、指定账号验收不能代替所有Android版本/角色或正式发布。
- 已完成真机验证与修复的具体证据见 `docs/android-device-validation-2026-11-26.md`；原生端尚无订单/客户独立页面，不计为已验证。

```bash
# 仓库根目录；替换实际SDK路径和设备序列号
ANDROID_HOME=/path/to/android-sdk bash Android/gradlew -p Android \
  -PAPI_BASE_URL=https://47.250.165.79 assembleDebug lintDebug
adb devices -l
adb -s <serial> install -r Android/app/build/outputs/apk/debug/app-debug.apk
```

---

## 图片存储开发与验证约定

1. `media-service/main.go` 负责 N1 文件操作，`Server/utils/remote_media.py` 负责后端远程存储，`Server/utils/media.py` 负责上传校验和引用/清理队列。
2. 远程上传先完成文件校验和写入，再在短数据库事务内更新引用；网络写入不得长期持有 SQLite 事务锁。
3. 删除与替换通过 `cleanup_media` 任务再次核对引用后回收文件并失效缓存。写入结果不确定时保留现场，不盲目删除或重试业务写入。
4. 阿里云缓存使用独立 2GiB 文件系统，淘汰目标 1.5GiB；上传暂存使用独立 512MiB 文件系统。数据库备份使用 512MiB预算检查，不与文件系统硬上限混淆。
5. N1 断线时缓存图可读，未缓存图片和图片写操作返回503，登录/订单/文字业务保持独立。N1 同机回收区不是独立设备备份。
6. 变更验证按范围选择：Django `store.test_deployment` / `store.test_remote_media`；`python3 -m unittest discover -s deploy -p 'test_*.py'`；在 `media-service/` 执行 `go test -race ./...`。
7. 联合恢复须提供 N1 原文件或回收区并核对哈希；只恢复数据库和清单时，不能声明图片已恢复。

---

## 常见任务指引

### 新增一个后端 API
1. 在对应 app 的 `views.py`（或 `views/` 子模块）编写函数视图，加 `@jwt_required` 与权限装饰器
2. 在 app 的 `urls.py` 注册路由
3. 涉及新模型时，修改 `models.py`（或 `models/` 子模块）后执行 `makemigrations` + `migrate`
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
- 后端实现：`Server/store/services/ali1688.py`
- 参考实现：`AliData/manager/cloth_trade_manager.py`
- 签名算法：HMAC-SHA1，详见 `_calculate_signature` / `CalculateSignature` 方法
- 凭证配置：通过店铺的 `PlatformApiConfig` 管理，前端在店铺详情页配置

### 提交代码与更新日志
每次 `git commit` 后，必须同步在 `docs/log.txt` 追加一条记录，规则如下：

1. **倒序排列**：最新提交写在文件最上面（紧跟标题说明之后的第一条），不要追加到末尾。
2. **每个 commit 一条**：不合并多条提交；分批提交时每批 commit 各写一条记录。
3. **格式**（每条记录之间用 `---` 分隔）：

   ```
   ------------------------------------------------------------
   [YYYY-MM-DD] type: 提交说明
     Commit: <hash 前 7 位>
     分支:   <分支名>
     变更:   <N files changed, +X / -Y>
     说明:
       - <要点1>
       - <要点2>
   ```

4. **操作步骤**（`docs/log.txt` 与代码合并到同一个 commit，不再单独提交日志）：
   - `git add <代码文件>` 后 `git commit`，用 `git log --oneline -1` 取 hash
   - 用 `git show --stat <hash>` 取变更统计（files changed、插入/删除行数）
   - 将记录写入 `docs/log.txt` 最上面，然后 `git add docs/log.txt`
   - `git commit --amend --no-edit` 将 log.txt 并入刚才的 commit
   - 分批提交时每个功能一个 commit，各自 amend 合并对应的 log 记录
   - 说明：amend 后最终 hash 会变化，log 中 `Commit:` 字段记录的是代码提交点（amend 前）的 hash，最终 hash 以 `git log` 为准

5. `type` 遵循 conventional commit：`feat` / `fix` / `refactor` / `docs` / `chore` 等。

6. **不要提交**：`Page/dist/` 等构建产物。
