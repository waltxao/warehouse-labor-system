<template>
  <div class="dashboard">
    <!-- 顶部操作栏：左侧筛选器，右侧按钮 -->
    <div class="top-bar">
      <div class="filter-group">
        <el-select
          v-model="selectedWeek"
          placeholder="选择周次"
          style="width: 240px"
          @change="fetchData"
        >
          <el-option
            v-for="w in availableWeeks"
            :key="w.iso_week"
            :label="w.label"
            :value="w.iso_week"
          />
        </el-select>

        <el-select
          v-model="selectedWarehouse"
          placeholder="全部仓库"
          style="width: 180px; margin-left: 12px"
          @change="fetchData"
        >
          <el-option label="全部仓库 (汇总)" value="" />
          <el-option
            v-for="wh in warehouses"
            :key="wh.code"
            :label="wh.code"
            :value="wh.code"
          />
        </el-select>
      </div>

      <div class="action-group">
        <el-button type="primary" @click="fetchData">查询</el-button>
        <el-button class="export-btn" @click="exportPng">导出 PNG</el-button>
        <el-button
          v-if="selectedWarehouse"
          class="push-btn"
          :loading="pushing"
          @click="pushToWechat"
        >
          推送到企业微信
        </el-button>
      </div>
    </div>

    <!-- 图表说明区 -->
    <div class="chart-description">
      <div class="desc-title">
        {{ dateRange }}期间{{ warehouseDisplay }}實際出勤人數與實際需求人力情況
      </div>
      <div class="desc-content">
        <p><span class="desc-label">實際需求人力：</span>按各工序效能係數預測的人力需求，其中：跟車、留倉計算：1人，上門開客、Partime計算：0.5人；</p>
        <p><span class="desc-label">實際出勤人數：</span>當日實際出勤人數，（包含跟車、留倉、上門開客等人員）；</p>
        <p><span class="desc-label">近3月實際需求人力平均值：</span>取近3個月實際出勤人數計算的平均值，用作標準線；</p>
        <p class="desc-ps">Ps：每週PST週日更新數據，同步渠道：【🔁區域經理】</p>
      </div>
    </div>

    <!-- 图表区 -->
    <TrendChart
      ref="chartRef"
      :days="chartData.days"
      :attendance="chartData.attendance_sums"
      :requiredSo="chartData.required_so_sums"
      :avgSums="chartData.avg_sums"
      :title="chartTitle"
    />

    <!-- 数据概览 -->
    <div class="stats-grid" :style="{ gridTemplateColumns: selectedWarehouse ? 'repeat(3, 1fr)' : 'repeat(4, 1fr)' }">
      <div class="stat-card">
        <div class="stat-label">周总出勤人次</div>
        <div class="stat-value">{{ totalAttendance }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">周总需求人力</div>
        <div class="stat-value">{{ totalRequired }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">周总均值基线</div>
        <div class="stat-value">{{ totalAvg }}</div>
      </div>
      <div class="stat-card" v-if="!selectedWarehouse">
        <div class="stat-label">仓库数量</div>
        <div class="stat-value">{{ warehouseCount }}</div>
      </div>
    </div>

    <PageIntro :items="[
      '选择周次和仓库后点击查询，图表展示该周每日出勤人数与需求人力趋势',
      '蓝色实线为实际出勤人数，浅蓝实线为实际需求人力，橙色虚线为近3月均值基线',
      '上方KPI卡片显示周总出勤人次、需求人力、均值基线汇总数据',
      '点击导出 PNG 可保存当前图表为图片',
      '选择单个仓库后，可点击推送到企业微信按钮将图表发送到对应仓库群'
    ]" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";

function fmtNum(v: number): string {
  if (v === null || v === undefined || isNaN(v)) return "0";
  const rounded = Math.round(v * 100) / 100;
  if (rounded % 1 === 0) return String(rounded);
  return String(parseFloat(rounded.toFixed(2)));
}
import TrendChart from "../components/TrendChart.vue";
import client from "../api/client";
import PageIntro from "../components/PageIntro.vue";
import { pushChart } from "../api/webhook";
import { ElMessage } from "element-plus";

interface WeekInfo {
  iso_week: string;
  label: string;
  start_date: string | null;
  end_date: string | null;
}

interface WarehouseInfo {
  id: number;
  code: string;
  name: string | null;
}

const selectedWeek = ref("");
const availableWeeks = ref<WeekInfo[]>([]);
const selectedWarehouse = ref("");
const warehouses = ref<WarehouseInfo[]>([]);
const chartRef = ref();
const warehouseCount = ref(0);
const dateRange = ref("");

const chartData = ref({
  days: [] as string[],
  attendance_sums: [] as number[],
  required_so_sums: [] as number[],
  avg_sums: [] as number[],
});

const chartTitle = computed(() => {
  const wh = selectedWarehouse.value || "全仓汇总";
  return `仓库人力数据趋势 - ${wh}`;
});

const warehouseDisplay = computed(() => {
  if (!selectedWarehouse.value) return "全仓";
  return selectedWarehouse.value + "仓";
});

const totalAttendance = computed(() =>
  fmtNum(chartData.value.attendance_sums.reduce((a: number, b: number) => a + b, 0))
);
const totalRequired = computed(() =>
  fmtNum(chartData.value.required_so_sums.reduce((a: number, b: number) => a + b, 0))
);
const totalAvg = computed(() =>
  fmtNum(chartData.value.avg_sums.reduce((a: number, b: number) => a + b, 0))
);

async function fetchWeeks() {
  try {
    const resp: any = await client.get("/trends/weeks/list");
    if (resp?.code === 0 && resp.data) {
      availableWeeks.value = resp.data;
      if (availableWeeks.value.length > 0 && !selectedWeek.value) {
        selectedWeek.value = availableWeeks.value[0].iso_week;
      }
    }
  } catch (e) {
    console.error("Fetch weeks error:", e);
  }
}

async function fetchWarehouses() {
  try {
    const resp: any = await client.get("/warehouses");
    if (resp?.code === 0 && resp.data) {
      warehouses.value = resp.data;
      warehouseCount.value = resp.data.length;
    }
  } catch (e) {
    console.error("Fetch warehouses error:", e);
  }
}

async function fetchData() {
  if (!selectedWeek.value) return;
  try {
    let url = `/trends/summary/${selectedWeek.value}`;
    if (selectedWarehouse.value) {
      url += `?warehouse=${selectedWarehouse.value}`;
    }
    const resp: any = await client.get(url);
    if (resp?.code === 0 && resp.data) {
      const d = resp.data;
      chartData.value = {
        days: d.days,
        attendance_sums: d.attendance_sums,
        required_so_sums: d.required_so_sums,
        avg_sums: d.avg_sums,
      };
      dateRange.value = d.date_range || "";
    }
  } catch (e) {
    console.error("Fetch error:", e);
  }
}

function exportPng() {
  const url = chartRef.value?.getDataURL();
  if (url) {
    const a = document.createElement("a");
    a.href = url;
    a.download = `warehouse-trend-${selectedWeek.value}.png`;
    a.click();
  }
}

const pushing = ref(false);

async function pushToWechat() {
  if (!selectedWarehouse.value || !selectedWeek.value) return;
  pushing.value = true;
  try {
    const dataUrl = chartRef.value?.getDataURL();
    if (!dataUrl) {
      ElMessage.error("图表导出失败");
      return;
    }
    const base64 = dataUrl.split("base64,")[1] || dataUrl;
    const resp: any = await pushChart({
      warehouse_code: selectedWarehouse.value,
      iso_week: selectedWeek.value,
      chart_base64: base64,
    });
    if (resp?.code === 0) {
      ElMessage.success("推送成功");
    } else {
      ElMessage.error(resp?.message || "推送失败");
    }
  } catch (e: any) {
    ElMessage.error(e?.message || "推送失败");
  } finally {
    pushing.value = false;
  }
}

onMounted(async () => {
  await Promise.all([fetchWeeks(), fetchWarehouses()]);
  await fetchData();
});
</script>

<style scoped>
.dashboard {
  padding: 20px;
  background: #F2F2F7;
  min-height: calc(100vh - 60px);
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  background: #fff;
  padding: 16px 20px;
  border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  border: 1px solid #E5E5EA;
}

.filter-group {
  display: flex;
  align-items: center;
}

.action-group {
  display: flex;
  gap: 8px;
}

/* 查询按钮主色 */
:deep(.el-button--primary) {
  background-color: #007AFF;
  border-color: #007AFF;
  font-weight: 500;
  transition: all 200ms cubic-bezier(0.34, 1.56, 0.64, 1);
}
:deep(.el-button--primary:hover) {
  background-color: #0051D5;
  border-color: #0051D5;
}

/* 导出按钮边框样式 */
:deep(.export-btn) {
  background: #fff;
  border: 1px solid #E5E5EA;
  color: #007AFF;
  font-weight: 500;
  transition: all 200ms cubic-bezier(0.34, 1.56, 0.64, 1);
}
:deep(.export-btn:hover) {
  border-color: #007AFF;
  color: #007AFF;
  background: #F2F2F7;
}

/* 筛选器样式覆盖 */
:deep(.el-select__wrapper) {
  border-radius: 12px;
  box-shadow: 0 0 0 1px #E5E5EA inset;
  transition: box-shadow 200ms cubic-bezier(0.34, 1.56, 0.64, 1);
}
:deep(.el-select__wrapper:hover) {
  box-shadow: 0 0 0 1px #5AC8FA inset;
}
:deep(.el-select__wrapper.is-focused) {
  box-shadow: 0 0 0 1px #007AFF inset;
}

.chart-description {
  background: #FFF8E7;
  border-radius: 16px;
  padding: 16px 20px;
  margin-bottom: 16px;
  box-shadow: 0 1px 3px rgba(255,149,0,0.10);
  border-left: 4px solid #FF9500;
}

.desc-title {
  font-size: 15px;
  font-weight: 600;
  color: #1C1C1E;
  margin-bottom: 8px;
}

.desc-content {
  font-size: 13px;
  color: #8E8E93;
  line-height: 1.8;
}

.desc-content p {
  margin: 2px 0;
}

.desc-label {
  font-weight: 600;
  color: #1C1C1E;
}

.desc-ps {
  color: #8E8E93;
  font-style: italic;
  margin-top: 4px !important;
}

.stats-grid {
  display: grid;
  gap: 16px;
  margin-top: 16px;
}

.stat-card {
  background: #fff;
  border-radius: 16px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  border: 1px solid #E5E5EA;
  transition: transform 200ms cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 200ms cubic-bezier(0.34, 1.56, 0.64, 1);
}

.stat-card:hover {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 8px 24px rgba(0,0,0,0.08);
}

.stat-label {
  font-size: 14px;
  color: #8E8E93;
  margin-bottom: 8px;
  font-weight: 500;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1C1C1E;
  font-family: 'SF Mono', ui-monospace, monospace;
  letter-spacing: -0.02em;
}

:deep(.push-btn) {
  background: #FF9500;
  border: 1px solid #FF9500;
  color: #fff;
  font-weight: 500;
  transition: all 200ms cubic-bezier(0.34, 1.56, 0.64, 1);
}
:deep(.push-btn:hover) {
  background: #E68600;
  border-color: #E68600;
}
</style>
