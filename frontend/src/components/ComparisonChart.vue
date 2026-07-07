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

const palette = ['#1E40AF', '#3B82F6', '#60A5FA', '#93C5FD', '#BFDBFE', '#DBEAFE']

const WEEKDAY_NAMES = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']

function formatDateLabel(dateStr: string): string {
  try {
    const parts = dateStr.split('-')
    if (parts.length < 3) return dateStr
    const y = parseInt(parts[0])
    const m = parseInt(parts[1])
    const d = parseInt(parts[2])
    const date = new Date(y, m - 1, d)
    const mm = String(m).padStart(2, '0')
    const dd = String(d).padStart(2, '0')
    const weekday = WEEKDAY_NAMES[date.getDay()]
    return `${mm}/${dd}\n${weekday}`
  } catch {
    return dateStr
  }
}

function fmtNum(v: number | null): string {
  if (v === null || v === undefined || isNaN(v)) return ''
  const r = Math.round(v * 100) / 100
  if (r % 1 === 0) return String(r)
  return String(parseFloat(r.toFixed(2)))
}

function renderChart() {
  if (!chartRef.value) return
  if (!chart) chart = echarts.init(chartRef.value)

  const xLabels = props.dates.map(formatDateLabel)

  chart.setOption({
    backgroundColor: '#ffffff',
    color: palette,
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255,255,255,0.98)',
      borderColor: '#DBEAFE',
      borderWidth: 1,
      borderRadius: 8,
      padding: [8, 12],
      textStyle: {
        color: '#1E3A8A',
        fontFamily: 'Fira Sans, sans-serif',
        fontSize: 13,
      },
      extraCssText: 'box-shadow: 0 4px 16px rgba(30,58,138,0.16);',
      formatter: (params: any) => {
        let html = `<div style="font-weight:bold;margin-bottom:4px;color:#1E3A8A;">${params[0].axisValue}</div>`
        params.forEach((p: any) => {
          html += `<div style="color:${p.color};">● ${p.seriesName}: ${fmtNum(p.value)}</div>`
        })
        return html
      },
    },
    legend: {
      data: props.series.map((s) => s.name),
      textStyle: {
        color: '#1E3A8A',
        fontFamily: 'Fira Sans, sans-serif',
        fontSize: 13,
      },
      itemGap: 20,
      top: 8,
    },
    grid: { left: '8%', right: '8%', bottom: '18%', top: '15%' },
    xAxis: {
      type: 'category',
      data: xLabels,
      axisLabel: {
        color: '#1E3A8A',
        fontFamily: 'Fira Code, monospace',
        fontSize: 12,
        interval: 0,
        rotate: 0,
        margin: 15,
      },
      axisLine: { lineStyle: { color: '#DBEAFE' } },
      axisTick: { alignWithLabel: true },
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: '#64748B',
        fontFamily: 'Fira Sans, sans-serif',
        fontSize: 13,
        formatter: (val: number) => fmtNum(val),
      },
      splitLine: { lineStyle: { type: 'dashed', color: '#E9EEF6' } },
      axisLine: { show: false },
    },
    dataZoom: [{ type: 'inside' }, { type: 'slider' }],
    series: props.series.map((s) => ({
      name: s.name,
      type: props.chartType,
      data: s.data,
      smooth: props.chartType === 'line',
      symbol: props.chartType === 'line' ? 'circle' : 'none',
      symbolSize: 8,
      itemStyle:
        props.chartType === 'bar'
          ? { borderRadius: [4, 4, 0, 0] }
          : {},
      barMaxWidth: 36,
      lineStyle: { width: 3 },
      label: {
        show: true,
        position: props.chartType === 'bar' ? 'top' : 'top',
        fontFamily: 'Fira Code, monospace',
        fontSize: 11,
        fontWeight: 'bold',
        color: '#1E3A8A',
        formatter: (p: any) => fmtNum(p.value),
      },
    })),
  }, true)
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
  height: 450px;
  background: #ffffff;
}
</style>
