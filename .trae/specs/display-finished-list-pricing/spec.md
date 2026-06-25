# 成品列表页显示成本、售价、利润、利润率 Spec

## Why
Android 原生 App 的商品列表卡片当前仅显示售价，缺少成本、利润和利润率信息。用户无法在移动端快速了解成品的盈利情况。Vue 桌面端已对成品显示成本/售价/利润/利润率四项，Android 端需对齐。

## What Changes
- 修改 Android `ProductCard` Composable，对成品类型商品在售价行增加显示：成本、利润、利润率
- 利润和利润率在客户端计算（后端不返回）：
  - 利润 = `selling_price - cost_price`
  - 利润率 = `(selling_price - cost_price) / selling_price × 100`，保留 1 位小数
- 利润/利润率带颜色标识：利润率 ≥30% 绿色、≥15% 橙色、<15% 红色；利润 ≥0 绿色、<0 红色
- 非成品类型（串珠/配件）不显示利润/利润率，仅成品显示
- 不修改后端 API、不修改 DTO、不修改 Vue 前端

## Impact
- Affected specs: add-android-native-app（商品列表 Requirement 受影响）
- Affected code:
  - 修改：[ProductListScreen.kt](file:///d:/workplace_shop/WeWin/Android/app/src/main/java/com/wewin/app/ui/products/ProductListScreen.kt) — `ProductCard` Composable（约 line 351-425）
  - 只读复用：[ProductDto.kt](file:///d:/workplace_shop/WeWin/Android/app/src/main/java/com/wewin/app/data/remote/dto/ProductDto.kt) — 已有 `cost_price`、`selling_price`、`product_type` 字段
  - 不改动：`Server/`、`Page/`、其他 Android 文件

## ADDED Requirements

### Requirement: 成品列表卡片价格信息展示
Android 商品列表的成品类型卡片 SHALL 在售价之外，额外显示成本、利润和利润率，便于移动端快速核对盈利情况。

#### Scenario: 成品卡片显示四项价格
- **WHEN** 用户在商品列表浏览成品类型商品
- **THEN** 每张成品卡片显示：成本（¥xx.xx）、售价（¥xx.xx）、利润（¥xx.xx）、利润率（xx.x%），数值保留两位小数（利润率保留一位）

#### Scenario: 利润颜色标识
- **WHEN** 成品卡片的利润率 ≥30%
- **THEN** 利润率文字显示为绿色
- **WHEN** 成品卡片的利润率 ≥15% 且 <30%
- **THEN** 利润率文字显示为橙色
- **WHEN** 成品卡片的利润率 <15%
- **THEN** 利润率文字显示为红色
- **WHEN** 成品卡片的利润 ≥0
- **THEN** 利润文字显示为绿色
- **WHEN** 成品卡片的利润 <0
- **THEN** 利润文字显示为红色

#### Scenario: 售价为零时利润率处理
- **WHEN** 成品的 `selling_price` 为 0
- **THEN** 利润率显示为 "-"，避免除零错误

#### Scenario: 非成品类型不显示利润
- **WHEN** 用户浏览串珠或配件类型商品
- **THEN** 卡片仅显示售价，不显示成本、利润、利润率

## MODIFIED Requirements

### Requirement: 商品列表与筛选
系统 SHALL 提供商品列表页，成品类型卡片在原有售价基础上增加成本、利润、利润率展示；其他类型保持仅显示售价。
