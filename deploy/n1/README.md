# N1 数据备份端

数据端源码统一在主仓库 deploy/ 下维护：backup.py（联合备份与校验）、backup_exchange.py（受限导出/校验拉取）、restore_backup.py（隔离恢复）。N1 运行目录仅安装这三份脚本，不维护另一份代码分支。N1同时承担在线图片原文件存储，数据库仍在阿里云。本页只介绍备份客户端；媒体服务和专用隧道见 ../N1-MEDIA.md。

## 安装与对齐

使用 Python 3.7+，需要系统 ssh 和 crontab。将本目录及 deploy/ 三个 Python 源文件一起从已检出的发布版本传到 N1；可在临时目录中安装，不必覆盖 N1 上旧的 WeWin 源码或数据库。

先在仓库外准备专用 id_ed25519 和固定的 known_hosts。私钥权限0600。对应公钥在阿里云 authorized_keys 中使用 restrict 与固定 backup_exchange.py serve 命令，只允许 list/get/ack；不得给备份密钥任意 shell 权限。首次密钥配置沿用部署说明，实际密钥不放入 Git。

```bash
python3 deploy/n1/install_backup.py --source ./deploy \
  --root /home/admin/Documents/workplace_shop/wewin-backups \
  --host root@47.250.165.79 --check
# 核对后执行安装；只管理自己的三份脚本及定时任务块
python3 deploy/n1/install_backup.py --source ./deploy \
  --root /home/admin/Documents/workplace_shop/wewin-backups \
  --host root@47.250.165.79 --apply
```

--check 是只读，返回0表示已一致，返回1表示需要更新。安装会保留原有 FRP @reboot 和所有无关 cron，精确接管原有同一条备份命令；不同的未标记备份命令会报错，避免安装重复任务。重复 --apply 不会添加多条任务。检查日志用 `tail -n 30 ~/Documents/workplace_shop/wewin-backups/pull.log`。

备份内容、密钥、known_hosts、临时传输、运行日志均留在仓库外。N1 三份实际运行脚本的 SHA-256 已与阿里云仓库核对一致，见 docs/code-integration-2026-11-25.md。
