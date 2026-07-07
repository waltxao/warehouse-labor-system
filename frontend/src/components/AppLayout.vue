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
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../stores/auth'

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
</script>

<style scoped>
.app-aside {
  background: linear-gradient(180deg, #1E3A8A 0%, #1E40AF 100%);
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
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  transition: all 150ms ease;
  border-left: 3px solid transparent;
  user-select: none;
}
.nav-item:hover {
  background: rgba(255, 255, 255, 0.10);
  color: #fff;
}
.nav-item.active {
  background: #DBEAFE;
  color: #1E40AF;
  border-left: 3px solid #D97706;
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
  box-shadow: 0 1px 3px rgba(30, 58, 138, 0.08);
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
  color: #1E3A8A;
  font-weight: 500;
}
</style>
