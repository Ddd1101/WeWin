# WeWin 统一部署入口

前端源码在 Page/，后端源码在 Server/，数据端源码在 deploy/；N1安装入口在 deploy/n1/。当前为阿里云在线SQLite + N1在线图片原文件，阿里云仅2GB有界缓存，访问 https://47.250.165.79。

## 生产服务启停（阿里云）

在仓库根目录执行，使用有 systemd 管理权限的账号。服务单元需按 [部署说明](deploy/README.md) 预先安装。

```bash
bash start.sh                  # 数据定时任务 → 后端/唯一调度 → Nginx
bash stop.sh --dry-run          # 查看停止范围，不执行
bash stop.sh                   # 停止本项目 Web、后端及三个定时任务
python3 deploy/service_control.py all status

bash start_frontend.sh          # Nginx :80/:443
bash start_backend.sh           # Gunicorn 127.0.0.1:8003 + 调度
bash start_data.sh              # 备份/媒体探测/证书续期定时器
# 对应 stop_frontend.sh / stop_backend.sh / stop_data.sh
```

所有脚本支持 --dry-run；python3 start_services.py 是 start.sh 的兼容入口。脚本只调用明确的 systemd 单元，不按进程名 pkill，不启动旧8080 SPA服务或生产 runserver。FRP/SSH管理通道独立运行，启停WeWin不会停止这些管理通道。

## 构建与源码同步

```bash
# 在有足够内存的构建机运行；输出目录必须在仓库外且为空
python3 deploy/build_frontend.py --output /tmp/wewin-web-release
# 将该目录的产物发布到阿里云 /srv/wewin/web，保留仍被旧页面引用的哈希资源

# 在阿里云核对 Git 管理的运行源码；--check 发现差异返回1
python3 deploy/sync_runtime.py --destination /srv/wewin/app --check
python3 deploy/sync_runtime.py --destination /srv/wewin/app --apply
```

同步工具只复制 Git 跟踪的 Server/deploy 代码与示例，跳过数据库、媒体、环境文件、私钥和虚拟环境，不删除目标文件，不自动执行迁移或重启。生产配置使用 deploy/app.env.example 作为参考，实际文件保存在 /etc/wewin/app.env。依赖或schema变更需先备份、安排停写、安装依赖及迁移，再检查生产配置和重启服务。具体切换和恢复见 [deploy/README.md](deploy/README.md)。

## N1 数据端

按 [deploy/n1/README.md](deploy/n1/README.md) 将三份备份脚本从本仓库安装到 N1。安装工具校验专用密钥已在仓库外配置，精确维护自己的cron块，保留FRP和其他任务。N1除数据库/媒体清单备份外，还运行在线图片服务和独立SSH媒体隧道；安装与迁移见 [deploy/N1-MEDIA.md](deploy/N1-MEDIA.md)。数据库仍留在阿里云。

## 开发环境与日志

本地开发使用 make run-backend、make run-frontend；激活所需虚拟环境后运行。make build-frontend 的产物仍在 Page/dist，构建产物不提交。

生产日志使用 journalctl -u wewin、journalctl -u wewin-scheduler、journalctl -u wewin-backup；N1日志为 ~/Documents/workplace_shop/wewin-backups/pull.log。

[整合核验记录](docs/code-integration-2026-11-25.md) · [上线验收记录](docs/deployment-validation-2026-11-25.md)
