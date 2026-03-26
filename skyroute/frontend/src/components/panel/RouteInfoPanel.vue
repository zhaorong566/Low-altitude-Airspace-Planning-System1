<script setup lang="ts">
import { computed, ref } from 'vue'
import { useTaskStore } from '@/stores/useTaskStore'
import { useRouteStore } from '@/stores/useRouteStore'
import { routeLength, formatDistance, formatDuration } from '@/utils/geoUtils'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { RadarChart, LineChart } from 'echarts/charts'
import { GridComponent, RadarComponent, TooltipComponent, LegendComponent } from 'echarts/components'

use([CanvasRenderer, RadarChart, LineChart, GridComponent, RadarComponent, TooltipComponent, LegendComponent])

const taskStore = useTaskStore()
const routeStore = useRouteStore()

const selectedTask = computed(() => taskStore.selectedTask)
const conflicts = computed(() => routeStore.conflicts)

const totalDist = computed(() => {
  const wps = selectedTask.value?.waypoints
  if (!wps?.length) return 0
  return routeLength(wps)
})

const totalDuration = computed(() => {
  const wps = selectedTask.value?.waypoints
  if (!wps?.length) return 0
  return wps[wps.length - 1]?.timestamp || 0
})

const altitudeChartOption = computed(() => {
  const wps = selectedTask.value?.waypoints
  if (!wps?.length) return {}
  return {
    backgroundColor: 'transparent',
    grid: { top: 10, bottom: 25, left: 40, right: 10 },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: wps.map((_, i) => i),
      axisLine: { lineStyle: { color: '#2a3a55' } },
      axisLabel: { color: '#8b9bb4', fontSize: 10 },
    },
    yAxis: {
      type: 'value',
      name: '高度(m)',
      nameTextStyle: { color: '#8b9bb4', fontSize: 10 },
      axisLine: { lineStyle: { color: '#2a3a55' } },
      axisLabel: { color: '#8b9bb4', fontSize: 10 },
      splitLine: { lineStyle: { color: '#1a2235' } },
    },
    series: [{
      type: 'line',
      data: wps.map(wp => wp.alt),
      smooth: true,
      lineStyle: { color: '#1890ff', width: 2 },
      areaStyle: { color: 'rgba(24, 144, 255, 0.15)' },
      symbol: 'none',
    }],
  }
})

const radarOption = computed(() => {
  const scores = selectedTask.value?.routeScores
  if (!scores) return {}
  return {
    backgroundColor: 'transparent',
    radar: {
      indicator: [
        { name: '安全性', max: 100 },
        { name: '噪音控制', max: 100 },
        { name: '效率', max: 100 },
        { name: '合规性', max: 100 },
        { name: '能耗', max: 100 },
      ],
      shape: 'polygon',
      splitNumber: 4,
      axisName: { color: '#8b9bb4', fontSize: 11 },
      splitLine: { lineStyle: { color: '#2a3a55' } },
      splitArea: { areaStyle: { color: ['rgba(26,34,53,0.5)', 'rgba(26,34,53,0.2)'] } },
    },
    series: [{
      type: 'radar',
      data: [{
        value: [
          scores.risk || 80,
          scores.noise || 75,
          scores.efficiency || 85,
          88,
          82,
        ],
        name: '综合评分',
        lineStyle: { color: '#1890ff' },
        areaStyle: { color: 'rgba(24,144,255,0.2)' },
        itemStyle: { color: '#1890ff' },
      }],
    }],
  }
})
</script>

<template>
  <div class="route-panel">
    <div v-if="!selectedTask" class="empty-panel">
      <el-icon size="32"><Location /></el-icon>
      <p>点击左侧任务查看详情</p>
    </div>

    <template v-else>
      <!-- Task header -->
      <div class="panel-section">
        <div class="task-title">
          <span class="task-name">{{ selectedTask.name }}</span>
          <span class="badge" :class="`badge-${selectedTask.status}`">
            {{ selectedTask.status }}
          </span>
        </div>
        <div class="task-drone">
          <el-icon><Cpu /></el-icon>
          {{ selectedTask.droneId || selectedTask.drone_id }}
          <span class="task-type">· {{ selectedTask.taskType || selectedTask.task_type }}</span>
        </div>
      </div>

      <!-- Route metrics -->
      <div class="panel-section">
        <div class="sky-title">航路指标</div>
        <div class="metrics-grid">
          <div class="metric">
            <div class="metric-value">{{ formatDistance(totalDist) }}</div>
            <div class="metric-label">总距离</div>
          </div>
          <div class="metric">
            <div class="metric-value">{{ formatDuration(totalDuration) }}</div>
            <div class="metric-label">预计时长</div>
          </div>
          <div class="metric">
            <div class="metric-value">
              {{ selectedTask.waypoints?.length || 0 }}
            </div>
            <div class="metric-label">航路点</div>
          </div>
          <div class="metric">
            <div class="metric-value text-yellow-400">
              {{ selectedTask.routeScores?.efficiency || '--' }}%
            </div>
            <div class="metric-label">效率评分</div>
          </div>
        </div>
      </div>

      <!-- Altitude profile -->
      <div class="panel-section" v-if="selectedTask.waypoints?.length">
        <div class="sky-title">高度剖面</div>
        <v-chart :option="altitudeChartOption" style="height: 120px" autoresize />
      </div>

      <!-- Radar chart -->
      <div class="panel-section" v-if="selectedTask.routeScores">
        <div class="sky-title">综合评估</div>
        <v-chart :option="radarOption" style="height: 180px" autoresize />
      </div>

      <!-- Score details -->
      <div class="panel-section" v-if="selectedTask.routeScores">
        <div class="sky-title">评分明细</div>
        <div class="score-list">
          <div class="score-row">
            <span>安全风险</span>
            <el-progress
              :percentage="selectedTask.routeScores.risk || 0"
              color="#52c41a"
              :stroke-width="6"
            />
          </div>
          <div class="score-row">
            <span>噪音影响</span>
            <el-progress
              :percentage="selectedTask.routeScores.noise || 0"
              color="#1890ff"
              :stroke-width="6"
            />
          </div>
          <div class="score-row">
            <span>路径效率</span>
            <el-progress
              :percentage="selectedTask.routeScores.efficiency || 0"
              color="#faad14"
              :stroke-width="6"
            />
          </div>
        </div>
      </div>

      <!-- Conflicts -->
      <div class="panel-section" v-if="conflicts.length">
        <div class="sky-title conflict-title">
          <el-icon><Warning /></el-icon>
          冲突告警 ({{ conflicts.length }})
        </div>
        <div class="conflict-list">
          <div
            v-for="(conflict, idx) in conflicts"
            :key="idx"
            class="conflict-item"
            :class="`conflict-${conflict.severity}`"
          >
            <div class="conflict-header">
              <span class="conflict-severity">{{ conflict.severity.toUpperCase() }}</span>
              <span class="conflict-time">T+{{ conflict.time?.toFixed(0) }}s</span>
            </div>
            <div class="conflict-desc">{{ conflict.description }}</div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.route-panel {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  height: 100%;
  overflow-y: auto;
}

.empty-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 12px;
  color: var(--color-text-sub);
}

.panel-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.task-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
  flex: 1;
}

.task-drone {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--color-text-sub);
}

.task-type {
  color: var(--color-primary);
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.metric {
  background: var(--color-card);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  padding: 8px 10px;
  text-align: center;
}

.metric-value {
  font-size: 16px;
  font-weight: 700;
  color: var(--color-text);
}

.metric-label {
  font-size: 11px;
  color: var(--color-text-sub);
  margin-top: 2px;
}

.score-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.score-row {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  color: var(--color-text-sub);
}

.score-row span {
  width: 60px;
  flex-shrink: 0;
}

.score-row .el-progress {
  flex: 1;
}

.conflict-title {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #ff4d4f;
}

.conflict-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.conflict-item {
  border-radius: 4px;
  padding: 8px 10px;
  border-left: 3px solid;
}

.conflict-critical { border-color: #ff4d4f; background: rgba(255,77,79,0.1); }
.conflict-high { border-color: #ff7a00; background: rgba(255,122,0,0.1); }
.conflict-medium { border-color: #faad14; background: rgba(250,173,20,0.1); }
.conflict-low { border-color: #52c41a; background: rgba(82,196,26,0.1); }

.conflict-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.conflict-severity {
  font-size: 11px;
  font-weight: 700;
  color: var(--color-text);
}

.conflict-time {
  font-size: 11px;
  color: var(--color-text-sub);
}

.conflict-desc {
  font-size: 11px;
  color: var(--color-text-sub);
}
</style>
