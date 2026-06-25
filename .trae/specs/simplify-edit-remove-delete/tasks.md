# Tasks

- [x] Task 1: 简化 ProductEditScreen，仅保留图片上传
  - [x] SubTask 1.1: 移除 `CommonFieldsCard`、`BeadFieldsCard`、`AccessoryFieldsCard`、`FinishedFieldsCard` 四个 Composable 及其子组件 `BeadComponentRow`、`AccessoryComponentRow`、`FormCard`、`productTypeDisplay`、`ErrorBanner`（如不再使用）
  - [x] SubTask 1.2: 简化 `ProductEditContent`，移除所有字段更新回调参数，仅保留 `onPickImage` 和 `onSubmit`
  - [x] SubTask 1.3: 简化 `ProductEditScreen` 对 `ProductEditContent` 的调用，移除不再需要的回调传递
  - [x] SubTask 1.4: 清理不再使用的 import（Delete、Add、ArrowDropDown、FilterChip、Switch、DropdownMenu 等）

- [x] Task 2: 清理 ProductEditViewModel 中不再被 UI 调用的方法
  - [x] SubTask 2.1: 保留 `setImageUri`、`submit`、`uiState`、初始化加载逻辑
  - [x] SubTask 2.2: 移除不再被 UI 使用的字段更新方法（updateCode、updateName、onProductTypeChange、updatePurchaseCost 等）及 BOM 组件方法（addBeadComponent 等）；若 submit 依赖这些状态字段则保留状态本身，仅移除公开的 update 方法
  - [x] SubTask 2.3: 确保 submit 提交时仍能正确构建 multipart 请求（图片 + 全量字段，未改动的字段用初始值）

- [x] Task 3: 移除 ProductDetailScreen 的删除功能
  - [x] SubTask 3.1: 移除 TopAppBar actions 中的删除 IconButton（第 107-112 行）
  - [x] SubTask 3.2: 移除 `showDeleteDialog` 状态变量（第 78 行）
  - [x] SubTask 3.3: 移除删除确认 `AlertDialog`（第 163-194 行）
  - [x] SubTask 3.4: 移除 `deleteSuccess` 的 `LaunchedEffect` 导航（第 80-84 行）
  - [x] SubTask 3.5: 清理不再使用的 import（Delete、AlertDialog、TextButton 等）

- [x] Task 4: 清理 ProductDetailViewModel 的删除逻辑
  - [x] SubTask 4.1: 移除 `deleteProduct()` 方法（第 80-108 行）
  - [x] SubTask 4.2: 从 `ProductDetailUiState` 移除 `isDeleting` 和 `deleteSuccess` 字段
  - [x] SubTask 4.3: 清理不再使用的 import

- [x] Task 5: 编译验证
  - [x] SubTask 5.1: 执行 `./gradlew assembleDebug` 确认无编译错误

- [x] Task 6: 安装到手机并验证
  - [x] SubTask 6.1: adb install 安装 APK
  - [x] SubTask 6.2: 验证详情页无删除按钮
  - [x] SubTask 6.3: 验证编辑页仅显示图片上传和保存按钮
  - [x] SubTask 6.4: 验证编辑模式选图保存成功

# Task Dependencies
- Task 1、Task 3 可并行
- Task 2 依赖 Task 1（确认哪些方法不再被 UI 调用）
- Task 4 依赖 Task 3
- Task 5 依赖 Task 1-4 全部完成
- Task 6 依赖 Task 5
