<template>
  <div class="chart-wrapper">
    <div class="chart-header">
      <h3 class="chart-title">{{ title }}</h3>
      <div class="chart-legend">
        <span class="legend-item">
          <span class="legend-dot" style="background: #2563EB;"></span>
          實際出勤人數
        </span>
        <span class="legend-item">
          <span class="legend-dot" style="background: #3B82F6;"></span>
          實際需求人力
        </span>
        <span class="legend-item">
          <span class="legend-line" style="border-top: 2px dashed #6B7280;"></span>
          近3月需求人力平均值
        </span>
      </div>
    </div>
    <div ref="chartRef" class="chart-container"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from "vue";
import * as echarts from "echarts";

const props = defineProps<{
  days: string[];
  attendance: number[];
  requiredSo: number[];
  avgSums: number[];
  title?: string;
}>();

const chartRef = ref<HTMLElement>();
let chart: echarts.ECharts | null = null;

const titleText = props.title || "仓库人力数据趋势分析";

function renderChart() {
  if (!chartRef.value) return;
  if (!chart) {
    chart = echarts.init(chartRef.value);
  }

  const option: echarts.EChartsOption = {
    title: {
      show: false,
    },
    backgroundColor: "#ffffff",
    tooltip: {
      trigger: "axis",
      appendToBody: true,
      backgroundColor: "rgba(255,255,255,0.98)",
      borderColor: "#D2D2D7",
      borderWidth: 1,
      padding: [8, 12],
      textStyle: {
        color: "#1D1D1F",
        fontFamily: "'Segoe UI', 'Segoe UI', sans-serif",
        fontSize: 13,
      },
      extraCssText: "border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);",
      formatter: (params: any) => {
        let html = `<div style="font-weight:bold;margin-bottom:4px;color:#1D1D1F;">${params[0].axisValue}</div>`;
        params.forEach((p: any) => {
          const raw = p.value ? Number(p.value) : 0; const rounded = Math.round(raw * 100) / 100; const val = rounded % 1 === 0 ? String(rounded) : String(parseFloat(rounded.toFixed(2)));
          html += `<div style="color:${p.color};">● ${p.seriesName}: ${val}</div>`;
        });
        return html;
      },
    },
    legend: {
      show: false,
    },
    grid: {
      left: "8%",
      right: "8%",
      bottom: "18%",
      top: "18%",
    },
    xAxis: {
      type: "category",
      data: props.days,
      axisLabel: {
        fontFamily: "'Cascadia Code', ui-monospace, monospace",
        fontSize: 12,
        color: "#1D1D1F",
        rotate: 0,
        interval: 0,
        fontWeight: "bold",
        margin: 15,
        formatter: (val: string) => val.replace(" ", "\n"),
      },
      axisLine: { lineStyle: { color: "#D2D2D7" } },
      axisTick: { alignWithLabel: true },
    },
    yAxis: {
      type: "value",
      axisLabel: {
        fontFamily: "'Segoe UI', 'Segoe UI', sans-serif",
        fontSize: 13,
        color: "#6E6E73",
      },
      splitLine: { lineStyle: { type: "dashed", color: "#D2D2D7" } },
      axisLine: { show: false },
    },
    series: [
      {
        name: "實際出勤人數",
        type: "line",
        data: props.attendance,
        smooth: true,
        symbol: "circle",
        symbolSize: 8,
        itemStyle: { color: "#2563EB" },
        lineStyle: { width: 3, color: "#2563EB" },
        label: {
          show: true,
          position: "top",
          fontFamily: "'Cascadia Code', ui-monospace, monospace",
          fontSize: 12,
          color: "#2563EB",
          fontWeight: "bold",
          formatter: (p: any) => { if (!p.value) return ""; const r = Math.round(p.value * 100) / 100; return r % 1 === 0 ? String(r) : String(parseFloat(r.toFixed(2))); },
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "rgba(37,99,235,0.12)" },
            { offset: 1, color: "rgba(37,99,235,0)" },
          ]),
        },
      },
      {
        name: "實際需求人力",
        type: "line",
        data: props.requiredSo,
        smooth: true,
        symbol: "circle",
        symbolSize: 8,
        itemStyle: { color: "#3B82F6" },
        lineStyle: { width: 3, color: "#3B82F6" },
        label: {
          show: true,
          position: "top",
          fontFamily: "'Cascadia Code', ui-monospace, monospace",
          fontSize: 12,
          color: "#3B82F6",
          fontWeight: "bold",
          formatter: (p: any) => { if (!p.value) return ""; const r = Math.round(p.value * 100) / 100; return r % 1 === 0 ? String(r) : String(parseFloat(r.toFixed(2))); },
        },
      },
      {
        name: "近3月需求人力平均值",
        type: "line",
        data: props.avgSums,
        smooth: true,
        symbol: "diamond",
        symbolSize: 10,
        itemStyle: { color: "#6B7280" },
        lineStyle: { width: 2, color: "#6B7280", type: "dashed" },
        label: {
          show: true,
          position: "bottom",
          fontFamily: "'Cascadia Code', ui-monospace, monospace",
          fontSize: 12,
          color: "#6B7280",
          fontWeight: "bold",
          formatter: (p: any) => { if (!p.value) return ""; const r = Math.round(p.value * 100) / 100; return r % 1 === 0 ? String(r) : String(parseFloat(r.toFixed(2))); },
        },
      },
    ],
  };

  chart.setOption(option, true);
}

function handleResize() {
  chart?.resize();
}

onMounted(() => {
  renderChart();
  window.addEventListener("resize", handleResize);
});

onUnmounted(() => {
  window.removeEventListener("resize", handleResize);
  chart?.dispose();
});

watch(
  () => [props.days, props.attendance, props.requiredSo, props.avgSums],
  () => renderChart(),
  { deep: true }
);

defineExpose({
  getDataURL: () =>
    chart?.getDataURL({ type: "png", pixelRatio: 2, backgroundColor: "#fff" }),
});
</script>

<style scoped>
.chart-wrapper {
  background: #fff;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  border: 1px solid #D2D2D7;
  transition: box-shadow 200ms cubic-bezier(0.34, 1.56, 0.64, 1);
}
.chart-wrapper:hover {
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
}
.chart-header {
  margin-bottom: 10px;
}
.chart-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: #1D1D1F;
}
.chart-legend {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}
.legend-item {
  font-size: 13px;
  color: #6E6E73;
  display: flex;
  align-items: center;
  gap: 6px;
}
.legend-dot {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
}
.legend-line {
  display: inline-block;
  width: 20px;
  height: 0;
}
.chart-container {
  width: 100%;
  height: 450px;
  background: #fff;
}
</style>
