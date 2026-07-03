<template>
  <div ref="chartRef" class="comparison-chart"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps<{
  dates: string[]
  series: { name: string; data: (number | null)[] }[]
  chartType: 'bar' | 'line'
}>()

const chartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

function renderChart() {
  if (!chartRef.value) return
  if (!chart) chart = echarts.init(chartRef.value)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: props.series.map((s) => s.name) },
    grid: { left: 50, right: 30, top: 50, bottom: 60 },
    xAxis: { type: 'category', data: props.dates },
    yAxis: { type: 'value' },
    dataZoom: [{ type: 'inside' }, { type: 'slider' }],
    series: props.series.map((s) => ({ ...s, type: props.chartType })),
  })
}

function handleResize() {
  chart?.resize()
}

onMounted(() => {
  nextTick(renderChart)
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
  chart = null
})

watch(() => [props.dates, props.series, props.chartType], renderChart, { deep: true })
</script>

<style scoped>
.comparison-chart {
  width: 100%;
  height: 400px;
}
</style>
