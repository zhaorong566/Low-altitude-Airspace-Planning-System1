<script setup lang="ts">
import { computed } from 'vue'
import { useTaskStore } from '@/stores/useTaskStore'
import { useWeatherStore } from '@/stores/useWeatherStore'
import { useRouteStore } from '@/stores/useRouteStore'

const emit = defineEmits<{ (e: 'create-task'): void }>()

const taskStore = useTaskStore()
const weatherStore = useWeatherStore()
const routeStore = useRouteStore()

const stats = computed(() => taskStore.stats)
const weather = computed(() => weatherStore.weather)
const conflictCount = computed(() => routeStore.conflicts.length)

const windLabel = computed(() => {
  const speed = weather.value?.wind_speed ?? weather.value?.windSpeed ?? 0
  if (speed > 15) return { text: '大风', color: '#ff4d4f' }
  if (speed > 8) return { text: '中风', color: '#faad14' }
  return { text: '微风', color: '#52c41a' }
})
</script>

<template>
  <header class="stats-bar">
    <!-- Logo -->
    <div class="logo">
      <span class="logo-icon">✈</span>
      <div>
        <div class="logo-title">SkyRoute</div>
        <div class="logo-sub">城市低空智能航路规划平台</div>
      </div>
    </div>

    <!-- Stats -->
    <div class="stats-grid">
      <div class="stat-item">
        <div class="stat-value text-blue-400">{{ stats.totalTasks }}</div>
        <div class="stat-label">总任务</div>
      </div>
      <div class="stat-item">
        <div class="stat-value text-green-400 pulse">{{ stats.executingTasks }}</div>
        <div class="stat-label">执行中</div>
      </div>
      <div class="stat-item">
        <div class="stat-value text-yellow-400">{{ stats.pendingTasks }}</div>
        <div class="stat-label">待审批</div>
      </div>
      <div class="stat-item">
        <div class="stat-value" :style="{ color: conflictCount > 0 ? '#ff4d4f' : '#52c41a' }">
          {{ conflictCount }}
        </div>
        <div class="stat-label">冲突数</div>
      </div>
      <div class="stat-item">
        <div class="stat-value text-cyan-400">{{ stats.activeDrones }}</div>
        <div class="stat-label">活跃机</div>
      </div>
    </div>

    <!-- Weather -->
    <div class="weather-info" v-if="weather">
      <div class="weather-item">
        <span class="weather-icon">🌡</span>
        <span>{{ weather.temperature?.toFixed(1) }}°C</span>
      </div>
      <div class="weather-item">
        <span class="weather-icon">💨</span>
        <span :style="{ color: windLabel.color }">
          {{ weather.wind_speed ?? weather.windSpeed }}m/s {{ windLabel.text }}
        </span>
      </div>
      <div class="weather-item">
        <span class="weather-icon">👁</span>
        <span>能见度{{ weather.visibility?.toFixed(0) }}km</span>
      </div>
    </div>

    <!-- Actions -->
    <div class="actions">
      <el-button type="primary" size="small" @click="emit('create-task')">
        <el-icon><Plus /></el-icon> 新建任务
      </el-button>
      <el-button size="small">
        <el-icon><Refresh /></el-icon>
      </el-button>
    </div>
  </header>
</template>

<style scoped>
.stats-bar {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 8px 20px;
  background: var(--color-panel);
  border-bottom: 1px solid var(--color-border);
  height: 56px;
  flex-shrink: 0;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.logo-icon {
  font-size: 24px;
  color: var(--color-primary);
}

.logo-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--color-primary);
  line-height: 1.2;
}

.logo-sub {
  font-size: 10px;
  color: var(--color-text-sub);
}

.stats-grid {
  display: flex;
  gap: 16px;
  flex-shrink: 0;
}

.stat-item {
  text-align: center;
  min-width: 40px;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  line-height: 1.2;
}

.stat-label {
  font-size: 10px;
  color: var(--color-text-sub);
  margin-top: 2px;
}

.weather-info {
  display: flex;
  gap: 14px;
  color: var(--color-text-sub);
  font-size: 12px;
  flex-shrink: 0;
}

.weather-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.weather-icon {
  font-size: 14px;
}

.actions {
  margin-left: auto;
  display: flex;
  gap: 8px;
}
</style>
