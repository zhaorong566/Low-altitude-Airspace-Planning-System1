<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import StatsDashboard from '@/components/panel/StatsDashboard.vue'
import TaskPanel from '@/components/panel/TaskPanel.vue'
import CesiumViewer from '@/components/cesium/CesiumViewer.vue'
import RouteInfoPanel from '@/components/panel/RouteInfoPanel.vue'
import TimelinePanel from '@/components/panel/TimelinePanel.vue'
import CreateTaskDialog from '@/components/dialog/CreateTaskDialog.vue'
import ConflictDialog from '@/components/dialog/ConflictDialog.vue'
import { useTaskStore } from '@/stores/useTaskStore'
import { useWeatherStore } from '@/stores/useWeatherStore'
import { useSocket } from '@/composables/useSocket'
import { useRouteApi } from '@/composables/useRouteApi'

const taskStore = useTaskStore()
const weatherStore = useWeatherStore()
const socket = useSocket()
const api = useRouteApi()

const showCreateDialog = ref(false)
const showConflictDialog = ref(false)

onMounted(async () => {
  await taskStore.fetchTasks()
  try {
    const weather = await api.getWeather()
    weatherStore.setWeather(weather)
  } catch {
    weatherStore.setWeather({
      temperature: 22, humidity: 55, pressure: 1013,
      wind_speed: 4, wind_direction: 225, visibility: 10,
      cloud_cover: 20, weather_code: 800, description: '晴天',
      flight_risk: 'low', timestamp: new Date().toISOString(),
    })
  }
  try {
    socket.connect('/')
  } catch {
    console.warn('WebSocket unavailable, running in offline mode')
  }
})

onUnmounted(() => {
  socket.disconnect()
})
</script>

<template>
  <div class="dashboard">
    <StatsDashboard @create-task="showCreateDialog = true" />
    <div class="main-layout">
      <aside class="left-panel">
        <TaskPanel />
      </aside>
      <main class="map-area">
        <CesiumViewer />
      </main>
      <aside class="right-panel">
        <RouteInfoPanel />
      </aside>
    </div>
    <TimelinePanel />
    <CreateTaskDialog v-model="showCreateDialog" />
    <ConflictDialog v-model="showConflictDialog" />
  </div>
</template>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}
.main-layout {
  flex: 1;
  display: flex;
  overflow: hidden;
}
.left-panel {
  width: 320px;
  min-width: 280px;
  background: var(--color-panel);
  border-right: 1px solid var(--color-border);
  overflow-y: auto;
}
.map-area {
  flex: 1;
  position: relative;
  overflow: hidden;
}
.right-panel {
  width: 360px;
  min-width: 300px;
  background: var(--color-panel);
  border-left: 1px solid var(--color-border);
  overflow-y: auto;
}
</style>
