# Low-altitude-Airspace-Planning-System1

城市低空智能航路规划系统（SkyRoute），包含前后端与基础依赖（PostgreSQL/PostGIS、Redis），用于任务管理、航路规划、冲突检测与可视化展示。

## 项目结构

```text
.
├── README.md
└── skyroute
    ├── docker-compose.yml   # 一键启动依赖与前后端服务
    ├── backend              # FastAPI + Socket.IO
    └── frontend             # Vue3 + Vite + Cesium
```

## 技术栈

- 前端：Vue 3、Vite、TypeScript、Pinia、Element Plus、Cesium
- 后端：FastAPI、Socket.IO、SQLAlchemy、Alembic
- 基础设施：PostgreSQL(PostGIS)、Redis、Docker Compose

## 环境要求

- Docker + Docker Compose（推荐）
- 或本地开发环境：
  - Python 3.11+
  - Node.js 20+
  - PostgreSQL 15 + PostGIS
  - Redis 7+

## 快速启动（推荐：Docker）

在仓库根目录执行：

```bash
cd skyroute
docker compose up --build
```

启动后默认访问地址：

- 前端：http://localhost:5173
- 后端 API：http://localhost:8000
- 健康检查：http://localhost:8000/api/v1/health

## 本地开发启动

### 1) 启动后端

```bash
cd skyroute/backend
cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:socket_app --host 0.0.0.0 --port 8000 --reload
```

### 2) 启动前端

```bash
cd skyroute/frontend
npm install
npm run dev
```

## 配置说明（backend/.env）

关键变量示例见：`skyroute/backend/.env.example`

- `DATABASE_URL`：PostgreSQL 连接地址
- `REDIS_URL`：Redis 连接地址
- `OPENWEATHER_API_KEY`：天气服务 API Key（可选）
- `CESIUM_ION_TOKEN`：Cesium Token（可选）
- `CORS_ORIGINS`：允许的前端来源，支持逗号分隔

## 说明

- 若使用 Docker Compose，`docker-compose.yml` 已内置默认开发配置。
- 前端打包命令为：`npm run build`。
