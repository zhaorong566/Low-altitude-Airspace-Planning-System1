"""
仿真服务 - 预置飞行任务和实时仿真数据生成
提供北京朝阳区演示数据
"""
import math
import time
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from uuid import uuid4


# 预置演示任务数据（北京朝阳区）
DEMO_TASKS = [
    {
        "id": "task-delivery-001",
        "name": "朝阳快递配送A线",
        "drone_id": "drone-001",
        "task_type": "delivery",
        "priority": "normal",
        "status": "executing",
        "origin": {"lat": 39.9204, "lon": 116.4430, "alt": 5.0},
        "destination": {"lat": 39.9524, "lon": 116.4743, "alt": 5.0},
        "planned_start": "2024-01-15T09:00:00",
    },
    {
        "id": "task-delivery-002",
        "name": "三里屯快递配送B线",
        "drone_id": "drone-002",
        "task_type": "delivery",
        "priority": "high",
        "status": "executing",
        "origin": {"lat": 39.9312, "lon": 116.4568, "alt": 5.0},
        "destination": {"lat": 39.9476, "lon": 116.4201, "alt": 5.0},
        "planned_start": "2024-01-15T09:05:00",
    },
    {
        "id": "task-inspect-001",
        "name": "CBD建筑群巡检",
        "drone_id": "drone-003",
        "task_type": "inspection",
        "priority": "normal",
        "status": "approved",
        "origin": {"lat": 39.9090, "lon": 116.4607, "alt": 5.0},
        "destination": {"lat": 39.9156, "lon": 116.4782, "alt": 5.0},
        "planned_start": "2024-01-15T10:00:00",
    },
    {
        "id": "task-emergency-001",
        "name": "朝阳医院紧急医疗配送",
        "drone_id": "drone-004",
        "task_type": "emergency",
        "priority": "emergency",
        "status": "executing",
        "origin": {"lat": 39.9058, "lon": 116.4387, "alt": 5.0},
        "destination": {"lat": 39.9221, "lon": 116.4533, "alt": 5.0},
        "planned_start": "2024-01-15T09:30:00",
    },
    {
        "id": "task-survey-001",
        "name": "望京区域测绘任务",
        "drone_id": "drone-005",
        "task_type": "survey",
        "priority": "low",
        "status": "pending",
        "origin": {"lat": 40.0010, "lon": 116.4680, "alt": 5.0},
        "destination": {"lat": 40.0192, "lon": 116.4912, "alt": 5.0},
        "planned_start": "2024-01-15T14:00:00",
    },
    # 故意冲突的两条路线
    {
        "id": "task-conflict-001",
        "name": "朝阳路东向配送（冲突测试）",
        "drone_id": "drone-006",
        "task_type": "delivery",
        "priority": "normal",
        "status": "planning",
        "origin": {"lat": 39.9300, "lon": 116.4400, "alt": 5.0},
        "destination": {"lat": 39.9300, "lon": 116.4700, "alt": 5.0},
        "planned_start": "2024-01-15T11:00:00",
    },
    {
        "id": "task-conflict-002",
        "name": "朝阳路西向配送（冲突测试）",
        "drone_id": "drone-007",
        "task_type": "delivery",
        "priority": "normal",
        "status": "planning",
        "origin": {"lat": 39.9310, "lon": 116.4700, "alt": 5.0},
        "destination": {"lat": 39.9310, "lon": 116.4400, "alt": 5.0},
        "planned_start": "2024-01-15T11:00:00",
    },
]

DEMO_DRONES = [
    {"drone_id": "drone-001", "name": "朝阳快鸟-01", "model": "DJI Matrice 300 RTK", "battery_level": 85},
    {"drone_id": "drone-002", "name": "朝阳快鸟-02", "model": "DJI Matrice 300 RTK", "battery_level": 92},
    {"drone_id": "drone-003", "name": "巡检鹰-01", "model": "DJI M30T", "battery_level": 78},
    {"drone_id": "drone-004", "name": "急救翼-01", "model": "Wingcopter 198", "battery_level": 99},
    {"drone_id": "drone-005", "name": "测绘星-01", "model": "DJI Phantom 4 RTK", "battery_level": 60},
    {"drone_id": "drone-006", "name": "测试机-01", "model": "DJI Mini 3", "battery_level": 70},
    {"drone_id": "drone-007", "name": "测试机-02", "model": "DJI Mini 3", "battery_level": 65},
]


class SimulationService:
    """飞行仿真服务"""

    def __init__(self):
        self._task_routes: Dict[str, List[Dict]] = {}
        self._simulation_start = time.time()

    def get_demo_tasks(self) -> List[Dict[str, Any]]:
        """获取演示任务列表"""
        return DEMO_TASKS

    def get_demo_drones(self) -> List[Dict[str, Any]]:
        """获取演示无人机列表"""
        return DEMO_DRONES

    def generate_route_for_task(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """为演示任务生成模拟航路（抛物线轨迹）"""
        origin = task["origin"]
        dest = task["destination"]
        task_type = task.get("task_type", "delivery")

        # 根据任务类型设置高度
        alt_map = {
            "delivery": 60.0,
            "inspection": 80.0,
            "emergency": 70.0,
            "survey": 100.0,
            "patrol": 50.0,
        }
        cruise_alt = alt_map.get(task_type, 60.0)

        steps = 20
        waypoints = []
        for i in range(steps + 1):
            t = i / steps
            lat = origin["lat"] + t * (dest["lat"] - origin["lat"])
            lon = origin["lon"] + t * (dest["lon"] - origin["lon"])
            # 抛物线高度
            alt = 5 + 4 * cruise_alt * t * (1 - t) + (origin.get("alt", 5) * (1 - t) + dest.get("alt", 5) * t)
            speed = 10.0 if 0 < i < steps else 0.0
            waypoints.append({
                "lat": round(lat, 7),
                "lon": round(lon, 7),
                "alt": round(alt, 1),
                "speed": speed,
                "timestamp": round(i * 15.0, 1),
            })

        self._task_routes[task["id"]] = waypoints
        return waypoints

    def get_current_position(
        self, task_id: str, elapsed_seconds: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """获取无人机当前仿真位置"""
        route = self._task_routes.get(task_id)
        if not route:
            return None

        if elapsed_seconds is None:
            elapsed_seconds = (time.time() - self._simulation_start) % route[-1]["timestamp"]

        # 插值
        for i in range(len(route) - 1):
            t0 = route[i]["timestamp"]
            t1 = route[i + 1]["timestamp"]
            if t0 <= elapsed_seconds <= t1:
                ratio = (elapsed_seconds - t0) / max(t1 - t0, 0.001)
                lat = route[i]["lat"] + ratio * (route[i + 1]["lat"] - route[i]["lat"])
                lon = route[i]["lon"] + ratio * (route[i + 1]["lon"] - route[i]["lon"])
                alt = route[i]["alt"] + ratio * (route[i + 1]["alt"] - route[i]["alt"])
                return {
                    "task_id": task_id,
                    "lat": round(lat, 7),
                    "lon": round(lon, 7),
                    "alt": round(alt, 1),
                    "speed": route[i]["speed"],
                    "heading": self._calc_heading(route[i], route[i + 1]),
                    "timestamp": elapsed_seconds,
                }
        return None

    def _calc_heading(self, wp1: Dict, wp2: Dict) -> float:
        """计算两点之间的航向角"""
        dlat = wp2["lat"] - wp1["lat"]
        dlon = wp2["lon"] - wp1["lon"]
        angle = math.degrees(math.atan2(dlon, dlat))
        return (angle + 360) % 360
