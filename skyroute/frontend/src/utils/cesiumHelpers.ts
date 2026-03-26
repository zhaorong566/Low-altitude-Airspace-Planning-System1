// Cesium辅助工具函数

export function latLonAltToCartesian(Cesium: any, lat: number, lon: number, alt: number) {
  return Cesium.Cartesian3.fromDegrees(lon, lat, alt)
}

export function waypointsToPositions(Cesium: any, waypoints: Array<{ lat: number; lon: number; alt: number }>) {
  return waypoints.flatMap(wp => [wp.lon, wp.lat, wp.alt])
}

export function createColorMaterial(Cesium: any, color: any, alpha = 1.0) {
  return new Cesium.ColorMaterialProperty(color.withAlpha(alpha))
}

export function getTaskColor(Cesium: any, taskType: string, status: string) {
  if (status === 'executing') {
    switch (taskType) {
      case 'emergency': return Cesium.Color.RED
      case 'delivery': return Cesium.Color.CYAN
      case 'inspection': return Cesium.Color.YELLOW
      case 'survey': return Cesium.Color.MAGENTA
      default: return Cesium.Color.WHITE
    }
  }
  if (status === 'approved') return Cesium.Color.GREEN
  if (status === 'pending') return Cesium.Color.GRAY
  return Cesium.Color.WHITE
}

export function getSeverityColor(Cesium: any, severity: string) {
  switch (severity) {
    case 'critical': return Cesium.Color.RED
    case 'high': return Cesium.Color.ORANGE
    case 'medium': return Cesium.Color.YELLOW
    default: return Cesium.Color.WHITE
  }
}

export function metersToCartographicRadians(Cesium: any, meters: number) {
  return meters / Cesium.Ellipsoid.WGS84.maximumRadius
}
