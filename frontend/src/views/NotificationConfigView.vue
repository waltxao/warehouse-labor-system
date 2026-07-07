<template>
  <div class="page-container">
    <!-- 顶部栏：标题 + 新建按钮 -->
    <div class="top-bar">
      <div class="title-group">
        <h2 class="page-title">推送配置</h2>
        <p class="page-subtitle">配置各仓库的企业微信 Webhook，用于推送人力数据图表</p>
      </div>
      <el-button class="primary-btn" @click="openCreate">新建配置</el-button>
    </div>

    <!-- 配置表格 -->
    <div class="content-card">
      <el-table :data="configs" stripe class="webhook-table" v-loading="loading">
        <el-table-column prop="warehouse_code" label="仓库代码" width="120" />
        <el-table-column prop="warehouse_name" label="仓库名称" width="120" />
        <el-table-column label="Webhook URL" min-width="260">
          <template #default="{ row }">
            <span class="url-cell" :title="row.webhook_url">{{ row.webhook_url }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="notify_users" label="通知人员" min-width="160">
          <template #default="{ row }">
            <span>{{ row.notify_users || '—' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <span :class="['status-tag', row.is_active ? 'active' : 'inactive']">
              {{ row.is_active ? '启用' : '禁用' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button size="small" link class="edit-link" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" link class="del-link" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 编辑/新建对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑推送配置' : '新建推送配置'" width="520px">
      <el-form label-width="110px" :model="form">
        <el-form-item label="仓库">
          <el-select
            v-model="form.warehouse_id"
            placeholder="选择仓库"
            style="width: 100%"
            :disabled="isEdit"
          >
            <el-option
              v-for="wh in warehouses"
              :key="wh.id"
              :label="wh.code + (wh.name ? ' - ' + wh.name : '')"
              :value="wh.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Webhook URL">
          <el-input
            v-model="form.webhook_url"
            placeholder="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx"
          />
        </el-form-item>
        <el-form-item label="通知人员昵称">
          <el-input
            v-model="form.notify_users"
            placeholder="企业微信昵称，逗号分隔，如：张三,李四"
          />
        </el-form-item>
        <el-form-item label="启用状态">
          <el-switch v-model="form.is_active" />
        </el-form-item>
        <el-form-item label="推送文字模板">
          <el-input
            v-model="form.message_template"
            type="textarea"
            :rows="4"
            placeholder="留空使用默认模板。支持变量：{warehouse} {date_range} {notify_users} {total_attendance} {total_required}"
          />
        </el-form-item>
        <el-form-item label="定时推送">
          <el-switch v-model="form.schedule_enabled" />
        </el-form-item>
        <template v-if="form.schedule_enabled">
          <el-form-item label="推送日期">
            <el-select v-model="form.schedule_day" style="width: 100%">
              <el-option label="周一" :value="0" />
              <el-option label="周二" :value="1" />
              <el-option label="周三" :value="2" />
              <el-option label="周四" :value="3" />
              <el-option label="周五" :value="4" />
              <el-option label="周六" :value="5" />
              <el-option label="周日" :value="6" />
            </el-select>
          </el-form-item>
          <el-form-item label="推送时间">
            <el-time-picker v-model="form.schedule_time" format="HH:mm" value-format="HH:mm" placeholder="选择时间" style="width: 100%" />
          </el-form-item>
        </template>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button class="primary-btn" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <PageIntro :items="[
      '为每个仓库配置企业微信 Webhook 地址和通知人员昵称',
      '通知人员昵称使用英文逗号分隔，如：张三,李四',
      '配置完成后，在总览页可点击推送按钮将图表发送到企业微信群',
      '推送消息包含图表截图和 markdown 富文本，并@通知人员昵称',
      '仅管理员可访问此页面'
    ]" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getWebhooks, createWebhook, updateWebhook, deleteWebhook } from '../api/webhook'
import PageIntro from '../components/PageIntro.vue'
import client from '../api/client'

interface WebhookConfig {
  id: number
  warehouse_id: number
  warehouse_code: string
  warehouse_name: string | null
  webhook_url: string
  notify_users: string | null
  is_active: boolean
  message_template: string | null
  schedule_enabled: boolean
  schedule_day: number
  schedule_time: string
}

interface WarehouseInfo {
  id: number
  code: string
  name: string | null
}

const configs = ref<WebhookConfig[]>([])
const warehouses = ref<WarehouseInfo[]>([])
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref<number | null>(null)

const form = reactive({
  warehouse_id: 0,
  webhook_url: '',
  notify_users: '',
  is_active: true,
  message_template: '',
  schedule_enabled: false,
  schedule_day: 0,
  schedule_time: '09:00',
})

async function fetchConfigs() {
  loading.value = true
  try {
    const resp: any = await getWebhooks()
    if (resp?.code === 0) {
      configs.value = resp.data
    }
  } catch (e: any) {
    ElMessage.error(e?.message || '加载配置失败')
  } finally {
    loading.value = false
  }
}

async function fetchWarehouses() {
  try {
    const resp: any = await client.get('/warehouses')
    if (resp?.code === 0) {
      warehouses.value = resp.data
    }
  } catch (e) {
    /* 忽略 */
  }
}

function openCreate() {
  isEdit.value = false
  editId.value = null
  form.warehouse_id = 0
  form.webhook_url = ''
  form.notify_users = ''
  form.is_active = true
  form.message_template = ''
  form.schedule_enabled = false
  form.schedule_day = 0
  form.schedule_time = '09:00'
  dialogVisible.value = true
}

function openEdit(row: WebhookConfig) {
  isEdit.value = true
  editId.value = row.id
  form.warehouse_id = row.warehouse_id
  form.webhook_url = row.webhook_url
  form.notify_users = row.notify_users || ''
  form.is_active = row.is_active
  form.message_template = (row as any).message_template || ''
  form.schedule_enabled = (row as any).schedule_enabled || false
  form.schedule_day = (row as any).schedule_day ?? 0
  form.schedule_time = (row as any).schedule_time || '09:00'
  dialogVisible.value = true
}

async function handleSave() {
  if (!form.warehouse_id) {
    ElMessage.warning('请选择仓库')
    return
  }
  if (!form.webhook_url) {
    ElMessage.warning('请输入 Webhook URL')
    return
  }
  saving.value = true
  try {
    if (isEdit.value && editId.value !== null) {
      await updateWebhook(editId.value, {
        webhook_url: form.webhook_url,
        notify_users: form.notify_users,
        is_active: form.is_active,
        message_template: form.message_template,
        schedule_enabled: form.schedule_enabled,
        schedule_day: form.schedule_day,
        schedule_time: form.schedule_time,
      } as any)
      ElMessage.success('更新成功')
    } else {
      await createWebhook({
        warehouse_id: form.warehouse_id,
        webhook_url: form.webhook_url,
        notify_users: form.notify_users,
        message_template: form.message_template,
        schedule_enabled: form.schedule_enabled,
        schedule_day: form.schedule_day,
        schedule_time: form.schedule_time,
      } as any)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    await fetchConfigs()
  } catch (e: any) {
    ElMessage.error(e?.message || '保存失败')
  } finally {
    saving.value = false
  }
}

async function handleDelete(row: WebhookConfig) {
  try {
    await ElMessageBox.confirm(
      `确认删除仓库 ${row.warehouse_code} 的推送配置？`,
      '删除确认',
      { confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning' }
    )
    await deleteWebhook(row.id)
    ElMessage.success('删除成功')
    await fetchConfigs()
  } catch (e: any) {
    if (e !== 'cancel' && e?.message !== 'cancel') {
      ElMessage.error(e?.message || '删除失败')
    }
  }
}

onMounted(async () => {
  await Promise.all([fetchConfigs(), fetchWarehouses()])
})
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
  padding: 20px 24px;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.title-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #1D1D1F;
  margin: 0;
}

.page-subtitle {
  font-size: 13px;
  color: #6E6E73;
  margin: 0;
}

.content-card {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  min-height: 400px;
}

/* 主色按钮 */
:deep(.primary-btn) {
  background: #2563EB;
  border: 1px solid #2563EB;
  color: #fff;
  font-weight: 500;
  border-radius: 10px;
  transition: all 200ms cubic-bezier(0.34, 1.56, 0.64, 1);
}
:deep(.primary-btn:hover) {
  background: #1D4ED8;
  border-color: #1D4ED8;
  transform: translateY(-1px);
}

/* 表格样式 */
:deep(.webhook-table) {
  border-radius: 12px;
  overflow: hidden;
}
:deep(.webhook-table th.el-table__cell) {
  background: #F5F5F7;
  color: #1D1D1F;
  font-weight: 600;
  font-size: 14px;
}
:deep(.webhook-table .el-table__cell) {
  border-color: #D2D2D7;
  color: #1D1D1F;
}
:deep(.webhook-table tr:hover > td.el-table__cell) {
  background: #F5F5F7 !important;
}

.url-cell {
  display: inline-block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #6E6E73;
  font-size: 13px;
  font-family: 'Cascadia Code', ui-monospace, monospace;
}

.status-tag {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 500;
}
.status-tag.active {
  background: rgba(48, 209, 88, 0.12);
  color: #30D158;
}
.status-tag.inactive {
  background: rgba(110,110,115, 0.12);
  color: #6E6E73;
}

:deep(.edit-link) {
  color: #2563EB;
  font-weight: 500;
}
:deep(.del-link) {
  color: #FF3B30;
  font-weight: 500;
}

/* 对话框内表单 */
:deep(.el-dialog) {
  border-radius: 16px;
}
:deep(.el-input__wrapper),
:deep(.el-select__wrapper) {
  border-radius: 10px;
}
:deep(.el-switch.is-checked .el-switch__core) {
  background-color: #30D158;
  border-color: #30D158;
}
</style>
