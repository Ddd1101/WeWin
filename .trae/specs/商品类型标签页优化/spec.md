# 商品类型标签页优化 - Product Requirement Document

## Overview
- **Summary**: 将商品管理页面改造为标签页形式，分别为串珠、手串成品、手串配件设置独立的卡片页显示，提供更清晰的商品分类浏览体验
- **Purpose**: 解决当前所有商品混在一起显示的问题，让用户可以更方便地按商品类型浏览和管理
- **Target Users**: 店铺管理人员、商品维护人员

## Goals
- 将商品管理页面改造为标签页布局
- 每个标签页只显示对应类型的商品
- 保持现有功能完整性（筛选、添加、编辑、删除等）
- 优化用户体验，提升操作效率

## Non-Goals (Out of Scope)
- 不改变商品的数据结构
- 不改变商品的添加/编辑逻辑
- 不改变后端API接口
- 不添加新的商品类型

## Background & Context
- 当前商品管理页面将所有类型的商品（串珠、手串成品、配件）混在一个表格中显示
- 用户需要通过筛选功能才能查看特定类型的商品
- 改造为标签页形式后，用户可以更直观地按类型管理商品

## Functional Requirements
- **FR-1**: 商品管理页面顶部显示三个标签页：串珠、手串成品、手串配件
- **FR-2**: 点击标签页时，表格中只显示对应类型的商品
- **FR-3**: 每个标签页保持独立的筛选、分页状态
- **FR-4**: 在每个标签页添加商品时，默认选择对应的商品类型
- **FR-5**: 保持所有现有功能（编辑、删除、展开查看明细等）

## Non-Functional Requirements
- **NFR-1**: 标签页切换响应迅速，无明显延迟
- **NFR-2**: 界面风格与现有页面保持一致
- **NFR-3**: 在不同屏幕尺寸下都有良好的显示效果

## Constraints
- **Technical**: 使用Vue 3 + Element Plus现有组件
- **Business**: 保持现有业务逻辑不变
- **Dependencies**: 依赖现有的后端API接口

## Assumptions
- 商品类型数据结构保持不变
- 现有API接口支持按类型筛选商品
- 用户习惯通过标签页切换来浏览不同类型的内容

## Acceptance Criteria

### AC-1: 标签页显示
- **Given**: 用户进入商品管理页面
- **When**: 页面加载完成
- **Then**: 顶部显示三个标签页：串珠、手串成品、手串配件
- **Verification**: `human-judgment`

### AC-2: 默认显示
- **Given**: 用户首次进入商品管理页面
- **When**: 页面加载
- **Then**: 默认选中第一个标签页（串珠），并显示对应类型的商品
- **Verification**: `human-judgment`

### AC-3: 标签页切换
- **Given**: 用户在某个标签页
- **When**: 点击另一个标签页
- **Then**: 表格内容更新为对应类型的商品，筛选和分页状态重置
- **Verification**: `human-judgment`

### AC-4: 添加商品
- **Given**: 用户在某个标签页
- **When**: 点击"添加商品"按钮
- **Then**: 对话框中的商品类型自动选择为当前标签页对应的类型
- **Verification**: `human-judgment`

### AC-5: 功能保持完整
- **Given**: 用户在任意标签页
- **When**: 执行编辑、删除、查看明细等操作
- **Then**: 所有功能正常工作，与之前保持一致
- **Verification**: `human-judgment`

### AC-6: 筛选功能
- **Given**: 用户在某个标签页
- **When**: 使用筛选功能
- **Then**: 筛选只在当前标签页的商品类型范围内生效
- **Verification**: `human-judgment`

## Open Questions
- 无
