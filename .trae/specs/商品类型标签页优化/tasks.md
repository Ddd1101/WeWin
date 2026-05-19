# 商品类型标签页优化 - The Implementation Plan (Decomposed and Prioritized Task List)

## [ ] Task 1: 添加标签页组件，修改页面布局
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 在商品管理页面顶部添加Element Plus的el-tabs组件
  - 创建三个标签页：串珠、手串成品、手串配件
  - 调整现有布局，将表格放在标签页内容区域中
  - 移除原有的商品类型筛选器（因为已经通过标签页实现）
- **Acceptance Criteria Addressed**: [AC-1, AC-2]
- **Test Requirements**:
  - `human-judgement` TR-1.1: 页面顶部正确显示三个标签页
  - `human-judgement` TR-1.2: 默认选中第一个标签页（串珠）
- **Notes**: 标签页的值可以使用 'bead', 'finished', 'accessory'

## [ ] Task 2: 实现标签页切换时的数据过滤
- **Priority**: P0
- **Depends On**: [Task 1]
- **Description**: 
  - 添加activeTab响应式变量来跟踪当前选中的标签页
  - 修改fetchProducts函数，根据activeTab自动过滤商品类型
  - 标签页切换时，重置分页和筛选条件并重新获取数据
- **Acceptance Criteria Addressed**: [AC-2, AC-3]
- **Test Requirements**:
  - `human-judgement` TR-2.1: 切换标签页时，表格内容正确更新
  - `human-judgement` TR-2.2: 切换标签页时，分页重置为第一页
- **Notes**: activeTab应该与商品类型的值对应

## [ ] Task 3: 修改添加商品功能，默认选择当前标签页类型
- **Priority**: P1
- **Depends On**: [Task 2]
- **Description**: 
  - 修改handleAddProduct函数，根据当前activeTab设置默认的商品类型
  - 确保在对话框中商品类型字段正确显示默认值
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `human-judgement` TR-3.1: 在串珠标签页点击添加，商品类型默认选择串珠
  - `human-judgement` TR-3.2: 在成品标签页点击添加，商品类型默认选择成品
  - `human-judgement` TR-3.3: 在配件标签页点击添加，商品类型默认选择配件
- **Notes**: 需要确保productTypes正确加载后才能匹配

## [ ] Task 4: 优化筛选功能，移除商品类型筛选
- **Priority**: P1
- **Depends On**: [Task 2]
- **Description**: 
  - 从筛选区域移除商品类型的下拉框
  - 保留状态筛选功能
  - 确保筛选和重置功能正常工作
- **Acceptance Criteria Addressed**: [AC-6]
- **Test Requirements**:
  - `human-judgement` TR-4.1: 筛选区域只显示状态筛选
  - `human-judgement` TR-4.2: 状态筛选功能正常工作
  - `human-judgement` TR-4.3: 重置功能正常工作
- **Notes**: 商品类型已经通过标签页固定，不需要再筛选

## [ ] Task 5: 确保所有现有功能正常工作
- **Priority**: P0
- **Depends On**: [Task 3, Task 4]
- **Description**: 
  - 验证编辑功能在所有标签页都正常
  - 验证删除功能在所有标签页都正常
  - 验证成品详情展开功能正常
  - 验证图片上传功能正常
- **Acceptance Criteria Addressed**: [AC-5]
- **Test Requirements**:
  - `human-judgement` TR-5.1: 编辑商品功能正常
  - `human-judgement` TR-5.2: 删除商品功能正常
  - `human-judgement` TR-5.3: 成品详情展开功能正常
  - `human-judgement` TR-5.4: 分页功能正常工作
- **Notes**: 需要全面测试各个功能点
