<template>
  <div>
    <el-card>
      <el-form inline>
        <el-form-item :label="t('selectWarehouse')">
          <el-select v-model="selectedWarehouse" @change="loadData" placeholder="选择仓库">
            <el-option v-for="w in warehouses" :key="w.code" :label="w.code" :value="w.code" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('selectWeek')">
          <el-input v-model="isoWeek" placeholder="例如 2026-W27" style="width: 160px" @change="loadData" />
        </el-form-item>
        <el-button :loading="loading" @click="loadData">查询</el-button>
        <el-button @click="exportPng" :disabled="!chartData">{{ t('export') }} PNG</el-button>
      </el-form>

      <TrendChart
        v-if="chartData"
        ref="trendChartRef"
        :days="chartData.dates"
        :attendance="chartData.attendance"
        :required-so="chartData.required_so"
        :avg-sums="chartData.three_month_avg"
      />

      <el-empty v-else description="请选择仓库与周次后查询趋势数据" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import TrendChart from '../components/TrendChart.vue'
import { getChartData } from '../api/trends'
import client from '../api/client'
import { getCurrentIsoWeek } from '../utils/date'

const route = useRoute()
const { t } = useI18n()
const selectedWarehouse = ref((route.params.warehouseCode as string) || '')
const isoWeek = ref(getCurrentIsoWeek())
const chartData = ref<any>(null)
const warehouses = ref<any[]>([])
const loading = ref(false)
const trendChartRef = ref<InstanceType<typeof TrendChart>>()

onMounted(async () => {
  try {
    const resp: any = await client.get('/warehouses')
    warehouses.value = resp.data
    if (!selectedWarehouse.value && warehouses.value.length) {
      selectedWarehouse.value = warehouses.value[0].code
    }
    if (selectedWarehouse.value) await loadData()
  } catch {
    /* 忽略 */
  }
})

async function loadData() {
  if (!selectedWarehouse.value || !isoWeek.value) return
  loading.value = true
  try {
    const resp: any = await getChartData(selectedWarehouse.value, isoWeek.value)
    chartData.value = resp.data
  } catch (err: any) {
    chartData.value = null
  } finally {
    loading.value = false
  }
}

function exportPng() {
  const url = trendChartRef.value?.getDataURL()
  if (!url) return
  const a = document.createElement('a')
  a.href = url
  a.download = `trend-${selectedWarehouse.value}-${isoWeek.value}.png`
  a.click()
}
</script>
