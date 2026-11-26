# WeWin 部署与验证记录（2026-11-25）

## 实际上线范围

采用方案推荐的云侧主存储拓扑。阿里云的 SQLite 与媒体移到 `/var/lib/wewin`，Nginx 提供 https://47.250.165.79，Gunicorn 2 worker 使用 Django 5.2.19，独立 APScheduler 由 systemd 管理。N1 在 `/home/admin/Documents/workplace_shop/wewin-backups` 保存异步联合备份。所有提交在 Ali-Server 的原仓库完成，本机不提交。

选择依据：阿里云有约 27GB 可用磁盘；N1 使用 Debian 10/Python 3.7，admin 无免密 sudo，也无 Docker socket 权限；现场 N1 SSH 管理连接曾短暂关闭，新连接恢复成功。异步备份避免这些条件影响在线读写。N1 在线 MariaDB/SSHFS 属于方案的另一分支，本次不把配置预留声明为已完成该拓扑验收。

## 已执行验证

| 项目 | 证据 / 结果 |
| --- | --- |
| Python 与数据兼容 | Python 3.12.3 / Django 5.2.19；原 SQLite 上 migrate 无待执行迁移；check --deploy --database default 无问题；makemigrations --check --dry-run 无变更 |
| 后端回归 | 12 项部署测试通过：图片替换/无效内容/事务失败/跨企业权限/媒体不可用/数据库不可用/备份屏障/拉单成功水位/旧备份新确认不能掩盖过期 |
| 备份回归 | 4 项测试通过：联合恢复保留微秒时间与数据、损坏归档拒绝、路径穿越拒绝、未确认批次不清理 |
| Web 构建 | npm ci 后 Vite 构建成功；ECS 默认 Node 堆不足，改用本机构建后复制产物；既有大 chunk 告警仍存在 |
| HTTPS | 真实受信任公网 IP 证书签发成功，HTTP 308 到 HTTPS；Certbot renew --dry-run 成功；每日两次续期 timer 已启用 |
| 网络暴露 | 8003 仅监听 127.0.0.1；从本机探测 8003、13306、10022 均不可达；保留原管理 FRP 6000/7000 |
| 真实 API | 在临时独立企业完成 HTTPS 登录、商品创建/编辑、订单列表、客户报价、图片上传/替换/无效图片拒绝、BOM 图片 URL、跨企业访问拒绝 |
| Web 浏览器 | Ego Lite 实际登录、打开商品配件页；图片 naturalWidth=16 且 complete=true；截图位于本机 `/tmp/wewin-products-validation.png` |
| 性能抽样 | 本机网络 10 次商品 HTTPS 请求 P50=728.7ms、P95=1221.5ms，均未超时；阿里云本机完整 API 冒烟 10 请求中位数9.2ms、最大692.4ms。该样本不能代表全天/高峰容量 |
| 定期媒体写探测 | wewin-storage-check.timer 每5分钟以应用用户执行读、写、重命名、删除；首次运行成功，ready 同时检查探测结果新鲜度 |
| 媒体故障 | 临时移走媒体探测文件：ready 503、移除图片请求 503、原图片引用保留；恢复探测文件后 ready 200 |
| 备份写入屏障 | 持有独占写锁时业务 API 503、静态页面200；释放后 API 200 |
| 单调度器 | 第二个 run_scheduler 进程被锁拒绝；systemd 重启后 web/scheduler 正常运行；生产自动拉单配置数为0，未触发真实店铺拉单 |
| 备份传输失败 | 对不可达备份端点执行拉取，返回失败；已完成批次和 latest.json 保持不变；正常链路继续补传后续批次 |
| N1 备份恢复 | 初始批次与包含验证图片的批次在 N1 恢复成功；逐文件 SHA-256、SQLite integrity_check、foreign_key_check 通过。含图批次有10条引用，其中1条新验证图完整，其余9条为上线前缺图 |
| 管理员凭据 | 发现公开默认密码仍有效，已替换随机强密码并移除登录提示/敏感控制台日志；默认密码登录401，新密码登录200；JWT密钥另行轮换，旧会话失效。新凭据仅保存在 Ali-Server `/root/wewin-credentials/superadmin.json`（0600） |
| Android | HTTPS API 基址的 assembleDebug 成功，17MB APK 在本机 `Android/app/build/outputs/apk/debug/app-debug.apk` 及 Ali-Server `/srv/wewin/artifacts/wewin-https-debug.apk`；未连接 Android 设备，未做真机验收或正式签名发布 |

## 数据核对

初始冻结备份 `20261125T131154471344Z`：1,328 商品、9,921 SKU、2,205 订单、2 客户、3 企业、6 用户。N1 联合恢复得到相同行数，并校验整个 SQLite 文件和全部媒体文件的哈希，因此没有 dumpdata 的微秒截断问题。权限/报价/BOM 访问另由独立企业 API 演练覆盖。

服务器初始媒体目录未发现原有9条图片引用对应文件，恢复结果仍为这9条缺图，没有清除或伪造图片。详情保存在 Ali-Server `/var/backups/wewin-initial/missing-media.json`。测试企业、测试商品/图片、测试客户及报价在验证后清理；管理员密码和JWT轮换是本次生产配置的有意变更。

## 运行安排与验收限制

阿里云每小时产生一致备份；N1 每5分钟拉取，完整校验后确认。传输期间原有完整批次保持可用，失败的传输不会变成成功批次。`/health/backup/` 对源批次与确认时间同时检查，超过25小时返回503，需由运维监控系统采集；本次没有配置外部消息告警接收人。恢复流程和具体命令见 `deploy/README.md`。

未执行真实 Android 设备测试、跨日高峰负载、整机断电/重启、真实店铺订单补拉。应用进程重启、重复调度拒绝、依赖故障与恢复已验证。旧端口8003/8080在部署前未运行WeWin，新入口为HTTPS；旧APK必须安装使用HTTPS基址的新构建。

测试清理后再次核对：企业3、用户6、商品1328、SKU 9921、订单2205、客户2、客户商品报价5、报价历史12；无 deployment-* 测试用户残留。web、scheduler、nginx 以及备份、媒体探测、证书续期 timer 均为 active。APK SHA-256：`4adecd04350afbe8a3a65fc45cc066a816ceda79eceae63570bddb664f5d020b`，本机与阿里云文件一致。

最终清理后批次：`20261125T141157824834Z`，大小1,954,770字节，SHA-256：`3ce22254781fa06c0ee4683e46cf6d5adc1baf59bc1cc961d5cb7f069ea2895e`。N1 已完成逐文件校验并确认接收，记录时间为北京时间 2026-11-25 22:19；阿里云备份健康检查恢复为正常。
