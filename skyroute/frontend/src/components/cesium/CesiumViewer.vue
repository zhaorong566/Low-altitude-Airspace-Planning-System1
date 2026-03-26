<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useTaskStore } from '@/stores/useTaskStore'
import { useDroneStore } from '@/stores/useDroneStore'
import { useRouteStore } from '@/stores/useRouteStore'
import { getTaskColor, getSeverityColor } from '@/utils/cesiumHelpers'

const taskStore = useTaskStore()
const droneStore = useDroneStore()
const routeStore = useRouteStore()

const viewerId = 'cesium-container'
const viewer = ref<any>(null)
const isReady = ref(false)
const errorMsg = ref('')

// Track entities for cleanup
const routeEntities = new Map<string, any[]>()
const droneEntities = new Map<string, any>()
let conflictEntities: any[] = []
let animationFrame: number | null = null

onMounted(async () => {
  await initCesium()
})

onUnmounted(() => {
  if (animationFrame) cancelAnimationFrame(animationFrame)
  if (viewer.value && !viewer.value.isDestroyed()) {
    viewer.value.destroy()
  }
})

async function initCesium() {
  try {
    // Dynamic import to handle Cesium
    const Cesium = await import('cesium')
    
    const container = document.getElementById(viewerId)
    if (!container) return

    viewer.value = new Cesium.Viewer(viewerId, {
      baseLayerPicker: false,
      geocoder: false,
      homeButton: false,
      sceneModePicker: false,
      navigationHelpButton: false,
      animation: false,
      timeline: false,
      fullscreenButton: false,
      vrButton: false,
      infoBox: false,
      selectionIndicator: false,
      shouldAnimate: true,
      msaaSamples: 4,
    })

    // Style adjustments
    viewer.value.scene.backgroundColor = Cesium.Color.fromCssColorString('#0a0e1a')

    // Fly to Beijing Chaoyang
    viewer.value.camera.flyTo({
      destination: Cesium.Cartesian3.fromDegrees(116.46, 39.93, 8000),
      orientation: {
        heading: Cesium.Math.toRadians(0),
        pitch: Cesium.Math.toRadians(-55),
        roll: 0,
      },
      duration: 2.5,
    })

    isReady.value = true
    renderAll(Cesium)

    // Watch for data changes
    watch(() => taskStore.tasks, () => renderAll(Cesium), { deep: true })
    watch(() => droneStore.positions, () => updateDrones(Cesium), { deep: true })
    watch(() => routeStore.conflicts, () => renderConflicts(Cesium), { deep: true })

  } catch (e: any) {
    errorMsg.value = `Cesium加载失败: ${e.message}`
    console.error(e)
  }
}

function renderAll(Cesium: any) {
  renderRoutes(Cesium)
  renderNoFlyZones(Cesium)
}

function renderRoutes(Cesium: any) {
  if (!viewer.value) return
  // Clear old route entities
  routeEntities.forEach((entities) => {
    entities.forEach(e => viewer.value.entities.remove(e))
  })
  routeEntities.clear()

  for (const task of taskStore.tasks) {
    if (!task.waypoints?.length) continue
    const entities: any[] = []
    const color = getTaskColor(Cesium, task.taskType as string, task.status as string)

    const positions = task.waypoints.map(wp =>
      Cesium.Cartesian3.fromDegrees(wp.lon, wp.lat, wp.alt)
    )

    // Route polyline
    const routeEntity = viewer.value.entities.add({
      polyline: {
        positions,
        width: task.status === 'executing' ? 4 : 2,
        material: new Cesium.PolylineGlowMaterialProperty({
          glowPower: 0.3,
          color: color.withAlpha(task.status === 'executing' ? 0.9 : 0.5),
        }),
        clampToGround: false,
      },
    })
    entities.push(routeEntity)

    // Origin/destination markers
    const originEntity = viewer.value.entities.add({
      position: Cesium.Cartesian3.fromDegrees(task.origin.lon, task.origin.lat, task.origin.alt + 5),
      point: {
        pixelSize: 10,
        color: Cesium.Color.GREEN,
        outlineColor: Cesium.Color.WHITE,
        outlineWidth: 2,
      },
      label: {
        text: `[起] ${task.name.substring(0, 6)}`,
        font: '12px Microsoft YaHei',
        fillColor: Cesium.Color.WHITE,
        outlineColor: Cesium.Color.BLACK,
        outlineWidth: 2,
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
        pixelOffset: new Cesium.Cartesian2(0, -15),
        disableDepthTestDistance: Number.POSITIVE_INFINITY,
      },
    })
    entities.push(originEntity)

    const destEntity = viewer.value.entities.add({
      position: Cesium.Cartesian3.fromDegrees(
        task.destination.lon, task.destination.lat, task.destination.alt + 5
      ),
      point: {
        pixelSize: 10,
        color: Cesium.Color.RED,
        outlineColor: Cesium.Color.WHITE,
        outlineWidth: 2,
      },
    })
    entities.push(destEntity)

    routeEntities.set(task.id, entities)
  }
}

function updateDrones(Cesium: any) {
  if (!viewer.value) return
  droneStore.positions.forEach((pos, droneId) => {
    const position = Cesium.Cartesian3.fromDegrees(pos.lon, pos.lat, pos.alt)
    
    if (droneEntities.has(droneId)) {
      const entity = droneEntities.get(droneId)
      entity.position = position
    } else {
      const entity = viewer.value.entities.add({
        position,
        point: {
          pixelSize: 14,
          color: Cesium.Color.CYAN,
          outlineColor: Cesium.Color.WHITE,
          outlineWidth: 2,
        },
        label: {
          text: droneId.replace('drone-', 'D'),
          font: '11px Arial',
          fillColor: Cesium.Color.CYAN,
          outlineColor: Cesium.Color.BLACK,
          outlineWidth: 2,
          style: Cesium.LabelStyle.FILL_AND_OUTLINE,
          verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
          pixelOffset: new Cesium.Cartesian2(0, -18),
          disableDepthTestDistance: Number.POSITIVE_INFINITY,
        },
      })
      droneEntities.set(droneId, entity)
    }
  })
}

function renderConflicts(Cesium: any) {
  if (!viewer.value) return
  conflictEntities.forEach(e => viewer.value.entities.remove(e))
  conflictEntities = []

  for (const conflict of routeStore.conflicts) {
    const color = getSeverityColor(Cesium, conflict.severity as string)
    const entity = viewer.value.entities.add({
      position: Cesium.Cartesian3.fromDegrees(conflict.lon, conflict.lat, conflict.alt),
      ellipsoid: {
        radii: new Cesium.Cartesian3(80, 80, 40),
        material: color.withAlpha(0.3),
        outline: true,
        outlineColor: color,
      },
      label: {
        text: `⚠ ${conflict.severity.toUpperCase()}`,
        font: 'bold 13px Arial',
        fillColor: color,
        outlineColor: Cesium.Color.BLACK,
        outlineWidth: 2,
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        disableDepthTestDistance: Number.POSITIVE_INFINITY,
      },
    })
    conflictEntities.push(entity)
  }
}

function renderNoFlyZones(Cesium: any) {
  if (!viewer.value) return
  const zones = [
    { name: '首都机场限制区', lat: 40.0799, lon: 116.5877, radius: 5000 },
    { name: '中南海禁飞区', lat: 39.9197, lon: 116.3835, radius: 2000 },
    { name: '天安门广场', lat: 39.9042, lon: 116.3975, radius: 1500 },
    { name: '国贸核心区', lat: 39.9090, lon: 116.4607, radius: 800 },
    { name: '朝阳公园禁区', lat: 39.9357, lon: 116.4814, radius: 600 },
  ]

  for (const zone of zones) {
    viewer.value.entities.add({
      position: Cesium.Cartesian3.fromDegrees(zone.lon, zone.lat, 0),
      ellipse: {
        semiMajorAxis: zone.radius,
        semiMinorAxis: zone.radius,
        height: 0,
        extrudedHeight: 180,
        material: Cesium.Color.RED.withAlpha(0.15),
        outline: true,
        outlineColor: Cesium.Color.RED.withAlpha(0.8),
        outlineWidth: 2,
      },
      label: {
        text: zone.name,
        font: '12px Microsoft YaHei',
        fillColor: Cesium.Color.RED,
        outlineColor: Cesium.Color.BLACK,
        outlineWidth: 2,
        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
        disableDepthTestDistance: Number.POSITIVE_INFINITY,
        pixelOffset: new Cesium.Cartesian2(0, -zone.radius / 50),
      },
    })
  }
}
</script>

<template>
  <div class="cesium-wrapper">
    <div :id="viewerId" class="cesium-container" />
    <div v-if="!isReady && !errorMsg" class="cesium-loading">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>加载三维地图中...</span>
    </div>
    <div v-if="errorMsg" class="cesium-error">
      <el-icon><Warning /></el-icon>
      <span>{{ errorMsg }}</span>
    </div>
    <!-- Map overlay legend -->
    <div class="map-legend">
      <div class="legend-item"><span class="dot" style="background:#1890ff"></span>配送航线</div>
      <div class="legend-item"><span class="dot" style="background:#ff4d4f"></span>紧急航线</div>
      <div class="legend-item"><span class="dot" style="background:#faad14"></span>巡检航线</div>
      <div class="legend-item"><span class="dot" style="background:rgba(255,0,0,0.4);border:1px solid red"></span>禁飞区</div>
    </div>
  </div>
</template>

<style scoped>
.cesium-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
  background: #0a0e1a;
}

.cesium-container {
  width: 100%;
  height: 100%;
}

.cesium-loading, .cesium-error {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #8b9bb4;
  font-size: 14px;
  background: rgba(10, 14, 26, 0.8);
}

.cesium-error {
  color: #ff4d4f;
}

.map-legend {
  position: absolute;
  bottom: 20px;
  left: 20px;
  background: rgba(17, 24, 39, 0.9);
  border: 1px solid #2a3a55;
  border-radius: 6px;
  padding: 10px 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #8b9bb4;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}
</style>
