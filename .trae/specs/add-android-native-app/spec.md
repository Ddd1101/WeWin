# WeWin 安卓原生 App Spec

## Why
当前 WeWin 仅有 Vue Web 前端与 `Page/android` Capacitor WebView 包装，移动端体验受限。商品管理是高频移动场景（现场盘点、随手录单），需要原生 App 提供更流畅的体验、本地凭证持久化与拍照上传能力。本变更在项目根目录新建独立的 `Android/` 原生工程，复用现有 Django 后端 API，优先实现商品管理模块。

## What Changes
- 在项目根目录新建 `Android/` 目录，承载独立的 Kotlin + Jetpack Compose 原生 Android 工程
- 实现登录页（用户名/密码 → JWT），Token 持久化到 DataStore，OkHttp 拦截器自动注入 `Authorization: Bearer <token>`
- 实现主框架：底部导航 + 顶部栏，含「商品」「我的」两个主入口
- **商品管理模块（优先）**：
  - 商品列表（按类型 bead/accessory/finished 分页筛选、关键字搜索、启用状态过滤）
  - 商品详情（基础信息 + SKU 列表 + 成品组成明细 + 图片）
  - 新建商品（按类型动态表单：串珠/配件/成品，含成品串珠+配件组成选择）
  - 编辑商品（复用新建表单，回填数据）
  - 删除商品（二次确认）
  - 商品图片拍照/相册上传（multipart/form-data）
  - 商品统计卡片（总数/启用/各类型数量）
- 实现「我的」页：展示当前用户信息、企业、退出登录
- 401 响应自动清除 Token 并跳转登录页
- API 基址可配置（BuildConfig / local.properties），默认指向 `http://10.0.2.2:8003`（模拟器访问宿主机）
- 不修改后端代码，完全复用现有 `/api/account/*` 与 `/api/store/products/*` 端点

## Impact
- Affected specs: 无（新增独立模块，不改动 customer_module / deployment / 商品类型标签页优化）
- Affected code:
  - 新增：`Android/` 整个工程目录
  - 复用（只读）：[Server/account/views.py](file:///d:/workplace_shop/WeWin/Server/account/views.py)（登录接口）、[Server/store/views.py](file:///d:/workplace_shop/WeWin/Server/store/views.py)（商品接口）、[Server/store/urls.py](file:///d:/workplace_shop/WeWin/Server/store/urls.py)
  - 不改动：`Server/`、`Page/`、`AliData/` 任何现有文件
- 与 `Page/android`（Capacitor WebView 包装）并存，二者互不依赖；本 App 为原生实现

## ADDED Requirements

### Requirement: 原生 Android 工程
系统 SHALL 在 `Android/` 目录下提供一个独立的 Kotlin + Jetpack Compose Android 工程，最小 SDK 24，目标 SDK 34，应用 ID `com.wewin.app`。

#### Scenario: 工程可构建
- **WHEN** 开发者在 `Android/` 目录执行 `./gradlew assembleDebug`
- **THEN** 生成可安装的 APK，无编译错误

#### Scenario: 网络配置可切换
- **WHEN** 开发者在 `local.properties` 设置 `API_BASE_URL`
- **THEN** App 运行时使用该地址作为后端基址；未设置时默认 `http://10.0.2.2:8003`

### Requirement: JWT 登录与鉴权
系统 SHALL 提供登录页，通过 `POST /api/account/login/` 获取 JWT，并将 Token 持久化到 DataStore；所有后续请求通过 OkHttp 拦截器自动注入 `Authorization: Bearer <token>`。

#### Scenario: 登录成功
- **WHEN** 用户输入正确用户名密码并提交
- **THEN** 调用登录接口成功，Token 与用户信息存入 DataStore，跳转主页

#### Scenario: 登录失败
- **WHEN** 用户名或密码错误
- **THEN** 显示后端返回的 `error` 字段，停留在登录页

#### Scenario: Token 失效自动登出
- **WHEN** 任意接口返回 401
- **THEN** 清除本地 Token 与用户信息，跳转登录页

### Requirement: 商品列表与筛选
系统 SHALL 提供商品列表页，调用 `GET /api/store/products/`，支持按 `product_type`、`is_active`、关键字筛选与分页加载。

#### Scenario: 按类型筛选
- **WHEN** 用户切换「全部/串珠/配件/成品」标签
- **THEN** 列表按对应 `product_type` 重新拉取并展示

#### Scenario: 下拉加载更多
- **WHEN** 用户滚动到底部且仍有下一页
- **THEN** 自动以 `page+1` 拉取并追加到列表

### Requirement: 商品详情
系统 SHALL 提供商品详情页，调用 `GET /api/store/products/<id>/detail/`，展示基础信息、SKU 列表、成品组成（串珠+配件）及图片。

#### Scenario: 查看成品详情
- **WHEN** 用户点开一个 finished 类型商品
- **THEN** 展示基础信息、工费/弹性成本、组成串珠列表（含数量）、组成配件列表（含数量）、图片

### Requirement: 新建/编辑商品
系统 SHALL 提供商品表单页，根据 `product_type` 动态渲染字段；新建调用 `POST /api/store/products/create/`，编辑调用 `PUT /api/store/products/<id>/update/`；含图片时以 `multipart/form-data` 提交。

#### Scenario: 新建串珠
- **WHEN** 用户选择类型「串珠」并填写货号、名称、价格、材质、规格、颜色、克重、品质等级后提交
- **THEN** 成功创建并返回列表页，新商品出现在顶部

#### Scenario: 编辑成品组成
- **WHEN** 用户在成品表单中添加/调整串珠与配件组成数量后提交
- **THEN** 成品组成更新成功，详情页展示最新组成

#### Scenario: 图片上传
- **WHEN** 用户在表单中拍照或从相册选择图片并提交
- **THEN** 图片以 multipart 上传，成功后详情页展示新图片

### Requirement: 删除商品
系统 SHALL 在详情页或列表项提供删除入口，调用 `DELETE /api/store/products/<id>/delete/`，删除前需二次确认。

#### Scenario: 确认删除
- **WHEN** 用户点击删除并在确认对话框中点击「确定」
- **THEN** 调用删除接口，成功后返回列表并移除该项

### Requirement: 商品统计
系统 SHALL 在商品列表顶部展示统计卡片，调用 `GET /api/store/products/stats/`，展示总数、启用数、各类型数量。

#### Scenario: 首次进入商品页
- **WHEN** 用户进入商品页
- **THEN** 顶部展示统计卡片，数据来自 stats 接口

### Requirement: 我的页与退出登录
系统 SHALL 提供「我的」页，展示当前用户信息（用户名、类型、企业），并提供退出登录入口。

#### Scenario: 退出登录
- **WHEN** 用户点击「退出登录」
- **THEN** 清除本地 Token 与用户信息，跳转登录页
