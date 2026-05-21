# 商品管理企业权限控制 - 实现计划

## [ ] 任务 1: 全面审核现有权限控制实现
- **优先级**: P0
- **依赖**: 无
- **描述**: 
  - 仔细阅读所有商品相关视图函数的权限检查逻辑
  - 验证权限检查是否覆盖所有场景
  - 标记潜在的漏洞或不一致之处
- **验收标准覆盖**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6
- **测试需求**:
  - 人工评审: 代码走查清单
  - 详细检查每个 API 的权限逻辑
- **注意事项**: 重点关注边缘情况，如用户无所属企业、临时用户等

## [ ] 任务 2: 识别和修复权限控制问题
- **优先级**: P0
- **依赖**: 任务 1
- **描述**:
  - 修复发现的任何权限控制问题
  - 确保权限检查逻辑的一致性
  - 添加缺失的权限检查（如需要）
- **验收标准覆盖**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6
- **测试需求**:
  - 程序验证: 单元测试验证修复后的权限逻辑
- **注意事项**: 保持代码风格与现有代码一致

## [ ] 任务 3: 提取公共权限检查函数
- **优先级**: P1
- **依赖**: 任务 2
- **描述**:
  - 将重复的权限检查逻辑提取为公共辅助函数
  - 提高代码复用性和可维护性
- **验收标准覆盖**: NFR-2, NFR-3
- **测试需求**:
  - 人工评审: 代码质量检查
- **注意事项**: 保持向后兼容，不改变现有行为

## [ ] 任务 4: 创建集成测试用例
- **优先级**: P0
- **依赖**: 任务 2
- **描述**:
  - 为每个验收标准创建对应的集成测试
  - 测试各种用户角色的权限边界
  - 验证跨企业数据隔离
- **验收标准覆盖**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6
- **测试需求**:
  - 程序验证: 完整的集成测试套件
- **注意事项**: 测试要覆盖各种边缘情况

## [ ] 任务 5: 运行测试并验证
- **优先级**: P0
- **依赖**: 任务 3, 4
- **描述**:
  - 运行所有测试用例
  - 确保所有验收标准通过
  - 记录测试结果
- **验收标准覆盖**: 所有
- **测试需求**:
  - 程序验证: 所有测试通过
- **注意事项**: 无

## 关键实现细节

### 现有权限检查逻辑分析

#### 1. get_products (获取商品列表) - 已实现 ✅
```python
# 第 855-992 行
products = []
if current_user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
    products = Product.objects.all()
elif current_user.user_type in [UserType.ENTERPRISE_LEADER, UserType.ENTERPRISE_ADMIN, UserType.ENTERPRISE_USER]:
    if current_user.company:
        products = Product.objects.filter(company=current_user.company)
```

#### 2. get_product_detail (获取商品详情) - 已实现 ✅
```python
# 第 1453-1569 行
has_permission = False
if current_user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
    has_permission = True
elif current_user.user_type in [UserType.ENTERPRISE_LEADER, UserType.ENTERPRISE_ADMIN, UserType.ENTERPRISE_USER]:
    if current_user.company == product.company:
        has_permission = True
```

#### 3. create_product (创建商品) - 已实现 ✅
```python
# 第 995-1188 行
has_permission = False
if current_user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
    has_permission = True
elif current_user.user_type in [UserType.ENTERPRISE_LEADER, UserType.ENTERPRISE_ADMIN]:
    if current_user.company:
        has_permission = True
```

#### 4. update_product (更新商品) - 已实现 ✅
```python
# 第 1191-1410 行
has_permission = False
if current_user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
    has_permission = True
elif current_user.user_type in [UserType.ENTERPRISE_LEADER, UserType.ENTERPRISE_ADMIN]:
    if current_user.company == product.company:
        has_permission = True
```

#### 5. delete_product (删除商品) - 已实现 ✅
```python
# 第 1413-1449 行
has_permission = False
if current_user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
    has_permission = True
elif current_user.user_type == UserType.ENTERPRISE_LEADER:
    if current_user.company == product.company:
        has_permission = True
```

#### 6. get_beads 和 get_accessories - 已实现 ✅
```python
# 第 1573-1664 行
# 都已实现企业过滤逻辑
```

### 潜在改进点
1. 将重复的权限检查逻辑提取为公共辅助函数
2. 添加临时用户的显式处理
3. 添加更详细的测试用例
