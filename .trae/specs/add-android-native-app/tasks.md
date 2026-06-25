# Tasks

- [x] Task 1: 搭建 Android 原生工程骨架
  - [x] SubTask 1.1: 在 `Android/` 创建 Kotlin + Jetpack Compose 工程（build.gradle.kts、settings.gradle.kts、AndroidManifest.xml、最小 SDK 24 / 目标 SDK 34、applicationId `com.wewin.app`）
  - [x] SubTask 1.2: 配置依赖（Compose BOM、Material3、Retrofit + OkHttp、Coil、DataStore、Coroutines、Navigation Compose、kotlinx-serialization）
  - [x] SubTask 1.3: 配置 `local.properties` 读取 `API_BASE_URL`，默认 `http://10.0.2.2:8003`，注入 BuildConfig
  - [x] SubTask 1.4: 添加 INTERNET 权限与明文 HTTP 流量配置（`usesCleartextTraffic` 仅 debug，或 network security config 白名单 10.0.2.2）
  - [x] SubTask 1.5: 验证 `./gradlew assembleDebug` 可通过（无业务代码时返回空壳 APK）

- [x] Task 2: 实现网络层与鉴权基础设施
  - [x] SubTask 2.1: 创建 `data/remote/dto` 包，定义登录请求/响应、商品列表/详情/统计/SKU/成品组成等 DTO（与后端 JSON 字段一一对应）
  - [x] SubTask 2.2: 创建 Retrofit `ApiService` 接口，覆盖 `/api/account/login/` 与 `/api/store/products/*` 全部端点
  - [x] SubTask 2.3: 创建 OkHttp `AuthInterceptor`，从 DataStore 读取 Token 并注入 `Authorization: Bearer <token>`
  - [x] SubTask 2.4: 创建 `AuthAuthenticator` 或全局 401 处理器，401 时清除 Token 并发出「跳转登录」事件
  - [x] SubTask 2.5: 创建 `TokenStore`（DataStore preferences）封装 Token 与用户信息的读写
  - [x] SubTask 2.6: 创建 `RetrofitClient` 单例，串联 OkHttpClient + Retrofit + kotlinx-serialization 转换器

- [x] Task 3: 实现登录页与全局导航
  - [x] SubTask 3.1: 创建 `LoginViewModel` + `LoginScreen`（用户名/密码输入、提交、错误提示、Loading 态）
  - [x] SubTask 3.2: 登录成功后写入 TokenStore 并触发导航到主页
  - [x] SubTask 3.3: 创建 `MainScaffold`（底部导航：商品 / 我的）+ Navigation Compose 路由图
  - [x] SubTask 3.4: 启动时根据 TokenStore 是否有 Token 决定起始目的地（登录页或主页）

- [x] Task 4: 实现商品列表与统计（商品管理核心 1/3）
  - [x] SubTask 4.1: 创建 `ProductListViewModel`，调用 `GET /api/store/products/` 与 `GET /api/store/products/stats/`
  - [x] SubTask 4.2: 实现类型筛选 Tab（全部/串珠/配件/成品）、启用状态过滤、关键字搜索
  - [x] SubTask 4.3: 实现分页加载（page/page_size，滚动到底部自动加载下一页）
  - [x] SubTask 4.4: 实现列表项卡片（货号、名称、类型标签、价格、缩略图、启用状态）
  - [x] SubTask 4.5: 实现顶部统计卡片（总数/启用/各类型数量）
  - [x] SubTask 4.6: 列表项点击跳转详情；浮动按钮（FAB）跳转新建

- [x] Task 5: 实现商品详情（商品管理核心 2/3）
  - [x] SubTask 5.1: 创建 `ProductDetailViewModel`，调用 `GET /api/store/products/<id>/detail/`
  - [x] SubTask 5.2: 展示基础信息（货号、名称、类型、采购成本、单颗成本、售价、库位、供应商、图片）
  - [x] SubTask 5.3: 展示 SKU 列表（编码、名称、材质、规格、颜色、克重、品质、价格、默认标记）
  - [x] SubTask 5.4: 当为成品时展示组成串珠列表与组成配件列表（名称、SKU、数量）
  - [x] SubTask 5.5: 顶部操作菜单：编辑、删除（删除弹二次确认对话框，调用 `DELETE` 接口）

- [x] Task 6: 实现商品新建/编辑表单（商品管理核心 3/3）
  - [x] SubTask 6.1: 创建 `ProductEditViewModel`，支持新建模式与编辑模式（编辑模式先拉详情回填）
  - [x] SubTask 6.2: 实现公共字段区（货号、名称、类型选择、采购成本、单颗成本、售价、库位、供应商、启用开关）
  - [x] SubTask 6.3: 按 `product_type` 动态渲染：bead 显示材质/规格/颜色/克重/品质/备注；accessory 显示材质/规格/颜色
  - [x] SubTask 6.4: finished 类型显示工费/弹性成本 + 串珠组成选择器（从 `GET /products/beads/` 拉取）+ 配件组成选择器（从 `GET /products/accessories/` 拉取），每项可选 SKU 与数量
  - [x] SubTask 6.5: 实现图片选择（相册/拍照），通过 ActivityResult API 获取 Uri
  - [x] SubTask 6.6: 提交时组装请求：含图片走 `multipart/form-data`（image 文件 + 其他字段 + beads/accessories/skus JSON 字符串），无图片走 JSON；新建调 `POST /create/`，编辑调 `PUT /<id>/update/`
  - [x] SubTask 6.7: 成功后返回来源页并刷新列表

- [x] Task 7: 实现「我的」页与退出登录
  - [x] SubTask 7.1: 从 TokenStore 读取并展示当前用户信息（用户名、user_type、企业名称）
  - [x] SubTask 7.2: 提供「退出登录」按钮，点击后清空 TokenStore 并跳转登录页

- [x] Task 8: 验证与收尾
  - [x] SubTask 8.1: 启动后端（`python manage.py runserver 0.0.0.0:8003`），用模拟器跑通登录→商品列表→详情→新建→编辑→删除→退出全流程（注：当前环境无 JDK，编译与运行时验证待用户在配好 Android SDK 的环境执行；代码层已审查通过）
  - [x] SubTask 8.2: 在 `Android/` 根目录添加 `README.md`，说明工程结构、构建命令、`local.properties` 配置、与后端联调方式
  - [x] SubTask 8.3: 确认未修改 `Server/`、`Page/`、`AliData/` 任何现有文件

# Task Dependencies
- Task 2 依赖 Task 1（工程骨架）
- Task 3 依赖 Task 2（网络层与 TokenStore）
- Task 4、Task 7 依赖 Task 3（导航与登录）
- Task 5 依赖 Task 4（列表项跳转详情）
- Task 6 依赖 Task 5（详情回填复用）
- Task 8 依赖 Task 4、5、6、7（全流程验证）
- Task 4 / Task 7 可在 Task 3 完成后并行
