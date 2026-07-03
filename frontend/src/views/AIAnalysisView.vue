<template>
  <el-card>
    <el-form inline>
      <el-form-item label="分析类型">
        <el-select v-model="form.type" style="width: 160px">
          <el-option label="周对比" value="weekly_compare" />
          <el-option label="多仓对比" value="multi_warehouse" />
          <el-option label="月趋势" value="monthly_trend" />
          <el-option label="异常检测" value="anomaly_detection" />
        </el-select>
      </el-form-item>
      <el-form-item label="仓库">
        <el-select v-model="form.warehouseCodes" multiple collapse-tags style="min-width: 240px">
          <el-option v-for="w in warehouses" :key="w.code" :label="w.code" :value="w.code" />
        </el-select>
      </el-form-item>
      <el-form-item :label="t('selectWeek')">
        <el-input v-model="form.isoWeek" placeholder="例如 2026-W27" style="width: 160px" />
      </el-form-item>
      <el-button type="primary" :loading="loading" @click="runAnalysis">{{ t('analyze') }}</el-button>
    </el-form>

    <div
      v-if="report"
      class="ai-report"
      v-html="renderedReport"
    ></div>
    <el-empty v-else description="选择参数后点击分析生成 AI 报告" />
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { analyze } from '../api/ai'
import MarkdownIt from 'markdown-it'
import client from '../api/client'
import { getCurrentIsoWeek } from '../utils/date'

const { t } = useI18n()
const md = new MarkdownIt()
const warehouses = ref<any[]>([])
const loading = ref(false)
const report = ref('')
const renderedReport = computed(() => md.render(report.value))
const form = ref({
  type: 'weekly_compare',
  warehouseCodes: [] as string[],
  isoWeek: getCurrentIsoWeek(),
})

onMounted(async () => {
  try {
    const resp: any = await client.get('/warehouses')
    warehouses.value = resp.data
  } catch {
    /* 忽略 */
  }
})

async function runAnalysis() {
  if (form.value.warehouseCodes.length === 0 || !form.value.isoWeek) return
  loading.value = true
  try {
    const resp: any = await analyze(form.value.type, form.value.warehouseCodes, form.value.isoWeek)
    report.value = resp.data?.report || ''
  } catch {
    report.value = ''
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.ai-report {
  margin-top: 20px;
  padding: 20px;
  background: #f9f9f9;
  border-radius: 8px;
  line-height: 1.7;
}
</style>
