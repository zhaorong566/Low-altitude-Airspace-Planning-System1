<script setup lang="ts">
import { computed } from 'vue'
import { useRouteStore } from '@/stores/useRouteStore'
import { useTaskStore } from '@/stores/useTaskStore'
import { ElMessage } from 'element-plus'

const props = defineProps<{ modelValue: boolean }>()
const emit = defineEmits<{ (e: 'update:modelValue', v: boolean): void }>()

const routeStore = useRouteStore()
const taskStore = useTaskStore()

const conflicts = computed(() => routeStore.conflicts)

function getTaskName(id: string) {
  return taskStore.tasks.find(t => t.id === id)?.name || id
}

function getSeverityType(severity: string) {
  const map: Record<string, 'danger' | 'warning' | 'info' | 'success'> = {
    critical: 'danger',
    high: 'warning',
    medium: 'warning',
    low: 'info',
  }
  return map[severity] || 'info'
}

function resolveConflict(idx: number) {
  const updated = [...conflicts.value]
  updated.splice(idx, 1)
  routeStore.setConflicts(updated)
  ElMessage.success('冲突已标记为处理')
}

function resolveAll() {
  routeStore.clearConflicts()
  emit('update:modelValue', false)
  ElMessage.success('所有冲突已清除')
}
</script>

<template>
  <el-dialog
    :model-value="modelValue"
    @update:model-value="emit('update:modelValue', $event)"
    title="⚠ 航路冲突告警"
    width="500px"
  >
    <div v-if="!conflicts.length" class="no-conflict">
      <el-icon color="#52c41a" size="32"><CircleCheck /></el-icon>
      <p>当前无航路冲突</p>
    </div>

    <div v-else class="conflict-list">
      <el-alert
        :title="`检测到 ${conflicts.length} 处航路冲突，请及时处理`"
        type="error"
        :closable="false"
        style="margin-bottom: 12px"
      />

      <div
        v-for="(conflict, idx) in conflicts"
        :key="idx"
        class="conflict-card"
      >
        <div class="conflict-top">
          <el-tag :type="getSeverityType(conflict.severity as string)" size="small">
            {{ conflict.severity.toUpperCase() }}
          </el-tag>
          <span class="conflict-time">冲突时刻: T+{{ conflict.time?.toFixed(0) }}s</span>
          <el-button
            size="small"
            text
            type="primary"
            @click="resolveConflict(idx)"
          >
            标记处理
          </el-button>
        </div>

        <div class="conflict-tasks">
          <span class="task-badge">{{ getTaskName(conflict.taskId1 || conflict.task_id_1 || '') }}</span>
          <span class="vs">VS</span>
          <span class="task-badge">{{ getTaskName(conflict.taskId2 || conflict.task_id_2 || '') }}</span>
        </div>

        <div class="conflict-details">
          <div>📍 位置: {{ conflict.lat?.toFixed(4) }}°N, {{ conflict.lon?.toFixed(4) }}°E</div>
          <div>↕ 高度: {{ conflict.alt?.toFixed(0) }}m</div>
          <div>↔ 水平间隔: {{ (conflict.hSep || conflict.h_sep || 0).toFixed(1) }}m
            <span class="sep-warn">(需≥50m)</span>
          </div>
          <div>↕ 垂直间隔: {{ (conflict.vSep || conflict.v_sep || 0).toFixed(1) }}m
            <span class="sep-warn">(需≥30m)</span>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <el-button @click="emit('update:modelValue', false)">关闭</el-button>
      <el-button type="danger" :disabled="!conflicts.length" @click="resolveAll">
        清除所有冲突
      </el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.no-conflict {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 24px;
  color: #52c41a;
}

.conflict-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 400px;
  overflow-y: auto;
}

.conflict-card {
  background: rgba(255,77,79,0.05);
  border: 1px solid rgba(255,77,79,0.2);
  border-radius: 6px;
  padding: 10px 12px;
}

.conflict-top {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.conflict-time {
  font-size: 12px;
  color: var(--color-text-sub);
  flex: 1;
}

.conflict-tasks {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.task-badge {
  background: rgba(24,144,255,0.1);
  border: 1px solid rgba(24,144,255,0.3);
  color: #1890ff;
  border-radius: 4px;
  padding: 2px 8px;
  font-size: 12px;
  flex: 1;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.vs {
  font-weight: 700;
  color: #ff4d4f;
  font-size: 12px;
}

.conflict-details {
  font-size: 11px;
  color: var(--color-text-sub);
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.sep-warn {
  color: #ff7875;
  margin-left: 4px;
}
</style>
