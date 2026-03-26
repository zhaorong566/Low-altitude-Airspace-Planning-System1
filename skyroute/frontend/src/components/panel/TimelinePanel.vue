<script setup lang="ts">
import { computed } from 'vue'
import { useTaskStore } from '@/stores/useTaskStore'

const taskStore = useTaskStore()

const timelineItems = computed(() => {
  return taskStore.tasks
    .filter(t => t.plannedStart || t.planned_start)
    .map(t => ({
      id: t.id,
      name: t.name,
      startTime: t.plannedStart || t.planned_start || '',
      status: t.status,
      taskType: t.taskType || t.task_type,
      droneId: t.droneId || t.drone_id,
    }))
    .sort((a, b) => a.startTime.localeCompare(b.startTime))
})

const typeColors: Record<string, string> = {
  delivery: '#1890ff',
  inspection: '#faad14',
  emergency: '#ff4d4f',
  survey: '#b37feb',
  patrol: '#52c41a',
}

function formatTime(iso: string) {
  try {
    return new Date(iso).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  } catch {
    return '--'
  }
}
</script>

<template>
  <div class="timeline-panel">
    <div class="timeline-header">
      <span class="sky-title">飞行时间轴</span>
      <span class="timeline-date">今日 · {{ new Date().toLocaleDateString('zh-CN') }}</span>
    </div>
    <div class="timeline-scroll">
      <div class="timeline-track">
        <!-- Hour markers -->
        <div class="time-markers">
          <span v-for="h in [8,9,10,11,12,13,14,15,16,17,18]" :key="h" class="time-mark">
            {{ h.toString().padStart(2, '0') }}:00
          </span>
        </div>
        <!-- Task bars -->
        <div class="task-bars">
          <div
            v-for="item in timelineItems"
            :key="item.id"
            class="task-bar"
            :class="{ active: taskStore.selectedTaskId === item.id }"
            :style="{
              background: typeColors[item.taskType as string] || '#1890ff',
              opacity: item.status === 'completed' ? 0.4 : 0.8,
            }"
            :title="`${item.name} | ${item.droneId} | ${formatTime(item.startTime)}`"
            @click="taskStore.selectTask(item.id)"
          >
            <span class="bar-label">{{ item.name.substring(0, 8) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.timeline-panel {
  height: 70px;
  background: var(--color-panel);
  border-top: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  padding: 6px 16px;
  flex-shrink: 0;
}

.timeline-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}

.timeline-date {
  font-size: 11px;
  color: var(--color-text-sub);
}

.timeline-scroll {
  flex: 1;
  overflow-x: auto;
}

.timeline-track {
  position: relative;
  min-width: 800px;
}

.time-markers {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: var(--color-text-sub);
  margin-bottom: 2px;
}

.task-bars {
  display: flex;
  gap: 6px;
  align-items: center;
  height: 22px;
}

.task-bar {
  height: 18px;
  min-width: 80px;
  border-radius: 3px;
  display: flex;
  align-items: center;
  padding: 0 8px;
  cursor: pointer;
  transition: opacity 0.2s;
  border: 1px solid transparent;
}

.task-bar:hover {
  opacity: 1 !important;
}

.task-bar.active {
  border-color: white;
}

.bar-label {
  font-size: 10px;
  color: white;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
