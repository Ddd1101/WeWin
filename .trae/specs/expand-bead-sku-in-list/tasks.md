# Tasks

- [x] Task 1: 在 `ProductListViewModel` 中新增 SKU 懒加载与缓存能力
  - [x] SubTask 1.1: 新增 UI 状态字段，按 productId 维度保存每个商品的 SKU 列表、加载状态（idle/loading/success/error）、错误信息
  - [x] SubTask 1.2: 新增 `loadSkusIfNeeded(productId, existingSkus)` 方法：若 `existingSkus` 非空直接返回；否则检查缓存，未缓存且未在加载中时调用 `apiService.getProductSkus(id)`，更新对应加载状态与结果
  - [x] SubTask 1.3: 暴露 UI 可观察的状态（如 StateFlow 或在现有 UiState 中增加 `skuMap: Map<Int, SkuLoadState>`）

- [x] Task 2: 改造 `ProductListScreen.kt` 的 `ProductCard` 支持串珠展开
  - [x] SubTask 2.1: 为 `ProductCard` 增加 `isExpanded: Boolean`、`onToggleExpand: () -> Unit`、`skuLoadState: SkuLoadState?`、`onRetryLoadSkus: () -> Unit` 参数
  - [x] SubTask 2.2: 仅当 `product.product_type == "bead"` 时显示展开指示图标（向下/向上箭头），点击切换展开状态；配件/成品卡片保持原交互不变
  - [x] SubTask 2.3: 展开时在卡片主体下方渲染 SKU 列表区域：加载中显示 CircularProgressIndicator；失败显示错误提示+重试按钮；空列表显示"暂无 SKU"；成功显示 SKU 参数行
  - [x] SubTask 2.4: 新增 `SkuRow` Composable，紧凑展示单个 SKU 的参数（编码/名称、规格、颜色、克重、采购成本、成本价、售价、品质等级、库位、供应商、备注、默认/启用标签）

- [x] Task 3: 在 `ProductListScreen` 列表渲染处串联展开状态与 ViewModel
  - [x] SubTask 3.1: 在列表级维护一个 `expandedIds: MutableState<Set<Int>>`（或 remember mutableStateListOf），记录当前展开的 productId 集合
  - [x] SubTask 3.2: 渲染 `ProductCard` 时，对 `bead` 类型传入 `isExpanded = expandedIds.contains(product.id)`、`onToggleExpand` 更新集合、`skuLoadState = viewModel.skuMap[product.id]`、`onRetryLoadSkus = { viewModel.loadSkusIfNeeded(...) }`
  - [x] SubTask 3.3: 展开时若需要懒加载，调用 `viewModel.loadSkusIfNeeded(product.id, product.skus)`（在 LaunchedEffect 或 onToggleExpand 回调中触发，避免重复请求）

- [x] Task 4: 编译验证
  - [x] SubTask 4.1: 运行 `.\gradlew.bat :app:assembleDebug`（JAVA_HOME 指向 `D:\AndroidStudio\jbr`）确认编译通过
  - [x] SubTask 4.2: 安装到真机，验证串珠筛选视图下卡片可展开/收起、SKU 参数正确显示、懒加载与重试正常

# Task Dependencies
- Task 2 依赖 Task 1（需要 ViewModel 暴露的 SKU 加载状态类型）
- Task 3 依赖 Task 1 与 Task 2
- Task 4 依赖 Task 3
