import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { isAuthenticated, getUser } from '@/utils/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { requiresAuth: false, guestOnly: true }
  },
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomeView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/chapter/:id',
    name: 'chapter',
    component: () => import('@/views/ChapterView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/questions',
    name: 'questions',
    component: () => import('@/views/QuestionsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/practice',
    name: 'practice',
    component: () => import('@/views/PracticeView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/agent',
    name: 'agent',
    component: () => import('@/views/AgentView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/visualize',
    name: 'visualize',
    component: () => import('@/views/KnowledgeVisualizationView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/chapter/:chapterId/knowledge-point/:kpId',
    name: 'knowledge-point',
    component: () => import('@/views/KnowledgePointView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('@/views/ProfileView.vue'),
    meta: { requiresAuth: true }
  },
  // 管理端路由
  {
    path: '/admin',
    name: 'admin',
    component: () => import('@/views/AdminView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authenticated = isAuthenticated()

  if (to.meta.requiresAuth !== false && !authenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else if (to.meta.guestOnly && authenticated) {
    next({ name: 'home' })
  } else if (to.meta.requiresAdmin) {
    const user = getUser()
    if (!user || (user.role !== 'admin' && user.role !== 'teacher')) {
      next({ name: 'home' })
      return
    }
    next()
  } else {
    next()
  }
})

export default router
