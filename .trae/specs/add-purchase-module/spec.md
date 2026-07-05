# 采购模块 Spec

## Why

企业员工目前在商品管理模块只能查看串珠、配件、手串成品的成本信息（含 SKU 的采购成本、供应商、库位等），但无法直接将这些需要采购的物料转化为可执行的采购任务并指派给具体采购人员，导致采购流程依赖线下沟通、易遗漏、无追踪。需要一个端到端的采购清单模块，让任何员工都能从商品/SKU 一键加入采购清单并指派，被指派人可在手机上更新采购进度。

## What Changes

### 后端（Django 新建 `purchase` app）
- 新建 `purchase` app，挂载到 `api/purchase/`，加入 `INSTALLED_APPS`
- 新增 `PurchaseList` 模型：采购清单（企业隔离 + 指派人 + 状态 + 计划日期）
- 新增 `PurchaseItem` 模型：采购项（关联 Product/SKU + 数量 + 单位 + 单价 + 采购状态 + 已购数量）
- 新增 `PurchaseListStatus` / `PurchaseItemStatus` 枚举
- 新增采购清单 CRUD + 状态流转 API（函数视图，沿用 `customer` app 的 `authenticate_jwt` 模式）
- 新增"添加到下一日采购清单" API：将指定采购项复制到 `planned_date = 明天` 的采购清单
- 复用已有 `GET api/account/users/` 作为指派人员数据源（无需新增）

### Android 端
- 底部导航栏新增"采购"入口（第三个 Tab，图标 `Icons.Filled.ShoppingCart`）
- 新增 `PurchaseListScreen` + `PurchaseListViewModel`：采购清单列表（按状态筛选、按"我指派的 / 指派给我的 / 全部"分类）
- 新增 `PurchaseDetailScreen` + `PurchaseDetailViewModel`：采购清单详情，含采购项列表与状态操作
- 新增 `PurchaseItemEditScreen`/弹窗：创建采购清单时录入清单信息 + 采购项
- 新增"加入采购清单"入口（底部弹窗 `AddToPurchaseSheet`）：
  - 串珠列表卡片、配件列表卡片点击进入"加入采购清单"
  - 串珠/配件商品详情页提供"加入采购清单"按钮
  - 成品详情页的"成品组成"中每个串珠项、配件项行提供"加入采购清单"按钮
- 新增 DTO：`PurchaseListDto`、`PurchaseItemDto`、`UserBriefDto`、`CreatePurchaseListRequest` 等
- `ApiService.kt` 追加采购相关端点
- `Screen.kt` 追加路由：`PurchaseList`、`PurchaseDetail/{id}`、`PurchaseCreate`

## Impact

- **Affected specs**: 无（全新模块）。与 `expand-bead-sku-in-list`、`display-finished-bead-pricing` 在 UI 集成点有交叉，但不修改其已有逻辑。
- **Affected code (后端)**:
  - `Server/wewin/settings.py`（INSTALLED_APPS 追加 `purchase`）
  - `Server/wewin/urls.py`（追加 `api/purchase/` 路由）
  - 新建 `Server/purchase/`（models/views/urls/apps/migrations/admin）
- **Affected code (Android)**:
  - `Android/.../ui/navigation/Screen.kt`（路由）
  - `Android/.../ui/navigation/MainScaffold.kt`（底部导航第三个 Tab + NavHost 注册）
  - `Android/.../ui/navigation/AppNavGraph.kt`（PurchaseDetail/PurchaseCreate 顶层路由）
  - `Android/.../data/remote/ApiService.kt`（端点）
  - `Android/.../data/remote/dto/`（新增采购 DTO 文件）
  - `Android/.../ui/products/ProductListScreen.kt`（串珠/配件卡片加入口）
  - `Android/.../ui/products/ProductDetailScreen.kt`（详情页 + 成品组成行加入口）
  - 新建 `Android/.../ui/purchase/`（PurchaseListScreen、PurchaseDetailScreen、PurchaseCreateScreen 及对应 ViewModel）

## ADDED Requirements

### Requirement: 采购清单创建
系统 SHALL 允许任何已登录的企业员工从商品管理模块将串珠、配件或手串成品中的串珠/配件项加入采购清单，并在创建时指派给本企业的某位员工。

#### Scenario: 从串珠列表卡片加入采购清单
- **WHEN** 员工在串珠列表页点击某串珠卡片的"加入采购清单"
- **THEN** 弹出底部弹窗，预填该串珠信息（名称、货号、默认 SKU 的采购成本/供应商/库位），员工可录入采购数量、单位、指派人、计划日期、备注后提交
- **AND** 提交成功后该采购清单项归入新建或选定的采购清单

#### Scenario: 从成品详情组成项加入采购清单
- **WHEN** 员工在手串成品详情页的"成品组成"卡片中，点击某个串珠项或配件项行的"加入采购清单"
- **THEN** 弹出底部弹窗，预填该项的 Product/SKU 信息（含 `bead_id`/`accessory_id` + `sku_id`），员工录入数量/指派人等后提交

#### Scenario: 指派给企业员工
- **WHEN** 员工在创建采购清单时打开指派人选择器
- **THEN** 系统通过 `GET api/account/users/` 返回当前用户可见范围内的本企业员工列表供选择

### Requirement: 采购清单查看与筛选
系统 SHALL 提供采购清单列表页，按企业隔离展示，并支持按状态和指派维度筛选。

#### Scenario: 默认查看指派给我的清单
- **WHEN** 被指派员工进入采购清单 Tab
- **THEN** 默认展示"指派给我"且状态非"已完成"的采购清单

#### Scenario: 按状态筛选
- **WHEN** 员工切换状态筛选（全部 / 待采购 / 进行中 / 已完成）
- **THEN** 列表按所选状态过滤

#### Scenario: 按指派维度切换
- **WHEN** 员工切换"我指派的 / 指派给我的 / 全部"
- **THEN** 列表按对应维度过滤

### Requirement: 采购项状态流转
系统 SHALL 允许被指派人更新采购项的采购状态，状态流转为 待采购 → 已购买部分 → 已购买。

#### Scenario: 标记已购买
- **WHEN** 被指派人在采购清单详情页对某采购项点击"已购买"
- **THEN** 该项状态变为"已购买"，`purchased_quantity` 设为 `quantity`，记录更新时间
- **AND** 若清单内所有项均为"已购买"，则清单状态自动变为"已完成"

#### Scenario: 标记已购买部分
- **WHEN** 被指派人对某采购项点击"已购买部分"并录入已购数量
- **THEN** 该项状态变为"已购买部分"，`purchased_quantity` 更新为录入值
- **AND** 清单状态若为"待采购"则自动变为"进行中"

#### Scenario: 添加到下一日采购清单
- **WHEN** 被指派人对某采购项（未完成或部分完成）点击"添加到下一日采购清单"
- **THEN** 系统创建或复用 `planned_date = 明天` 且指派人相同的采购清单
- **AND** 将该项的剩余未购数量（`quantity - purchased_quantity`）作为新采购项复制到该清单
- **AND** 原采购项保持不变（不自动关闭）

### Requirement: 采购清单权限
系统 SHALL 按企业隔离数据，并按角色区分操作权限。

#### Scenario: 企业隔离
- **WHEN** 任何用户访问采购清单 API
- **THEN** 仅返回该用户所属企业的采购清单（SUPER_ADMIN/SITE_ADMIN 可跨企业）

#### Scenario: 创建人权限
- **WHEN** 采购清单创建人请求编辑清单基本信息或取消清单
- **THEN** 系统允许操作

#### Scenario: 被指派人权限
- **WHEN** 被指派人请求更新采购项状态或添加到下一日
- **THEN** 系统允许操作

#### Scenario: 其他员工只读
- **WHEN** 非创建人且非被指派人的同企业员工访问
- **THEN** 仅可查看，不可修改状态

### Requirement: 采购清单详情展示
系统 SHALL 在采购清单详情页展示清单基本信息与所有采购项的完整参数。

#### Scenario: 详情页内容
- **WHEN** 员工点击采购清单列表中的某一项
- **THEN** 展示清单标题、指派人、计划日期、状态、备注、创建人、创建时间
- **AND** 展示每个采购项：货号/SKU 编码、名称、材质/规格/颜色、数量+单位、单价、供应商、库位、品质等级、备注、采购状态、已购数量
- **AND** 被指派人看到状态操作按钮（已购买 / 已购买部分 / 添加到下一日）

## Constraints

- 后端沿用函数视图 + 手工 JWT 解析 + 字典序列化模式（与 `customer` app 一致），不引入 DRF serializers
- 后端 PUT + multipart 不适用本模块（采购清单无图片上传）
- Android 端 ViewModel 模式与 `ProductListViewModel` 保持一致（StateFlow + UiState + `parseError`）
- 新增底部导航 Tab 不破坏现有"商品 / 我的"两个 Tab 的交互
- 从商品模块加入采购清单采用底部弹窗（`ModalBottomSheet`），不跳转页面，避免打断商品浏览流程
- 采购清单创建支持"新建清单"或"加入已有未完成清单"两种模式

## Assumptions

- 复用现有 `GET api/account/users/` 获取企业员工列表，无需新增用户 API
- 采购数量单位为"克"（串珠）或"件"（配件），由前端根据 `product_type` 默认填充，可手动修改
- 单价默认取 SKU 的 `purchase_cost`（串珠克价）或 `cost_price`（配件单价），可手动修改
- "下一日"指 `planned_date = today + 1 day`，按日期聚合清单
- 采购清单不涉及库存扣减（与库存系统解耦），仅记录采购任务
- 暂不支持采购清单的附件上传、多人协作评论（可后续迭代）

## Open Questions

1. 采购清单是否需要"取消/作废"状态？（当前 spec 暂用 待采购/进行中/已完成 三态，未含取消）
2. 是否需要采购清单的搜索功能（按货号/名称/指派人）？（当前 spec 仅做筛选，未含搜索，可在迭代中补充）
3. 采购完成后是否需要记录实际采购单价和供应商（可能与清单预设不同）？（当前 spec 在"已购买部分/已购买"时仅记录已购数量，未强制录入实际单价）
