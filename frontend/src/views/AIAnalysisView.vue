<template>
  <div class="page-container">
    <!-- 顶部操作栏：左侧筛选器，右侧按钮 -->
    <div class="top-bar">
      <div class="filter-group">
        <el-select v-model="form.type" placeholder="分析类型" style="width: 160px">
          <el-option label="周对比" value="weekly_compare" />
          <el-option label="多仓对比" value="multi_warehouse" />
          <el-option label="月趋势" value="monthly_trend" />
          <el-option label="异常检测" value="anomaly_detection" />
        </el-select>

        <el-select
          v-model="form.warehouseCodes"
          multiple
          collapse-tags
          collapse-tags-tooltip
          placeholder="选择仓库"
          style="min-width: 260px"
        >
          <el-option
            v-for="w in warehouses"
            :key="w.code"
            :label="w.code"
            :value="w.code"
          />
        </el-select>

        <el-select v-model="form.isoWeek" placeholder="选择周次" style="width: 260px">
          <el-option
            v-for="w in availableWeeks"
            :key="w.iso_week"
            :label="w.label"
            :value="w.iso_week"
          />
        </el-select>
      </div>

      <div class="action-group">
        <el-button type="primary" :loading="loading" @click="runAnalysis">{{ t('analyze') }}</el-button>
      </div>
    </div>

    <!-- 内容区 -->
    <div class="content-card">
      <div v-if="report" class="ai-report" v-html="renderedReport"></div>
      <el-empty v-else description="选择参数后点击分析生成 AI 报告" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { analyze } from '../api/ai'
import MarkdownIt from 'markdown-it'
import client from '../api/client'

const { t } = useI18n()
const md = new MarkdownIt()
const warehouses = ref<any[]>([])
const availableWeeks = ref<any[]>([])
const loading = ref(false)
const report = ref('')
const renderedReport = computed(() => md.render(report.value))
const form = ref({
  type: 'weekly_compare',
  warehouseCodes: [] as string[],
  isoWeek: '',
})

async function fetchWeeks() {
  try {
    const resp: any = await client.get('/trends/weeks/list')
    if (resp?.code === 0 && resp.data) {
      availableWeeks.value = resp.data
      if (availableWeeks.value.length > 0 && !form.value.isoWeek) {
        form.value.isoWeek = availableWeeks.value[0].iso_week
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

/* AI 报告区域 */
.ai-report {
  line-height: 1.8;
  color: #1E3A8A;
  font-size: 14px;
  font-family: 'Fira Sans', sans-serif;
}

.ai-report :deep(h1),
.ai-report :deep(h2),
.ai-report :deep(h3),
.ai-report :deep(h4) {
  color: #1E40AF;
  font-weight: 600;
  margin: 18px 0 10px;
  line-height: 1.4;
}

.ai-report :deep(h1) { font-size: 22px; }
.ai-report :deep(h2) { font-size: 18px; }
.ai-report :deep(h3) { font-size: 16px; }

.ai-report :deep(p) {
  margin: 10px 0;
}

.ai-report :deep(ul),
.ai-report :deep(ol) {
  padding-left: 22px;
  margin: 10px 0;
}

.ai-report :deep(li) {
  margin: 4px 0;
}

.ai-report :deep(strong) {
  color: #1E40AF;
  font-weight: 600;
}

.ai-report :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 14px 0;
  border-radius: 8px;
  overflow: hidden;
}

.ai-report :deep(th),
.ai-report :deep(td) {
  border: 1px solid #DBEAFE;
  padding: 10px 14px;
  text-align: left;
  font-size: 13px;
}

.ai-report :deep(th) {
  background: #EFF6FF;
  color: #1E40AF;
  font-weight: 600;
}

.ai-report :deep(code) {
  background: #EFF6FF;
  color: #1E40AF;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Fira Code', monospace;
  font-size: 13px;
}

.ai-report :deep(blockquote) {
  border-left: 4px solid #3B82F6;
  background: #F8FAFC;
  padding: 10px 16px;
  margin: 12px 0;
  color: #64748B;
  border-radius: 0 8px 8px 0;
}
</style>
