import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Drone, DronePosition } from '@/types'

export const useDroneStore = defineStore('drone', () => {
  const drones = ref<Drone[]>([])
  const positions = ref<Map<string, DronePosition>>(new Map())
  const loading = ref(false)

  const activeDrones = computed(() =>
    drones.value.filter(d => !d.isAvailable || positions.value.has(d.droneId || d.drone_id || ''))
  )

  function setDrones(list: any[]) {
    drones.value = list.map(d => ({
      id: d.id,
      droneId: d.drone_id || d.droneId,
      drone_id: d.drone_id,
      name: d.name,
      model: d.model || 'DJI Matrice 300',
      batteryLevel: d.battery_level ?? d.batteryLevel ?? 100,
      battery_level: d.battery_level,
      maxPayload: d.max_payload ?? 2.5,
      maxSpeed: d.max_speed ?? 15,
      maxAltitude: d.max_altitude ?? 120,
      isAvailable: d.is_available !== false,
    }))
  }

  function updatePositions(posList: any[]) {
    for (const pos of posList) {
      const id = pos.drone_id || pos.droneId
      positions.value.set(id, {
        droneId: id,
        taskId: pos.task_id || pos.taskId,
        lat: pos.lat,
        lon: pos.lon,
        alt: pos.alt,
        heading: pos.heading || 0,
        speed: pos.speed || 0,
        batteryLevel: pos.battery_level,
        timestamp: pos.timestamp || Date.now() / 1000,
      })
    }
  }

  function getPosition(droneId: string): DronePosition | undefined {
    return positions.value.get(droneId)
  }

  return {
    drones,
    positions,
    loading,
    activeDrones,
    setDrones,
    updatePositions,
    getPosition,
  }
})
