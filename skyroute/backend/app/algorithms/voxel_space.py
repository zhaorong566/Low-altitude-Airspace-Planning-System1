"""
体素空间模块 - 将三维空间离散化为体素格网，用于路径规划的障碍物表示
"""
import numpy as np
from typing import Tuple, List, Optional
import math


class VoxelSpace:
    """
    三维体素空间
    将经纬度高度坐标系转换为整数体素坐标，支持障碍物标记和碰撞检测
    """

    def __init__(
        self,
        lat_min: float,
        lat_max: float,
        lon_min: float,
        lon_max: float,
        alt_min: float = 0.0,
        alt_max: float = 200.0,
        voxel_size: float = 10.0,
    ):
        self.lat_min = lat_min
        self.lat_max = lat_max
        self.lon_min = lon_min
        self.lon_max = lon_max
        self.alt_min = alt_min
        self.alt_max = alt_max
        self.voxel_size = voxel_size

        # 计算每个维度的体素数量
        # 纬度1度≈111000米，经度1度在北京约≈89000米
        self.lat_scale = 111000.0 / voxel_size
        self.lon_scale = 89000.0 / voxel_size
        self.alt_scale = 1.0 / voxel_size

        nx = max(1, int((lat_max - lat_min) * self.lat_scale) + 1)
        ny = max(1, int((lon_max - lon_min) * self.lon_scale) + 1)
        nz = max(1, int((alt_max - alt_min) * self.alt_scale) + 1)

        # 使用布尔数组存储障碍物
        self.grid = np.zeros((nx, ny, nz), dtype=bool)
        self.shape = (nx, ny, nz)

    def geo_to_voxel(self, lat: float, lon: float, alt: float) -> Tuple[int, int, int]:
        """将地理坐标转换为体素坐标"""
        x = int((lat - self.lat_min) * self.lat_scale)
        y = int((lon - self.lon_min) * self.lon_scale)
        z = int((alt - self.alt_min) * self.alt_scale)
        # 限制在网格范围内
        x = max(0, min(x, self.shape[0] - 1))
        y = max(0, min(y, self.shape[1] - 1))
        z = max(0, min(z, self.shape[2] - 1))
        return x, y, z

    def voxel_to_geo(self, x: int, y: int, z: int) -> Tuple[float, float, float]:
        """将体素坐标转换回地理坐标"""
        lat = self.lat_min + (x + 0.5) / self.lat_scale
        lon = self.lon_min + (y + 0.5) / self.lon_scale
        alt = self.alt_min + (z + 0.5) / self.alt_scale
        return lat, lon, alt

    def mark_obstacle(self, lat: float, lon: float, alt: float, radius: float = 50.0):
        """在指定位置标记圆柱形障碍物"""
        cx, cy, cz = self.geo_to_voxel(lat, lon, alt)
        r_x = int(radius / (111000.0 / self.voxel_size) * self.lat_scale) + 1
        r_y = int(radius / (89000.0 / self.voxel_size) * self.lon_scale) + 1

        for dx in range(-r_x, r_x + 1):
            for dy in range(-r_y, r_y + 1):
                nx_idx = cx + dx
                ny_idx = cy + dy
                if 0 <= nx_idx < self.shape[0] and 0 <= ny_idx < self.shape[1]:
                    # 整列高度标记为障碍
                    self.grid[nx_idx, ny_idx, :] = True

    def mark_no_fly_zone(
        self,
        lat_center: float,
        lon_center: float,
        radius_m: float,
        alt_min: float = 0.0,
        alt_max: float = 200.0,
    ):
        """标记禁飞区（圆形区域，带高度范围）"""
        cx, cy, _ = self.geo_to_voxel(lat_center, lon_center, alt_min)
        _, _, z_min = self.geo_to_voxel(lat_center, lon_center, alt_min)
        _, _, z_max = self.geo_to_voxel(lat_center, lon_center, alt_max)

        r_x = int(radius_m * self.lat_scale / 111000.0) + 2
        r_y = int(radius_m * self.lon_scale / 89000.0) + 2

        for dx in range(-r_x, r_x + 1):
            for dy in range(-r_y, r_y + 1):
                xi = cx + dx
                yi = cy + dy
                if 0 <= xi < self.shape[0] and 0 <= yi < self.shape[1]:
                    # 计算实际距离
                    dlat = dx / self.lat_scale
                    dlon = dy / self.lon_scale
                    dist = math.sqrt(
                        (dlat * 111000.0) ** 2 + (dlon * 89000.0) ** 2
                    )
                    if dist <= radius_m:
                        for zi in range(z_min, min(z_max + 1, self.shape[2])):
                            self.grid[xi, yi, zi] = True

    def is_occupied(self, lat: float, lon: float, alt: float) -> bool:
        """检查指定坐标是否被障碍物占据"""
        x, y, z = self.geo_to_voxel(lat, lon, alt)
        return bool(self.grid[x, y, z])

    def is_voxel_occupied(self, x: int, y: int, z: int) -> bool:
        """检查指定体素坐标是否被占据"""
        if not (0 <= x < self.shape[0] and 0 <= y < self.shape[1] and 0 <= z < self.shape[2]):
            return True  # 边界外视为障碍
        return bool(self.grid[x, y, z])

    def get_neighbors(self, x: int, y: int, z: int) -> List[Tuple[int, int, int]]:
        """获取26-连通邻居体素（3D网格）"""
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                for dz in [-1, 0, 1]:
                    if dx == 0 and dy == 0 and dz == 0:
                        continue
                    nx_idx = x + dx
                    ny_idx = y + dy
                    nz_idx = z + dz
                    if (
                        0 <= nx_idx < self.shape[0]
                        and 0 <= ny_idx < self.shape[1]
                        and 0 <= nz_idx < self.shape[2]
                        and not self.grid[nx_idx, ny_idx, nz_idx]
                    ):
                        neighbors.append((nx_idx, ny_idx, nz_idx))
        return neighbors
