部署与监控建议（生产）

目标
- 通过反向代理统一入口
- 将敏感配置从代码中剥离
- 建立可观测性与备份策略

建议架构
- 入口：Nginx 或 Caddy（HTTPS 终止 + 反向代理）
- 应用：FastAPI 容器
- 数据库：PostgreSQL 容器
- 对象存储：MinIO 容器
- 监控：Prometheus + Grafana（可选）
- 日志：Loki 或 ELK（可选）

环境变量
- ADMIN_TOKEN / JWT_SECRET 必须设置为强随机值
- 数据库、MinIO 账号建议改为独立生产值
- MINIO_PUBLIC_ENDPOINT 指向公网域名（如 cdn.example.com）

安全与网络
- 仅暴露反向代理端口（80/443）
- 数据库与 MinIO 仅内网访问
- 使用容器网络隔离

健康检查
- API：/health
- MinIO：/minio/health/live
- PostgreSQL：容器内 psql 或 TCP 端口探测

备份策略
- PostgreSQL：每天定时 pg_dump + 保留 7~30 天
- MinIO：定期 bucket 备份或开启对象版本控制
- 重要配置：.env 与密钥妥善保管

监控指标建议
- API：QPS、错误率、响应时间、数据库连接池
- DB：连接数、慢查询、磁盘空间
- MinIO：存储量、请求量、错误率

上线前检查清单
- 迁移已执行（alembic upgrade head）
- 管理员 Token 与 JWT Secret 已替换
- 反向代理已配置 HTTPS
- 备份与监控已启用
