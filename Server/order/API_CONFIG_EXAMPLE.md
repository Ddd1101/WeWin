# 订单数据拉取模块 - API配置示例

## 1. 店铺API配置说明

在Django Admin后台为店铺配置API信息，需要在店铺的 `api_config` 字段中填入以下格式的JSON数据：

### 1688平台配置示例
```json
{
  "app_key": "3527689",
  "app_secret": "Zw5KiCjSnL",
  "access_token": "999d182a-3576-4aee-97c5-8eeebce5e085"
}
```

### 配置字段说明
- `app_key`: 1688开放平台应用的App Key
- `app_secret`: 1688开放平台应用的App Secret
- `access_token`: 店铺授权的Access Token

## 2. 使用管理命令拉取订单

### 拉取所有启用的1688店铺最近7天的订单
```bash
python manage.py pull_orders
```

### 拉取指定店铺最近30天的订单
```bash
python manage.py pull_orders --store-id 1 --days 30
```

### 参数说明
- `--store-id`: 可选，指定店铺ID
- `--days`: 可选，拉取最近几天的订单，默认为7天

## 3. 代码结构说明

```
order/
├── platform_adapters/      # 平台适配器
│   ├── base.py            # 平台适配器基类
│   └── ali_1688.py        # 1688平台适配器
├── industry_adapters/      # 行业适配器
│   ├── base.py            # 行业适配器基类
│   └── crystal_bracelet.py # 水晶手串行业适配器
├── services/               # 服务层
│   ├── adapter_factory.py # 适配器工厂
│   ├── order_processor.py # 订单数据处理器
│   └── order_pull_service.py # 订单拉取服务
└── management/
    └── commands/
        └── pull_orders.py # Django管理命令
```

## 4. 扩展指南

### 添加新平台适配器
1. 在 `platform_adapters/` 目录下创建新的适配器类
2. 继承 `BasePlatformAdapter` 并实现所有抽象方法
3. 在 `AdapterFactory` 中注册新平台

### 添加新行业适配器
1. 在 `industry_adapters/` 目录下创建新的适配器类
2. 继承 `BaseIndustryAdapter` 并实现所有抽象方法
3. 在 `AdapterFactory` 中注册新行业

## 5. 定时任务配置

可以使用Celery或系统cron配置定时任务，例如：

```bash
# 每天凌晨2点拉取所有店铺最近1天的订单
0 2 * * * cd /path/to/Server && python manage.py pull_orders --days 1
```
