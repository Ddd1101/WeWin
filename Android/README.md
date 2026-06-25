# WeWin Android App

WeWin 电商 ERP 系统的安卓原生客户端，使用 Kotlin + Jetpack Compose 开发，复用 Django 后端 API，优先支持商品管理模块。

## 技术栈
- Kotlin + Jetpack Compose（Material3）
- Retrofit + OkHttp（网络）
- kotlinx-serialization（JSON）
- DataStore Preferences（Token 持久化）
- Coil（图片加载）
- Navigation Compose（路由）
- Coroutines（异步）

## 工程结构
```
Android/
├── build.gradle.kts              # 根构建脚本（声明 AGP/Kotlin 插件版本）
├── settings.gradle.kts           # 工程设置（仓库名、模块）
├── gradle.properties             # Gradle 属性
├── gradlew / gradlew.bat         # Gradle Wrapper 脚本
├── gradle/wrapper/               # Gradle Wrapper 配置（Gradle 8.5）
└── app/
    ├── build.gradle.kts          # 模块构建脚本（依赖、SDK、BuildConfig）
    ├── local.properties.example  # API_BASE_URL 配置示例
    ├── proguard-rules.pro        # ProGuard 规则
    └── src/main/
        ├── AndroidManifest.xml   # 清单（INTERNET 权限、网络安全配置）
        ├── res/
        │   ├── drawable/         # 图标资源
        │   ├── mipmap-anydpi-v26/# 自适应启动图标
        │   ├── values/           # colors / strings / themes
        │   └── xml/
        │       └── network_security_config.xml  # 允许 10.0.2.2 明文 HTTP
        └── java/com/wewin/app/
            ├── MainActivity.kt          # 入口 Activity
            ├── WeWinApp.kt              # Application，初始化 RetrofitClient
            ├── data/
            │   ├── local/
            │   │   ├── TokenStore.kt        # DataStore 持久化 Token 与用户信息
            │   │   └── AuthEventBus.kt      # 401 登出事件总线
            │   └── remote/
            │       ├── ApiService.kt        # Retrofit 接口定义（登录、商品 CRUD）
            │       ├── RetrofitClient.kt    # Retrofit/OkHttp 单例初始化
            │       ├── AuthInterceptor.kt   # 自动注入 Bearer Token
            │       ├── Global401Interceptor.kt  # 401 清 Token 并触发登出
            │       └── dto/                 # 数据传输对象（与后端 JSON 对应）
            │           ├── LoginRequest.kt / LoginResponse.kt
            │           ├── ProductDto.kt / ProductListResponse.kt
            │           ├── ProductStatsDto.kt / ProductTypesDto.kt
            │           ├── BeadDto.kt / AccessoryDto.kt / FinishedDto.kt
            │           ├── SkuDto.kt / SkuListResponse.kt
            │           ├── BeadListDto.kt / AccessoryListDto.kt
            │           ├── FinishedBeadItemDto.kt / FinishedAccessoryItemDto.kt
            │           ├── FinishedComponentRequest.kt  # 成品组成提交结构
            │           ├── MessageResponse.kt / ErrorResponse.kt
            └── ui/
                ├── login/
                │   ├── LoginScreen.kt       # 登录页 UI
                │   └── LoginViewModel.kt    # 登录逻辑
                ├── navigation/
                │   ├── Screen.kt            # 路由定义
                │   ├── AppNavGraph.kt       # 顶层导航图（登录/主页/详情/编辑）
                │   └── MainScaffold.kt      # 主页底部导航（商品/我的）
                ├── products/
                │   ├── ProductListScreen.kt     # 商品列表（统计卡片、筛选、搜索、分页）
                │   ├── ProductListViewModel.kt
                │   ├── ProductDetailScreen.kt   # 商品详情（基础信息/SKU/成品组成）
                │   ├── ProductDetailViewModel.kt
                │   ├── ProductEditScreen.kt     # 新建/编辑（动态表单、图片上传）
                │   └── ProductEditViewModel.kt
                ├── profile/
                │   └── ProfileScreen.kt     # 我的页（用户信息、退出登录）
                └── theme/
                    ├── Color.kt / Theme.kt / Type.kt  # Material3 主题
```

## 环境要求
- Android Studio Hedgehog 或更高
- JDK 17
- Android SDK 34（compileSdk）
- Gradle 8.5（wrapper 已含）

## 配置
1. 复制 `app/local.properties.example` 为 `app/local.properties`（或根目录 `local.properties`）
2. 修改 `API_BASE_URL` 指向后端地址：
   - 模拟器访问宿主机：`http://10.0.2.2:8003`
   - 真机调试：`http://<你的电脑局域网IP>:8003`
3. 确保后端 Django 服务已启动（`cd Server && python manage.py runserver 0.0.0.0:8003`）

## 构建与运行
```bash
# Debug 构建
./gradlew assembleDebug

# 安装到连接的设备/模拟器
./gradlew installDebug
```

或在 Android Studio 中直接打开 `Android/` 目录运行。

## 功能
- 登录（JWT 鉴权，Token 持久化，401 自动登出）
- 商品管理（核心）：
  - 商品列表（类型筛选、搜索、分页、统计卡片）
  - 商品详情（基础信息、SKU、成品组成）
  - 新建/编辑商品（动态表单、成品组成选择、图片上传）
  - 删除商品（二次确认）
- 我的（用户信息、退出登录）

## 与后端联调
- 后端 API 文档见项目根目录 `AGENT.md`
- 商品相关接口前缀：`/api/store/products/`
- 登录接口：`/api/account/login/`
- 所有业务接口需 `Authorization: Bearer <token>` 头
- 图片上传走 multipart/form-data

## 与 Page/android 的关系
`Page/android/` 是 Vue 前端的 Capacitor WebView 包装，与本原生 App 相互独立。本 App 为纯原生实现，体验更流畅，后续可逐步覆盖更多模块。
