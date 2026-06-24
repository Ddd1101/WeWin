# 成品详情页克价模拟按钮 Spec

## Why
网页版 Page 下商品管理模块中，手串成品条目有"模拟"按钮，支持调整串珠克价和配件单价来实时模拟成本、利润和利润率变化。手机端成品详情页目前缺少此能力，用户无法在移动端进行克价模拟试算。

## What Changes
- 在手机端成品详情页（ProductDetailScreen.kt）的成品（product_type == "finished"）页面中新增"克价模拟"按钮
- 点击按钮弹出底部表单（BottomSheet）/对话框，展示当前成品的串珠和配件组成，允许用户调整：
  - 串珠：新克价（基于 bead_weight 克重计算新成本）
  - 配件：新单价（按件计算新成本）
- 实时计算并展示：原成本、新成本、成本变动、原利润、新利润、原利润率、新利润率
- 提供"重置"按钮恢复原值，"关闭"按钮退出模拟
- 颜色提示：新成本高于原成本显示红色，否则绿色；新利润率≥30%绿色、≥15%橙色、否则红色

## Impact
- Affected specs: 无（新增独立功能）
- Affected code:
  - `Android/app/src/main/java/com/wewin/app/ui/products/ProductDetailScreen.kt`（新增模拟按钮入口 + 模拟弹窗 UI + 计算逻辑）
  - 复用现有 DTO：`FinishedDto`、`FinishedBeadItemDto`、`FinishedAccessoryItemDto`、`ProductDto`（无需修改 DTO）

## ADDED Requirements

### Requirement: 成品详情页克价模拟按钮
系统 SHALL 在成品（product_type == "finished"）详情页中显示"克价模拟"按钮，点击后打开模拟弹窗。

#### Scenario: 非成品类型不显示按钮
- **WHEN** 商品类型为 bead / accessory / 其他
- **THEN** 详情页不显示"克价模拟"按钮

#### Scenario: 成品类型显示按钮
- **WHEN** 商品类型为 finished
- **THEN** 详情页显示"克价模拟"按钮（位于 PriceHeroCard 下方或 FinishedInfoCard 内）

### Requirement: 模拟弹窗展示组成明细
系统 SHALL 在模拟弹窗中展示当前成品的串珠和配件组成，并提供可编辑的新克价/新单价输入框。

#### Scenario: 串珠明细展示
- **GIVEN** 成品有串珠组成（finished.beads 非空）
- **THEN** 弹窗展示每个串珠的：名称、数量、克重、原克价、新克价（可编辑）、原小计、新小计
- **AND** 新小计 = 新克价 × 克重 × 数量

#### Scenario: 配件明细展示
- **GIVEN** 成品有配件组成（finished.accessories 非空）
- **THEN** 弹窗展示每个配件的：名称、数量、原单价、新单价（可编辑）、原小计、新小计
- **AND** 新小计 = 新单价 × 数量

#### Scenario: 无组成明细
- **GIVEN** 成品没有串珠和配件
- **THEN** 弹窗显示"无明细"提示

### Requirement: 模拟弹窗实时计算汇总
系统 SHALL 实时计算并展示模拟后的成本与利润指标。

#### Scenario: 汇总指标展示
- **THEN** 弹窗底部展示以下指标：
  - 原成本 = Σ(串珠 bead_cost_price × quantity) + Σ(配件 accessory_cost_price × quantity) + labor_cost + elastic_cost
  - 新成本 = Σ(新克价 × bead_weight × quantity) + Σ(新单价 × quantity) + labor_cost + elastic_cost
  - 成本变动 = 新成本 - 原成本（正数显示 + 前缀）
  - 原利润 = selling_price - 原成本
  - 新利润 = selling_price - 新成本
  - 原利润率 = (selling_price - 原成本) / selling_price × 100%
  - 新利润率 = (selling_price - 新成本) / selling_price × 100%

#### Scenario: 颜色提示
- **WHEN** 新成本 > 原成本
- **THEN** 新成本和成本变动显示红色
- **WHEN** 新成本 ≤ 原成本
- **THEN** 新成本和成本变动显示绿色
- **WHEN** 新利润率 ≥ 30%
- **THEN** 新利润率显示绿色
- **WHEN** 15% ≤ 新利润率 < 30%
- **THEN** 新利润率显示橙色
- **WHEN** 新利润率 < 15%
- **THEN** 新利润率显示红色
- **WHEN** 新利润 < 0
- **THEN** 新利润显示红色
- **WHEN** 新利润 ≥ 0
- **THEN** 新利润显示绿色

### Requirement: 模拟弹窗重置功能
系统 SHALL 提供"重置"按钮，将所有新克价/新单价恢复为原值。

#### Scenario: 点击重置
- **WHEN** 用户修改了部分新克价/新单价后点击"重置"
- **THEN** 所有串珠的新克价恢复为 bead_purchase_cost 原值
- **AND** 所有配件的新单价恢复为 accessory_cost_price 原值
- **AND** 汇总指标重新计算

### Requirement: 模拟弹窗关闭功能
系统 SHALL 提供"关闭"按钮，关闭模拟弹窗且不修改任何后端数据。

#### Scenario: 点击关闭
- **WHEN** 用户点击"关闭"
- **THEN** 弹窗关闭，返回详情页
- **AND** 不向后端发送任何请求（纯前端模拟）
