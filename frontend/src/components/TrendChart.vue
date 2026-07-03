<template>
  <div ref="chartRef" class="trend-chart"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps<{
  dates: string[]
  attendance: (number | null)[]
  requiredSo: (number | null)[]
  threeMonthAvg: (number | null)[]
}>()

const chartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

function renderChart() {
  if (!chartRef.value) return
  if (!chart) chart = echarts.init(chartRef.value)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['实际出勤人数', '实际工作需求人数SO', '近3月需求均值'] },
    grid: { left: 50, right: 30, top: 50, bottom: 60 },
    xAxis: { type: 'category', data: props.dates },
    yAxis: { type: 'value' },
    dataZoom: [{ type: 'inside' }, { type: 'slider' }],
    series: [
      {
        name: '实际出勤人数',
        type: 'line',
        data: props.attendance,
        itemStyle: { color: '#16a34a' },
        lineStyle: { color: '#16a34a' },
        smooth: true,
      },
      {
        name: '实际工作需求人数SO',
        type: 'line',
        data: props.requiredSo,
        itemStyle: { color: '#2563eb' },
        lineStyle: { color: '#2563eb' },
        smooth: true,
      },
      {
        name: '近3月需求均值',
        type: 'line',
        data: props.threeMonthAvg,
        itemStyle: { color: '#f59e0b' },
        lineStyle: { color: '#f59e0b', type: 'dashed' },
        smooth: true,
      },
    ],
  })
}

function handleResize() {
  chart?.resize()
}

function getDataURL() {
  return chart?.getDataURL({ type: 'png', backgroundColor: '#fff' })
}

defineExpose({ getDataURL, resize: handleResize })

onMounted(() => {
  nextTick(renderChart)
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
  chart = null
})

watch(() => props.dates, renderChart, { deep: true })
</script>

<style scoped>
.trend-chart {
  width: 100%;
  height: 400px;
}
</style>
