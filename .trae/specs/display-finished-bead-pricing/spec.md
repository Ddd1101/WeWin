# 手串成品详情页串珠条目价格展示 Spec

## Why
Android 原生 App 的手串成品详情页中，每条串珠组成条目当前仅显示"成本"（即单价），缺少克价和小计信息。Vue 前端已完整展示克价/单价/小计三列，Android 端信息不一致，用户无法在移动端快速核对单珠成本构成与合计。

## What Changes
- 修改 Android `FinishedBeadItemRow` Composable，在串珠条目中增加显示：
  - **克价**（`bead_purchase_cost`，单位 元/g）
  - **单价**（`bead_cost_price`，将原"成本"标签改为"单价"）
  - **小计**（`bead_cost_price × quantity`，前端计算）
- 不修改后端 API、不修改 DTO、不修改数据模型
- 不修改 Vue 前端（已具备这三项展示）

## Impact
- Affected specs: 无（独立 UI 微调，不影响 add-android-native-app 的其他功能）
- Affected code:
  - 修改：[ProductDetailScreen.kt](file:///d:/workplace_shop/WeWin/Android/app/src/main/java/com/wewin/app/ui/products/ProductDetailScreen.kt) — `FinishedBeadItemRow`（约 line 445-500）
  - 只读复用：[FinishedBeadItemDto.kt](file:///d:/workplace_shop/WeWin/Android/app/src/main/java/com/wewin/app/data/remote/dto/FinishedBeadItemDto.kt) — DTO 已含 `bead_purchase_cost`、`bead_cost_price`、`quantity`，无需改动
  - 不改动：`Server/`、`Page/` 任何文件

## ADDED Requirements

### Requirement: 串珠条目价格展示
Android 手串成品详情页的每条串珠组成条目 SHALL 同时展示克价、单价和小计三项价格信息。

#### Scenario: 三项价格完整展示
- **WHEN** 用户在 Android App 中打开一个手串成品商品详情页
- **THEN** 成品组成卡片中的每条串珠条目显示：克价（元/g）、单价（元）、小计（元），且数值保留两位小数

#### Scenario: 克价缺失时优雅降级
- **WHEN** 某条串珠的 `bead_purchase_cost` 为 null（无 SKU 且商品无采购成本）
- **THEN** 克价显示为"-"，单价和小计仍正常展示

#### Scenario: 小计计算正确
- **WHEN** 串珠条目的单价为 `bead_cost_price`、数量为 `quantity`
- **THEN** 小计 = `bead_cost_price × quantity`，结果保留两位小数
