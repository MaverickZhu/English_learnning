基础设施说明

服务清单
- api：FastAPI 应用（需在 backend 中提供 Dockerfile 与应用入口）
- db：PostgreSQL 数据库
- minio：对象存储，用于图片与音频

启动方式
1. 进入本目录
2. 运行 docker compose up -d

端口说明
- API: 28000 -> 8000
- PostgreSQL: 25432 -> 5432
- MinIO: 9000, 9001

数据挂载
- ../data/postgres：数据库数据
- ../data/minio：对象存储数据
