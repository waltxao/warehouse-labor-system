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

    <PageIntro :items="[
      '选择分析类型（周对比、多仓对比、月趋势、异常检测）',
      '选择目标仓库和周次后点击分析按钮',
      'AI 生成 Markdown 格式的分析报告，支持标题、表格、列表渲染',
      '报告自动保存到日志，可后续查看'
    ]" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { analyze } from '../api/ai'
import MarkdownIt from 'markdown-it'
import client from '../api/client'
import PageIntro from '../components/PageIntro.vue'

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
  flex-wrap: wrap;
  gap: 12px;
}

.action-group {
  display: flex;
  gap: 8px;
}

.content-card {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  border: 1px solid #D2D2D7;
  min-height: 400px;
  transition: transform 200ms cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 200ms cubic-bezier(0.34, 1.56, 0.64, 1);
}

.content-card:hover {
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
}

:deep(.el-button--primary) {
  background-color: #2563EB;
  border-color: #2563EB;
  font-weight: 500;
  transition: all 200ms cubic-bezier(0.34, 1.56, 0.64, 1);
}
:deep(.el-button--primary:hover) {
  background-color: #1D4ED8;
  border-color: #1D4ED8;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(37,99,235,0.20);
}

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

/* AI 报告区域 */
.ai-report {
  line-height: 1.8;
  color: #1D1D1F;
  font-size: 14px;
  font-family: 'Segoe UI', 'Segoe UI', sans-serif;
}

.ai-report :deep(h1),
.ai-report :deep(h2),
.ai-report :deep(h3),
.ai-report :deep(h4) {
  color: #2563EB;
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
  color: #2563EB;
  font-weight: 600;
}

.ai-report :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 14px 0;
  border-radius: 12px;
  overflow: hidden;
}

.ai-report :deep(th),
.ai-report :deep(td) {
  border: 1px solid #D2D2D7;
  padding: 10px 14px;
  text-align: left;
  font-size: 13px;
}

.ai-report :deep(th) {
  background: #F5F5F7;
  color: #2563EB;
  font-weight: 600;
}

.ai-report :deep(code) {
  background: #F5F5F7;
  color: #2563EB;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Cascadia Code', ui-monospace, monospace;
  font-size: 13px;
}

.ai-report :deep(blockquote) {
  border-left: 4px solid #3B82F6;
  background: #F5F5F7;
  padding: 10px 16px;
  margin: 12px 0;
  color: #6E6E73;
  border-radius: 0 8px 8px 0;
}
</style>
