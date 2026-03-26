import { ref, onUnmounted } from 'vue'
import { io, Socket } from 'socket.io-client'
import { useTaskStore } from '@/stores/useTaskStore'
import { useDroneStore } from '@/stores/useDroneStore'
import { useRouteStore } from '@/stores/useRouteStore'
import { useWeatherStore } from '@/stores/useWeatherStore'

let socket: Socket | null = null

export function useSocket() {
  const connected = ref(false)
  const error = ref<string | null>(null)

  const taskStore = useTaskStore()
  const droneStore = useDroneStore()
  const routeStore = useRouteStore()
  const weatherStore = useWeatherStore()

  function connect(url = '/') {
    if (socket?.connected) return

    socket = io(url, {
      transports: ['websocket', 'polling'],
      reconnectionAttempts: 5,
      reconnectionDelay: 2000,
    })

    socket.on('connect', () => {
      connected.value = true
      error.value = null
    })

    socket.on('disconnect', () => {
      connected.value = false
    })

    socket.on('connect_error', (err) => {
      error.value = err.message
      connected.value = false
    })

    socket.on('init:data', (data: any) => {
      if (data.tasks) {
        data.tasks.forEach((t: any) => taskStore.updateTaskFromSocket(t))
      }
      if (data.drones) {
        droneStore.setDrones(data.drones)
      }
    })

    socket.on('drone:positions', (data: any) => {
      if (data.positions) {
        droneStore.updatePositions(data.positions)
      }
    })

    socket.on('conflict:detected', (data: any) => {
      if (data.conflicts) {
        routeStore.setConflicts(data.conflicts)
      }
    })

    socket.on('conflict:resolved', () => {
      routeStore.clearConflicts()
    })

    socket.on('task:status_changed', (data: any) => {
      taskStore.updateTaskFromSocket(data)
    })

    socket.on('weather:updated', (data: any) => {
      weatherStore.setWeather(data)
    })

    socket.on('route:planned', (data: any) => {
      if (data.task_id && data.waypoints) {
        taskStore.updateTaskFromSocket({ id: data.task_id, waypoints: data.waypoints })
      }
    })
  }

  function disconnect() {
    socket?.disconnect()
    socket = null
    connected.value = false
  }

  function emit(event: string, data?: any) {
    socket?.emit(event, data)
  }

  function requestRoutePlan(origin: any, dest: any, taskId = 'temp') {
    emit('request_route_plan', { task_id: taskId, origin, dest })
  }

  onUnmounted(() => {
    // Don't disconnect on unmount - keep connection alive
  })

  return {
    connected,
    error,
    connect,
    disconnect,
    emit,
    requestRoutePlan,
  }
}
