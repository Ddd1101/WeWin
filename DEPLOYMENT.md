# WeWin 项目部署说明

## 服务访问地址

- **前端**: http://10.0.8.11:8080 (或 http://服务器IP:8080)
- **后端**: http://10.0.8.11:8003 (或 http://服务器IP:8003)

## 启动和停止服务

### 前端服务

#### 启动前端
```bash
./start_frontend.sh
```

#### 停止前端
```bash
./stop_frontend.sh
```

### 后端服务

#### 启动后端
```bash
./start_backend.sh
```

#### 停止后端
```bash
./stop_backend.sh
```

### 同时启动/停止两个服务 (可选)

也可以使用原来的脚本：
```bash
./start.sh   # 启动两个服务
./stop.sh    # 停止两个服务
```

## 查看日志

- 前端日志: `frontend.log`
- 后端日志: `backend.log`

## 服务说明

### 前端服务
- 使用自定义Python SPA服务器
- 监听 0.0.0.0:8080
- 支持单页面应用路由重写
- 服务目录: Page/dist

### 后端服务
- 使用Django开发服务器
- 监听 0.0.0.0:8003
- 虚拟环境: Server/venv
- 依赖已安装: requirements.txt
