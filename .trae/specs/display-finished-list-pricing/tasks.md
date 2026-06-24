# Tasks

- [x] Task 1: 修改 ProductCard，对成品显示成本、利润、利润率
  - [x] SubTask 1.1: 在售价行增加成本展示（`¥${product.cost_price}`），成品类型显示
  - [x] SubTask 1.2: 新增利润计算（`selling_price - cost_price`）和利润率计算（`(selling_price - cost_price) / selling_price * 100`，售价为0时显示"-"），仅成品类型显示
  - [x] SubTask 1.3: 利润率颜色：≥30% 绿色、≥15% 橙色、<15% 红色；利润颜色：≥0 绿色、<0 红色
  - [x] SubTask 1.4: 调整布局，使成本/售价/利润/利润率在卡片内排列整齐，不溢出

- [x] Task 2: 编译验证
  - [x] SubTask 2.1: 执行 `./gradlew assembleDebug` 确认无编译错误

- [x] Task 3: 安装到手机并验证
  - [x] SubTask 3.1: adb install 安装 APK
  - [x] SubTask 3.2: 验证成品卡片显示成本、售价、利润、利润率
  - [x] SubTask 3.3: 验证串珠/配件卡片不显示利润/利润率
  - [x] SubTask 3.4: 验证利润率颜色正确

# Task Dependencies
- Task 2 依赖 Task 1
- Task 3 依赖 Task 2
