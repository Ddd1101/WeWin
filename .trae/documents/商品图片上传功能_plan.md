# 商品图片上传功能实施计划

## 1. 需求概述

为商品管理模块添加商品图片上传功能，具体要求：
- 新建商品时可以不强制上传图片
- 支持后续通过编辑页面上传和修改图片
- 在商品列表中显示缩略图

## 2. 代码研究结论

项目架构：
- **后端**: Django 5.2.11 + SQLite
- **前端**: Vue 3 + Element Plus + Vite
- **API 调用**: Axios

现有商品管理模块:
- 数据模型: `Product`、`Bead`、`Accessory`、`FinishedProduct` ([`Server/store/models.py`](file:///d:/workplace_shop/WeWin/Server/store/models.py))
- 后端 API: 完整的 CRUD 操作 ([`Server/store/views.py`](file:///d:/workplace_shop/WeWin/Server/store/views.py))
- 前端界面: 商品管理页面 ([`Page/src/views/Products.vue`](file:///d:/workplace_shop/WeWin/Page/src/views/Products.vue))

现状：项目尚未配置媒体文件服务，也没有图片上传相关功能。

## 3. 需要修改的文件

### 后端修改
1. [`Server/wewin/settings.py`](file:///d:/workplace_shop/WeWin/Server/wewin/settings.py) - 添加媒体文件配置
2. [`Server/wewin/urls.py`](file:///d:/workplace_shop/WeWin/Server/wewin/urls.py) - 添加媒体文件路由
3. [`Server/store/models.py`](file:///d:/workplace_shop/WeWin/Server/store/models.py) - 为 Product 模型添加图片字段
4. [`Server/store/views.py`](file:///d:/workplace_shop/WeWin/Server/store/views.py) - 修改商品相关 API 以支持图片处理
5. [`Server/store/urls.py`](file:///d:/workplace_shop/WeWin/Server/store/urls.py) - 添加图片上传相关路由

### 前端修改
1. [`Page/src/api/index.js`](file:///d:/workplace_shop/WeWin/Page/src/api/index.js) - 添加图片上传 API 方法
2. [`Page/src/views/Products.vue`](file:///d:/workplace_shop/WeWin/Page/src/views/Products.vue) - 完善商品图片上传和展示功能

## 4. 实施步骤

### 步骤 1: 后端 - 配置媒体文件服务
- 在 `settings.py` 中添加 `MEDIA_URL` 和 `MEDIA_ROOT` 配置
- 在 `urls.py` 中添加媒体文件服务路由

### 步骤 2: 后端 - 数据模型更新
- 在 `Product` 模型中添加 `image` 字段（ImageField，可空）
- 创建并执行数据库迁移

### 步骤 3: 后端 - API 更新
- 修改 `get_products`、`get_product_detail` 返回图片URL
- 修改 `create_product`、`update_product` 支持处理图片上传
- 添加图片上传专用 API（可选）

### 步骤 4: 前端 - API 封装
- 在 `api/index.js` 中添加图片上传相关方法封装

### 步骤 5: 前端 - 界面更新
- 在商品列表中添加缩略图显示列
- 在商品添加/编辑对话框中添加图片上传组件
- 支持图片预览、上传和删除功能

## 5. 技术考虑

- **图片存储**: 使用 Django 的 ImageField，存储在本地 media 目录
- **图片格式**: 支持常见图片格式（jpg、jpeg、png、gif、webp）
- **图片大小限制**: 限制最大文件大小（如 5MB）
- **缩略图**: 在前端通过 CSS 控制显示大小，或使用后端生成缩略图（当前计划采用前端控制）
- **图片访问权限**: 通过 Django 媒体文件服务提供访问
- **CORS 配置**: 已配置 `CORS_ALLOW_ALL_ORIGINS = True`，无需额外修改

## 6. 风险处理

1. **数据库迁移风险**: 在添加字段前备份数据库（SQLite 直接备份 db.sqlite3 文件）
2. **图片上传安全**: 验证文件类型、限制文件大小
3. **图片存储路径**: 使用相对路径，便于部署迁移
4. **前后端数据格式**: 确保图片 URL 的正确传输和解析

## 7. 验收标准

- [ ] 新建商品时可以不选图片
- [ ] 编辑商品时可以上传/修改/删除图片
- [ ] 商品列表正确显示缩略图
- [ ] 图片上传成功后能正确访问
- [ ] 功能在开发环境正常运行
