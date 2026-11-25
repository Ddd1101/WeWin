# 前端、后端与数据端代码整合核验

整合源仓库：Ali-Server /root/Documents/workplace_shop/WeWin，分支 update/storage_2026_11_22，基于已发布提交6f1ddd8。既有前后端与备份业务代码已在该提交内，本次补齐统一运维入口和N1安装入口；不重写已推送历史。

## 代码归属

| 部分 | 仓库位置 | 实际运行位置 |
| --- | --- | --- |
| Web前端 | Page/；deploy/build_frontend.py；start/stop_frontend.sh | /srv/wewin/web，由Nginx提供服务 |
| Django后端 | Server/；deploy/app.env.example；start/stop_backend.sh | /srv/wewin/app/Server |
| 自动拉单 | Server/store/tasks.py；management/commands/run_scheduler.py | wewin-scheduler.service |
| 数据备份及恢复 | deploy/backup.py、backup_exchange.py、restore_backup.py | 阿里云 /srv/wewin/app/deploy；N1 wewin-backups/bin |
| N1安装 | deploy/n1/install_backup.py、README.md | 普通admin用户维护三份脚本及备份cron块 |
| 统一服务入口 | deploy/service_control.py；start.sh、stop.sh、start_services.py、Makefile | 阿里云systemd |

## 核验结果

- 开始整合时阿里云Git工作区干净，HEAD和GitHub一致。Nginx站点及8个systemd unit/timer文件与仓库字节一致。
- 运行源码仅发现 MariaDB可选依赖清单、测试文件落后；生产配置示例也在随后审计中发现版本差异，均纳入受限同步。业务接口模块没有未入库的线上改动。
- N1三份运行脚本与阿里云仓库SHA-256完全一致；旧N1 WeWin工作区无未提交修改，不复制其历史数据库或回退到旧源码。
- 前后端/数据端启停命令只读预览通过，服务状态正常。没有为验证而停止线上服务。
- N1真实Python3.7环境下 --check → --apply → --check 通过，重复安装无差异；专用私钥哈希未变化，原FRP @reboot命令保持一致。
- 构建入口检查输出必须在仓库外，拒绝覆盖非空目录；本轮未修改前端业务源码，未重复执行完整前端构建。
- 本机工作区的既有未提交修改保留；所有新修改和提交均在阿里云仓库完成。

## 提交边界

按前端入口、后端入口、N1数据端、统一运维与文档四批提交。每个代码提交后将 docs/log.txt 记录写到最上方，再 amend 合入同一提交；日志的 Commit 字段按仓库约定记录 amend 前的代码提交点。

数据库、媒体、备份归档、私钥、实际环境配置、构建产物和虚拟环境不属于本轮提交内容。N1/阿里云上的第三方FRP程序与独立ShopManager工程不复制进本仓库。
