import { createRouter, createWebHistory } from 'vue-router'
import type { Router, RouteRecordRaw } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: MainLayout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '仪表板' },
      },
      {
        path: 'workflows',
        name: 'WorkflowMonitor',
        component: () => import('@/views/WorkflowMonitor/WorkflowMonitor.vue'),
        meta: { title: '工作流监控' },
      },
      {
        path: 'workflow-poc',
        name: 'WorkflowGraphPOC',
        component: () => import('@/views/WorkflowMonitor/WorkflowGraphPOCPage.vue'),
        meta: { title: 'G6 POC测试' },
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/Settings.vue'),
        meta: { title: '设置' },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/404.vue'),
  },
]

const router: Router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// 路由守卫
router.beforeEach((to, _from, next) => {
  // 设置页面标题
  document.title = `${(to.meta.title as string) || '监控平台'} - BMAD`
  next()
})

export default router
