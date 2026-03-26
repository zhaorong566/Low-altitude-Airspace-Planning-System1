"""
WebSocket事件处理 - 基于python-socketio的实时通信
"""
import socketio
import asyncio
import time
from typing import Dict, Any

from app.services.simulation_service import SimulationService
from app.services.weather_service import WeatherService

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    logger=False,
    engineio_logger=False,
)

_sim_service = SimulationService()
_weather_service = WeatherService()
_connected_clients: Dict[str, Any] = {}
_simulation_task = None


@sio.event
async def connect(sid, environ, auth=None):
    """客户端连接"""
    _connected_clients[sid] = {"subscriptions": [], "connected_at": time.time()}
    await sio.emit("server:ready", {"status": "connected", "sid": sid}, to=sid)

    # 发送初始数据
    tasks = _sim_service.get_demo_tasks()
    drones = _sim_service.get_demo_drones()
    for task in tasks:
        route = _sim_service.generate_route_for_task(task)
        task["waypoints"] = route

    await sio.emit("init:data", {"tasks": tasks, "drones": drones}, to=sid)


@sio.event
async def disconnect(sid):
    """客户端断开"""
    _connected_clients.pop(sid, None)


@sio.event
async def subscribe_area(sid, data):
    """订阅区域更新"""
    if sid in _connected_clients:
        _connected_clients[sid]["subscriptions"].append(data)
    await sio.emit("subscription:confirmed", {"area": data}, to=sid)


@sio.event
async def drone_command(sid, data):
    """无人机指令"""
    drone_id = data.get("drone_id")
    command = data.get("command")
    await sio.emit(
        "drone:command_ack",
        {"drone_id": drone_id, "command": command, "status": "accepted"},
        to=sid,
    )


@sio.event
async def request_route_plan(sid, data):
    """请求路径规划"""
    from app.services.planning_service import PlanningService
    planner = PlanningService()
    try:
        result = await planner.plan_route(
            task_id=data.get("task_id", "temp"),
            origin=(data["origin"]["lat"], data["origin"]["lon"], data["origin"].get("alt", 50)),
            destination=(data["dest"]["lat"], data["dest"]["lon"], data["dest"].get("alt", 50)),
        )
        await sio.emit("route:planned", result, to=sid)
    except Exception as e:
        await sio.emit("route:error", {"error": str(e)}, to=sid)


async def broadcast_simulation():
    """后台任务：广播无人机实时位置和事件"""
    tasks = _sim_service.get_demo_tasks()
    for task in tasks:
        _sim_service.generate_route_for_task(task)

    iteration = 0
    while True:
        await asyncio.sleep(1.0)
        if not _connected_clients:
            continue

        iteration += 1
        elapsed = (time.time() - _sim_service._simulation_start) % 300

        # 广播无人机位置
        positions = []
        for task in tasks:
            pos = _sim_service.get_current_position(task["id"], elapsed)
            if pos:
                pos["drone_id"] = task["drone_id"]
                pos["task_id"] = task["id"]
                positions.append(pos)

        if positions:
            await sio.emit("drone:positions", {"positions": positions})

        # 每30秒广播天气更新
        if iteration % 30 == 0:
            weather = await _weather_service.get_current_weather()
            await sio.emit("weather:updated", weather)

        # 每10秒检查冲突
        if iteration % 10 == 0:
            from app.services.planning_service import PlanningService
            planner = PlanningService()
            task_data = [
                {
                    "id": t["id"],
                    "waypoints": _sim_service._task_routes.get(t["id"], []),
                }
                for t in tasks
                if t["id"] in _sim_service._task_routes
            ]
            conflicts = planner.detect_conflicts(task_data)
            if conflicts:
                await sio.emit("conflict:detected", {"conflicts": conflicts})


async def start_simulation():
    """启动仿真广播任务"""
    global _simulation_task
    _simulation_task = asyncio.create_task(broadcast_simulation())


async def stop_simulation():
    """停止仿真广播任务"""
    global _simulation_task
    if _simulation_task:
        _simulation_task.cancel()
        _simulation_task = None
