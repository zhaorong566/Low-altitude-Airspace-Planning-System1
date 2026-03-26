<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useTaskStore } from '@/stores/useTaskStore'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'

const props = defineProps<{ modelValue: boolean }>()
const emit = defineEmits<{
  (e: 'update:modelValue', v: boolean): void
}>()

const taskStore = useTaskStore()
const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
  name: '',
  droneId: 'drone-001',
  taskType: 'delivery',
  priority: 'normal',
  originLat: 39.9204,
  originLon: 116.4430,
  originAlt: 50,
  destLat: 39.9524,
  destLon: 116.4743,
  destAlt: 50,
  plannedStart: '',
})

const rules = {
  name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  droneId: [{ required: true, message: '请选择无人机', trigger: 'change' }],
  originLat: [{ required: true, type: 'number' as const, message: '请输入起点纬度' }],
  originLon: [{ required: true, type: 'number' as const, message: '请输入起点经度' }],
  destLat: [{ required: true, type: 'number' as const, message: '请输入终点纬度' }],
  destLon: [{ required: true, type: 'number' as const, message: '请输入终点经度' }],
}

const drones = [
  { id: 'drone-001', name: '朝阳快鸟-01' },
  { id: 'drone-002', name: '朝阳快鸟-02' },
  { id: 'drone-003', name: '巡检鹰-01' },
  { id: 'drone-004', name: '急救翼-01' },
  { id: 'drone-005', name: '测绘星-01' },
]

async function handleSubmit() {
  await formRef.value?.validate()
  loading.value = true
  try {
    await taskStore.createTask({
      name: form.name,
      droneId: form.droneId,
      taskType: form.taskType,
      priority: form.priority,
      origin: { lat: form.originLat, lon: form.originLon, alt: form.originAlt },
      destination: { lat: form.destLat, lon: form.destLon, alt: form.destAlt },
      plannedStart: form.plannedStart || undefined,
    })
    ElMessage.success('任务创建成功，正在规划航路...')
    emit('update:modelValue', false)
    resetForm()
  } catch (e: any) {
    ElMessage.error(`创建失败: ${e.message}`)
  } finally {
    loading.value = false
  }
}

function resetForm() {
  formRef.value?.resetFields()
}

// Preset locations for quick selection
const presets = [
  { name: '国贸→望京', oLat: 39.9090, oLon: 116.4607, dLat: 40.0047, dLon: 116.4731 },
  { name: '三里屯→朝阳医院', oLat: 39.9368, oLon: 116.4547, dLat: 39.9221, dLon: 116.4533 },
  { name: 'CBD→奥体中心', oLat: 39.9090, oLon: 116.4607, dLat: 39.9843, dLon: 116.3958 },
]

function applyPreset(p: typeof presets[0]) {
  form.originLat = p.oLat
  form.originLon = p.oLon
  form.destLat = p.dLat
  form.destLon = p.dLon
}
</script>

<template>
  <el-dialog
    :model-value="modelValue"
    @update:model-value="emit('update:modelValue', $event)"
    title="创建飞行任务"
    width="560px"
    :close-on-click-modal="false"
  >
    <!-- Preset buttons -->
    <div class="presets">
      <span class="preset-label">快捷预设：</span>
      <el-button
        v-for="p in presets"
        :key="p.name"
        size="small"
        text
        type="primary"
        @click="applyPreset(p)"
      >
        {{ p.name }}
      </el-button>
    </div>

    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="90px"
      label-position="left"
    >
      <el-form-item label="任务名称" prop="name">
        <el-input v-model="form.name" placeholder="输入任务名称" />
      </el-form-item>

      <el-row :gutter="12">
        <el-col :span="12">
          <el-form-item label="无人机" prop="droneId">
            <el-select v-model="form.droneId" style="width: 100%">
              <el-option
                v-for="d in drones"
                :key="d.id"
                :label="`${d.name} (${d.id})`"
                :value="d.id"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="任务类型">
            <el-select v-model="form.taskType" style="width: 100%">
              <el-option label="快递配送" value="delivery" />
              <el-option label="设施巡检" value="inspection" />
              <el-option label="紧急医疗" value="emergency" />
              <el-option label="区域测绘" value="survey" />
              <el-option label="安防巡逻" value="patrol" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="优先级">
        <el-radio-group v-model="form.priority">
          <el-radio label="low">低</el-radio>
          <el-radio label="normal">正常</el-radio>
          <el-radio label="high">高</el-radio>
          <el-radio label="emergency">紧急</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-divider>起点坐标</el-divider>
      <el-row :gutter="12">
        <el-col :span="8">
          <el-form-item label="纬度" prop="originLat" label-width="40px">
            <el-input-number v-model="form.originLat" :precision="6" :step="0.001" style="width:100%" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="经度" prop="originLon" label-width="40px">
            <el-input-number v-model="form.originLon" :precision="6" :step="0.001" style="width:100%" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="高度" label-width="40px">
            <el-input-number v-model="form.originAlt" :min="5" :max="200" style="width:100%" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-divider>终点坐标</el-divider>
      <el-row :gutter="12">
        <el-col :span="8">
          <el-form-item label="纬度" prop="destLat" label-width="40px">
            <el-input-number v-model="form.destLat" :precision="6" :step="0.001" style="width:100%" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="经度" prop="destLon" label-width="40px">
            <el-input-number v-model="form.destLon" :precision="6" :step="0.001" style="width:100%" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="高度" label-width="40px">
            <el-input-number v-model="form.destAlt" :min="5" :max="200" style="width:100%" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="计划起飞">
        <el-date-picker
          v-model="form.plannedStart"
          type="datetime"
          placeholder="选择起飞时间"
          style="width: 100%"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="emit('update:modelValue', false)">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        创建并规划航路
      </el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.presets {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.preset-label {
  font-size: 12px;
  color: var(--color-text-sub);
}
</style>
