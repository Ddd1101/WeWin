# 串珠列表条目展开 SKU Spec

## Why
Android 商品列表的串珠筛选视图当前每张卡片只显示商品大类信息（货号、名称、图片、规格等），用户若要查看该串珠下各 SKU 的具体参数（采购成本、成本价、克重、品质等级、售价、库位、供应商、备注等），必须进入详情页。同一大类的多个 SKU 在列表层不可见，移动端核对多 SKU 参数效率低。

## What Changes
- 修改 Android `ProductListScreen.kt` 的 `ProductCard`：当商品类型为 `bead`（串珠）时，卡片支持点击展开/收起
- 展开后在该卡片下方以列表形式显示该商品的所有 SKU，每个 SKU 行展示关键参数（SKU 编码/名称、规格、颜色、克重、采购成本、成本价、售价、品质等级、库位、供应商、备注、是否默认、是否启用）
- 串珠卡片增加一个展开指示图标（展开/收起箭头），点击卡片主体切换展开状态
- SKU 数据来源：
  - 优先使用 `ProductDto.skus`（若列表 API 已返回则直接展示）
  - 若 `skus` 为空，则首次展开时调用 `getProductSkus(id)` 懒加载并缓存到 ViewModel 状态
- 不修改后端 API、不修改 DTO、不修改 Vue 前端
- 不改变配件、成品类型卡片的现有交互

## Impact
- Affected specs: add-android-native-app（商品列表 Requirement 受影响）；display-finished-list-pricing（成品卡片价格展示不受影响，本次只动串珠卡片）
- Affected code:
  - 修改：[ProductListScreen.kt](file:///d:/workplace_shop/WeWin/Android/app/src/main/java/com/wewin/app/ui/products/ProductListScreen.kt) — `ProductCard` Composable 及其调用处
  - 修改：[ProductListViewModel.kt](file:///d:/workplace_shop/WeWin/Android/app/src/main/java/com/wewin/app/ui/products/ProductListViewModel.kt) — 新增 SKU 懒加载与缓存逻辑
  - 只读复用：[ApiService.kt](file:///d:/workplace_shop/WeWin/Android/app/src/main/java/com/wewin/app/data/remote/ApiService.kt) — 已有 `getProductSkus(id)`
  - 只读复用：[SkuDto.kt](file:///d:/workplace_shop/WeWin/Android/app/src/main/java/com/wewin/app/data/remote/dto/SkuDto.kt) — 已有全部参数字段
  - 只读复用：[ProductDto.kt](file:///d:/workplace_shop/WeWin/Android/app/src/main/java/com/wewin/app/data/remote/dto/ProductDto.kt) — 已有 `skus: List<SkuDto>`
  - 不改动：`Server/`、`Page/`、其他 Android 文件

## ADDED Requirements

### Requirement: 串珠卡片展开 SKU 列表
Android 商品列表在串珠筛选视图下，每张串珠卡片 SHALL 支持点击展开，展开后在卡片内部显示该商品的所有 SKU 及其参数，便于移动端快速核对多 SKU 信息。

#### Scenario: 串珠卡片显示展开指示
- **WHEN** 用户在商品列表筛选"串珠"类型
- **THEN** 每张串珠卡片右下角（或右侧）显示一个展开指示图标（如向下箭头），表明该卡片可展开

#### Scenario: 点击展开 SKU 列表
- **WHEN** 用户点击某张串珠卡片的可展开区域
- **THEN** 该卡片下方展开一个 SKU 列表区域，显示该商品的所有 SKU
- **AND** 展开指示图标变为收起状态（如向上箭头）

#### Scenario: 再次点击收起
- **WHEN** 用户在已展开的串珠卡片上再次点击
- **THEN** SKU 列表区域收起，卡片恢复到未展开状态
- **AND** 展开指示图标恢复为展开状态

#### Scenario: SKU 参数展示
- **WHEN** 串珠卡片处于展开状态
- **THEN** 每个 SKU 以一行（或多行紧凑布局）展示以下参数：SKU 编码/名称、规格(size)、颜色(color)、克重(weight)、采购成本(purchase_cost)、成本价(cost_price)、售价(selling_price)、品质等级(quality_level)、库位(location)、供应商(supplier)、备注(remark)、是否默认(is_default)、是否启用(is_active)
- **AND** 默认 SKU 有视觉标识（如"默认"标签或高亮边框）

#### Scenario: SKU 数据懒加载
- **WHEN** 用户首次展开某串珠卡片，且该商品 `ProductDto.skus` 为空
- **THEN** 触发调用 `getProductSkus(id)` 获取 SKU 列表
- **AND** 加载期间显示加载中状态（如小尺寸 CircularProgressIndicator）
- **AND** 加载完成后展示 SKU 列表，并将结果缓存，后续展开不再重复请求

#### Scenario: SKU 加载失败
- **WHEN** `getProductSkus(id)` 调用失败（网络错误或非 2xx）
- **THEN** 展开区域显示错误提示与"重试"按钮，点击重试重新请求

#### Scenario: 无 SKU 时显示空状态
- **WHEN** 串珠卡片展开后该商品没有任何 SKU
- **THEN** 展开区域显示"暂无 SKU"提示文案

#### Scenario: 多卡片独立展开
- **WHEN** 用户同时展开多张串珠卡片
- **THEN** 每张卡片的展开状态相互独立，展开一张不会自动收起另一张

## MODIFIED Requirements

### Requirement: 商品列表与筛选
系统 SHALL 提供商品列表页，串珠类型卡片在原有信息基础上增加"点击展开 SKU 列表"的交互；配件、成品类型卡片保持原有交互不变。
