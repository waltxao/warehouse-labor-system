<template>
  <el-container style="height: 100vh">
    <el-aside width="220px" class="app-aside">
      <div class="app-title">{{ t('systemTitle') }}</div>
      <nav class="nav-list">
        <div
          class="nav-item"
          :class="{ active: activeMenu === '/dashboard' }"
          @click="navigate('/dashboard')"
        >
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect width="7" height="9" x="3" y="3" rx="1" />
            <rect width="7" height="5" x="14" y="3" rx="1" />
            <rect width="7" height="9" x="14" y="12" rx="1" />
            <rect width="7" height="5" x="3" y="16" rx="1" />
          </svg>
          <span>{{ t('dashboard') }}</span>
        </div>

        <div
          v-if="auth.hasRole('global_viewer', 'admin')"
          class="nav-item"
          :class="{ active: activeMenu === '/comparison' }"
          @click="navigate('/comparison')"
        >
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 3v18h18" />
            <path d="M18 17V9" />
            <path d="M13 17V5" />
            <path d="M8 17v-3" />
          </svg>
          <span>{{ t('comparison') }}</span>
        </div>

        <div
          v-if="auth.hasRole('admin')"
          class="nav-item"
          :class="{ active: activeMenu === '/upload' }"
          @click="navigate('/upload')"
        >
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="17 8 12 3 7 8" />
            <line x1="12" x2="12" y1="3" y2="15" />
          </svg>
          <span>{{ t('upload') }}</span>
        </div>

        <div
          class="nav-item"
          :class="{ active: activeMenu === '/alerts' }"
          @click="navigate('/alerts')"
        >
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9" />
            <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0" />
          </svg>
          <span>{{ t('alerts') }}</span>
        </div>

        <div
          v-if="auth.hasRole('admin')"
          class="nav-item"
          :class="{ active: activeMenu === '/notifications' }"
          @click="navigate('/notifications')"
        >
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14.536 21.686a.5.5 0 0 0 .937-.024l6.5-19a.496.496 0 0 0-.635-.635l-19 6.5a.5.5 0 0 0-.024.937l7.93 3.18a2 2 0 0 1 1.112 1.11z"/>
            <path d="m21.854 2.147-10.94 10.939"/>
          </svg>
          <span>{{ t('notifications') || '推送配置' }}</span>
        </div>

        <div
          class="nav-item"
          :class="{ active: activeMenu === '/ai-analysis' }"
          @click="navigate('/ai-analysis')"
        >
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .962 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.962 0z" />
            <path d="M20 3v4" />
            <path d="M22 5h-4" />
            <path d="M4 17v2" />
            <path d="M5 18H3" />
          </svg>
          <span>{{ t('aiAnalysis') }}</span>
        </div>

        <div
          v-if="auth.hasRole('admin')"
          class="nav-item"
          :class="{ active: activeMenu === '/users' }"
          @click="navigate('/users')"
        >
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
            <circle cx="9" cy="7" r="4" />
            <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
            <path d="M16 3.13a4 4 0 0 1 0 7.75" />
          </svg>
          <span>{{ t('users') }}</span>
        </div>

        <div
          v-if="auth.hasRole('admin')"
          class="nav-item"
          :class="{ active: activeMenu === '/settings' }"
          @click="navigate('/settings')"
        >
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z" />
            <circle cx="12" cy="12" r="3" />
          </svg>
          <span>{{ t('settings') }}</span>
        </div>
      </nav>
      <div class="sidebar-footer">
        <span class="version-text">v2.2.0 · Walt</span>
      </div>
    </el-aside>
    <el-container>
      <el-header class="app-header">
        <div class="app-header__spacer" />
        <el-select v-model="currentLang" @change="changeLang" size="small" style="width: 120px; margin-right: 16px;">
          <el-option label="简体中文" value="zh-CN" />
          <el-option label="繁體中文" value="zh-TW" />
        </el-select>
        <el-dropdown>
          <span class="app-user">
            {{ auth.user?.username || '-' }} ({{ auth.user?.role || '-' }})
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="handleLogout">{{ t('logout') }}</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>

  <!-- 浮动推送按钮 -->
  <div class="float-push-btn" @click="openPushDialog">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:24px;height:24px;">
      <path d="M14.536 21.686a.5.5 0 0 0 .937-.024l6.5-19a.496.496 0 0 0-.635-.635l-19 6.5a.5.5 0 0 0-.024.937l7.93 3.18a2 2 0 0 1 1.112 1.11z"/>
      <path d="m21.854 2.147-10.94 10.939"/>
    </svg>
    <span class="float-push-label">推送到企业微信</span>
  </div>

  <!-- 推送对话框 -->
  <el-dialog v-model="pushDialogVisible" title="推送到企业微信" width="520px">
    <el-form label-width="80px">
      <el-form-item label="周次">
        <el-select v-model="pushForm.iso_week" placeholder="选择周次" style="width: 100%">
          <el-option v-for="w in pushWeeks" :key="w.iso_week" :label="w.label" :value="w.iso_week" />
        </el-select>
      </el-form-item>
      <el-form-item label="仓库">
        <el-checkbox-group v-model="pushForm.warehouse_codes">
          <el-checkbox v-for="wh in pushWarehouses" :key="wh.code" :label="wh.code" :value="wh.code" style="display: block; margin-bottom: 8px;">
            {{ wh.code }}{{ wh.name && wh.name !== wh.code ? ' (' + wh.name + ')' : '' }}
          </el-checkbox>
        </el-checkbox-group>
        <p v-if="pushWarehouses.length === 0" style="color: #6E6E73; font-size: 13px;">暂无已配置且启用的推送仓库，请先在推送配置中添加</p>
      </el-form-item>
      <el-form-item label="定时推送">
        <el-switch v-model="pushForm.schedule_enabled" />
      </el-form-item>
      <template v-if="pushForm.schedule_enabled">
        <el-form-item label="推送日期">
          <el-select v-model="pushForm.schedule_day" style="width: 100%">
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
          <el-time-picker v-model="pushForm.schedule_time" format="HH:mm" value-format="HH:mm" placeholder="选择时间" style="width: 100%" />
        </el-form-item>
      </template>
    </el-form>
    <template #footer>
      <el-button @click="pushDialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="pushing" @click="executePush">推送</el-button>
    </template>
  </el-dialog>

  <!-- 推送结果对话框 -->
  <el-dialog v-model="pushResultVisible" title="推送结果" width="500px">
    <div v-if="pushResults">
      <p style="margin-bottom: 12px; font-size: 14px; color: #1D1D1F;">{{ pushResults.message }}</p>
      <div v-for="r in pushResults.results" :key="r.code" style="margin-bottom: 6px; font-size: 13px;">
        <span :style="{ color: r.success ? '#059669' : '#DC2626' }">{{ r.success ? '✓' : '✗' }}</span>
        <span style="margin-left: 8px; font-weight: 500;">{{ r.code }}</span>
        <span style="margin-left: 8px; color: #6E6E73;">{{ r.success ? '成功' : r.message }}</span>
      </div>
    </div>
    <template #footer>
      <el-button type="primary" @click="pushResultVisible = false">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'
import client from '../api/client'
import { getWebhooks, pushAll } from '../api/webhook'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const { t, locale } = useI18n()
const currentLang = ref(locale.value)
function changeLang(lang: string) {
  locale.value = lang
  localStorage.setItem('app-lang', lang)
}

const activeMenu = computed(() => {
  // 趋势页没有独立菜单项，高亮总览
  if (route.path.startsWith('/trends')) return '/dashboard'
  return route.path
})

function navigate(path: string) {
  router.push(path)
}

onMounted(() => {
  if (auth.isAuthenticated && !auth.user) {
    auth.fetchUser().catch(() => {
      /* 忽略，401 拦截器会处理 */
    })
  }
})

function handleLogout() {
  auth.logout()
  router.push('/login')
}

const pushDialogVisible = ref(false)
const pushResultVisible = ref(false)
const pushing = ref(false)
const pushResults = ref<any>(null)
const pushWeeks = ref<any[]>([])
const pushWarehouses = ref<{code: string, name: string}[]>([])
const pushForm = reactive({
  iso_week: '',
  warehouse_codes: [] as string[],
  schedule_enabled: false,
  schedule_day: 0,
  schedule_time: '09:00',
})

async function openPushDialog() {
  // 获取周次列表
  try {
    const resp: any = await client.get('/trends/weeks/list')
    if (resp?.code === 0 && resp.data) {
      pushWeeks.value = resp.data
      if (pushWeeks.value.length > 0) {
        pushForm.iso_week = pushWeeks.value[0].iso_week
      }
    }
  } catch {}

  // 获取已配置且启用的仓库
  try {
    const resp: any = await getWebhooks()
    if (resp?.code === 0 && resp.data) {
      pushWarehouses.value = resp.data
        .filter((w: any) => w.is_active)
        .map((w: any) => ({ code: w.warehouse_code, name: w.warehouse_name || w.warehouse_code }))
    } else {
      pushWarehouses.value = []
    }
  } catch {
    pushWarehouses.value = []
  }

  pushForm.warehouse_codes = []
  pushForm.schedule_enabled = false
  pushDialogVisible.value = true
}

async function executePush() {
  if (!pushForm.iso_week) { ElMessage.warning('请选择周次'); return }
  if (pushForm.warehouse_codes.length === 0) { ElMessage.warning('请选择至少一个仓库'); return }
  
  pushing.value = true
  pushResults.value = null
  try {
    const resp: any = await pushAll({ 
      iso_week: pushForm.iso_week, 
      warehouse_codes: pushForm.warehouse_codes 
    })
    if (resp?.code === 0 && resp.data) {
      pushResults.value = resp.data
      pushResultVisible.value = true
      pushDialogVisible.value = false
      ElMessage.success(resp.data.message || '推送完成')
    } else {
      ElMessage.error(resp?.message || '推送失败')
    }
  } catch (e: any) {
    ElMessage.error(e?.message || '推送失败')
  } finally {
    pushing.value = false
  }
}
</script>

<style scoped>
.app-aside {
  background: #1D1D1F;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}
.app-title {
  color: #fff;
  padding: 22px 20px 18px;
  font-size: 16px;
  font-weight: 600;
  line-height: 1.4;
  letter-spacing: 0.02em;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
.nav-list {
  display: flex;
  flex-direction: column;
  padding: 10px 8px;
  gap: 2px;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  color: rgba(255, 255, 255, 0.75);
  cursor: pointer;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  transition: all 200ms cubic-bezier(0.34, 1.56, 0.64, 1);
  border-left: 3px solid transparent;
  user-select: none;
}
.nav-item:hover {
  background: rgba(255, 255, 255, 0.10);
  color: #fff;
}
.nav-item.active {
  background: rgba(255,255,255,0.12);
  color: #FFFFFF;
  border-left: 3px solid #2563EB;
  font-weight: 600;
}
.nav-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}
.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  border-bottom: none;
  z-index: 10;
}
.app-header__spacer {
  flex: 1;
}
.app-user {
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: #1D1D1F;
  font-weight: 500;
}
.sidebar-footer {
  padding: 16px 20px;
  border-top: 1px solid rgba(255,255,255,0.08);
}
.version-text {
  font-size: 11px;
  color: rgba(255,255,255,0.4);
  font-family: 'Segoe UI', sans-serif;
}
.float-push-btn {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9999;
  display: flex;
  align-items: center;
  gap: 8px;
  background: #2563EB;
  color: #fff;
  padding: 12px 20px;
  border-radius: 28px;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(37, 99, 235, 0.3);
  transition: all 200ms cubic-bezier(0.34, 1.56, 0.64, 1);
  font-size: 14px;
  font-weight: 500;
}
.float-push-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 24px rgba(37, 99, 235, 0.4);
  background: #1D4ED8;
}
.float-push-label {
  white-space: nowrap;
}
</style>
