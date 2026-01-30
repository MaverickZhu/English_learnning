后端占位说明

技术栈
- Python + FastAPI

建议结构
- app/
  - main.py
  - api/
  - services/
  - models/
  - schemas/

说明
已提供最小可运行 FastAPI 骨架与健康检查接口。

本地开发
- 安装依赖：pip install -r requirements.txt
- 启动：uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

数据库迁移
- 生成迁移：alembic revision --autogenerate -m "init"
- 执行迁移：alembic upgrade head

种子数据
- 执行：python -m app.scripts.seed

健康检查
- GET /health

内容 CRUD
- /words
- /sentences
- /passages
- /exercises

筛选参数（用于列表接口）
- level= A1/A2/B1/B2
- tags= travel,work
- keyword= 关键字模糊搜索
 - sort_by= id/text/title/type/level
 - sort_order= asc/desc
 - cursor_id= 上一页最后一条的 id（开启游标分页）

列表返回结构
- total: 总数
- items: 当前页数据
 - next_cursor: 下一页游标

内容管理后台接口
- POST /admin/words/bulk
- POST /admin/sentences/bulk
- POST /admin/passages/bulk
- POST /admin/exercises/bulk
- POST /admin/words/bulk-delete
- POST /admin/sentences/bulk-delete
- POST /admin/passages/bulk-delete
- POST /admin/exercises/bulk-delete
- POST /admin/tags/bulk-assign
- POST /admin/tags/assign
- POST /admin/import/validate
- POST /admin/import/execute
- POST /admin/import/upload
- POST /admin/import/async-upload
- GET /admin/import/jobs/{job_id}
- GET /admin/import/jobs
- POST /admin/import/jobs/{job_id}/retry
- GET /admin/import/template
- GET /admin/audit
- GET /admin/audit/export

批量导入错误明细
- errors: [{ index, field, message }]
- error_summary: [{ field, message, count }]

批量导入模式
- mode= upsert | insert_only | update_only
 - atomic= true 时全有或全无

字段校验规则
- level: A1/A2/B1/B2/C1
- tags: 最多 20 个，每个长度 <= 32
- exercise_type: image_choice/listening_choice/sentence_order/cloze

后台接口鉴权
- Header: X-Admin-Token
- 环境变量: ADMIN_TOKEN (默认 change-me)

对象存储（MinIO）
- MINIO_ENDPOINT / MINIO_ACCESS_KEY / MINIO_SECRET_KEY
- MINIO_PUBLIC_ENDPOINT 用于生成可访问的预签名 URL
- MINIO_IMAGE_BUCKET 默认 images
- MINIO_AUDIO_BUCKET 默认 audio
- 可参考 backend/.env.example

媒体上传与访问（Admin）
- POST /admin/media/upload (multipart: kind=image|audio, file)
- GET /admin/media/presign?kind=image|audio&object_name=xxx

导入模板校验
- entity_type: word/sentence/passage/exercise
- 返回 valid + errors + error_summary

导入工具
- 校验 JSON/CSV: python -m app.scripts.import_tool --entity word --file data.csv
- 导出错误 CSV: python -m app.scripts.import_tool --entity word --file data.csv --export-errors errors.csv

审计查询过滤
- start_at/end_at: ISO 格式时间字符串
- sort_by: id/created_at/action
- sort_order: asc/desc

审计导出
- GET /admin/audit/export?limit=1000&offset=0&sort_by=created_at&sort_order=desc

导入文件上传
- multipart/form-data: entity_type, mode, atomic, mapping(可选), file
- mapping 示例: {"text": "单词", "meaning": "释义"}

异步导入
- /admin/import/async-upload 返回 job_id
- /admin/import/jobs/{job_id} 查询状态
- /admin/import/jobs 列表查询
- /admin/import/jobs/{job_id}/cancel 取消任务
- /admin/import/jobs/{job_id}/export 导出结果
- /admin/import/jobs/{job_id}/errors 下载错误明细
- /admin/import/jobs/{job_id}/errors?skip=0&limit=50 分页
- /admin/import/jobs/{job_id}/export.csv 导出 CSV

文件大小限制
- MAX_IMPORT_BYTES（默认 5MB）

导入任务过滤
- start_at/end_at: ISO 格式时间字符串

用户与认证
- POST /auth/register
- POST /auth/login
- JWT_SECRET 环境变量用于签发 Token
- ACCESS_TOKEN_EXPIRE_MINUTES 默认 120
- 需要用户态访问的接口请携带 Authorization: Bearer <token>

练习与评分
- POST /practice/generate
- POST /practice/score
- POST /practice/score/batch

学习进度与掌握度（基础）
- POST /progress/record
- GET /progress/history?user_id=1
- POST /progress/summary

学习计划
- POST /plans
- GET /plans?user_id=1
- GET /plans/active?user_id=1
- POST /plans/{plan_id}/activate

复习提醒
- POST /review/reminder
- GET /review/reminders?user_id=1
- POST /review/reminders/{reminder_id}/done

错题本
- POST /mistakes/record
- GET /mistakes?user_id=1

掌握度
- POST /mastery/summary

考级模拟（基础）
- POST /exam/generate
- POST /exam/submit
- GET /exam/results?user_id=1
- POST /exam/config
- GET /exam/configs
- GET /exam/config/{name}

学习报告
- POST /reports/summary
  - 返回：suggestions、by_level
- POST /reports/summary/export
- POST /reports/summary/export.json
- POST /reports/trend
- POST /reports/trend/by-type
- POST /reports/recommendations
  - 返回：preview、link
