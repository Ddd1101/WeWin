# N1 在线图片部署

当前目标：阿里云运行应用和 SQLite，N1存放全部在线图片原文件。阿里云只保留2GB有界缓存和512MB上传暂存，图片 URL 仍为 `https://47.250.165.79/media/products/...`。

## 程序与凭据

`media-service/` 是Go标准库实现的独立图片服务。构建使用经过官方SHA-256校验的Go 1.27.4：

```bash
cd media-service
go test -race ./...
CGO_ENABLED=0 GOOS=linux GOARCH=arm64 go build -ldflags='-s -w' -trimpath -o /outside/repository/wewin-media .
```

N1运行目录为 `~/Documents/workplace_shop/wewin-media`。将程序安装到 `bin/wewin-media`、`deploy/n1/run_media.py` 安装到 `bin/run_media.py`。`origin.json` 参照 `deploy/media-origin.example.json`，使用独立随机读写凭据、0600权限；`tunnel.json` 内容为 `{"host":"wewin-media-tunnel@47.250.165.79"}`。

图片服务只监听 N1 `127.0.0.1:18080`，原文件在 `objects/products`，临时文件在 `objects/.tmp`，删除回收区在 `objects/.trash`。每张图最多100MB，4个并发上传。低于5GB剩余空间时拒绝写入。回收区保留7天且最多5GB，不删除在线原文件；没有第二个存储设备时，这不能防止N1物理损坏丢图。

内部接口为 `GET/HEAD/PUT/DELETE /objects/products/...`、`GET /manifest`、`GET /health`。读取使用读凭据，写入使用独立写凭据。PUT必须提供Content-Length及X-Content-SHA256，临时落盘、大小/格式/哈希校验后原子发布。同名同哈希重试是幂等操作，同名不同哈希拒绝覆盖。DELETE移入回收区。原文件由Django进一步校验，N1也校验文件签名及扩展名。

## 独立SSH隧道

N1使用专用 `id_ed25519` 和固定 `known_hosts` 主动连接阿里云SSH22：

```
N1:127.0.0.1:18080 ← SSH反向转发 ← Ali:127.0.0.1:10080
```

阿里云专用账号为 `wewin-media-tunnel`，仅允许上述remote forwarding。authorized_keys使用 `restrict,port-forwarding,permitlisten="127.0.0.1:10080"`；sshd Match配置限制 AllowTcpForwarding remote、PermitListen 127.0.0.1:10080、MaxSessions 0、关闭密码、TTY、agent及X11转发。执行sshd -t成功后再reload，保留现有SSH会话。该通道不依赖FRP7000/6000，公网不开放10080/18080。

以N1 admin运行以下两类命令，并将它们纳入专属cron块；保留原有备份和FRP任务：

```bash
python3 ~/Documents/workplace_shop/wewin-media/bin/run_media.py --root ~/Documents/workplace_shop/wewin-media --role origin
python3 ~/Documents/workplace_shop/wewin-media/bin/run_media.py --root ~/Documents/workplace_shop/wewin-media --role tunnel
```

每类各有一个@reboot后台入口和一个每5分钟恢复入口。监督脚本使用flock避免重复运行，子进程退出后5秒重试，SSH使用15秒keepalive、3次失败断开重连。发送SIGTERM到监督进程会结束对应子进程。更新程序后结束旧origin监督进程再启动新版本，检查日志 origin.log/tunnel.log；不要宽泛pkill其他Python或SSH进程。

## 阿里云配置与容量上限

用root执行 `deploy/provision_media_volumes.sh`，创建2GB缓存与512MB上传临时文件系统，配置fstab开机挂载。运行单元通过RequiresMountsFor依赖它们。缓存淘汰目标1.5GB；独立文件系统提供最终硬上限。

在 `/etc/wewin/app.env` 添加MEDIA_ORIGIN_URL=http://127.0.0.1:10080、读写凭据、MEDIA_CLEANUP_DIR=/var/lib/wewin/media-cleanup、MEDIA_CACHE_ROOT=/var/cache/wewin-media、FILE_UPLOAD_TEMP_DIR=/var/lib/wewin-upload/django。实际文件root:wewin、0640，绝不入Git。

在 `/etc/wewin/media-origin.conf` 配置 Nginx 的 `proxy_set_header Authorization "Bearer READ_CREDENTIAL";`，0600权限。安装新 `deploy/nginx.conf`，执行nginx -t后reload。Gunicorn总超时150秒；带图片的Web与Android请求支持180秒等待，普通API保留原超时。Nginx限制商品写接口4个并发请求。

Django先在数据库事务外上传新图，然后在短事务中更新引用。新上传有24小时孤儿宽限期；旧图在数据库引用消失后进入清理队列。`wewin-media-cleanup.timer` 每5分钟重试，清理前再次检查商品引用，并删除对应Nginx缓存文件。缓存目录由Nginx管理，因此清理单元以root运行，但仅操作受限媒体队列和指定缓存目录。

N1断线时，缓存命中的图片仍可读；未缓存图片和图片上传/删除返回503，普通商品编辑、登录和订单仍可用。`/health/core/` 检查数据库业务，`/health/media/`检查N1服务，`/health/ready/`检查整体依赖；这些检查不会自动重启后端。

## 迁移和回退

停图片写入及旧调度后，用 `deploy/migrate_media.py` 将源媒体复制到N1并按哈希核对。迁移报告放仓库外。原9条缺图引用保留清单，不生成占位图。冻结SQLite快照、旧生产配置及旧运行代码后切换服务；验证上传、图片与BOM URL后恢复业务。

开放新写入前可恢复旧运行代码和旧媒体配置。开放写入后若回退，先暂停图片写入，将N1新增/变更图片复制回云侧并校验，再切换。不能直接恢复迁移前目录。

图片和旧的含图备份校验并转存N1后，清理云側全量图片副本；云侧只保留缓存和临时文件。

## 备份及恢复

新备份包含SQLite、media-manifest.json及归档哈希清单，不包含图片原文件。N1每5分钟拉取；云侧备份暂存总预算512MB，预算耗尽会停止新增批次并报告故障。N1清单与数据库快照协调生成，原文件不可覆盖；旧引用的图仍可在回收期内恢复。

恢复使用 `deploy/restore_backup.py --archive BATCH.tar.gz --destination NEW_DIR --media-root ~/Documents/workplace_shop/wewin-media/objects`。工具从在线原文件或回收区找到文件，核对清单哈希并复制到新恢复目录。没有提供--media-root时只验证数据库及清单，报告 media_verified=false，不能声称完成联合恢复。
