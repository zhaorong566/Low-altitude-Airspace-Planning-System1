import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { FlightTask, SystemStats } from '@/types'
import { TaskStatus } from '@/types'
import { useRouteApi } from '@/composables/useRouteApi'

export const useTaskStore = defineStore('task', () => {
  const tasks = ref<FlightTask[]>([])
  const selectedTaskId = ref<string | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const api = useRouteApi()

  const selectedTask = computed(() =>
    tasks.value.find(t => t.id === selectedTaskId.value) || null
  )

  const executingTasks = computed(() =>
    tasks.value.filter(t => t.status === TaskStatus.EXECUTING || t.status === 'executing')
  )

  const pendingTasks = computed(() =>
    tasks.value.filter(t => t.status === TaskStatus.PENDING || t.status === 'pending')
  )

  const stats = computed<SystemStats>(() => ({
    totalTasks: tasks.value.length,
    executingTasks: executingTasks.value.length,
    pendingTasks: pendingTasks.value.length,
    completedToday: tasks.value.filter(t => t.status === 'completed').length,
    activeDrones: executingTasks.value.length,
    conflictCount: 0,
    avgEfficiency: tasks.value.reduce((acc, t) => acc + (t.routeScores?.efficiency || 80), 0) / Math.max(tasks.value.length, 1),
  }))

  async function fetchTasks() {
    loading.value = true
    error.value = null
    try {
      const data = await api.getTasks()
      tasks.value = data.tasks.map(normalizeTask)
    } catch (e: any) {
      error.value = e.message
      // 降级到演示数据
      tasks.value = getMockTasks()
    } finally {
      loading.value = false
    }
  }

  async function createTask(taskData: Partial<FlightTask>) {
    loading.value = true
    try {
      const result = await api.createTask(taskData)
      const normalized = normalizeTask(result)
      tasks.value.unshift(normalized)
      return normalized
    } catch (e: any) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  function selectTask(id: string | null) {
    selectedTaskId.value = id
  }

  function updateTaskFromSocket(data: Partial<FlightTask> & { id: string }) {
    const idx = tasks.value.findIndex(t => t.id === data.id)
    if (idx >= 0) {
      tasks.value[idx] = { ...tasks.value[idx], ...data }
    }
  }

  function normalizeTask(raw: any): FlightTask {
    return {
      id: raw.id,
      name: raw.name,
      droneId: raw.drone_id || raw.droneId,
      drone_id: raw.drone_id,
      status: raw.status,
      taskType: raw.task_type || raw.taskType || 'delivery',
      task_type: raw.task_type,
      priority: raw.priority || 'normal',
      origin: raw.origin || { lat: raw.origin_lat, lon: raw.origin_lon, alt: raw.origin_alt || 50 },
      destination: raw.destination || { lat: raw.dest_lat, lon: raw.dest_lon, alt: raw.dest_alt || 50 },
      waypoints: raw.waypoints || [],
      plannedStart: raw.planned_start || raw.plannedStart,
      planned_start: raw.planned_start,
      routeScores: raw.route_scores || raw.routeScores,
      createdAt: raw.created_at || raw.createdAt,
    }
  }

  function getMockTasks(): FlightTask[] {
    return [
      {
        id: 'task-delivery-001',
        name: '朝阳快递配送A线',
        droneId: 'drone-001',
        status: 'executing',
        taskType: 'delivery',
        priority: 'normal',
        origin: { lat: 39.9204, lon: 116.4430, alt: 5 },
        destination: { lat: 39.9524, lon: 116.4743, alt: 5 },
        waypoints: generateMockWaypoints(39.9204, 116.4430, 39.9524, 116.4743, 60),
        routeScores: { risk: 85, noise: 78, efficiency: 92 },
      },
      {
        id: 'task-delivery-002',
        name: '三里屯快递配送B线',
        droneId: 'drone-002',
        status: 'executing',
        taskType: 'delivery',
        priority: 'high',
        origin: { lat: 39.9312, lon: 116.4568, alt: 5 },
        destination: { lat: 39.9476, lon: 116.4201, alt: 5 },
        waypoints: generateMockWaypoints(39.9312, 116.4568, 39.9476, 116.4201, 55),
        routeScores: { risk: 72, noise: 65, efficiency: 88 },
      },
      {
        id: 'task-inspect-001',
        name: 'CBD建筑群巡检',
        droneId: 'drone-003',
        status: 'approved',
        taskType: 'inspection',
        priority: 'normal',
        origin: { lat: 39.9090, lon: 116.4607, alt: 5 },
        destination: { lat: 39.9156, lon: 116.4782, alt: 5 },
        waypoints: generateMockWaypoints(39.9090, 116.4607, 39.9156, 116.4782, 80),
        routeScores: { risk: 90, noise: 82, efficiency: 95 },
      },
      {
        id: 'task-emergency-001',
        name: '朝阳医院紧急医疗配送',
        droneId: 'drone-004',
        status: 'executing',
        taskType: 'emergency',
        priority: 'emergency',
        origin: { lat: 39.9058, lon: 116.4387, alt: 5 },
        destination: { lat: 39.9221, lon: 116.4533, alt: 5 },
        waypoints: generateMockWaypoints(39.9058, 116.4387, 39.9221, 116.4533, 70),
        routeScores: { risk: 95, noise: 60, efficiency: 98 },
      },
      {
        id: 'task-survey-001',
        name: '望京区域测绘任务',
        droneId: 'drone-005',
        status: 'pending',
        taskType: 'survey',
        priority: 'low',
        origin: { lat: 40.0010, lon: 116.4680, alt: 5 },
        destination: { lat: 40.0192, lon: 116.4912, alt: 5 },
        waypoints: generateMockWaypoints(40.0010, 116.4680, 40.0192, 116.4912, 100),
        routeScores: { risk: 88, noise: 85, efficiency: 75 },
      },
    ]
  }

  function generateMockWaypoints(
    lat1: number, lon1: number,
    lat2: number, lon2: number,
    cruiseAlt: number,
  ) {
    const steps = 20
    return Array.from({ length: steps + 1 }, (_, i) => {
      const t = i / steps
      return {
        lat: lat1 + t * (lat2 - lat1),
        lon: lon1 + t * (lon2 - lon1),
        alt: 5 + 4 * cruiseAlt * t * (1 - t) + 5,
        speed: i === 0 || i === steps ? 0 : 10,
        timestamp: i * 15,
      }
    })
  }

  return {
    tasks,
    selectedTaskId,
    selectedTask,
    loading,
    error,
    executingTasks,
    pendingTasks,
    stats,
    fetchTasks,
    createTask,
    selectTask,
    updateTaskFromSocket,
  }
})
