# Checklist

## 工程骨架
- [x] `Android/` 目录存在，包含完整 Kotlin + Jetpack Compose 工程（build.gradle.kts / settings.gradle.kts / AndroidManifest.xml）
- [x] `applicationId` 为 `com.wewin.app`，最小 SDK 24，目标 SDK 34
- [x] 依赖包含 Compose BOM、Material3、Retrofit、OkHttp、Coil、DataStore、Coroutines、Navigation Compose、kotlinx-serialization
- [x] `local.properties` 中 `API_BASE_URL` 可被 BuildConfig 读取，未设置时默认 `http://10.0.2.2:8003`
- [x] AndroidManifest 已声明 INTERNET 权限，且允许访问 10.0.2.2（network security config 或 debug cleartext）
- [ ] `./gradlew assembleDebug` 可成功生成 APK

## 网络层与鉴权
- [x] DTO 与后端 JSON 字段一一对应（登录响应、商品列表、商品详情、SKU、成品组成、统计）
- [x] Retrofit `ApiService` 覆盖 `/api/account/login/` 与全部 `/api/store/products/*` 端点
- [x] `AuthInterceptor` 自动为请求注入 `Authorization: Bearer <token>`
- [x] `TokenStore`（DataStore）能持久化保存与读取 Token、用户信息
- [x] 任意接口返回 401 时，清除 Token 并触发跳转登录页

## 登录与导航
- [x] 登录页可输入用户名密码，提交调用 `POST /api/account/login/`
- [x] 登录成功后 Token 与用户信息写入 DataStore，跳转主页
- [x] 登录失败时展示后端返回的 `error` 字段
- [x] 启动时根据本地是否存在 Token 决定起始页
- [x] 主页含底部导航「商品 / 我的」

## 商品列表与统计
- [x] 调用 `GET /api/store/products/` 拉取列表，支持 `product_type` / `is_active` / 关键字筛选
- [x] 类型筛选 Tab：全部 / 串珠 / 配件 / 成品
- [x] 滚动到底部自动加载下一页（page/page_size 分页）
- [x] 列表项展示货号、名称、类型标签、价格、缩略图、启用状态
- [x] 顶部统计卡片调用 `GET /api/store/products/stats/`，展示总数/启用/各类型数量
- [x] 列表项点击跳转详情；FAB 跳转新建

## 商品详情
- [x] 调用 `GET /api/store/products/<id>/detail/` 拉取详情
- [x] 展示基础信息（货号、名称、类型、成本、售价、库位、供应商、图片）
- [x] 展示 SKU 列表（编码、名称、材质、规格、颜色、克重、品质、价格、默认标记）
- [x] finished 类型展示组成串珠列表与组成配件列表（名称、SKU、数量）
- [x] 顶部菜单含「编辑」「删除」，删除前弹二次确认对话框
- [x] 删除调用 `DELETE /api/store/products/<id>/delete/`，成功后返回列表

## 商品新建/编辑
- [x] 新建模式调 `POST /api/store/products/create/`，编辑模式先拉详情回填后调 `PUT /api/store/products/<id>/update/`
- [x] 公共字段：货号、名称、类型、采购成本、单颗成本、售价、库位、供应商、启用开关
- [x] bead 类型动态显示材质/规格/颜色/克重/品质/备注
- [x] accessory 类型动态显示材质/规格/颜色
- [x] finished 类型显示工费/弹性成本 + 串珠组成选择器（拉 `/products/beads/`）+ 配件组成选择器（拉 `/products/accessories/`），每项可选 SKU 与数量
- [x] 支持相册/拍照选择图片
- [x] 含图片时以 `multipart/form-data` 提交（image 文件 + beads/accessories/skus 以 JSON 字符串字段）
- [x] 提交成功后返回来源页并刷新列表

## 我的页
- [x] 展示当前用户信息（用户名、user_type、企业名称）
- [x] 「退出登录」按钮点击后清空 TokenStore 并跳转登录页

## 收尾
- [x] `Android/README.md` 说明工程结构、构建命令、local.properties 配置、与后端联调方式
- [x] 未修改 `Server/`、`Page/`、`AliData/` 任何现有文件
- [ ] 全流程验证通过：登录 → 商品列表 → 详情 → 新建 → 编辑 → 删除 → 退出
