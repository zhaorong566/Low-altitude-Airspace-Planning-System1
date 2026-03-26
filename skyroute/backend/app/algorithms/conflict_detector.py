"""
冲突检测模块 - 4D冲突检测（三维空间 + 时间维度）
检测多架无人机路径之间的时空冲突
"""
import math
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ConflictSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Conflict:
    task_id_1: str
    task_id_2: str
    conflict_lat: float
    conflict_lon: float
    conflict_alt: float
    conflict_time: float
    severity: ConflictSeverity
    horizontal_separation: float
    vertical_separation: float
    description: str


class ConflictDetector:
    """
    4D冲突检测器
    使用时空插值法检测两条航路之间的最近点
    """

    def __init__(
        self,
        horizontal_separation: float = 50.0,
        vertical_separation: float = 30.0,
        time_step: float = 1.0,
    ):
        """
        Args:
            horizontal_separation: 水平安全间隔（米）
            vertical_separation: 垂直安全间隔（米）
            time_step: 时间步长（秒）
        """
        self.h_sep = horizontal_separation
        self.v_sep = vertical_separation
        self.time_step = time_step

    def _interpolate_position(
        self,
        waypoints: List[Dict],
        t: float,
    ) -> Optional[Tuple[float, float, float]]:
        """在给定时间t对航路点进行插值，获取位置"""
        if not waypoints:
            return None
        if t <= waypoints[0].get("timestamp", 0):
            return waypoints[0]["lat"], waypoints[0]["lon"], waypoints[0]["alt"]
        if t >= waypoints[-1].get("timestamp", 0):
            return waypoints[-1]["lat"], waypoints[-1]["lon"], waypoints[-1]["alt"]

        for i in range(len(waypoints) - 1):
            t0 = waypoints[i].get("timestamp", i * 30.0)
            t1 = waypoints[i + 1].get("timestamp", (i + 1) * 30.0)
            if t0 <= t <= t1:
                if t1 == t0:
                    ratio = 0.0
                else:
                    ratio = (t - t0) / (t1 - t0)
                lat = waypoints[i]["lat"] + ratio * (waypoints[i + 1]["lat"] - waypoints[i]["lat"])
                lon = waypoints[i]["lon"] + ratio * (waypoints[i + 1]["lon"] - waypoints[i]["lon"])
                alt = waypoints[i]["alt"] + ratio * (waypoints[i + 1]["alt"] - waypoints[i]["alt"])
                return lat, lon, alt

        return None

    def _horizontal_distance(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """计算水平距离（米）"""
        dlat = (lat1 - lat2) * 111000.0
        dlon = (lon1 - lon2) * 89000.0
        return math.sqrt(dlat ** 2 + dlon ** 2)

    def detect(
        self,
        task_id_1: str,
        waypoints_1: List[Dict],
        task_id_2: str,
        waypoints_2: List[Dict],
    ) -> List[Conflict]:
        """
        检测两条航路之间的冲突
        
        Returns:
            冲突列表
        """
        conflicts = []
        if not waypoints_1 or not waypoints_2:
            return conflicts

        # 确定检测时间范围
        t_start = max(
            waypoints_1[0].get("timestamp", 0),
            waypoints_2[0].get("timestamp", 0),
        )
        t_end = min(
            waypoints_1[-1].get("timestamp", 0),
            waypoints_2[-1].get("timestamp", 0),
        )

        if t_end <= t_start:
            return conflicts

        t = t_start
        in_conflict = False
        last_conflict: Optional[Conflict] = None

        while t <= t_end:
            pos1 = self._interpolate_position(waypoints_1, t)
            pos2 = self._interpolate_position(waypoints_2, t)

            if pos1 is None or pos2 is None:
                t += self.time_step
                continue

            lat1, lon1, alt1 = pos1
            lat2, lon2, alt2 = pos2

            h_dist = self._horizontal_distance(lat1, lon1, lat2, lon2)
            v_dist = abs(alt1 - alt2)

            if h_dist < self.h_sep and v_dist < self.v_sep:
                if not in_conflict:
                    in_conflict = True
                    # 冲突严重程度判断
                    h_ratio = h_dist / self.h_sep
                    v_ratio = v_dist / self.v_sep
                    combined = (h_ratio + v_ratio) / 2

                    if combined < 0.2:
                        severity = ConflictSeverity.CRITICAL
                    elif combined < 0.5:
                        severity = ConflictSeverity.HIGH
                    elif combined < 0.7:
                        severity = ConflictSeverity.MEDIUM
                    else:
                        severity = ConflictSeverity.LOW

                    conflict = Conflict(
                        task_id_1=task_id_1,
                        task_id_2=task_id_2,
                        conflict_lat=(lat1 + lat2) / 2,
                        conflict_lon=(lon1 + lon2) / 2,
                        conflict_alt=(alt1 + alt2) / 2,
                        conflict_time=t,
                        severity=severity,
                        horizontal_separation=round(h_dist, 2),
                        vertical_separation=round(v_dist, 2),
                        description=f"水平间隔{h_dist:.1f}m，垂直间隔{v_dist:.1f}m，时间{t:.0f}s",
                    )
                    last_conflict = conflict
                    conflicts.append(conflict)
            else:
                in_conflict = False

            t += self.time_step

        return conflicts

    def detect_all(
        self,
        tasks: List[Dict[str, Any]],
    ) -> List[Conflict]:
        """批量检测所有任务之间的冲突"""
        all_conflicts = []
        for i in range(len(tasks)):
            for j in range(i + 1, len(tasks)):
                t1 = tasks[i]
                t2 = tasks[j]
                wp1 = t1.get("waypoints", [])
                wp2 = t2.get("waypoints", [])
                conflicts = self.detect(
                    str(t1.get("id", i)),
                    wp1,
                    str(t2.get("id", j)),
                    wp2,
                )
                all_conflicts.extend(conflicts)
        return all_conflicts
