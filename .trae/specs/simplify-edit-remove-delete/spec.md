# 简化商品编辑页并移除删除功能 Spec

## Why
Android 原生 App 的商品编辑页当前包含大量字段编辑能力（货号、名称、价格、材质、规格、颜色、克重、品质、工费、弹性成本、串珠/配件组成等），移动端维护这些字段体验不佳，且存在误改风险。同时商品删除入口（详情页 TopAppBar 删除按钮 + 确认对话框）在移动端容易误触。用户决定：移动端编辑页仅保留图片上传能力，其他字段编辑交由 PC/Web 端处理；同时移除所有删除入口（详情页商品删除 + 编辑页成品 BOM 子项删除）。

## What Changes
- **编辑页（ProductEditScreen.kt）**：移除 `CommonFieldsCard`、`BeadFieldsCard`、`AccessoryFieldsCard`、`FinishedFieldsCard` 四个字段卡片及其全部子组件（`BeadComponentRow`、`AccessoryComponentRow`），仅保留 `ImagePickerSection`（图片选择/预览）和保存按钮
- **编辑页 ViewModel（ProductEditViewModel.kt）**：保留图片上传与提交逻辑；提交时除图片外其他字段沿用回填的初始值（后端 update 接口接收全量字段，未改动的字段原样回传）
- **详情页（ProductDetailScreen.kt）**：移除 TopAppBar 的删除图标按钮、删除确认对话框（`AlertDialog`）、`showDeleteDialog` 状态、`deleteSuccess` 的 `LaunchedEffect` 导航
- **详情页 ViewModel（ProductDetailViewModel.kt）**：移除 `deleteProduct()` 方法及 `isDeleting`、`deleteSuccess` 状态字段
- **不修改**：ApiService 的 `deleteProduct` 端点定义（保留接口，仅 UI 层不再调用）、后端代码、Vue 前端

## Impact
- Affected specs: add-android-native-app（商品详情、新建/编辑、删除三个 Requirement 受影响）
- Affected code:
  - 修改：[ProductEditScreen.kt](file:///d:/workplace_shop/WeWin/Android/app/src/main/java/com/wewin/app/ui/products/ProductEditScreen.kt) — 移除字段卡片，保留图片上传
  - 修改：[ProductDetailScreen.kt](file:///d:/workplace_shop/WeWin/Android/app/src/main/java/com/wewin/app/ui/products/ProductDetailScreen.kt) — 移除删除按钮与对话框
  - 修改：[ProductDetailViewModel.kt](file:///d:/workplace_shop/WeWin/Android/app/src/main/java/com/wewin/app/ui/products/ProductDetailViewModel.kt) — 移除 deleteProduct 及相关状态
  - 可能修改：[ProductEditViewModel.kt](file:///d:/workplace_shop/WeWin/Android/app/src/main/java/com/wewin/app/ui/products/ProductEditViewModel.kt) — 清理不再被 UI 调用的字段更新方法（如 updateCode 等），但保留提交逻辑
  - 不改动：`Server/`、`Page/`、`ApiService.kt`、路由定义

## MODIFIED Requirements

### Requirement: 商品详情
系统 SHALL 提供商品详情页展示商品信息，TopAppBar 仅保留返回与编辑入口，不再提供删除入口。

#### Scenario: 详情页无删除按钮
- **WHEN** 用户打开商品详情页
- **THEN** TopAppBar 仅显示返回按钮和编辑按钮，不显示删除按钮，不弹出删除确认对话框

### Requirement: 新建/编辑商品
系统 SHALL 提供商品编辑页，仅支持图片上传；其他字段（货号、名称、价格、材质、规格、颜色、克重、品质、工费、弹性成本、串珠/配件组成等）不在移动端编辑。新建模式下非图片字段由后端默认值处理；编辑模式下非图片字段保持原值不变。

#### Scenario: 编辑页仅显示图片上传
- **WHEN** 用户从详情页点击编辑或从列表页点击新建
- **THEN** 编辑页仅显示图片选择/预览区域和保存按钮，不显示任何文本输入字段、开关、下拉选择或组成列表

#### Scenario: 编辑模式保存图片
- **WHEN** 用户在编辑页选择新图片并点击保存
- **THEN** 调用 update 接口提交图片，其他字段沿用初始回填值，保存成功后返回详情页

#### Scenario: 新建模式保存图片
- **WHEN** 用户在新建页选择图片并点击保存
- **THEN** 调用 create 接口提交图片，其他字段使用空值/默认值，保存成功后返回列表页

## REMOVED Requirements

### Requirement: 删除商品
**Reason**: 移动端误删风险高，删除操作统一在 PC/Web 端进行
**Migration**: ApiService 的 `deleteProduct` 端点保留，Vue 前端的删除功能不受影响；仅移除 Android UI 层的删除入口与调用
