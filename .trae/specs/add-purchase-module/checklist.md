# 采购模块验收检查清单

## 后端模型与迁移
- [x] `purchase` app 已加入 `INSTALLED_APPS`，`api/purchase/` 路由已挂载到 `wewin/urls.py`
- [x] `PurchaseList` 模型包含字段：`company`、`created_by`、`assignee`、`title`、`status`、`planned_date`、`notes`、`created_at`、`updated_at`，`db_table='purchase_list'`
- [x] `PurchaseItem` 模型包含字段：`purchase_list`、`product`、`sku`、`product_type`、`product_name`、`sku_code`、`quantity`、`unit`、`unit_price`、`supplier`、`location`、`quality_level`、`material`、`size`、`color`、`remark`、`status`、`purchased_quantity`、`created_at`、`updated_at`，`db_table='purchase_item'`
- [x] `PurchaseListStatus`（PENDING/IN_PROGRESS/COMPLETED）与 `PurchaseItemStatus`（PENDING/PARTIALLY_PURCHASED/PURCHASED）枚举已定义
- [x] `makemigrations purchase` 与 `migrate` 执行成功，数据库表已创建

## 后端 API
- [x] `GET api/purchase/lists/` 支持 `status`、`assignee_scope`、`page`/`page_size` 参数，返回分页结构
- [x] `POST api/purchase/lists/create/` 可在单次请求中创建清单 + 多个采购项（事务保证）
- [x] `GET api/purchase/lists/<id>/` 返回清单 + 所有采购项完整字段
- [x] `PUT api/purchase/lists/<id>/update/` 仅创建人可调用，非创建人返回 403
- [x] `POST api/purchase/items/<id>/mark-purchased/` 将状态置为 PURCHASED 且 `purchased_quantity=quantity`；若清单全部完成则清单状态自动 COMPLETED
- [x] `POST api/purchase/items/<id>/mark-partial/` 接收 `purchased_quantity`，状态置为 PARTIALLY_PURCHASED；清单 PENDING → IN_PROGRESS
- [x] `POST api/purchase/items/<id>/carry-over-next-day/` 创建/复用 `planned_date=tomorrow` 且同 assignee 的清单，复制剩余数量为新项，原项不变
- [x] `GET api/purchase/lists/uncompleted/` 返回当前用户相关的未完成清单（供"加入已有清单"）
- [x] `POST api/purchase/lists/<id>/items/add/` 可向已有清单追加单个采购项
- [x] 所有采购 API 通过 JWT 鉴权，按 `company` 隔离（SUPER_ADMIN/SITE_ADMIN 可跨企业）
- [x] 状态更新类接口仅创建人或被指派人可调用，其他同企业员工返回 403

## Android DTO 与 API
- [x] `PurchaseListDto`、`PurchaseItemDto`、`PurchaseListStatus`、`PurchaseItemStatus` 已定义且 `@Serializable`
- [x] `UserBriefDto` 字段与 `api/account/users/` 返回项对齐
- [x] `CreatePurchaseListRequest` 含 `items: List<CreatePurchaseItemRequest>`，可序列化为后端期望的 JSON
- [x] `ApiService.kt` 已追加全部采购相关端点（列表/创建/详情/更新/未完成/追加 item/标记已购买/标记部分/添加到下一日）和 `GET api/account/users/`

## Android 导航与列表页
- [x] 底部导航栏新增第三个 Tab"采购"（`Icons.Filled.ShoppingCart`），点击切换到 `PurchaseListScreen`，原"商品 / 我的"Tab 行为不受影响
- [x] `PurchaseListScreen` 默认展示"指派给我"且非"已完成"的清单
- [x] 状态筛选（全部/待采购/进行中/已完成）与指派维度（我指派的/指派给我的/全部）切换后列表正确刷新
- [x] 列表卡片展示标题、指派人、计划日期、状态 Chip、进度（如 3/5 已购买），点击进入详情
- [x] FAB"新建采购清单"跳转 `PurchaseCreate` 路由

## Android 详情页与状态操作
- [x] `PurchaseDetailScreen` 展示清单基本信息（标题、指派人、计划日期、状态、备注、创建人、创建时间）
- [x] 采购项展示货号/SKU、名称、材质/规格/颜色、数量+单位、单价、供应商、库位、品质、备注、状态 Chip、已购数量
- [x] 被指派人可见操作按钮；非被指派人不可见操作按钮
- [x] "已购买"点击后状态变更为 PURCHASED，按钮消失，列表进度更新
- [x] "已购买部分"点击弹出对话框录入已购数量，提交后状态变更、清单状态按规则流转
- [x] "添加到下一日"点击后 Toast 提示成功，明日清单中可见该项

## Android "加入采购清单"集成
- [x] 串珠列表卡片有"加入采购清单"按钮，点击弹出 `AddToPurchaseSheet` 并预填该 Product + 默认 SKU 信息
- [x] 配件列表卡片有同款按钮
- [x] 串珠商品详情页有"加入采购清单"按钮
- [x] 配件商品详情页有"加入采购清单"按钮
- [x] 成品详情"成品组成"的每个串珠行有"加入采购清单"按钮，预填 `bead_id` + `sku_id`
- [x] 成品详情"成品组成"的每个配件行有"加入采购清单"按钮，预填 `accessory_id` + `sku_id`
- [x] 弹窗内"新建清单 / 加入已有清单"切换正常，指派人选择器从 `api/account/users/` 加载
- [x] 弹窗内数量/单位/单价默认填充（串珠克/克价，配件件/成本价）且可手动修改
- [x] 提交成功后 Toast 提示并关闭弹窗，不打断商品浏览流程

## 端到端联调
- [x] 从串珠列表加入采购清单并指派给某员工，被指派员工登录后列表可见
- [x] 从成品详情组成项加入采购清单，SKU 字段正确预填
- [x] 被指派员工可执行已购买/已购买部分/添加到下一日三种操作
- [x] 清单状态自动流转：部分购买 → 进行中；全部已购买 → 已完成
- [x] 企业隔离生效：A 企业用户不可见 B 企业的采购清单
- [x] 权限控制生效：非创建人/非被指派人不可修改状态（返回 403）
- [x] Release APK 编译签名安装成功，真机全流程跑通

## 非功能
- [x] 后端视图沿用 `customer` app 的 `authenticate_jwt` 模式，未引入 DRF serializers
- [x] Android ViewModel 沿用 `ProductListViewModel` 的 StateFlow + UiState + `parseError` 模式
- [x] 新增代码不修改 `expand-bead-sku-in-list` / `display-finished-bead-pricing` 既有逻辑
- [x] 无图片上传需求，未引入 multipart 处理
