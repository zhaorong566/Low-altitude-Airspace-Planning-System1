"""
规划服务 - 整合体素空间、路径规划和优化模块
"""
import math
from typing import List, Dict, Any, Optional
from uuid import UUID

from app.algorithms.voxel_space import VoxelSpace
from app.algorithms.path_planner import PathPlanner
from app.algorithms.optimizer import RouteOptimizer
from app.algorithms.conflict_detector import ConflictDetector
from app.core.config import settings


# 北京朝阳区预设禁飞区
BEIJING_NO_FLY_ZONES = [
    {"name": "首都机场限制区", "lat": 40.0799, "lon": 116.5877, "radius": 5000},
    {"name": "中南海禁飞区", "lat": 39.9197, "lon": 116.3835, "radius": 2000},
    {"name": "天安门广场", "lat": 39.9042, "lon": 116.3975, "radius": 1500},
    {"name": "国贸核心区", "lat": 39.9090, "lon": 116.4607, "radius": 800},
    {"name": "朝阳公园禁区", "lat": 39.9357, "lon": 116.4814, "radius": 600},
]

# 噪音敏感区域
NOISE_ZONES = [
    {"name": "朝阳医院", "lat": 39.9221, "lon": 116.4533, "radius": 300},
    {"name": "北京第二实验小学", "lat": 39.9168, "lon": 116.3958, "radius": 200},
    {"name": "朝阳居民区", "lat": 39.9430, "lon": 116.4590, "radius": 500},
    {"name": "三里屯居民区", "lat": 39.9368, "lon": 116.4547, "radius": 400},
    {"name": "望京居民密集区", "lat": 40.0047, "lon": 116.4731, "radius": 600},
]


class PlanningService:
    """路径规划服务"""

    def __init__(self):
        self.conflict_detector = ConflictDetector(
            horizontal_separation=settings.CONFLICT_SEPARATION_HORIZONTAL,
            vertical_separation=settings.CONFLICT_SEPARATION_VERTICAL,
        )

    def _create_voxel_space(
        self,
        origin: tuple,
        destination: tuple,
        padding: float = 0.05,
    ) -> VoxelSpace:
        """根据起终点创建体素空间"""
        lat_min = min(origin[0], destination[0]) - padding
        lat_max = max(origin[0], destination[0]) + padding
        lon_min = min(origin[1], destination[1]) - padding
        lon_max = max(origin[1], destination[1]) + padding

        vs = VoxelSpace(
            lat_min=lat_min,
            lat_max=lat_max,
            lon_min=lon_min,
            lon_max=lon_max,
            alt_min=0.0,
            alt_max=200.0,
            voxel_size=settings.VOXEL_SIZE,
        )

        # 标记禁飞区
        for zone in BEIJING_NO_FLY_ZONES:
            vs.mark_no_fly_zone(
                zone["lat"], zone["lon"], zone["radius"]
            )

        return vs

    async def plan_route(
        self,
        task_id: str,
        origin: tuple,
        destination: tuple,
        max_altitude: float = 120.0,
        preferred_speed: float = 10.0,
    ) -> Dict[str, Any]:
        """
        规划单条航路
        
        Returns:
            包含waypoints和评分的字典
        """
        vs = self._create_voxel_space(origin, destination)
        planner = PathPlanner(
            voxel_space=vs,
            noise_zones=NOISE_ZONES,
            preferred_altitude=60.0,
            max_altitude=max_altitude,
        )

        waypoints = planner.plan(origin, destination)
        if not waypoints:
            raise ValueError(f"无法为任务{task_id}规划路径")

        optimizer = RouteOptimizer(noise_zones=NOISE_ZONES)
        waypoints = optimizer.smooth_path(waypoints)
        waypoints = optimizer.optimize_altitude(waypoints)
        scores = optimizer.score_route(waypoints)

        return {
            "task_id": task_id,
            "waypoints": waypoints,
            **scores,
        }

    def detect_conflicts(self, tasks: List[Dict]) -> List[Dict]:
        """检测多任务间冲突"""
        conflicts = self.conflict_detector.detect_all(tasks)
        return [
            {
                "task_id_1": c.task_id_1,
                "task_id_2": c.task_id_2,
                "lat": c.conflict_lat,
                "lon": c.conflict_lon,
                "alt": c.conflict_alt,
                "time": c.conflict_time,
                "severity": c.severity.value,
                "h_sep": c.horizontal_separation,
                "v_sep": c.vertical_separation,
                "description": c.description,
            }
            for c in conflicts
        ]
