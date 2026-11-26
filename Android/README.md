# WeWin Android App

WeWin 的 Kotlin + Jetpack Compose 原生客户端，复用 Django API，当前覆盖商品管理和个人信息。生产 API 使用统一 HTTPS 入口，图片经阿里云缓存读取 N1 原文件。

## 功能与代码入口

| 功能 | 入口 |
| --- | --- |
| 登录、会话持久化与过期处理 | `ui/login/`、`data/local/TokenStore.kt`、认证拦截器 |
| 商品筛选、服务端搜索与分页 | `ProductListScreen.kt`、`ProductListViewModel.kt` |
| 基础信息、SKU、童装与成品详情 | `ProductDetailScreen.kt`、`ProductDetailViewModel.kt` |
| 四种商品的新建和编辑、图片选择及上传 | `ProductEditScreen.kt`、`ProductEditViewModel.kt` |
| 童装尺码成本与售价 | 编辑页的尺码行，数字尺码和英文尺码均支持 |
| 成品 BOM 与克价模拟 | 材料/SKU 搜索选择、数量和工费；详情页提供本地模拟 |
| 删除确认与材料引用保护 | 详情页删除入口，使用后端 BOM 保护规则 |
| 个人信息、所属企业和退出登录 | `ui/profile/ProfileScreen.kt` |

`data/remote/ApiService.kt` 定义接口；`RetrofitClient.kt` 配置 HTTPS 与超时；`dto/` 对应后端数据。仓库根目录 [AGENTS.md](../AGENTS.md) 和 [README.md](../README.md) 提供整体架构。

原生 App 当前未提供订单、客户报价等独立页面，这些功能使用 Web 后台。童装在原生端以商品与尺码表单查看/编辑，不是 Web Handsontable 的整表界面。

## 构建与安装

需要 JDK 17、Android SDK 34、Gradle Wrapper 8.5。API 地址优先顺序：Gradle `-PAPI_BASE_URL`、环境变量 `WEWIN_API_BASE_URL`、Android 根目录 `local.properties` 的 `API_BASE_URL`，默认 `https://47.250.165.79`。SDK 路径通过 `ANDROID_HOME` 或根目录 `local.properties` 的 `sdk.dir` 指定。

```bash
# 从仓库根目录运行；用实际 SDK 路径替换占位路径
ANDROID_HOME=/path/to/android-sdk bash Android/gradlew -p Android \
  -PAPI_BASE_URL=https://47.250.165.79 assembleDebug

adb devices -l
adb -s <serial> install -r Android/app/build/outputs/apk/debug/app-debug.apk
adb -s <serial> shell am start -n com.wewin.app/.MainActivity
```

开发时可显式指定模拟器 `http://10.0.2.2:8003` 或局域网后端。生产客户端只连接 HTTPS443，不直接访问 Gunicorn8003 或 N1 私有媒体端口。网络与存储部署见 [N1-MEDIA.md](../deploy/N1-MEDIA.md)。

## 编辑和错误处理

- 货号和类型在编辑已有商品时固定。成本、售价及重量须为有效非负数字；材料数量须为正整数。
- 编辑串珠/配件基本信息会同步默认 SKU，同时保留其他 SKU 的 ID 和数据。童装按尺码行保存成本和售价。
- 图片在 IO 线程复制到有上限的临时文件后上传，读取失败会报错，提交完成或失败后清理暂存。取消选择会保留原图，移除操作需要保存。
- 搜索查询整个企业可见数据，先筛选再分页。切换筛选取消旧请求并阻止旧结果覆盖；从编辑或详情返回列表时刷新。
- 错误密码保留登录页和错误提示；业务401清除本地会话并返回登录。网络失败允许重试，不自动重放写入。
- Debug 网络日志只记录 BASIC 请求信息，Release关闭网络日志；不输出登录正文、密码或 Token。

## 真机验证

使用 `P0110`（Android 17 / API37）验证当前 HTTPS 构建。详细范围、发现的问题、修复与清理结果见 [真机验证记录](../docs/android-device-validation-2026-11-26.md)。APK为调试构建，正式签名发布另行配置。
