<template>
  <div class="page-container">
    <!-- 顶部操作栏：左侧筛选器，右侧按钮 -->
    <div class="top-bar">
      <div class="filter-group">
        <el-select v-model="isoWeek" placeholder="选择周次" style="width: 260px" clearable>
          <el-option label="全部" value="" />
          <el-option
            v-for="w in availableWeeks"
            :key="w.iso_week"
            :label="w.label"
            :value="w.iso_week"
          />
        </el-select>
      </div>

      <div class="action-group">
        <el-button type="primary" @click="loadLogs">查询</el-button>
      </div>
    </div>

    <!-- 内容区 -->
    <div class="content-card">
      <el-tabs>
        <el-tab-pane label="告警日志">
          <el-table :data="logs" stripe class="alert-table">
            <el-table-column prop="trigger_date" label="触发日期" />
            <el-table-column prop="warehouse_code" label="仓库" />
            <el-table-column prop="metric" label="指标" />
            <el-table-column prop="trigger_value" label="触发值" />
            <el-table-column prop="status" label="状态" />
          </el-table>
        </el-tab-pane>

        <el-tab-pane v-if="auth.hasRole('admin')" label="告警规则">
          <el-button type="primary" @click="showDialog = true" style="margin-bottom: 16px">新建规则</el-button>
          <el-table :data="rules" stripe class="alert-table">
            <el-table-column prop="name" label="名称" />
            <el-table-column prop="metric" label="指标" />
            <el-table-column prop="condition_type" label="条件" />
            <el-table-column prop="threshold_value" label="阈值" />
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 新建规则对话框 -->
    <el-dialog v-model="showDialog" title="新建告警规则" width="480px">
      <el-form label-width="80px">
        <el-form-item label="名称"><el-input v-model="ruleForm.name" /></el-form-item>
        <el-form-item label="指标">
          <el-select v-model="ruleForm.metric" style="width: 100%">
            <el-option label="出勤人数" value="attendance" />
            <el-option label="需求SO" value="required_so" />
          </el-select>
        </el-form-item>
        <el-form-item label="条件">
          <el-select v-model="ruleForm.condition_type" style="width: 100%">
            <el-option label="大于" value="gt" />
            <el-option label="小于" value="lt" />
          </el-select>
        </el-form-item>
        <el-form-item label="阈值"><el-input-number v-model="ruleForm.threshold_value" :min="0" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import { getRules, createRule, getLogs } from '../api/alerts'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'
import client from '../api/client'

const { t } = useI18n()
const auth = useAuthStore()
const rules = ref<any[]>([])
const logs = ref<any[]>([])
const showDialog = ref(false)
const creating = ref(false)
const isoWeek = ref('')
const availableWeeks = ref<any[]>([])
const ruleForm = reactive({
  name: '',
  metric: 'attendance',
  condition_type: 'gt',
  threshold_value: 0,
})

async function fetchWeeks() {
  try {
    const resp: any = await client.get('/trends/weeks/list')
    if (resp?.code === 0 && resp.data) {
      availableWeeks.value = resp.data
    }
  } catch {
    /* 忽略 */
  }
}

onMounted(async () => {
  await Promise.all([loadRules(), loadLogs(), fetchWeeks()])
})

async function loadRules() {
  try {
    const resp: any = await getRules()
    rules.value = resp.data
  } catch {
    /* 忽略 */
  }
}

async function loadLogs() {
  try {
    const resp: any = await getLogs(isoWeek.value || undefined)
    logs.value = resp.data
  } catch {
    /* 忽略 */
  }
}

async function handleCreate() {
  creating.value = true
  try {
    await createRule(ruleForm)
    ElMessage.success('创建成功')
    showDialog.value = false
    await loadRules()
  } catch (err: any) {
    ElMessage.error(err?.message || '创建失败')
  } finally {
    creating.value = false
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

/* 标签页样式 */
:deep(.el-tabs__item) {
  color: #64748B;
  font-size: 15px;
  font-weight: 500;
  transition: color 200ms ease;
}
:deep(.el-tabs__item.is-active) {
  color: #1E40AF;
}
:deep(.el-tabs__active-bar) {
  background-color: #1E40AF;
}
:deep(.el-tabs__item:hover) {
  color: #3B82F6;
}

/* 表格样式 */
:deep(.alert-table) {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #DBEAFE;
}
:deep(.alert-table th.el-table__cell) {
  background: #EFF6FF;
  color: #1E40AF;
  font-weight: 600;
  font-size: 14px;
}
:deep(.alert-table .el-table__cell) {
  border-color: #DBEAFE;
  color: #1E3A8A;
}
:deep(.alert-table tr:hover > td.el-table__cell) {
  background: #F8FAFC !important;
}
:deep(.alert-table .el-table__row:hover) {
  transform: translateY(-1px);
}
</style>
