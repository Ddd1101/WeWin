# 手串成品详情展示功能实现计划

## 需求概述
商品管理页面，商品类型为手串成品支持点击后展示下拉框，下拉框显示：
1. 组成所需要的串珠和配件，带有缩略图、价格和数量
2. 工费、弹性成本
3. 手串成品的总成本（由上述所有费用总和自动算出）

## 代码库分析
1. **后端模型**：已有的 `FinishedProduct` 模型在 `store/models.py`
2. **后端API**：`store/views.py` 已有商品相关API
3. **前端页面**：`Page/src/views/Products.vue` 已有商品管理页面
4. **前端API**：`Page/src/api/index.js` 已有API调用函数

## 修改计划

### 1. 后端模型修改 (`store/models.py`)
- 在 `FinishedProduct` 模型中添加 `labor_cost`（工费）和 `elastic_cost`（弹性成本）字段
- 类型均为 `DecimalField`

### 2. 后端API修改 (`store/views.py`)
- 修改 `get_products` 函数，返回串珠和配件时包含图片URL和成本价格
- 修改 `get_product_detail` 函数，同样返回完整的组成信息
- 修改 `create_product` 和 `update_product` 函数，支持设置工费和弹性成本

### 3. 前端页面修改 (`Page/src/views/Products.vue`)
- 在商品列表中，为手串成品添加可展开的下拉框
- 下拉框展示：
  - 串珠列表（带缩略图、名称、价格、数量、小计）
  - 配件列表（带缩略图、名称、价格、数量、小计）
  - 工费、弹性成本输入框
  - 总成本自动计算显示
- 添加展开/收起状态管理
- 样式优化

## 实施步骤
1. 修改模型并创建迁移
2. 更新后端API
3. 更新前端页面

## 风险
- 数据库迁移需要正确执行
- 前端需要处理大量数据渲染时的性能
- 浮点数计算精度问题（使用Decimal处理）
