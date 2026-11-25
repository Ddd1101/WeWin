# WeWin 云侧主存储部署

本实现采用《数据与图片存储分离部署方案》的优先方案：阿里云运行应用、SQLite 和媒体，N1 异步拉取数据库与媒体的联合备份。N1 不参与在线 API 或图片请求。未部署 n1 在线 MariaDB/SSHFS；该分支的延迟、系统权限和故障验收需另行完成后才能切换。

## 当前部署

| 对象 | 位置 |
| --- | --- |
| HTTPS | https://47.250.165.79 |
| 提交用源码目录 | Ali-Server `/root/Documents/workplace_shop/WeWin` |
| 运行代码 | Ali-Server `/srv/wewin/app` |
| Python 环境 | `/opt/wewin-venv`，Python 3.12 / Django 5.2.19 |
| Web 产物 / Django 静态文件 | `/srv/wewin/web` / `/srv/wewin/static` |
| 生产配置 | `/etc/wewin/app.env`，root:wewin，0640 |
| SQLite / 图片 | `/var/lib/wewin/db.sqlite3` / `/var/lib/wewin/media` |
| 写入屏障 / 调度独占锁 | `/var/lib/wewin/writes.lock` / `scheduler.lock` |
| 阿里云备份批次 | `/var/backups/wewin` |
| N1 备份目录 | `/home/admin/Documents/workplace_shop/wewin-backups/batches` |
| 初始冻结快照及缺图清单 | `/var/backups/wewin-initial` |
| 管理员新凭据 | `/root/wewin-credentials/superadmin.json`，仅 root 可读，不入 Git |

公网只通过 Nginx 80（跳转/ACME）与 443 访问 WeWin。Gunicorn 绑定 `127.0.0.1:8003`，两 worker。Django Admin 公网返回 404；管理任务可通过 SSH 运行 Django 管理命令。若以后需要可视化 Admin，应另行配置受控 HTTPS 入口。原有 FRP 7000/6000 是 N1 管理链路，本次不改动它们，也不开放 13306/10022。媒体沿用现有凭 URL 访问的方式；企业私密附件应另建鉴权下载入口，不应放入该公开媒体目录。

使用 Let's Encrypt shortlived IP 证书，由 Certbot 5.10.0 签发，续期后 reload Nginx。`wewin-cert-renew.timer` 每日检查两次。密钥和证书不入仓库。

## 更新部署

先在有足够内存的构建机执行 `npm --prefix Page ci && npm --prefix Page run build -- --outDir /tmp/wewin-web-build`。2GB ECS 上默认 Node 堆不足，本次在本机构建后传输产物。不要提交 `Page/dist`、APK、数据库或环境文件。

在阿里云源码目录中拉取/提交源代码后，将 Server 和 deploy 同步到 `/srv/wewin/app`。复制代码时必须排除 `.env`、`db.sqlite3*`、`media`、`venv*`、`staticfiles`、`__pycache__`；运行数据永远不从 Git 检出。将前端产物同步到 `/srv/wewin/web`，保持旧的哈希资源直到下一次发布清理。升级依赖、数据库 schema 或运行配置之前先生成并校验联合备份，再暂停服务及调度完成切换。

```bash
/opt/wewin-venv/bin/pip install -r /srv/wewin/app/Server/requirements.txt
cd /srv/wewin/app/Server
WEWIN_ENV_FILE=/etc/wewin/app.env /opt/wewin-venv/bin/python manage.py check --deploy --database default
# 有 schema 变更时，在停写窗口执行 migrate --noinput
WEWIN_ENV_FILE=/etc/wewin/app.env /opt/wewin-venv/bin/python manage.py collectstatic --noinput
nginx -t
systemctl restart wewin wewin-scheduler
curl --fail https://47.250.165.79/health/ready/
```

`deploy/*.service`、`*.timer` 安装到 `/etc/systemd/system`，运行 `systemctl daemon-reload`。应用账号为 `wewin`，Nginx 用户加入 `wewin` 组，只读媒体。应用和调度服务启用 `ProtectSystem=strict`，仅允许写 `/var/lib/wewin`。配置中生产 DEBUG=False、明确主机白名单、稳定强 SECRET_KEY 和 HTTPS MEDIA_URL 为必需项。

Web 登录、注册和 API 使用同源入口。本机开发可显式设置 `VITE_API_BASE_URL`。Android 构建：

```bash
ANDROID_HOME=/path/to/android-sdk bash Android/gradlew -p Android -PAPI_BASE_URL=https://47.250.165.79 assembleDebug
```

此任务生成的是调试 APK，尚未进行真实 Android 设备验收或签名发布。客户端可继续使用既有 API 和图片字段。

## 备份与健康检查

- `wewin-backup.timer` 每小时产生新批次。API（包括可能有写入副作用的 GET）与拉单进程持有共享锁，备份取得独占锁，等待既有写入结束后复制 SQLite 与媒体；期间新 API 请求返回 503 和 Retry-After，不在文件复制期间接受写入。
- 每批包含 SQLite、媒体、逐文件 SHA-256 清单。SQLite 在线备份保留主键、JSON、Decimal 和微秒时间精度，先校验再原子发布批次。
- N1 的 admin crontab 每 5 分钟拉取未完成批次。专用密钥只允许阿里云 root 上的 `backup_exchange.py serve`，禁用 PTY/转发等能力并固定 SSH 主机密钥。只支持 list/get/ack，无法执行任意 shell。
- 下载使用临时文件，验证完整归档、路径和逐文件哈希后才重命名并确认。网络失败保留上一批；重连后按批次补传。阿里云保留至少 14 批且不删除尚未确认的批次，N1 独立保留 30 批。长期中断会增加阿里云磁盘占用，应监控剩余空间。
- `/health/live/` 检查进程；`/health/ready/` 检查数据库、媒体探测文件及定期写探测；`wewin-storage-check.timer` 每 5 分钟以应用用户完成写入、读取、重命名和删除验证，结果超过 15 分钟未更新视为不可用；`/health/backup/` 同时检查源批次年龄及 N1 确认时间。当前过期阈值 25 小时，返回 503 可供外部监控告警，本次未配置向个人发送通知。
- 目标 RPO 是每小时一次本地批次加 5 分钟轮询及实际传输时延。备份源和目标只有成功批次才可恢复，不以同步过程中的文件作为恢复源。

手动执行阿里云备份：`systemctl start wewin-backup`。N1 手动补传使用现有 crontab 中的完整命令。查日志：`journalctl -u wewin-backup` 和 N1 `wewin-backups/pull.log`。

## 联合恢复与回滚

在新目录演练恢复，绝不覆盖在线数据：

```bash
python3 deploy/restore_backup.py --archive /path/to/BATCH.tar.gz --destination /path/to/new-restore-directory
```

该命令拒绝已存在的目标目录，拒绝路径穿越、链接、重复路径和哈希不一致，并验证 SQLite 完整性、外键和媒体引用，输出 `restore-report.json`。部署前已有 9 条缺失图片引用，保留原引用并与基线清单比较，不生成占位图掩盖缺失。

应用回退时优先回退代码，保留当前生产库和媒体。如果必须恢复旧批次，先停止 web 和 scheduler，备份当前现场，确认并核对批次之后的新增/更新/删除，再整体切换数据库及媒体并校正属主；不能直接用旧库覆盖开放写入后的新数据。恢复后检查健康、权限、商品/BOM 图片、价格、订单及报价，再启动唯一调度器。

## 验证命令

```bash
cd Server
DEBUG=True /opt/wewin-venv/bin/python manage.py test store.test_deployment --noinput
DEBUG=True /opt/wewin-venv/bin/python manage.py makemigrations --check --dry-run
cd ..
python3 -m unittest discover -s deploy -p 'test_*.py' -v
```

`deploy/smoke.py` 在独立临时企业验证线上 HTTPS 登录、商品、订单列表、报价、上传替换及跨企业拒绝。必须先 prepare，再 run，完成后 cleanup；`--state` 指向仓库外权限受限文件。正式验收结果见 `docs/deployment-validation-2026-11-25.md`。
