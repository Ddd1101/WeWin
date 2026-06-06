# WeWin

## 前端服务

### 环境部署

1. 安装系统 nginx：
   ```bash
   sudo apt install nginx
   ```

2. 项目配置文件 `nginx_system.conf` 已包含 SPA 路由回退、静态资源缓存、gzip 等配置，无需额外修改系统 nginx 配置。

### 启动 / 停止 / 重启

| 操作 | 命令 |
|------|------|
| 启动 | `./start_frontend.sh` |
| 停止 | `./stop_frontend.sh` |
| 重启 | `./stop_frontend.sh && ./start_frontend.sh` |
| 重载配置（不中断服务） | `/usr/sbin/nginx -s reload` |

### 前端代码更新

1. 进入前端目录构建：
   ```bash
   cd Page && npm run build
   ```
2. 重载 nginx（不中断服务）：
   ```bash
   /usr/sbin/nginx -s reload
   ```

### 访问地址

`http://<服务器IP>:8080`

### 日志位置

`/tmp/nginx_access.log` 和 `/tmp/nginx_error.log`

### 配置说明

- 启动脚本通过 `/usr/sbin/nginx -c nginx_system.conf` 使用自定义配置，绕过沙箱环境 `/var/log` 和 `/run` 只读限制
- PID 文件：`/tmp/nginx.pid`
- 临时文件：`/tmp/nginx_*`
