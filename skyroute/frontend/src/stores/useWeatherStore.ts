import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { WeatherData } from '@/types'

export const useWeatherStore = defineStore('weather', () => {
  const weather = ref<WeatherData | null>(null)
  const lastUpdated = ref<Date | null>(null)

  const isFlyable = computed(() => {
    if (!weather.value) return true
    const risk = weather.value.flight_risk || weather.value.flightRisk
    return risk !== 'high'
  })

  const windSpeed = computed(() =>
    weather.value?.wind_speed ?? weather.value?.windSpeed ?? 0
  )

  const temperature = computed(() => weather.value?.temperature ?? 20)

  function setWeather(data: any) {
    weather.value = {
      temperature: data.temperature,
      humidity: data.humidity,
      pressure: data.pressure,
      windSpeed: data.wind_speed ?? data.windSpeed ?? 0,
      wind_speed: data.wind_speed,
      windDirection: data.wind_direction ?? data.windDirection ?? 0,
      wind_direction: data.wind_direction,
      visibility: data.visibility,
      cloudCover: data.cloud_cover ?? data.cloudCover ?? 0,
      cloud_cover: data.cloud_cover,
      weatherCode: data.weather_code ?? data.weatherCode ?? 800,
      description: data.description || '',
      flightRisk: data.flight_risk ?? data.flightRisk ?? 'low',
      flight_risk: data.flight_risk,
      timestamp: data.timestamp || new Date().toISOString(),
    }
    lastUpdated.value = new Date()
  }

  return {
    weather,
    lastUpdated,
    isFlyable,
    windSpeed,
    temperature,
    setWeather,
  }
})
