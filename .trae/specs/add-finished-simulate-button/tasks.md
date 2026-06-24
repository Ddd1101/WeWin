# Tasks

- [x] Task 1: 在 ProductDetailScreen.kt 中新增"克价模拟"按钮入口
  - [x] SubTask 1.1: 在成品详情页（product_type == "finished"）的 PriceHeroCard 下方或 FinishedInfoCard 内添加"克价模拟"按钮
  - [x] SubTask 1.2: 添加模拟弹窗显示状态（remember mutableStateOf 控制）
  - [x] SubTask 1.3: 点击按钮时打开模拟弹窗

- [x] Task 2: 实现模拟弹窗 UI 与状态管理
  - [x] SubTask 2.1: 创建模拟状态数据结构（串珠新克价列表、配件新单价列表的可变状态）
  - [x] SubTask 2.2: 打开弹窗时初始化新克价/新单价为原值
  - [x] SubTask 2.3: 实现串珠明细卡片：名称、数量、克重、原克价、新克价输入框、原小计、新小计
  - [x] SubTask 2.4: 实现配件明细卡片：名称、数量、原单价、新单价输入框、原小计、新小计
  - [x] SubTask 2.5: 处理无串珠和配件时的"无明细"空状态

- [x] Task 3: 实现模拟计算逻辑与汇总展示
  - [x] SubTask 3.1: 计算原成本（基于 DTO 原值）
  - [x] SubTask 3.2: 计算新成本（基于可编辑的新克价/新单价）
  - [x] SubTask 3.3: 计算成本变动、原利润、新利润、原利润率、新利润率
  - [x] SubTask 3.4: 实现汇总区 UI，按 spec 颜色规则展示各项指标
  - [x] SubTask 3.5: 新克价/新单价变化时汇总指标实时更新

- [x] Task 4: 实现重置与关闭功能
  - [x] SubTask 4.1: "重置"按钮将所有新克价/新单价恢复为原值
  - [x] SubTask 4.2: "关闭"按钮关闭弹窗，不发送后端请求

- [x] Task 5: 编译验证与真机验证
  - [x] SubTask 5.1: 执行 Gradle 编译，确保无编译错误
  - [x] SubTask 5.2: 安装 APK 到真机，打开成品详情页，验证模拟按钮显示、弹窗交互、计算正确性、重置/关闭功能

# Task Dependencies
- Task 2 依赖 Task 1（需要按钮入口触发弹窗）
- Task 3 依赖 Task 2（需要弹窗状态与可编辑输入）
- Task 4 依赖 Task 2、Task 3（需要弹窗与状态）
- Task 5 依赖 Task 1-4 全部完成
