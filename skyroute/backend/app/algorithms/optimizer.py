"""
路径优化模块 - B样条平滑、高度优化和多目标评分
"""
import math
import numpy as np
from typing import List, Dict, Any, Optional


class RouteOptimizer:
    """
    路径优化器
    对A*算法生成的折线路径进行平滑处理，并进行多目标优化
    """

    def __init__(
        self,
        noise_zones: Optional[List[Dict]] = None,
        preferred_altitude: float = 60.0,
    ):
        self.noise_zones = noise_zones or []
        self.preferred_altitude = preferred_altitude

    def smooth_path(
        self,
        waypoints: List[Dict[str, Any]],
        tension: float = 0.5,
        num_points: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Catmull-Rom样条曲线平滑路径
        
        Args:
            waypoints: 原始航路点列表
            tension: 张力系数（0-1）
            num_points: 输出点数量
        """
        if len(waypoints) < 3:
            return waypoints

        lats = np.array([wp["lat"] for wp in waypoints])
        lons = np.array([wp["lon"] for wp in waypoints])
        alts = np.array([wp["alt"] for wp in waypoints])

        # 添加首尾控制点（反射法）
        lats_ext = np.concatenate([[2 * lats[0] - lats[1]], lats, [2 * lats[-1] - lats[-2]]])
        lons_ext = np.concatenate([[2 * lons[0] - lons[1]], lons, [2 * lons[-1] - lons[-2]]])
        alts_ext = np.concatenate([[2 * alts[0] - alts[1]], alts, [2 * alts[-1] - alts[-2]]])

        smooth_lats = []
        smooth_lons = []
        smooth_alts = []

        n_segments = len(lats)
        pts_per_segment = max(2, num_points // n_segments)

        for i in range(1, len(lats_ext) - 2):
            p0 = np.array([lats_ext[i - 1], lons_ext[i - 1], alts_ext[i - 1]])
            p1 = np.array([lats_ext[i], lons_ext[i], alts_ext[i]])
            p2 = np.array([lats_ext[i + 1], lons_ext[i + 1], alts_ext[i + 1]])
            p3 = np.array([lats_ext[i + 2], lons_ext[i + 2], alts_ext[i + 2]])

            for j in range(pts_per_segment):
                t = j / pts_per_segment
                # Catmull-Rom公式
                point = (
                    0.5 * (
                        (2 * p1)
                        + (-p0 + p2) * t
                        + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t ** 2
                        + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3
                    )
                )
                smooth_lats.append(point[0])
                smooth_lons.append(point[1])
                smooth_alts.append(max(20.0, point[2]))  # 最低高度20m

        # 添加终点
        smooth_lats.append(lats[-1])
        smooth_lons.append(lons[-1])
        smooth_alts.append(alts[-1])

        # 构建输出航路点并重新计算时间戳
        smoothed = []
        elapsed = 0.0
        speed = 10.0
        for i, (lat, lon, alt) in enumerate(zip(smooth_lats, smooth_lons, smooth_alts)):
            if i > 0:
                dlat = (lat - smooth_lats[i - 1]) * 111000
                dlon = (lon - smooth_lons[i - 1]) * 89000
                dalt = alt - smooth_alts[i - 1]
                dist = math.sqrt(dlat ** 2 + dlon ** 2 + dalt ** 2)
                elapsed += dist / speed
            smoothed.append({
                "lat": round(lat, 7),
                "lon": round(lon, 7),
                "alt": round(alt, 1),
                "speed": speed,
                "timestamp": round(elapsed, 1),
            })
        return smoothed

    def optimize_altitude(
        self,
        waypoints: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        高度优化：调整路径高度使其更平滑，避免急剧变化
        优先保持在推荐高度范围内
        """
        if len(waypoints) < 2:
            return waypoints

        optimized = list(waypoints)
        for i in range(1, len(optimized) - 1):
            prev_alt = optimized[i - 1]["alt"]
            next_alt = optimized[i + 1]["alt"]
            current_alt = optimized[i]["alt"]

            # 平滑插值
            smooth_alt = (prev_alt + current_alt + next_alt) / 3.0
            # 约束在推荐高度附近
            target = (smooth_alt + self.preferred_altitude) / 2.0
            optimized[i] = {**optimized[i], "alt": round(max(20.0, min(150.0, target)), 1)}

        return optimized

    def score_route(
        self,
        waypoints: List[Dict[str, Any]],
    ) -> Dict[str, float]:
        """
        多目标路径评分
        
        Returns:
            dict with risk_score, noise_score, efficiency_score (0-100)
        """
        if len(waypoints) < 2:
            return {"risk_score": 50.0, "noise_score": 50.0, "efficiency_score": 50.0}

        # 计算总距离
        total_dist = 0.0
        altitude_variance = []
        noise_penalty = 0.0

        for i in range(len(waypoints) - 1):
            wp1, wp2 = waypoints[i], waypoints[i + 1]
            dlat = (wp2["lat"] - wp1["lat"]) * 111000
            dlon = (wp2["lon"] - wp1["lon"]) * 89000
            dalt = wp2["alt"] - wp1["alt"]
            dist = math.sqrt(dlat ** 2 + dlon ** 2 + dalt ** 2)
            total_dist += dist
            altitude_variance.append(wp2["alt"])

            # 噪音区域惩罚
            for zone in self.noise_zones:
                zd = math.sqrt(
                    ((wp2["lat"] - zone.get("lat", 0)) * 111000) ** 2
                    + ((wp2["lon"] - zone.get("lon", 0)) * 89000) ** 2
                )
                if zd < zone.get("radius", 200):
                    noise_penalty += 1.0

        # 效率评分（直线距离与实际距离之比）
        first, last = waypoints[0], waypoints[-1]
        direct_dist = math.sqrt(
            ((last["lat"] - first["lat"]) * 111000) ** 2
            + ((last["lon"] - first["lon"]) * 89000) ** 2
        )
        efficiency = min(100.0, (direct_dist / max(total_dist, 1)) * 100)

        # 风险评分（基于高度偏差）
        avg_alt = np.mean(altitude_variance) if altitude_variance else self.preferred_altitude
        alt_dev = abs(avg_alt - self.preferred_altitude)
        risk_score = max(0.0, 100.0 - alt_dev * 2)

        # 噪音评分
        noise_score = max(0.0, 100.0 - noise_penalty * 10)

        return {
            "risk_score": round(risk_score, 1),
            "noise_score": round(noise_score, 1),
            "efficiency_score": round(efficiency, 1),
            "total_distance": round(total_dist, 1),
            "total_duration": round(waypoints[-1].get("timestamp", 0), 1),
        }
