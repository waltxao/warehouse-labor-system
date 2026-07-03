import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getChartData } from '../api/trends'

export const useTrendStore = defineStore('trend', () => {
  const chartData = ref<any>(null)
  const loading = ref(false)

  async function loadChart(warehouseCode: string, isoWeek: string) {
    loading.value = true
    try {
      const resp: any = await getChartData(warehouseCode, isoWeek)
      chartData.value = resp.data
    } finally {
      loading.value = false
    }
  }

  function clear() {
    chartData.value = null
  }

  return { chartData, loading, loadChart, clear }
})
