"""
SkyRoute 后端主应用入口
城市低空智能航路规划平台 - FastAPI + Socket.io
"""
import socketio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.routes import tasks, planning, conflicts, drones, weather
from app.socket.events import sio, start_simulation, stop_simulation


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动仿真广播
    await start_simulation()
    yield
    # 清理资源
    await stop_simulation()


app = FastAPI(
    title="SkyRoute API",
    description="城市低空智能航路规划平台 REST API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(planning.router, prefix="/api/v1")
app.include_router(conflicts.router, prefix="/api/v1")
app.include_router(drones.router, prefix="/api/v1")
app.include_router(weather.router, prefix="/api/v1")


@app.get("/api/v1/health", tags=["system"])
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "service": "SkyRoute API", "version": "1.0.0"}


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "内部服务器错误", "error": str(exc)},
    )


# Socket.io ASGI集成
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)
