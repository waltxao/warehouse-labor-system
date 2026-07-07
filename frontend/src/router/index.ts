import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/LoginView.vue'),
    meta: { public: true },
  },
  {
    path: '/',
    component: () => import('../components/AppLayout.vue'),
    children: [
      { path: '', redirect: '/dashboard' },
      { path: 'dashboard', name: 'dashboard', component: () => import('../views/DashboardView.vue') },
      { path: 'trends/:warehouseCode', name: 'trends', component: () => import('../views/TrendView.vue') },
      {
        path: 'comparison',
        name: 'comparison',
        component: () => import('../views/ComparisonView.vue'),
        meta: { roles: ['global_viewer', 'admin'] },
      },
      {
        path: 'upload',
        name: 'upload',
        component: () => import('../views/UploadView.vue'),
        meta: { roles: ['admin'] },
      },
      { path: 'alerts', name: 'alerts', component: () => import('../views/AlertsView.vue') },
      {
        path: 'notifications',
        name: 'notifications',
        component: () => import('../views/NotificationConfigView.vue'),
        meta: { roles: ['admin'] },
      },
      { path: 'ai-analysis', name: 'ai-analysis', component: () => import('../views/AIAnalysisView.vue') },
      {
        path: 'users',
        name: 'users',
        component: () => import('../views/UsersView.vue'),
        meta: { roles: ['admin'] },
      },
      {
        path: 'settings',
        name: 'settings',
        component: () => import('../views/SettingsView.vue'),
        meta: { roles: ['admin'] },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 登录守卫 + 角色守卫
router.beforeEach(async (to, _from, next) => {
  const token = localStorage.getItem('access_token')
  if (to.meta.public) return next()
  if (!token) return next('/login')

  const roles = to.meta.roles as string[] | undefined
  if (roles) {
    const auth = useAuthStore()
    if (!auth.user) {
      try {
        await auth.fetchUser()
      } catch {
        /* 忽略，后续由 401 拦截处理 */
      }
    }
    if (auth.user && !roles.includes(auth.user.role)) {
      return next('/dashboard')
    }
  }
  next()
})

export default router
