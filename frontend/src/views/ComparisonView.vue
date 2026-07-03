<template>
  <el-card>
    <el-form inline>
      <el-form-item label="仓库（最多6个）">
        <el-select
          v-model="selectedWarehouses"
          multiple
          collapse-tags
          collapse-tags-tooltip
          :max-collapse-tags="6"
          placeholder="选择仓库"
          style="min-width: 320px"
        >
          <el-option v-for="w in warehouses" :key="w.code" :label="w.code" :value="w.code" />
        </el-select>
      </el-form-item>
      <el-form-item :label="t('selectWeek')">
        <el-input v-model="isoWeek" placeholder="例如 2026-W27" style="width: 160px" />
      </el-form-item>
      <el-form-item label="指标">
        <el-select v-model="metric" style="width: 140px">
          <el-option label="出勤人数" value="attendance" />
          <el-option label="需求SO" value="required_so" />
          <el-option label="节省人数" value="savings" />
          <el-option label="满足率" value="fulfillment_rate" />
        </el-select>
      </el-form-item>
      <el-form-item label="图表">
        <el-radio-group v-model="chartType">
          <el-radio-button value="bar">柱状图</el-radio-button>
          <el-radio-button value="line">折线图</el-radio-button>
        </el-radio-group>
      </el-form-item>
      <el-button type="primary" :loading="loading" @click="loadData">对比</el-button>
    </el-form>

    <ComparisonChart
      v-if="compData"
      :dates="compData.dates"
      :series="compData.series"
      :chart-type="chartType"
    />
    <el-empty v-else description="请选择仓库与周次后进行多仓对比" />
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import ComparisonChart from '../components/ComparisonChart.vue'
import { compare } from '../api/comparison'
import client from '../api/client'
import { getCurrentIsoWeek } from '../utils/date'

const { t } = useI18n()
const selectedWarehouses = ref<string[]>([])
const isoWeek = ref(getCurrentIsoWeek())
const metric = ref('attendance')
const chartType = ref<'bar' | 'line'>('bar')
const warehouses = ref<any[]>([])
const compData = ref<{ dates: string[]; series: { name: string; data: (number | null)[] }[] } | null>(null)
const loading = ref(false)

onMounted(async () => {
  try {
    const resp: any = await client.get('/warehouses')
    warehouses.value = resp.data
  } catch {
    /* 忽略 */
  }
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
