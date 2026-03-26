// ===== 坐标与航路类型 =====

export interface Waypoint {
  lat: number
  lon: number
  alt: number
  speed?: number
  timestamp?: number
}

export interface Route {
  id: string
  taskId: string
  waypoints: Waypoint[]
  totalDistance: number
  totalDuration: number
  minAltitude: number
  maxAltitude: number
  avgAltitude: number
  riskScore: number
  noiseScore: number
  efficiencyScore: number
  version: number
  createdAt: string
}

// ===== 任务类型 =====

export enum TaskStatus {
  PENDING = 'pending',
  PLANNING = 'planning',
  APPROVED = 'approved',
  EXECUTING = 'executing',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
}

export enum TaskPriority {
  LOW = 'low',
  NORMAL = 'normal',
  HIGH = 'high',
  EMERGENCY = 'emergency',
}

export enum TaskType {
  DELIVERY = 'delivery',
  INSPECTION = 'inspection',
  EMERGENCY = 'emergency',
  SURVEY = 'survey',
  PATROL = 'patrol',
}

export interface GeoPoint {
  lat: number
  lon: number
  alt: number
}

export interface FlightTask {
  id: string
  name: string
  droneId: string
  drone_id?: string
  status: TaskStatus | string
  taskType: TaskType | string
  task_type?: string
  priority: TaskPriority | string
  origin: GeoPoint
  destination: GeoPoint
  waypoints?: Waypoint[]
  plannedStart?: string
  planned_start?: string
  actualStart?: string
  actualEnd?: string
  routeData?: Route
  routeScores?: {
    risk?: number
    noise?: number
    efficiency?: number
  }
  createdAt?: string
}

// ===== 无人机类型 =====

export interface DronePosition {
  droneId: string
  drone_id?: string
  taskId?: string
  task_id?: string
  lat: number
  lon: number
  alt: number
  heading: number
  speed: number
  batteryLevel?: number
  timestamp: number
}

export interface Drone {
  id?: string
  droneId: string
  drone_id?: string
  name: string
  model: string
  currentLat?: number
  currentLon?: number
  currentAlt?: number
  batteryLevel: number
  battery_level?: number
  maxPayload: number
  maxSpeed: number
  maxAltitude: number
  isAvailable: boolean
  currentTaskId?: string
}

// ===== 冲突类型 =====

export enum ConflictSeverity {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

export interface Conflict {
  taskId1: string
  task_id_1?: string
  taskId2: string
  task_id_2?: string
  lat: number
  lon: number
  alt: number
  time: number
  severity: ConflictSeverity | string
  hSep: number
  h_sep?: number
  vSep: number
  v_sep?: number
  description: string
}

// ===== 天气类型 =====

export interface WeatherData {
  temperature: number
  humidity: number
  pressure: number
  windSpeed: number
  wind_speed?: number
  windDirection: number
  wind_direction?: number
  visibility: number
  cloudCover: number
  cloud_cover?: number
  weatherCode: number
  description: string
  flightRisk: string
  flight_risk?: string
  timestamp: string
}

// ===== API响应类型 =====

export interface ApiResponse<T> {
  data?: T
  message?: string
  error?: string
}

export interface TaskListResponse {
  tasks: FlightTask[]
  total: number
  limit?: number
  offset?: number
}

export interface PlanningRequest {
  taskId: string
  avoidNoFly?: boolean
  avoidNoise?: boolean
  optimizeAltitude?: boolean
  maxAltitude?: number
  preferredSpeed?: number
}

// ===== 统计类型 =====

export interface SystemStats {
  totalTasks: number
  executingTasks: number
  pendingTasks: number
  completedToday: number
  activeDrones: number
  conflictCount: number
  avgEfficiency: number
}
