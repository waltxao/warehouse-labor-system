<template>
  <div class="page-container">
    <!-- 顶部操作栏：左侧筛选器，右侧按钮 -->
    <div class="top-bar">
      <div class="filter-group">
        <el-select
          v-model="selectedWarehouses"
          multiple
          collapse-tags
          collapse-tags-tooltip
          :max-collapse-tags="6"
          placeholder="选择仓库（最多6个）"
          style="min-width: 320px"
        >
          <el-option
            v-for="w in warehouses"
            :key="w.code"
            :label="w.code"
            :value="w.code"
          />
        </el-select>

        <el-select
          v-model="isoWeek"
          placeholder="选择周次"
          style="width: 260px"
        >
          <el-option
            v-for="w in availableWeeks"
            :key="w.iso_week"
            :label="w.label"
            :value="w.iso_week"
          />
        </el-select>

        <el-select v-model="metric" placeholder="指标" style="width: 150px">
          <el-option label="出勤人数" value="attendance" />
          <el-option label="需求SO" value="required_so" />
          <el-option label="节省人数" value="savings" />
        </el-select>

        <el-radio-group v-model="chartType">
          <el-radio-button value="bar">柱状图</el-radio-button>
          <el-radio-button value="line">折线图</el-radio-button>
        </el-radio-group>
      </div>

      <div class="action-group">
        <el-button type="primary" :loading="loading" @click="loadData">对比</el-button>
      </div>
    </div>

    <!-- 内容区 -->
    <div class="content-card">
      <ComparisonChart
        v-if="compData"
        :dates="compData.dates"
        :series="compData.series"
        :chart-type="chartType"
      />
      <el-empty v-else description="请选择仓库与周次后进行多仓对比" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import ComparisonChart from '../components/ComparisonChart.vue'
import { compare } from '../api/comparison'
import client from '../api/client'

const { t } = useI18n()
const selectedWarehouses = ref<string[]>([])
const isoWeek = ref('')
const metric = ref('attendance')
const chartType = ref<'bar' | 'line'>('bar')
const warehouses = ref<any[]>([])
const availableWeeks = ref<any[]>([])
const compData = ref<{ dates: string[]; series: { name: string; data: (number | null)[] }[] } | null>(null)
const loading = ref(false)

async function fetchWeeks() {
  try {
    const resp: any = await client.get('/trends/weeks/list')
    if (resp?.code === 0 && resp.data) {
      availableWeeks.value = resp.data
      if (availableWeeks.value.length > 0 && !isoWeek.value) {
        isoWeek.value = availableWeeks.value[0].iso_week
      }
    }
  } catch {
    /* 忽略 */
  }
}

onMounted(async () => {
  try {
    const resp: any = await client.get('/warehouses')
    if (resp?.code === 0 && resp.data) {
      warehouses.value = resp.data
    } else {
      warehouses.value = resp.data
    }
  } catch {
    /* 忽略 */
  }
  await fetchWeeks()
})

async function loadData() {
  if (selectedWarehouses.value.length === 0 || !isoWeek.value) return
  if (selectedWarehouses.value.length > 6) return
  loading.value = true
  try {
    const resp: any = await compare(selectedWarehouses.value, isoWeek.value, metric.value)
    const data = resp.data
    const dates: string[] =
      data.warehouses?.[0]?.values?.map((v: any) => v.date) || []
    const series = (data.warehouses || []).map((w: any) => ({
      name: w.code,
      data: (w.values || []).map((v: any) => v.value),
    }))
    compData.value = { dates, series }
  } catch {
    compData.value = null
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.page-container {
  padding: 20px;
  background: #F8FAFC;
  min-height: calc(100vh - 60px);
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  background: #fff;
  padding: 16px 20px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(30, 58, 138, 0.08);
  border: 1px solid #DBEAFE;
}

.filter-group {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.action-group {
  display: flex;
  gap: 8px;
}

.content-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(30, 58, 138, 0.08);
  border: 1px solid #DBEAFE;
  min-height: 400px;
  transition: transform 200ms ease, box-shadow 200ms ease;
}

.content-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(30, 58, 138, 0.16);
}

:deep(.el-button--primary) {
  background-color: #1E40AF;
  border-color: #1E40AF;
  font-weight: 500;
  transition: all 200ms ease;
}
:deep(.el-button--primary:hover) {
  background-color: #1E3A8A;
  border-color: #1E3A8A;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(30, 64, 175, 0.25);
}

:deep(.el-radio-button__inner) {
  border-color: #DBEAFE;
  color: #1E40AF;
  transition: all 200ms ease;
}
:deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background-color: #1E40AF;
  border-color: #1E40AF;
  color: #fff;
  box-shadow: -1px 0 0 0 #1E40AF;
}

:deep(.el-select__wrapper) {
  border-radius: 8px;
  box-shadow: 0 0 0 1px #DBEAFE inset;
  transition: box-shadow 200ms ease;
}
:deep(.el-select__wrapper:hover) {
  box-shadow: 0 0 0 1px #3B82F6 inset;
}
:deep(.el-select__wrapper.is-focused) {
  box-shadow: 0 0 0 1px #1E40AF inset;
}
</style>
