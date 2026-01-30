English Learning Platform

这是一个同时支持 Web 与 React Native App 的在线英语学习平台策划与基础工程目录。项目目标是提供现代、教育感强的学习体验，支持语音播放、配图学习、练习、测试与考级模拟。

目录结构
- backend/           FastAPI 后端应用（占位）
- docs/              产品与设计文档
- infra/             Docker 与基础设施配置
- data/              挂载数据目录（数据库与媒体）
- web/               Web 前端体验版
- mobile/            移动端流程预览
- admin/             内容管理后台前端
- admin-react/       内容管理后台 React 版本

快速开始
1. 进入 infra 目录
2. 使用 docker-compose 启动服务
   - docker compose up -d

说明
- 当前已包含基础 Web 与移动端流程示例，可逐步接入 API。
- 生产部署与监控建议见 docs/deployment.md
