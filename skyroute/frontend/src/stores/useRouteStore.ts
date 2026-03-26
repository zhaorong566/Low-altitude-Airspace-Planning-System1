import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Route, Conflict } from '@/types'

export const useRouteStore = defineStore('route', () => {
  const routes = ref<Map<string, Route>>(new Map())
  const conflicts = ref<Conflict[]>([])
  const highlightedConflict = ref<Conflict | null>(null)

  function setRoute(taskId: string, route: Route) {
    routes.value.set(taskId, route)
  }

  function getRoute(taskId: string): Route | undefined {
    return routes.value.get(taskId)
  }

  function setConflicts(list: any[]) {
    conflicts.value = list.map(c => ({
      taskId1: c.task_id_1 || c.taskId1,
      task_id_1: c.task_id_1,
      taskId2: c.task_id_2 || c.taskId2,
      task_id_2: c.task_id_2,
      lat: c.lat,
      lon: c.lon,
      alt: c.alt,
      time: c.time,
      severity: c.severity,
      hSep: c.h_sep ?? c.hSep ?? 0,
      h_sep: c.h_sep,
      vSep: c.v_sep ?? c.vSep ?? 0,
      v_sep: c.v_sep,
      description: c.description || '',
    }))
  }

  function highlightConflict(conflict: Conflict | null) {
    highlightedConflict.value = conflict
  }

  function clearConflicts() {
    conflicts.value = []
    highlightedConflict.value = null
  }

  return {
    routes,
    conflicts,
    highlightedConflict,
    setRoute,
    getRoute,
    setConflicts,
    highlightConflict,
    clearConflicts,
  }
})
