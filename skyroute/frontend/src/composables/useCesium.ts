import { ref, onUnmounted } from 'vue'

export interface CesiumViewerOptions {
  containerId: string
  ionToken?: string
}

export function useCesium(options: CesiumViewerOptions) {
  const viewer = ref<any>(null)
  const isReady = ref(false)
  const error = ref<string | null>(null)

  async function initViewer() {
    try {
      const Cesium = (window as any).Cesium || await import('cesium')
      
      if (options.ionToken) {
        Cesium.Ion.defaultAccessToken = options.ionToken
      }

      const container = document.getElementById(options.containerId)
      if (!container) {
        throw new Error(`Container ${options.containerId} not found`)
      }

      viewer.value = new Cesium.Viewer(options.containerId, {
        terrainProvider: await Cesium.createWorldTerrainAsync().catch(() => undefined),
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
        shadows: false,
        shouldAnimate: true,
      })

      // 添加OSM Buildings
      try {
        await Cesium.createOsmBuildingsAsync().then((tileset: any) => {
          viewer.value.scene.primitives.add(tileset)
        })
      } catch (e) {
        console.warn('OSM Buildings unavailable:', e)
      }

      // 飞到北京朝阳区
      viewer.value.camera.flyTo({
        destination: Cesium.Cartesian3.fromDegrees(116.46, 39.93, 5000),
        orientation: {
          heading: Cesium.Math.toRadians(0),
          pitch: Cesium.Math.toRadians(-45),
          roll: 0,
        },
        duration: 2,
      })

      isReady.value = true
    } catch (e: any) {
      error.value = e.message
      console.error('Cesium init error:', e)
    }
  }

  function destroy() {
    if (viewer.value && !viewer.value.isDestroyed()) {
      viewer.value.destroy()
      viewer.value = null
    }
    isReady.value = false
  }

  onUnmounted(() => {
    destroy()
  })

  return {
    viewer,
    isReady,
    error,
    initViewer,
    destroy,
  }
}
