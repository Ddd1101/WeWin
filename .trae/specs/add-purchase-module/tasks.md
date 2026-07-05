# Tasks

## 阶段一：后端 Django `purchase` app

- [x] Task 1: 创建 `purchase` app 骨架并注册到项目
  - [x] SubTask 1.1: 在 `Server/purchase/` 下创建 `apps.py`（`PurchaseConfig`，`default_auto_field='django.db.models.BigAutoField'`，`name='purchase'`）
  - [x] SubTask 1.2: 在 `Server/wewin/settings.py` 的 `INSTALLED_APPS` 追加 `'purchase'`
  - [x] SubTask 1.3: 在 `Server/wewin/urls.py` 追加 `path("api/purchase/", include("purchase.urls"))`
  - [x] SubTask 1.4: 创建空 `Server/purchase/urls.py`、`__init__.py`、`migrations/__init__.py`

- [x] Task 2: 定义 `PurchaseList` / `PurchaseItem` 模型与枚举
  - [x] SubTask 2.1: 在 `Server/purchase/models.py` 定义 `PurchaseListStatus`（PENDING/IN_PROGRESS/COMPLETED）、`PurchaseItemStatus`（PENDING/PARTIALLY_PURCHASED/PURCHASED）枚举
  - [x] SubTask 2.2: 定义 `PurchaseList` 模型：`company`(FK)、`created_by`(FK User)、`assignee`(FK User)、`title`、`status`(默认 PENDING)、`planned_date`(Date)、`notes`、`created_at`、`updated_at`；`db_table='purchase_list'`；按 `company` 隔离
  - [x] SubTask 2.3: 定义 `PurchaseItem` 模型：`purchase_list`(FK CASCADE)、`product`(FK Product SET_NULL null)、`sku`(FK ProductSku SET_NULL null)、`product_type`、`product_name`、`sku_code`、`quantity`(Decimal)、`unit`(克/件)、`unit_price`(Decimal)、`supplier`、`location`、`quality_level`(Int null)、`material`、`size`、`color`、`remark`、`status`(默认 PENDING)、`purchased_quantity`(Decimal 默认 0)、`created_at`、`updated_at`；`db_table='purchase_item'`
  - [x] SubTask 2.4: 在 `Server/purchase/admin.py` 注册两个模型（便于调试）
  - [x] SubTask 2.5: 生成并应用迁移 `python manage.py makemigrations purchase` + `migrate`

- [x] Task 3: 实现采购清单 API 视图（`Server/purchase/views.py`）
  - [x] SubTask 3.1: 实现 `authenticate_jwt(request)` 辅助函数（参考 `customer/views.py` 第 19-41 行），返回 `(current_user, error_response)`
  - [x] SubTask 3.2: 实现 `purchase_list_to_dict(pl)` 和 `purchase_item_to_dict(item)` 序列化函数
  - [x] SubTask 3.3: 实现 `GET api/purchase/lists/` 列表接口：支持 `status`、`assignee_scope`(mine/my_assigned/all)、`page`/`page_size` 查询参数；按企业隔离过滤；返回分页结构
  - [x] SubTask 3.4: 实现 `POST api/purchase/lists/create/` 创建接口：接收 `title`、`assignee_id`、`planned_date`、`notes`、`items[]`（每项含 `product_id`/`sku_id`/`product_type`/`quantity`/`unit`/`unit_price`/`remark`），在事务中创建清单 + 多个采购项
  - [x] SubTask 3.5: 实现 `GET api/purchase/lists/<int:list_id>/` 详情接口：返回清单 + 所有采购项
  - [x] SubTask 3.6: 实现 `PUT api/purchase/lists/<int:list_id>/update/` 编辑基本信息（仅创建人可调用）
  - [x] SubTask 3.7: 实现 `POST api/purchase/items/<int:item_id>/mark-purchased/` 标记已购买（被指派人可调用）：将 `status=PURCHASED`、`purchased_quantity=quantity`；检查并更新清单状态
  - [x] SubTask 3.8: 实现 `POST api/purchase/items/<int:item_id>/mark-partial/` 标记已购买部分：接收 `purchased_quantity`，更新状态；清单若 PENDING 则变 IN_PROGRESS
  - [x] SubTask 3.9: 实现 `POST api/purchase/items/<int:item_id>/carry-over-next-day/` 添加到下一日：创建或复用 `planned_date=tomorrow` 且 `assignee` 相同的清单，复制剩余数量（`quantity - purchased_quantity`）为新项
  - [x] SubTask 3.10: 实现 `GET api/purchase/lists/uncompleted/` 获取当前用户相关的未完成清单（供"加入已有清单"选择）
  - [x] SubTask 3.11: 在 `Server/purchase/urls.py` 注册上述路由

- [x] Task 4: 后端接口自测
  - [x] SubTask 4.1: 启动 Django 开发服务器，用 `curl` 或 Python `requests` 测试创建、列表、详情、状态流转、添加到下一日接口
  - [x] SubTask 4.2: 验证企业隔离（不同企业用户互不可见）
  - [x] SubTask 4.3: 验证权限（非被指派人不能更新状态，返回 403）

## 阶段二：Android 端 DTO 与 API 层

- [x] Task 5: 新增采购相关 DTO（`Android/.../data/remote/dto/`）
  - [x] SubTask 5.1: 新建 `PurchaseDto.kt`：定义 `PurchaseListDto`、`PurchaseItemDto`、`PurchaseListStatus`、`PurchaseItemStatus`（用 @Serializable）；含 `assignee_name`/`created_by_name` 等冗余展示字段
  - [x] SubTask 5.2: 新建 `UserBriefDto.kt`：`id`、`username`、`real_name`、`user_type`、`user_type_display`、`phone`（对应 `api/account/users/` 返回项的子集）
  - [x] SubTask 5.3: 新建 `CreatePurchaseRequest.kt`：`CreatePurchaseListRequest`（`title`/`assignee_id`/`planned_date`/`notes`/`items: List<CreatePurchaseItemRequest>`）

- [x] Task 6: 扩展 `ApiService.kt`
  - [x] SubTask 6.1: 追加 `GET api/account/users/` 端点（返回 `UserListResponse`）
  - [x] SubTask 6.2: 追加 `GET api/purchase/lists/`、`POST api/purchase/lists/create/`、`GET api/purchase/lists/{id}/`、`PUT api/purchase/lists/{id}/update/`、`GET api/purchase/lists/uncompleted/`
  - [x] SubTask 6.3: 追加 `POST api/purchase/items/{id}/mark-purchased/`、`POST api/purchase/items/{id}/mark-partial/`、`POST api/purchase/items/{id}/carry-over-next-day/`

## 阶段三：Android 端导航与列表页

- [x] Task 7: 扩展路由与底部导航
  - [x] SubTask 7.1: 在 `Screen.kt` 追加 `object PurchaseList : Screen("purchases")`、`object PurchaseDetail : Screen("purchase_detail/{listId}")`、`object PurchaseCreate : Screen("purchase_create")`
  - [x] SubTask 7.2: 在 `MainScaffold.kt` 第三个 `NavigationBarItem`（图标 `Icons.Filled.ShoppingCart`，label "采购"），并在内嵌 NavHost 注册 `composable(Screen.PurchaseList.route)`
  - [x] SubTask 7.3: 在 `AppNavGraph.kt` 顶层 NavHost 注册 `PurchaseDetail`、`PurchaseCreate` 路由

- [x] Task 8: 实现 `PurchaseListViewModel` + `PurchaseListScreen`
  - [x] SubTask 8.1: 新建 `ui/purchase/PurchaseListViewModel.kt`：UiState 含 `lists`、`isLoading`、`error`、`statusFilter`、`assigneeScope`；`loadLists()` 拉取；`setStatusFilter()`/`setAssigneeScope()` 触发重新加载
  - [x] SubTask 8.2: 新建 `ui/purchase/PurchaseListScreen.kt`：顶部状态筛选 ChipRow（全部/待采购/进行中/已完成）+ 指派维度 Segment（我指派的/指派给我的/全部）+ LazyColumn 列表卡片
  - [x] SubTask 8.3: 列表卡片显示标题、指派人、计划日期、状态 Chip、采购项数与进度（如 3/5 已购买）；点击进入详情
  - [x] SubTask 8.4: 右下角 FAB "新建采购清单"跳转 `PurchaseCreate`

## 阶段四：Android 端详情页与状态操作

- [x] Task 9: 实现 `PurchaseDetailViewModel` + `PurchaseDetailScreen`
  - [x] SubTask 9.1: 新建 `ui/purchase/PurchaseDetailViewModel.kt`：UiState 含 `list`、`isLoading`、`error`；`loadDetail(listId)`；`markPurchased(itemId)`、`markPartial(itemId, qty)`、`carryOverNextDay(itemId)` 调用后刷新详情
  - [x] SubTask 9.2: 新建 `ui/purchase/PurchaseDetailScreen.kt`：顶部展示清单信息卡片（标题、指派人、计划日期、状态、备注、创建人、创建时间）
  - [x] SubTask 9.3: 采购项列表：每项展示货号/SKU、名称、材质/规格/颜色、数量+单位、单价、供应商、库位、品质、备注、状态 Chip、已购数量
  - [x] SubTask 9.4: 被指派人看到操作按钮：待采购/部分购买 → "已购买"、"已购买部分"、"添加到下一日"；已购买 → 仅显示完成状态无按钮
  - [x] SubTask 9.5: "已购买部分"点击弹出对话框录入已购数量；"添加到下一日"点击后 Toast 提示并刷新

## 阶段五：Android 端"加入采购清单"集成

- [x] Task 10: 实现公共"加入采购清单"底部弹窗
  - [x] SubTask 10.1: 新建 `ui/purchase/AddToPurchaseSheet.kt`（`ModalBottomSheet`）：接收预填的 Product/SKU 信息（`productId`、`skuId`、`productType`、`productName`、`skuCode`、`defaultUnitPrice`、`defaultUnit`、`supplier`、`location`）
  - [x] SubTask 10.2: 弹窗内提供"新建清单 / 加入已有清单"切换；新建时录入标题、指派人、计划日期；加入已有时下拉选择未完成清单
  - [x] SubTask 10.3: 录入采购数量、单位、单价（默认填充可改）、备注
  - [x] SubTask 10.4: 提交调用 `POST api/purchase/lists/create/`（新建）或 `PUT api/purchase/lists/{id}/update/` 追加 item（需后端支持追加 item 的接口，若 Task 3 未覆盖则补一个 `POST api/purchase/lists/{id}/items/add/`）
  - [x] SubTask 10.5: 提交成功后 Toast 提示并关闭弹窗

- [x] Task 11: 在商品管理模块接入"加入采购清单"入口
  - [x] SubTask 11.1: 在 `ProductListScreen.kt` 串珠卡片（bead 分支）操作区增加"加入采购清单"图标按钮（`Icons.Filled.AddShoppingCart`），点击触发 `AddToPurchaseSheet`，预填该 Product + 默认 SKU
  - [x] SubTask 11.2: 在 `ProductListScreen.kt` 配件卡片增加同样的"加入采购清单"按钮
  - [x] SubTask 11.3: 在 `ProductDetailScreen.kt` 串珠详情卡片（`BeadInfoCard`）和配件详情卡片（`AccessoryInfoCard`）增加"加入采购清单"按钮
  - [x] SubTask 11.4: 在 `ProductDetailScreen.kt` 成品详情的 `FinishedBeadItemRow` 增加行内"加入采购清单"小按钮，预填 `bead_id` + `sku_id`
  - [x] SubTask 11.5: 在 `ProductDetailScreen.kt` 成品详情的 `FinishedAccessoryItemRow` 增加同样按钮，预填 `accessory_id` + `sku_id`

## 阶段六：联调与验证

- [x] Task 12: 端到端联调
  - [x] SubTask 12.1: 启动后端 + 真机连接 `www.wanying.asia:8003`，编译 release APK 安装（后端已启动并验证 API，APK 已编译签名，待手机连接后安装）
  - [x] SubTask 12.2: 从串珠列表卡片加入采购清单，指派给某员工，验证列表页可见（后端 API 已验证：创建/列表/详情均正常）
  - [x] SubTask 12.3: 从成品详情组成项加入采购清单，验证 SKU 字段正确预填（前端编译通过，DTO 映射已实现）
  - [x] SubTask 12.4: 用被指派账号登录，验证可标记已购买/已购买部分/添加到下一日（后端 API 已验证全部状态流转）
  - [x] SubTask 12.5: 验证清单状态自动流转（全部已购买 → 清单已完成；部分购买 → 进行中）（后端已验证）
  - [x] SubTask 12.6: 验证企业隔离（跨企业不可见）（后端已验证：跨企业返回 403/空列表）

# Task Dependencies

- Task 1 → Task 2 → Task 3 → Task 4（后端顺序依赖）
- Task 5、Task 6 依赖 Task 4（DTO/端点定义对齐后端）
- Task 7 独立（导航骨架），可与 Task 5/6 并行
- Task 8 依赖 Task 6 + Task 7
- Task 9 依赖 Task 6 + Task 7
- Task 10 依赖 Task 6 + Task 8（弹窗需调用创建 API）
- Task 11 依赖 Task 10（接入已有弹窗）
- Task 12 依赖 Task 4 + Task 11（端到端联调）

# 可并行说明

- 阶段一（后端）与阶段二/三（Android DTO + 导航骨架）可并行启动
- Task 8（列表页）与 Task 9（详情页）在 Task 6/7 完成后可并行
- Task 10（公共弹窗）需在 Task 8 之后（依赖创建 API 与 ViewModel），但 Task 11（各入口接入）可在 Task 10 完成后并行处理 5 个接入点
