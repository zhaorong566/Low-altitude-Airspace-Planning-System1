<script setup lang="ts">
import { computed, ref } from 'vue'
import { useTaskStore } from '@/stores/useTaskStore'
import type { FlightTask } from '@/types'

const taskStore = useTaskStore()
const filterStatus = ref('all')
const searchText = ref('')

const filteredTasks = computed(() => {
  let list = taskStore.tasks
  if (filterStatus.value !== 'all') {
    list = list.filter(t => t.status === filterStatus.value)
  }
  if (searchText.value) {
    const q = searchText.value.toLowerCase()
    list = list.filter(t => t.name.toLowerCase().includes(q))
  }
  return list
})

function selectTask(task: FlightTask) {
  taskStore.selectTask(task.id)
}

function getStatusBadge(status: string) {
  const map: Record<string, string> = {
    executing: 'badge-executing',
    pending: 'badge-pending',
    approved: 'badge-approved',
    emergency: 'badge-emergency',
    completed: 'badge-completed',
    failed: 'badge-failed',
    planning: 'badge-pending',
  }
  return map[status] || 'badge-pending'
}

function getStatusLabel(status: string) {
  const map: Record<string, string> = {
    executing: '执行中',
    pending: '待审批',
    approved: '已批准',
    planning: '规划中',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消',
  }
  return map[status] || status
}

function getTypeIcon(type: string) {
  const map: Record<string, string> = {
    delivery: '📦',
    inspection: '🔍',
    emergency: '🚑',
    survey: '🗺',
    patrol: '👁',
  }
  return map[type] || '✈'
}

function getPriorityColor(priority: string) {
  const map: Record<string, string> = {
    emergency: '#ff4d4f',
    high: '#faad14',
    normal: '#52c41a',
    low: '#8c8c8c',
  }
  return map[priority] || '#52c41a'
}
</script>

<template>
  <div class="task-panel">
    <div class="panel-header">
      <span class="sky-title">飞行任务</span>
      <span class="task-count">{{ filteredTasks.length }}</span>
    </div>

    <!-- Search -->
    <div class="search-bar">
      <el-input
        v-model="searchText"
        placeholder="搜索任务..."
        size="small"
        clearable
        prefix-icon="Search"
      />
    </div>

    <!-- Filter tabs -->
    <div class="filter-tabs">
      <button
        v-for="f in [
          { value: 'all', label: '全部' },
          { value: 'executing', label: '执行中' },
          { value: 'pending', label: '待审批' },
          { value: 'approved', label: '已批准' },
        ]"
        :key="f.value"
        class="filter-tab"
        :class="{ active: filterStatus === f.value }"
        @click="filterStatus = f.value"
      >
        {{ f.label }}
      </button>
    </div>

    <!-- Task list -->
    <div class="task-list">
      <div
        v-for="task in filteredTasks"
        :key="task.id"
        class="task-item"
        :class="{ selected: taskStore.selectedTaskId === task.id }"
        @click="selectTask(task)"
      >
        <div class="task-header">
          <span class="task-icon">{{ getTypeIcon(task.taskType as string || task.task_type as string) }}</span>
          <span class="task-name">{{ task.name }}</span>
          <span
            class="badge"
            :class="getStatusBadge(task.status as string)"
          >
            {{ getStatusLabel(task.status as string) }}
          </span>
        </div>

        <div class="task-meta">
          <span class="meta-item">
            <el-icon><Avatar /></el-icon>
            {{ task.droneId || task.drone_id }}
          </span>
          <span
            class="priority-dot"
            :style="{ background: getPriorityColor(task.priority as string) }"
            :title="task.priority as string"
          />
        </div>

        <div class="task-route">
          <span class="route-point origin">起</span>
          <span class="route-line">──────</span>
          <span class="route-point dest">终</span>
          <span class="route-dist">
            {{ task.waypoints?.length ? `${task.waypoints.length}个航点` : '待规划' }}
          </span>
        </div>

        <div v-if="task.routeScores" class="score-bar">
          <div class="score-item">
            <span>效率</span>
            <el-progress
              :percentage="task.routeScores.efficiency || 0"
              :stroke-width="4"
              color="#1890ff"
              :show-text="false"
            />
            <span>{{ task.routeScores.efficiency }}%</span>
          </div>
        </div>
      </div>

      <div v-if="!filteredTasks.length" class="empty-state">
        <el-icon><Document /></el-icon>
        <span>暂无任务</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.task-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 12px;
  gap: 10px;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.task-count {
  background: var(--color-primary);
  color: white;
  border-radius: 10px;
  padding: 1px 8px;
  font-size: 12px;
  font-weight: 600;
}

.filter-tabs {
  display: flex;
  gap: 4px;
}

.filter-tab {
  flex: 1;
  padding: 4px 0;
  font-size: 11px;
  background: transparent;
  border: 1px solid var(--color-border);
  color: var(--color-text-sub);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-tab.active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
}

.task-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-item {
  background: var(--color-card);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  padding: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.task-item:hover {
  border-color: var(--color-primary);
  background: rgba(24, 144, 255, 0.05);
}

.task-item.selected {
  border-color: var(--color-primary);
  background: rgba(24, 144, 255, 0.1);
}

.task-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
}

.task-icon {
  font-size: 14px;
}

.task-name {
  flex: 1;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--color-text-sub);
  font-size: 11px;
  margin-bottom: 6px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 3px;
}

.priority-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  margin-left: auto;
}

.task-route {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--color-text-sub);
  margin-bottom: 6px;
}

.route-point {
  padding: 1px 5px;
  border-radius: 3px;
  font-size: 10px;
  font-weight: 600;
}

.origin { background: rgba(82, 196, 26, 0.2); color: #52c41a; }
.dest { background: rgba(255, 77, 79, 0.2); color: #ff4d4f; }

.route-dist {
  margin-left: auto;
  color: var(--color-primary);
}

.score-bar {
  margin-top: 4px;
}

.score-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: var(--color-text-sub);
}

.score-item .el-progress {
  flex: 1;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 40px 0;
  color: var(--color-text-sub);
  font-size: 13px;
}
</style>
