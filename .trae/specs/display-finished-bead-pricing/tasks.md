# Tasks

- [x] Task 1: 修改 `FinishedBeadItemRow` Composable，展示克价、单价、小计
  - [x] SubTask 1.1: 将原"成本"标签改为"单价"，值取 `item.bead_cost_price`
  - [x] SubTask 1.2: 新增"克价"展示，值取 `item.bead_purchase_cost`，null 时显示"-"，非空时格式为 `¥xx.xx/g`
  - [x] SubTask 1.3: 新增"小计"展示，值 = `item.bead_cost_price × item.quantity`，格式为 `¥xx.xx`
  - [x] SubTask 1.4: 调整布局使三项价格在行内排列整齐，与现有"货号""SKU"等信息层次清晰

# Task Dependencies
- 无外部依赖，Task 1 为独立 UI 改动
