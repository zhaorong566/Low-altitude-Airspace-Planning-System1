"""
路径规划模块 - 基于3D A*算法的无人机航路规划
支持禁飞区避让、噪音区域规避和高度优化
"""
import heapq
import math
from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass, field
import numpy as np

from app.algorithms.voxel_space import VoxelSpace


@dataclass(order=True)
class PQNode:
    """优先队列节点"""
    f_cost: float
    x: int = field(compare=False)
    y: int = field(compare=False)
    z: int = field(compare=False)
    g_cost: float = field(compare=False)
    parent: Optional[Tuple[int, int, int]] = field(default=None, compare=False)


class PathPlanner:
    """
    3D A*路径规划器
    在体素空间中寻找从起点到终点的最优路径
    """

    def __init__(
        self,
        voxel_space: VoxelSpace,
        noise_zones: Optional[List[Dict]] = None,
        preferred_altitude: float = 60.0,
        max_altitude: float = 120.0,
    ):
        self.voxel_space = voxel_space
        self.noise_zones = noise_zones or []
        self.preferred_altitude = preferred_altitude
        self.max_altitude = max_altitude

    def _heuristic(self, x1: int, y1: int, z1: int, x2: int, y2: int, z2: int) -> float:
        """3D欧氏距离启发函数"""
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2)

    def _altitude_penalty(self, z: int) -> float:
        """
        高度惩罚函数
        - 过低高度（<30m）增加惩罚
        - 过高高度（>100m）增加惩罚
        - 最优高度约60m
        """
        lat, lon, alt = self.voxel_space.voxel_to_geo(0, 0, z)
        if alt < 30:
            return 2.0 * (30 - alt) / 30
        elif alt > 100:
            return 1.5 * (alt - 100) / 100
        return 0.0

    def _noise_penalty(self, lat: float, lon: float) -> float:
        """噪音区域惩罚，靠近噪音敏感区域增加代价"""
        penalty = 0.0
        for zone in self.noise_zones:
            zlat = zone.get("lat", 0)
            zlon = zone.get("lon", 0)
            zradius = zone.get("radius", 100)
            dist = math.sqrt(
                ((lat - zlat) * 111000) ** 2 + ((lon - zlon) * 89000) ** 2
            )
            if dist < zradius:
                penalty += 3.0 * (1 - dist / zradius)
        return penalty

    def _move_cost(
        self,
        x1: int, y1: int, z1: int,
        x2: int, y2: int, z2: int,
    ) -> float:
        """计算从一个体素移动到相邻体素的代价"""
        base_cost = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2)
        lat2, lon2, alt2 = self.voxel_space.voxel_to_geo(x2, y2, z2)
        altitude_pen = self._altitude_penalty(z2)
        noise_pen = self._noise_penalty(lat2, lon2)
        return base_cost * (1.0 + altitude_pen + noise_pen)

    def plan(
        self,
        origin: Tuple[float, float, float],
        destination: Tuple[float, float, float],
    ) -> Optional[List[Dict[str, Any]]]:
        """
        执行A*路径规划
        
        Args:
            origin: (lat, lon, alt) 起点地理坐标
            destination: (lat, lon, alt) 终点地理坐标
            
        Returns:
            航路点列表，每个元素包含lat, lon, alt
        """
        vs = self.voxel_space
        start = vs.geo_to_voxel(*origin)
        goal = vs.geo_to_voxel(*destination)

        if vs.is_voxel_occupied(*start):
            # 起点在障碍内，向上移动
            start = (start[0], start[1], start[2] + 3)
        if vs.is_voxel_occupied(*goal):
            goal = (goal[0], goal[1], goal[2] + 3)

        open_set: List[PQNode] = []
        closed_set: set = set()
        came_from: Dict[Tuple[int, int, int], Optional[Tuple[int, int, int]]] = {}
        g_costs: Dict[Tuple[int, int, int], float] = {}

        g_costs[start] = 0.0
        h = self._heuristic(*start, *goal)
        heapq.heappush(open_set, PQNode(h, *start, 0.0, None))
        came_from[start] = None

        max_iterations = 50000
        iterations = 0

        while open_set and iterations < max_iterations:
            iterations += 1
            current = heapq.heappop(open_set)
            cx, cy, cz = current.x, current.y, current.z
            pos = (cx, cy, cz)

            if pos in closed_set:
                continue
            closed_set.add(pos)

            # 到达终点
            if (abs(cx - goal[0]) <= 1 and abs(cy - goal[1]) <= 1 and abs(cz - goal[2]) <= 1):
                return self._reconstruct_path(came_from, pos, origin, destination)

            for neighbor in vs.get_neighbors(cx, cy, cz):
                if neighbor in closed_set:
                    continue
                nx, ny, nz = neighbor
                tentative_g = g_costs.get(pos, float('inf')) + self._move_cost(cx, cy, cz, nx, ny, nz)

                if tentative_g < g_costs.get(neighbor, float('inf')):
                    g_costs[neighbor] = tentative_g
                    came_from[neighbor] = pos
                    h = self._heuristic(nx, ny, nz, *goal)
                    heapq.heappush(open_set, PQNode(tentative_g + h, nx, ny, nz, tentative_g, pos))

        # 未找到路径，返回直线路径（降级策略）
        return self._fallback_path(origin, destination)

    def _reconstruct_path(
        self,
        came_from: Dict,
        end: Tuple[int, int, int],
        origin: Tuple[float, float, float],
        destination: Tuple[float, float, float],
    ) -> List[Dict[str, Any]]:
        """重建路径，将体素坐标转回地理坐标"""
        path = []
        current = end
        while came_from.get(current) is not None:
            lat, lon, alt = self.voxel_space.voxel_to_geo(*current)
            path.append({"lat": round(lat, 7), "lon": round(lon, 7), "alt": round(alt, 1), "speed": 10.0})
            current = came_from[current]

        path.reverse()
        # 添加精确起终点
        waypoints = [
            {"lat": origin[0], "lon": origin[1], "alt": origin[2], "speed": 0.0},
            *path,
            {"lat": destination[0], "lon": destination[1], "alt": destination[2], "speed": 0.0},
        ]
        # 添加时间戳
        elapsed = 0.0
        for i, wp in enumerate(waypoints):
            if i > 0:
                prev = waypoints[i - 1]
                dist = math.sqrt(
                    ((wp["lat"] - prev["lat"]) * 111000) ** 2
                    + ((wp["lon"] - prev["lon"]) * 89000) ** 2
                    + (wp["alt"] - prev["alt"]) ** 2
                )
                elapsed += dist / max(wp["speed"], 1.0)
            wp["timestamp"] = round(elapsed, 1)
        return waypoints

    def _fallback_path(
        self,
        origin: Tuple[float, float, float],
        destination: Tuple[float, float, float],
    ) -> List[Dict[str, Any]]:
        """降级策略：返回带中间点的直线路径"""
        steps = 10
        waypoints = []
        for i in range(steps + 1):
            t = i / steps
            lat = origin[0] + t * (destination[0] - origin[0])
            lon = origin[1] + t * (destination[1] - origin[1])
            # 抛物线高度剖面
            alt = origin[2] + t * (destination[2] - origin[2]) + 4 * self.preferred_altitude * t * (1 - t)
            speed = 10.0 if 0 < i < steps else 0.0
            waypoints.append({
                "lat": round(lat, 7),
                "lon": round(lon, 7),
                "alt": round(alt, 1),
                "speed": speed,
                "timestamp": round(i * 30.0, 1),
            })
        return waypoints
