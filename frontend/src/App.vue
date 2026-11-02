<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { ElContainer, ElAside, ElMain, ElMenu, ElMenuItem, ElMenuItemGroup, ElDropdown, ElDropdownMenu, ElDropdownItem, ElAvatar, ElBadge } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import { Document, HelpFilled, ChatDotRound, PieChart, UserFilled, SwitchButton, DataLine, Setting, DataAnalysis } from '@element-plus/icons-vue'
import { getUser, logout as authLogout, isAuthenticated, formatDuration } from '@/utils/auth'
import { authApi, learningProgressApi } from '@/api'
import type { AuthUser } from '@/utils/auth'

const route = useRoute()
const router = useRouter()

const currentUser = ref<AuthUser | null>(null)
const studentProgress = ref<{
  total_study_minutes: number
  overall_completion_percentage: number
  total_modules_accessed: number
  last_learning_time?: string
} | null>(null)

const loadUser = () => {
  const user = getUser()
  currentUser.value = user
}

const loadProgress = async () => {
  const user = getUser()
  if (!user) return
  
  try {
    const progress = await authApi.getProgress(user.student_id)
    studentProgress.value = progress
  } catch (e) {
    console.error('加载学习进度失败:', e)
  }
}

// ==================== 全局学习时长统计（跨登录累计 + 实时更新） ====================
const studySeconds = ref(0)
const studySessionId = ref('')
let tickTimer: number | null = null
let syncTimer: number | null = null
let progressTimer: number | null = null

const getStudyStudentId = () => getUser()?.student_id || 'anonymous'

// 将当前累计学习时长写入后端；后端按 (session_id, module_type, module_id) 去重并累加增量
const flushStudyTime = async () => {
  if (!isAuthenticated() || studySeconds.value < 1 || !studySessionId.value) return
  try {
    await learningProgressApi.createRecord({
      session_id: studySessionId.value,
      student_id: getStudyStudentId(),
      module_type: 'study_session',
      module_id: 'global',
      module_name: '学习时长',
      duration_seconds: studySeconds.value,
      study_duration_minutes: Math.floor(studySeconds.value / 60),
      status: 'viewing',
      interaction_count: 0,
      last_study_time: new Date().toISOString()
    })
  } catch (e) {
    console.error('保存学习时长失败:', e)
  }
}

const startStudyTracking = () => {
  if (studySessionId.value) return
  let sid = sessionStorage.getItem('study_session_id') || ''
  if (!sid) {
    sid = `s-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
    sessionStorage.setItem('study_session_id', sid)
    sessionStorage.removeItem('study_session_seconds')
  }
  studySessionId.value = sid
  // 刷新页面时从本会话已累计的秒数继续，避免重新从 0 计时
  studySeconds.value = Number(sessionStorage.getItem('study_session_seconds') || 0)

  // 每秒累计（页面可见时才计时）
  tickTimer = window.setInterval(() => {
    if (document.visibilityState === 'visible' && isAuthenticated()) {
      studySeconds.value++
      sessionStorage.setItem('study_session_seconds', String(studySeconds.value))
    }
  }, 1000)

  // 每 15 秒同步一次，保证时长持久化并跨登录累计
  syncTimer = window.setInterval(() => { flushStudyTime() }, 15000)
}

// 已登录则确保计时与实时刷新均已启动
const ensureTracking = () => {
  if (!isAuthenticated()) return
  startStudyTracking()
  if (!progressTimer) {
    progressTimer = window.setInterval(() => { loadProgress() }, 15000)
  }
}

const handleLogout = async () => {
  // 退出前先落盘当前学习时长，并按账号隔离会话
  await flushStudyTime()
  authLogout()
  sessionStorage.removeItem('study_session_id')
  sessionStorage.removeItem('study_session_seconds')
  studySessionId.value = ''
  studySeconds.value = 0
  currentUser.value = null
  studentProgress.value = null
  router.push('/login')
}

const viewProfile = () => {
  router.push('/profile')
}

const formatMinutes = (minutes: number) => {
  if (minutes < 60) return `${minutes}分钟`
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return `${hours}小时${mins}分`
}

const menuItems = computed(() => {
  const items = [
    { path: '/', name: '课程首页', icon: Document },
    { path: '/questions', name: '题库练习', icon: HelpFilled },
    { path: '/visualize', name: '知识可视化', icon: PieChart },
    { path: '/agent', name: '智能助教', icon: ChatDotRound }
  ]
  if (currentUser.value && (currentUser.value.role === 'admin' || currentUser.value.role === 'teacher')) {
    items.push({ path: '/admin', name: '管理后台', icon: Setting })
  }
  return items
})

const activeMenu = computed(() => route.path)

watch(() => route.path, () => {
  loadUser()
  if (isAuthenticated()) {
    loadProgress()
  }
  ensureTracking()
})

onMounted(() => {
  loadUser()
  if (isAuthenticated()) {
    loadProgress()
  }
  ensureTracking()
  window.addEventListener('pagehide', flushStudyTime)
})

onBeforeUnmount(() => {
  flushStudyTime()
  if (tickTimer) window.clearInterval(tickTimer)
  if (syncTimer) window.clearInterval(syncTimer)
  if (progressTimer) window.clearInterval(progressTimer)
  window.removeEventListener('pagehide', flushStudyTime)
})
</script>

<template>
  <ElContainer style="height: 100%">
    <ElAside width="240px" style="background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);">
      <div class="logo-section">
        <div class="logo-icon">
          <DataAnalysis style="font-size: 1.8rem; color: #667eea;" />
        </div>
        <div class="logo-text">
          <div class="logo-title">DBMS</div>
          <div class="logo-subtitle">Course Hub</div>
        </div>
      </div>

      <div v-if="currentUser" class="user-section">
        <ElDropdown @command="(cmd: string) => { if (cmd === 'logout') handleLogout(); if (cmd === 'profile') viewProfile(); }">
          <div class="user-info" @click.stop>
            <ElAvatar :size="40" :style="{ background: 'linear-gradient(135deg, #667eea, #764ba2)' }">
              {{ currentUser.name?.charAt(0) || currentUser.username?.charAt(0) }}
            </ElAvatar>
            <div class="user-details">
              <div class="user-name">{{ currentUser.name || currentUser.username }}</div>
              <div class="user-id">{{ currentUser.student_id }}</div>
            </div>
          </div>
          <template #dropdown>
            <ElDropdownMenu>
              <ElDropdownItem command="profile">
                <el-icon><UserFilled /></el-icon>
                <span>个人中心</span>
              </ElDropdownItem>
              <ElDropdownItem command="logout" divided>
                <el-icon><SwitchButton /></el-icon>
                <span>退出登录</span>
              </ElDropdownItem>
            </ElDropdownMenu>
          </template>
        </ElDropdown>

        <div v-if="studentProgress" class="progress-card">
          <div class="progress-header">
            <el-icon><DataLine /></el-icon>
            <span>学习概况</span>
          </div>
          <div class="progress-stats">
            <div class="stat-item">
              <div class="stat-value">{{ formatMinutes(studentProgress.total_study_minutes) }}</div>
              <div class="stat-label">总学习时长</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ studentProgress.total_modules_accessed }}</div>
              <div class="stat-label">访问模块</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ studentProgress.overall_completion_percentage.toFixed(1) }}%</div>
              <div class="stat-label">完成进度</div>
            </div>
          </div>
        </div>
      </div>

      <ElMenu
        :default-active="activeMenu"
        mode="vertical"
        background-color="transparent"
        text-color="#bfcbd9"
        active-text-color="#667eea"
        router
        class="sidebar-menu"
      >
        <ElMenuItemGroup>
          <template #title>
            <span class="menu-group-title">学习导航</span>
          </template>
          <ElMenuItem v-for="item in menuItems" :key="item.path" :index="item.path">
            <component :is="item.icon" class="menu-icon" />
            <span>{{ item.name }}</span>
          </ElMenuItem>
        </ElMenuItemGroup>
      </ElMenu>

      <div class="sidebar-footer">
        <div class="footer-text">数据库系统课程</div>
      </div>
    </ElAside>

    <ElMain style="background: #f5f7fa; padding: 0;">
      <div class="main-header" v-if="currentUser">
        <div class="header-left">
          <span class="greeting">👋 欢迎回来，{{ currentUser.name || currentUser.username }}</span>
        </div>
        <div class="header-right">
          <div v-if="studentProgress" class="header-stats">
            <span class="stat-badge">
              ⏱️ 学习 {{ formatMinutes(studentProgress.total_study_minutes) }}
            </span>
            <span class="stat-badge">
              📊 进度 {{ studentProgress.overall_completion_percentage.toFixed(1) }}%
            </span>
          </div>
          <el-button 
            type="danger" 
            size="small" 
            text 
            @click="handleLogout"
            class="logout-btn"
          >
            退出
          </el-button>
        </div>
      </div>
      <div class="main-content">
        <router-view />
      </div>
    </ElMain>
  </ElContainer>
</template>

<style scoped>
.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.logo-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 10px;
  background: rgba(102, 126, 234, 0.15);
}

.logo-title {
  font-size: 1.3rem;
  font-weight: 700;
  color: white;
  letter-spacing: 2px;
}

.logo-subtitle {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.6);
  letter-spacing: 1px;
}

.user-section {
  padding: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.3s;
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.08);
}

.user-details {
  flex: 1;
  min-width: 0;
}

.user-name {
  font-size: 0.95rem;
  font-weight: 600;
  color: white;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-id {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.6);
}

.progress-card {
  margin-top: 16px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 14px;
}

.progress-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 12px;
}

.progress-stats {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 8px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 1.1rem;
  font-weight: 700;
  color: #667eea;
  line-height: 1.2;
}

.stat-label {
  font-size: 0.65rem;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 2px;
}

.sidebar-menu {
  border-right: none;
  flex: 1;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 200px;
}

:deep(.el-menu) {
  border-right: none;
}

:deep(.el-menu-item) {
  height: 48px;
  line-height: 48px;
  border-radius: 8px;
  margin: 4px 8px;
  width: calc(100% - 16px);
  overflow: hidden;
}

:deep(.el-menu-item span) {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

:deep(.el-menu-item:hover) {
  background: rgba(255, 255, 255, 0.08) !important;
}

:deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%) !important;
  color: white !important;
}

.menu-group-title {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.4);
  font-weight: 500;
  letter-spacing: 1px;
}

.sidebar-footer {
  padding: 16px 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  text-align: center;
}

.footer-text {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
}

.footer-subtitle {
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.4);
  margin-top: 4px;
}

.main-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 24px;
  background: white;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.header-left .greeting {
  font-size: 1rem;
  font-weight: 500;
  color: #303133;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-stats {
  display: flex;
  gap: 10px;
}

.stat-badge {
  padding: 6px 14px;
  background: linear-gradient(135deg, #f0f4ff 0%, #e8eeff 100%);
  border-radius: 20px;
  font-size: 0.85rem;
  color: #667eea;
  font-weight: 500;
}

.logout-btn {
  color: #909399;
}

.logout-btn:hover {
  color: #f56c6c !important;
}

.main-content {
  padding: 20px;
  min-height: calc(100vh - 65px);
}

.menu-icon {
  font-size: var(--icon-size-md) !important;
  margin-right: 8px;
}

@media (max-width: 768px) {
  .progress-stats {
    grid-template-columns: 1fr;
  }
  
  .header-stats {
    display: none;
  }
}
</style>
