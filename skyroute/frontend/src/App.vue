<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
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
import { ref } from 'vue'

const taskStore = useTaskStore()
const weatherStore = useWeatherStore()
const socket = useSocket()
const api = useRouteApi()

const showCreateDialog = ref(false)
const showConflictDialog = ref(false)

onMounted(async () => {
  // 加载初始数据
  await taskStore.fetchTasks()
  
  try {
    const weather = await api.getWeather()
    weatherStore.setWeather(weather)
  } catch (e) {
    // 使用默认天气数据
    weatherStore.setWeather({
      temperature: 22, humidity: 55, pressure: 1013,
      wind_speed: 4, wind_direction: 225, visibility: 10,
      cloud_cover: 20, weather_code: 800, description: '晴天',
      flight_risk: 'low', timestamp: new Date().toISOString(),
    })
  }

  // 尝试连接WebSocket
  try {
    socket.connect('/')
  } catch (e) {
    console.warn('WebSocket unavailable, using polling mode')
  }
})

onUnmounted(() => {
  socket.disconnect()
})
</script>

<template>
  <div class="app-container">
    <!-- 顶部状态栏 -->
    <StatsDashboard @create-task="showCreateDialog = true" />

    <!-- 主体三列布局 -->
    <div class="main-layout">
      <!-- 左侧任务面板 -->
      <aside class="left-panel">
        <TaskPanel />
      </aside>

      <!-- 中央地图视图 -->
      <main class="map-area">
        <CesiumViewer />
      </main>

      <!-- 右侧路线信息面板 -->
      <aside class="right-panel">
        <RouteInfoPanel />
      </aside>
    </div>

    <!-- 底部时间轴 -->
    <TimelinePanel />

    <!-- 对话框 -->
    <CreateTaskDialog v-model="showCreateDialog" />
    <ConflictDialog v-model="showConflictDialog" />
  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  width: 100vw;
  height: 100vh;
  background: var(--color-bg);
  overflow: hidden;
}

.main-layout {
  flex: 1;
  display: flex;
  overflow: hidden;
  gap: 0;
}

.left-panel {
  width: 320px;
  min-width: 280px;
  background: var(--color-panel);
  border-right: 1px solid var(--color-border);
  overflow-y: auto;
  z-index: 10;
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
  z-index: 10;
}
</style>
