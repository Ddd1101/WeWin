# 客户模块 - 产品需求文档

## Overview
- **Summary**: 为WeWin电商管理系统增加客户管理模块，包含客户基本信息管理、客户与商品关联、客户商品报价及报价历史功能，并实现基于企业和用户角色的权限控制体系。
- **Purpose**: 帮助企业用户管理客户信息、客户专属商品及报价，提升业务管理效率。
- **Target Users**: 企业负责人、企业管理员、企业普通用户。

## Goals
- 客户信息的增删改查管理
- 基于企业和角色的客户可见性权限控制
- 客户与商品的关联关系管理
- 商品对客户的报价及历史记录管理

## Non-Goals (Out of Scope)
- 不实现客户支付功能
- 不实现客户下单功能
- 不实现客户社交或通讯功能
- 不实现数据迁移或批量导入导出功能

## Background & Context
现有系统已具备企业管理、用户管理、商品管理、订单管理等核心功能，基于此架构扩展客户模块，保持代码风格和技术栈的一致性。使用 Django 后端 + Vue 3 前端，SQLite 数据库。

## Functional Requirements
- **FR-1**: 客户基本信息管理（创建、查看、编辑、删除）
- **FR-2**: 客户权限控制（企业隔离、角色权限、可见性配置）
- **FR-3**: 客户与商品关联配置
- **FR-4**: 客户商品报价管理（当前报价、报价历史）
- **FR-5**: 客户数据查询与列表展示

## Non-Functional Requirements
- **NFR-1**: 响应时间：API响应时间不超过2秒
- **NFR-2**: 数据一致性：企业间数据完全隔离，无越权访问
- **NFR-3**: 可用性：99.9%的功能可用性

## Constraints
- **Technical**: 遵循现有Django项目结构，使用JWT认证
- **Business**: 必须与现有企业用户权限体系对接
- **Dependencies**: 依赖现有的User、Company、Product模型

## Assumptions
- 企业用户已经完成登录认证
- 用户类型识别使用现有的UserType枚举
- 所有API都需要JWT认证
- 数据完全属于创建用户所在的企业

## Acceptance Criteria

### AC-1: 客户创建权限控制
- **Given**: 用户已登录系统
- **When**: 用户尝试创建客户
- **Then**: 仅企业负责人和企业管理员可以成功创建，其他角色返回权限错误
- **Verification**: `programmatic`

### AC-2: 企业数据隔离
- **Given**: 用户已登录并属于企业A
- **When**: 用户访问客户数据
- **Then**: 只能看到企业A的客户，无法访问其他企业的客户
- **Verification**: `programmatic`

### AC-3: 企业负责人权限
- **Given**: 企业负责人已登录
- **When**: 查看客户列表
- **Then**: 可以看到本企业所有客户
- **Verification**: `programmatic`

### AC-4: 企业管理员权限
- **Given**: 企业管理员已登录
- **When**: 查看客户列表
- **Then**: 可以看到自己创建的客户和被授权可见的客户
- **Verification**: `programmatic`

### AC-5: 企业普通用户权限
- **Given**: 企业普通用户已登录
- **When**: 查看客户列表
- **Then**: 只能看到被授权可见的客户
- **Verification**: `programmatic`

### AC-6: 客户商品关联
- **Given**: 用户有权限管理客户
- **When**: 为客户配置关联商品及报价
- **Then**: 系统保存关联关系和报价，并记录报价历史
- **Verification**: `programmatic`

### AC-7: 报价历史记录
- **Given**: 商品对客户的报价发生变更
- **When**: 新报价保存
- **Then**: 历史报价自动添加到报价历史记录中
- **Verification**: `programmatic`

### AC-8: 客户信息CRUD操作
- **Given**: 用户有相应权限
- **When**: 执行客户信息的创建、查看、编辑、删除操作
- **Then**: 操作成功执行，数据正确更新
- **Verification**: `programmatic`

## Open Questions
- [ ] 客户是否需要分类或标签功能？
- [ ] 是否需要客户联系人管理功能？
- [ ] 报价历史需要保留多长时间？
