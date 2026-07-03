<template>
  <el-container style="height: 100vh">
    <el-aside width="220px" class="app-aside">
      <div class="app-title">{{ t('systemTitle') }}</div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataBoard /></el-icon>
          <span>{{ t('dashboard') }}</span>
        </el-menu-item>
        <el-menu-item v-if="auth.hasRole('global_viewer', 'admin')" index="/comparison">
          <el-icon><DataAnalysis /></el-icon>
          <span>{{ t('comparison') }}</span>
        </el-menu-item>
        <el-menu-item v-if="auth.hasRole('admin')" index="/upload">
          <el-icon><Upload /></el-icon>
          <span>{{ t('upload') }}</span>
        </el-menu-item>
        <el-menu-item index="/alerts">
          <el-icon><Bell /></el-icon>
          <span>{{ t('alerts') }}</span>
        </el-menu-item>
        <el-menu-item index="/ai-analysis">
          <el-icon><MagicStick /></el-icon>
          <span>{{ t('aiAnalysis') }}</span>
        </el-menu-item>
        <el-menu-item v-if="auth.hasRole('admin')" index="/users">
          <el-icon><User /></el-icon>
          <span>{{ t('users') }}</span>
        </el-menu-item>
        <el-menu-item v-if="auth.hasRole('admin')" index="/settings">
          <el-icon><Setting /></el-icon>
          <span>{{ t('settings') }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="app-header">
        <div class="app-header__spacer" />
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
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const { t } = useI18n()

const activeMenu = computed(() => {
  // 趋势页没有独立菜单项，高亮总览
  if (route.path.startsWith('/trends')) return '/dashboard'
  return route.path
})

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
  background: #304156;
}
.app-title {
  color: #fff;
  padding: 20px;
  font-size: 16px;
  font-weight: bold;
  line-height: 1.4;
}
.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e6e6e6;
}
.app-header__spacer {
  flex: 1;
}
.app-user {
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
</style>
