import axios from 'axios'
import type { FlightTask, TaskListResponse, WeatherData } from '@/types'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
})

export function useRouteApi() {
  async function getTasks(): Promise<TaskListResponse> {
    const res = await api.get('/tasks/demo')
    return res.data
  }

  async function getTask(id: string): Promise<FlightTask> {
    const res = await api.get(`/tasks/${id}`)
    return res.data
  }

  async function createTask(data: Partial<FlightTask>): Promise<FlightTask> {
    const payload = {
      name: data.name,
      drone_id: data.droneId || data.drone_id,
      origin_lat: data.origin?.lat,
      origin_lon: data.origin?.lon,
      origin_alt: data.origin?.alt ?? 50,
      dest_lat: data.destination?.lat,
      dest_lon: data.destination?.lon,
      dest_alt: data.destination?.alt ?? 50,
      task_type: data.taskType || data.task_type || 'delivery',
      priority: data.priority || 'normal',
      planned_start: data.plannedStart || data.planned_start,
    }
    const res = await api.post('/tasks/', payload)
    return res.data
  }

  async function planRoute(taskId: string, options = {}) {
    const res = await api.post('/planning/plan', {
      task_id: taskId,
      ...options,
    })
    return res.data
  }

  async function detectConflicts(taskIds: string[]) {
    const res = await api.post('/planning/detect-conflicts', taskIds)
    return res.data
  }

  async function getConflicts() {
    const res = await api.get('/conflicts/')
    return res.data
  }

  async function getWeather(lat = 39.9, lon = 116.4): Promise<WeatherData> {
    const res = await api.get('/weather/current', { params: { lat, lon } })
    return res.data
  }

  async function getNoFlyZones() {
    const res = await api.get('/planning/no-fly-zones')
    return res.data
  }

  return {
    getTasks,
    getTask,
    createTask,
    planRoute,
    detectConflicts,
    getConflicts,
    getWeather,
    getNoFlyZones,
  }
}
