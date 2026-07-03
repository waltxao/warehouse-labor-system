<template>
  <el-card>
    <el-tabs>
      <el-tab-pane label="告警日志">
        <el-form inline style="margin-bottom: 12px">
          <el-form-item :label="t('selectWeek')">
            <el-input v-model="isoWeek" placeholder="留空查询全部" style="width: 180px" clearable />
          </el-form-item>
          <el-button @click="loadLogs">查询</el-button>
        </el-form>
        <el-table :data="logs" border stripe>
          <el-table-column prop="trigger_date" label="触发日期" />
          <el-table-column prop="warehouse_code" label="仓库" />
          <el-table-column prop="metric" label="指标" />
          <el-table-column prop="trigger_value" label="触发值" />
          <el-table-column prop="status" label="状态" />
        </el-table>
      </el-tab-pane>

      <el-tab-pane v-if="auth.hasRole('admin')" label="告警规则">
        <el-button type="primary" @click="showDialog = true">新建规则</el-button>
        <el-table :data="rules" border stripe style="margin-top: 12px">
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="metric" label="指标" />
          <el-table-column prop="condition_type" label="条件" />
          <el-table-column prop="threshold_value" label="阈值" />
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="showDialog" title="新建告警规则" width="480px">
      <el-form label-width="80px">
        <el-form-item label="名称"><el-input v-model="ruleForm.name" /></el-form-item>
        <el-form-item label="指标">
          <el-select v-model="ruleForm.metric" style="width: 100%">
            <el-option label="出勤人数" value="attendance" />
            <el-option label="需求SO" value="required_so" />
            <el-option label="满足率" value="fulfillment_rate" />
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
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import { getRules, createRule, getLogs } from '../api/alerts'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'

const { t } = useI18n()
const auth = useAuthStore()
const rules = ref<any[]>([])
const logs = ref<any[]>([])
const showDialog = ref(false)
const creating = ref(false)
const isoWeek = ref('')
const ruleForm = reactive({
  name: '',
  metric: 'attendance',
  condition_type: 'gt',
  threshold_value: 0,
})

onMounted(async () => {
  await Promise.all([loadRules(), loadLogs()])
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
