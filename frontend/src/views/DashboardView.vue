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
        <p><span class="desc-label">歷史均值：</span>取近3個月實際出勤人數計算的平均值，用作標準線；</p>
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

    <!-- 详细数据表格 -->
    <div class="detail-table">
      <el-table :data="tableData" stripe border style="width: 100%">
        <el-table-column prop="metric" label="指標" width="180" fixed />
        <el-table-column
          v-for="(day, i) in chartData.days"
          :key="i"
          :prop="`d${i}`"
          :label="day"
          align="center"
          :formatter="fmtCell"
        />
        <el-table-column prop="total" label="匯總" width="120" align="center" :formatter="fmtCell" />
      </el-table>
    </div>

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
        <div class="stat-label">周历史需求人数均值</div>
        <div class="stat-value">{{ totalAvg }}</div>
      </div>
      <div class="stat-card" v-if="!selectedWarehouse">
        <div class="stat-label">仓库数量</div>
        <div class="stat-value">{{ warehouseCount }}</div>
      </div>
    </div>

    <PageIntro :items="[
      '选择周次和仓库后点击查询，图表展示该周每日出勤人数与需求人力趋势',
      '蓝色实线为实际出勤人数，浅蓝实线为实际需求人力，灰色虚线为历史需求人数均值基线',
      '上方KPI卡片显示周总出勤人次、需求人力、均值基线汇总数据',
      '点击导出 PNG 可保存当前图表为图片'
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

function fmtCell(_row: any, _col: any, val: number): string {
  return fmtNum(val);
}

const tableData = computed(() => {
  const d = chartData.value;
  const makeRow = (metric: string, vals: number[]) => {
    const row: Record<string, number | string> = { metric };
    vals.forEach((v, i) => { row[`d${i}`] = v; });
    row.total = vals.reduce((a, b) => a + b, 0);
    return row;
  };
  return [
    makeRow('實際出勤人數', d.attendance_sums),
    makeRow('實際需求人力', d.required_so_sums),
    makeRow('歷史需求人數均值', d.avg_sums),
  ];
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

onMounted(async () => {
  await Promise.all([fetchWeeks(), fetchWarehouses()]);
  await fetchData();
});
</script>

<style scoped>
.dashboard {
  padding: 20px;
  background: #F5F5F7;
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
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  border: 1px solid #D2D2D7;
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
  background-color: #2563EB;
  border-color: #2563EB;
  font-weight: 500;
  transition: all 200ms cubic-bezier(0.34, 1.56, 0.64, 1);
}
:deep(.el-button--primary:hover) {
  background-color: #1D4ED8;
  border-color: #1D4ED8;
}

/* 导出按钮边框样式 */
:deep(.export-btn) {
  background: #fff;
  border: 1px solid #D2D2D7;
  color: #2563EB;
  font-weight: 500;
  transition: all 200ms cubic-bezier(0.34, 1.56, 0.64, 1);
}
:deep(.export-btn:hover) {
  border-color: #2563EB;
  color: #2563EB;
  background: #F5F5F7;
}

/* 筛选器样式覆盖 */
:deep(.el-select__wrapper) {
  border-radius: 12px;
  box-shadow: 0 0 0 1px #D2D2D7 inset;
  transition: box-shadow 200ms cubic-bezier(0.34, 1.56, 0.64, 1);
}
:deep(.el-select__wrapper:hover) {
  box-shadow: 0 0 0 1px #3B82F6 inset;
}
:deep(.el-select__wrapper.is-focused) {
  box-shadow: 0 0 0 1px #2563EB inset;
}

.chart-description {
  background: #F5F5F7;
  border-radius: 16px;
  padding: 16px 20px;
  margin-bottom: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.10);
  border-left: 4px solid #2563EB;
}

.desc-title {
  font-size: 15px;
  font-weight: 600;
  color: #1D1D1F;
  margin-bottom: 8px;
}

.desc-content {
  font-size: 13px;
  color: #6E6E73;
  line-height: 1.8;
}

.desc-content p {
  margin: 2px 0;
}

.desc-label {
  font-weight: 600;
  color: #1D1D1F;
}

.desc-ps {
  color: #6E6E73;
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
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  border: 1px solid #D2D2D7;
  transition: transform 200ms cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 200ms cubic-bezier(0.34, 1.56, 0.64, 1);
}

.stat-card:hover {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
}

.stat-label {
  font-size: 14px;
  color: #6E6E73;
  margin-bottom: 8px;
  font-weight: 500;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1D1D1F;
  font-family: 'Cascadia Code', ui-monospace, monospace;
  letter-spacing: -0.02em;
}

.detail-table {
  margin-top: 16px;
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  border: 1px solid #D2D2D7;
}

:deep(.detail-table .el-table) {
  border: none;
  font-size: 14px;
}

:deep(.detail-table .el-table__header th) {
  background: #1D1D1F !important;
  color: #fff;
  font-weight: 600;
  border-bottom: none;
}

:deep(.detail-table .el-table__body td) {
  border-bottom: 1px solid #D2D2D7;
}

:deep(.detail-table .el-table__body td:first-child) {
  font-weight: 600;
  color: #1D1D1F;
}

:deep(.detail-table .el-table__body td:last-child) {
  font-weight: 700;
  color: #2563EB;
  background: #EFF6FF;
}

</style>
