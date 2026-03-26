// 地理计算工具函数

const EARTH_RADIUS = 6371000 // meters

export function haversineDistance(
  lat1: number, lon1: number,
  lat2: number, lon2: number
): number {
  const R = EARTH_RADIUS
  const dLat = toRad(lat2 - lat1)
  const dLon = toRad(lon2 - lon1)
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
}

export function toRad(deg: number): number {
  return (deg * Math.PI) / 180
}

export function toDeg(rad: number): number {
  return (rad * 180) / Math.PI
}

export function bearing(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const dLon = toRad(lon2 - lon1)
  const y = Math.sin(dLon) * Math.cos(toRad(lat2))
  const x =
    Math.cos(toRad(lat1)) * Math.sin(toRad(lat2)) -
    Math.sin(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.cos(dLon)
  return (toDeg(Math.atan2(y, x)) + 360) % 360
}

export function routeLength(waypoints: Array<{ lat: number; lon: number; alt: number }>): number {
  let total = 0
  for (let i = 1; i < waypoints.length; i++) {
    const d = haversineDistance(
      waypoints[i - 1].lat, waypoints[i - 1].lon,
      waypoints[i].lat, waypoints[i].lon
    )
    const dAlt = waypoints[i].alt - waypoints[i - 1].alt
    total += Math.sqrt(d ** 2 + dAlt ** 2)
  }
  return total
}

export function formatDistance(meters: number): string {
  if (meters >= 1000) return `${(meters / 1000).toFixed(2)} km`
  return `${meters.toFixed(0)} m`
}

export function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}分${s.toString().padStart(2, '0')}秒`
}

export function interpolatePosition(
  waypoints: Array<{ lat: number; lon: number; alt: number; timestamp?: number }>,
  t: number
): { lat: number; lon: number; alt: number } | null {
  if (!waypoints.length) return null
  if (t <= (waypoints[0].timestamp || 0)) return waypoints[0]
  if (t >= (waypoints[waypoints.length - 1].timestamp || 0)) return waypoints[waypoints.length - 1]

  for (let i = 0; i < waypoints.length - 1; i++) {
    const t0 = waypoints[i].timestamp || i * 15
    const t1 = waypoints[i + 1].timestamp || (i + 1) * 15
    if (t0 <= t && t <= t1) {
      const r = (t - t0) / Math.max(t1 - t0, 0.001)
      return {
        lat: waypoints[i].lat + r * (waypoints[i + 1].lat - waypoints[i].lat),
        lon: waypoints[i].lon + r * (waypoints[i + 1].lon - waypoints[i].lon),
        alt: waypoints[i].alt + r * (waypoints[i + 1].alt - waypoints[i].alt),
      }
    }
  }
  return null
}
