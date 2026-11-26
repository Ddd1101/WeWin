# 新增童装商品管理 — 实施计划

> 日期：2026-11-23

## 一、Summary（概述）

在现有商品管理体系中新增「童装」商品类型，使商品管理从当前的三种类型（串珠/配件/成品）扩展为四种。童装采用**独立详情表**（OneToOne），字段包含尺码、面料、颜色、季节、性别、年龄段。

---

## 二、Current State Analysis（现状）

### 2.1 商品类型枚举
`Server/store/models/product.py` 的 `ProductType`：
```python
class ProductType(models.TextChoices):
    BEAD = 'bead', '串珠'
    ACCESSORY = 'accessory', '手串配件'
    FINISHED = 'finished', '手串成品'
```

### 2.2 详情表模式
每种类型通过 `OneToOneField(Product, primary_key=True)` 挂详情表：
- `Bead`：material/size/color/weight/quality_level/remark
- `Accessory`：material/size/color
- `FinishedProduct`：labor_cost/elastic_cost + 组成表

### 2.3 视图处理（`store/views/product_views.py`）
`create_product` / `update_product` / `get_products` / `get_product_detail` / `get_product_stats` 均按 `product_type` 用 if/elif 分支处理对应详情表。

### 2.4 前端
- `Page/src/views/products/Products.vue`：3 个 Tab（成品/串珠/配件），硬编码 name
- `Page/src/views/products/ProductFormDialog.vue`：按 `form.product_type` 用 `v-if` 渲染不同表单字段
- 类型列表来自 `getProductTypes` API（遍历 `ProductType.choices`，自动包含新类型）

---

## 三、Proposed Changes（具体改动）

### 3.1 后端模型 — `Server/store/models/product.py`

**① ProductType 新增童装**
```python
class ProductType(models.TextChoices):
    BEAD = 'bead', '串珠'
    ACCESSORY = 'accessory', '手串配件'
    FINISHED = 'finished', '手串成品'
    CHILDREN_CLOTHING = 'children_clothing', '童装'
```

**② 新增 ChildrenClothing 详情表**（放在 FinishedProduct 之后）
```python
class ChildrenClothing(models.Model):
    product = models.OneToOneField(
        Product, on_delete=models.CASCADE, primary_key=True, verbose_name='关联商品'
    )
    fabric = models.CharField(max_length=100, blank=True, null=True, verbose_name='面料')
    size = models.CharField(max_length=50, blank=True, null=True, verbose_name='尺码')
    color = models.CharField(max_length=100, blank=True, null=True, verbose_name='颜色')
    season = models.CharField(max_length=20, blank=True, null=True,
        choices=[('spring','春'),('summer','夏'),('autumn','秋'),('winter','冬')],
        verbose_name='季节')
    gender = models.CharField(max_length=20, blank=True, null=True,
        choices=[('boy','男童'),('girl','女童'),('unisex','中性')],
        verbose_name='性别')
    age_range = models.CharField(max_length=50, blank=True, null=True, verbose_name='年龄段')

    class Meta:
        db_table = 'children_clothing'
        verbose_name = '童装'
        verbose_name_plural = '童装'

    def __str__(self):
        return f'童装: {self.product.name}'
```
> 说明：`size` 用 CharField（童装尺码可能是身高"90/100/110"或字母"S/M/L"），非 IntegerField。`__init__.py` 已用 `from .product import *`，会自动导出，无需改动。

### 3.2 后端视图 — `Server/store/views/product_views.py`

**① get_product_stats**（约第 43-45 行）加：
```python
'children_clothing_count': products.filter(product_type=ProductType.CHILDREN_CLOTHING).count(),
```

**② get_products** 详情查询（约第 140 行 `elif product_type == ProductType.FINISHED` 后）加：
```python
elif product.product_type == ProductType.CHILDREN_CLOTHING:
    try:
        cc = ChildrenClothing.objects.get(product=product)
        product_data['children_clothing'] = {
            'fabric': cc.fabric, 'size': cc.size, 'color': cc.color,
            'season': cc.season, 'gender': cc.gender, 'age_range': cc.age_range,
        }
    except ChildrenClothing.DoesNotExist:
        pass
```

**③ create_product**（约第 369 行 finished 分支后）加：
```python
elif product_type == ProductType.CHILDREN_CLOTHING:
    ChildrenClothing.objects.create(
        product=product,
        fabric=data_dict.get('fabric', ''),
        size=data_dict.get('size', ''),
        color=data_dict.get('color', ''),
        season=data_dict.get('season', ''),
        gender=data_dict.get('gender', ''),
        age_range=data_dict.get('age_range', ''),
    )
```
> 童装成本直接用传入的 `cost_price`（不按克重计算），无需 sync_skus。

**④ update_product**（约第 634 行 finished 分支后）加 children_clothing 分支（update_or_create / get 后更新字段）。

**⑤ get_product_detail**（约第 836 行 finished 分支后）加 children_clothing 分支（返回详情字段）。

**⑥ 顶部 import** 加 `ChildrenClothing`（第 12 行）。

### 3.3 数据库迁移
```bash
cd Server
python manage.py makemigrations store
python manage.py migrate
```
（生成 `children_clothing` 表，新增 `ProductType` choices 不影响表结构。）

### 3.4 前端 — `Page/src/views/products/Products.vue`
在 Tab 区（约第 68 行 accessory tab 后）加：
```html
<el-tab-pane label="童装" name="children_clothing">
  <ProductTable ... />
</el-tab-pane>
```
其余逻辑（activeTab、fetchProducts 传参）已通用，无需改。

### 3.5 前端 — `Page/src/views/products/ProductFormDialog.vue`

**① 表单字段区**（约第 89 行 finished 字段后）加童装字段：
```html
<el-row v-if="form.product_type === 'children_clothing'" :gutter="20">
  <el-col :xs="24" :sm="12">
    <el-form-item label="面料" prop="fabric"><el-input v-model="form.fabric" /></el-form-item>
    <el-form-item label="尺码" prop="size"><el-input v-model="form.size" placeholder="如 90/100/110 或 S/M/L" /></el-form-item>
    <el-form-item label="颜色" prop="color"><el-input v-model="form.color" /></el-form-item>
  </el-col>
  <el-col :xs="24" :sm="12">
    <el-form-item label="季节" prop="season">
      <el-select v-model="form.season" placeholder="选择季节">
        <el-option label="春" value="spring" /><el-option label="夏" value="summer" />
        <el-option label="秋" value="autumn" /><el-option label="冬" value="winter" />
      </el-select>
    </el-form-item>
    <el-form-item label="性别" prop="gender">
      <el-select v-model="form.gender" placeholder="选择性别">
        <el-option label="男童" value="boy" /><el-option label="女童" value="girl" />
        <el-option label="中性" value="unisex" />
      </el-select>
    </el-form-item>
    <el-form-item label="年龄段" prop="age_range"><el-input v-model="form.age_range" placeholder="如 中童(4-6岁)" /></el-form-item>
  </el-col>
</el-row>
```

**② form 初始值**（约第 401 行）加：`fabric/size/color/season/gender/age_range`（空字符串）。

**③ resetForm 初始值**（约第 475 行）同步加这几个字段。

**④ 编辑回填**（openEdit 约第 507 行起）加：
```javascript
fabric: product.children_clothing?.fabric || '',
size: product.children_clothing?.size || '',
color: product.children_clothing?.color || '',
season: product.children_clothing?.season || '',
gender: product.children_clothing?.gender || '',
age_range: product.children_clothing?.age_range || '',
```

**⑤ handleSubmit**（约第 701 行）提交 payload 加：
```javascript
if (form.product_type === 'children_clothing') {
  payload.fabric = form.fabric
  payload.size = form.size
  payload.color = form.color
  payload.season = form.season
  payload.gender = form.gender
  payload.age_range = form.age_range
}
```

### 3.6 前端 — `Page/src/views/components/ProductTable.vue`
当前表格展示通用字段（货号/名称/成本/售价/利润等），童装可沿用通用列，**暂不改动**（童装详情字段不单独加列，避免过度设计）。

---

## 四、Assumptions & Decisions（假设与决策）

1. **童装用独立详情表**（用户已确认），字段为尺码/面料/颜色/季节/性别/年龄段。
2. **尺码用 CharField**（支持身高数字和字母码两种形式），不用 IntegerField。
3. **童装暂不 SKU 化**：尺码作为详情表单值字段（描述文本），多尺码的 SKU 级管理留作后续扩展。
4. **童装成本**：直接用表单传入的 `cost_price`（不按克重计算，与配件一致）。
5. **表名**：`children_clothing`（遵循 `Meta.db_table` 显式指定约定）。
6. 季节/性别用固定 choices（春/夏/秋/冬；男童/女童/中性），面料/尺码/颜色/年龄段为自由文本。

---

## 五、Verification（验证）

1. **后端**：`python manage.py check` 无报错；`makemigrations` 生成迁移；`migrate` 成功建表。
2. **接口**：`GET /api/store/products/types/` 返回包含 `children_clothing`；创建童装商品后 `GET /api/store/products/?product_type=children_clothing` 能查到，详情含面料/尺码/季节等字段。
3. **前端**：`npm run build` 通过；浏览器商品管理页出现「童装」Tab，可新增/编辑童装商品，字段（面料/尺码/颜色/季节/性别/年龄段）正常显示与保存。
4. **回归**：串珠/配件/成品三种类型的新增/编辑/列表/详情不受影响。
