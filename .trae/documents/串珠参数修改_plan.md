
# 串珠参数修改计划

## 需求说明
1. 价格单位修改为"元/克"
2. 新增单颗克重参数
3. 设置品质等级（1-10）
4. 增加备注输入
5. 这些信息只体现在串珠的下拉框中（成品详情页的串珠部分）

## 实施步骤

### 1. 修改后端模型 (Server/store/models.py)
- 在 `Bead` 模型中添加新字段：
  - `weight`：单颗克重 (DecimalField)
  - `quality_level`：品质等级 (IntegerField, 限制1-10)
  - `remark`：备注 (TextField, 允许为空)

### 2. 生成并执行数据库迁移
- 运行 `python manage.py makemigrations store`
- 运行 `python manage.py migrate store`

### 3. 修改后端视图 (Server/store/views.py)
- 更新 `get_products` 和 `get_product_detail`：在返回串珠信息时包含新增字段
- 更新 `create_product` 和 `update_product`：处理新增字段的保存

### 4. 修改前端页面 (Page/src/views/Products.vue)
- 更新串珠表单：在添加/编辑串珠时新增字段输入
- 更新成品详情展开部分：在显示串珠组成时展示新增字段
- 更新成本计算逻辑：考虑克重信息进行成本计算
- 添加相应的样式调整

## 修改文件清单
1. `Server/store/models.py`
2. `Server/store/views.py`
3. `Page/src/views/Products.vue`

## 注意事项
- 确保新增字段有合理的默认值
- 品质等级限制在 1-10 之间
- 备注字段允许为空
- 价格单位的修改主要是 UI 上的变化，数据结构保持不变
