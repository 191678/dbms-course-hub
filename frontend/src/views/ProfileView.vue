<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElCard, ElAvatar, ElTag, ElButton, ElForm, ElFormItem, ElInput, ElMessage, ElDescriptions, ElDescriptionsItem, ElSkeleton, ElEmpty, ElProgress } from 'element-plus'
import { User, Clock, Reading, Trophy, DataLine, Lock, Key, Check, Loading } from '@element-plus/icons-vue'
import { authApi } from '@/api'
import { getUser } from '@/utils/auth'
import { useRealtime } from '@/utils/useRealtime'
import type { StudentProfile, StudentProgressOverview } from '@/api'

const isLoading = ref(true)
const loadError = ref('')
const profile = ref<StudentProfile | null>(null)
const progress = ref<StudentProgressOverview | null>(null)

const changePwdForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})
const pwdLoading = ref(false)
const pwdError = ref('')
const pwdSuccess = ref(false)

const userInitial = computed(() => {
  return profile.value?.name?.charAt(0) || profile.value?.username?.charAt(0) || 'U'
})

const roleLabel = computed(() => {
  const map: Record<string, string> = {
    admin: '管理员',
    teacher: '教师',
    student: '学生'
  }
  return map[profile.value?.role || ''] || profile.value?.role || '学生'
})

const roleType = computed(() => {
  if (profile.value?.role === 'admin') return 'danger'
  if (profile.value?.role === 'teacher') return 'warning'
  return 'success'
})

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '从未登录'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatMinutes = (minutes: number) => {
  if (minutes < 60) return `${minutes} 分钟`
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return `${hours} 小时 ${mins} 分`
}

const loadProfile = async () => {
  isLoading.value = true
  loadError.value = ''
  try {
    profile.value = await authApi.getProfile()
    const userId = getUser()
    if (userId?.student_id) {
      progress.value = await authApi.getProgress(userId.student_id)
    }
  } catch (e: any) {
    const msg = e?.response?.status === 401
      ? '登录已过期，请重新登录'
      : '加载个人信息失败，请稍后重试'
    loadError.value = msg
    console.error('加载个人中心数据失败:', e)
  } finally {
    isLoading.value = false
  }
}

const validatePassword = () => {
  pwdError.value = ''
  if (!changePwdForm.value.oldPassword) {
    pwdError.value = '请输入原密码'
    return false
  }
  if (!changePwdForm.value.newPassword) {
    pwdError.value = '请输入新密码'
    return false
  }
  if (changePwdForm.value.newPassword.length < 6) {
    pwdError.value = '新密码至少6位'
    return false
  }
  if (changePwdForm.value.newPassword !== changePwdForm.value.confirmPassword) {
    pwdError.value = '两次密码不一致'
    return false
  }
  return true
}

const handleChangePassword = async () => {
  if (!validatePassword()) return

  pwdLoading.value = true
  pwdSuccess.value = false
  pwdError.value = ''

  try {
    await authApi.changePassword(
      changePwdForm.value.oldPassword,
      changePwdForm.value.newPassword
    )
    pwdSuccess.value = true
    ElMessage.success('密码修改成功')
    changePwdForm.value.oldPassword = ''
    changePwdForm.value.newPassword = ''
    changePwdForm.value.confirmPassword = ''
  } catch (e: any) {
    const detail = e?.response?.data?.detail || '密码修改失败，请稍后重试'
    pwdError.value = typeof detail === 'string' ? detail : '密码修改失败，请稍后重试'
  } finally {
    pwdLoading.value = false
  }
}

onMounted(() => {
  loadProfile()
})

// 数据变化后 1 秒内自动同步，无需手动刷新
useRealtime(() => { if (!document.hidden) loadProfile() })
</script>

<template>
  <div class="profile-page">
    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading-container">
      <ElSkeleton :rows="4" animated />
    </div>

    <!-- 错误状态 -->
    <div v-else-if="loadError" class="error-container">
      <ElEmpty :description="loadError">
        <ElButton type="primary" @click="loadProfile">重新加载</ElButton>
      </ElEmpty>
    </div>

    <!-- 主内容 -->
    <template v-else-if="profile">
      <div class="profile-grid">
        <!-- 左侧：用户信息卡片 -->
        <div class="profile-sidebar">
          <ElCard class="profile-card">
            <div class="avatar-section">
              <ElAvatar :size="96" class="profile-avatar">
                <span class="avatar-text">{{ userInitial }}</span>
              </ElAvatar>
              <h2 class="user-name">{{ profile.name || profile.username }}</h2>
              <ElTag :type="roleType" effect="dark" class="role-tag">{{ roleLabel }}</ElTag>
            </div>

            <ElDescriptions :column="1" class="info-list">
              <ElDescriptionsItem label="学号">
                <span class="info-value">{{ profile.student_id }}</span>
              </ElDescriptionsItem>
              <ElDescriptionsItem label="用户名">
                <span class="info-value">{{ profile.username }}</span>
              </ElDescriptionsItem>
              <ElDescriptionsItem label="账号状态">
                <ElTag :type="profile.is_active ? 'success' : 'danger'" size="small">
                  {{ profile.is_active ? '正常' : '已禁用' }}
                </ElTag>
              </ElDescriptionsItem>
              <ElDescriptionsItem label="注册时间">
                <span class="info-value">{{ formatDate(profile.created_at) }}</span>
              </ElDescriptionsItem>
              <ElDescriptionsItem label="最近登录">
                <span class="info-value">{{ formatDate(profile.last_login_at) }}</span>
              </ElDescriptionsItem>
            </ElDescriptions>
          </ElCard>

          <!-- 修改密码卡片 -->
          <ElCard class="password-card">
            <template #header>
              <div class="card-header">
                <el-icon><Lock /></el-icon>
                <span>修改密码</span>
              </div>
            </template>

            <ElForm label-position="top" class="password-form">
              <ElFormItem label="原密码">
                <ElInput
                  v-model="changePwdForm.oldPassword"
                  type="password"
                  placeholder="请输入原密码"
                  show-password
                  :prefix-icon="Key"
                />
              </ElFormItem>

              <ElFormItem label="新密码">
                <ElInput
                  v-model="changePwdForm.newPassword"
                  type="password"
                  placeholder="至少6位字符"
                  show-password
                  :prefix-icon="Lock"
                />
              </ElFormItem>

              <ElFormItem label="确认新密码">
                <ElInput
                  v-model="changePwdForm.confirmPassword"
                  type="password"
                  placeholder="再次输入新密码"
                  show-password
                  :prefix-icon="Check"
                />
              </ElFormItem>

              <div v-if="pwdError" class="form-error">
                <el-icon><Loading /></el-icon>
                {{ pwdError }}
              </div>
              <div v-if="pwdSuccess" class="form-success">
                ✓ 密码修改成功
              </div>

              <ElButton
                type="primary"
                :loading="pwdLoading"
                @click="handleChangePassword"
                class="submit-btn"
              >
                确认修改
              </ElButton>
            </ElForm>
          </ElCard>
        </div>

        <!-- 右侧：学习数据 -->
        <div class="profile-main">
          <!-- 学习统计 -->
          <ElCard class="stats-card">
            <template #header>
              <div class="card-header">
                <el-icon><DataLine /></el-icon>
                <span>学习概况</span>
              </div>
            </template>

            <div v-if="progress" class="stats-grid">
              <div class="stat-block">
                <div class="stat-icon-wrap stat-primary">
                  <el-icon :size="28"><Clock /></el-icon>
                </div>
                <div class="stat-details">
                  <div class="stat-number">{{ formatMinutes(progress.total_study_minutes) }}</div>
                  <div class="stat-label">累计学习时长</div>
                </div>
              </div>

              <div class="stat-block">
                <div class="stat-icon-wrap stat-success">
                  <el-icon :size="28"><Reading /></el-icon>
                </div>
                <div class="stat-details">
                  <div class="stat-number">{{ progress.total_modules_accessed }}</div>
                  <div class="stat-label">访问模块数</div>
                </div>
              </div>

              <div class="stat-block">
                <div class="stat-icon-wrap stat-warning">
                  <el-icon :size="28"><Trophy /></el-icon>
                </div>
                <div class="stat-details">
                  <div class="stat-number">{{ progress.overall_completion_percentage.toFixed(1) }}%</div>
                  <div class="stat-label">总体完成进度</div>
                </div>
              </div>

              <div class="stat-block">
                <div class="stat-icon-wrap stat-info">
                  <el-icon :size="28"><User /></el-icon>
                </div>
                <div class="stat-details">
                  <div class="stat-number">{{ formatDate(progress.last_learning_time) }}</div>
                  <div class="stat-label">最近学习时间</div>
                </div>
              </div>
            </div>

            <ElEmpty v-else description="暂无学习数据" :image-size="100" />
          </ElCard>

          <!-- 模块进度列表 -->
          <ElCard v-if="progress && progress.module_progress_list.length > 0" class="modules-card">
            <template #header>
              <div class="card-header">
                <el-icon><Reading /></el-icon>
                <span>各模块学习进度</span>
              </div>
            </template>

            <div class="modules-list">
              <div
                v-for="mod in progress.module_progress_list"
                :key="mod.module_uuid"
                class="module-item"
              >
                <div class="module-header">
                  <span class="module-name">{{ mod.module_name }}</span>
                  <span class="module-percent">{{ mod.completion_percentage.toFixed(1) }}%</span>
                </div>
                <ElProgress
                  :percentage="Math.round(mod.completion_percentage)"
                  :stroke-width="8"
                  :color="mod.completion_percentage >= 80 ? '#67c23a' : mod.completion_percentage >= 50 ? '#e6a23c' : '#409eff'"
                  class="module-progress"
                />
                <div class="module-meta">
                  <span>📚 学习 {{ formatMinutes(mod.study_duration_minutes) }}</span>
                  <span v-if="mod.mastered_count">✓ 已掌握 {{ mod.mastered_count }}</span>
                  <span v-if="mod.not_mastered_count">✗ 未掌握 {{ mod.not_mastered_count }}</span>
                </div>
              </div>
            </div>
          </ElCard>

          <!-- 功能菜单 -->
          <ElCard class="actions-card">
            <template #header>
              <div class="card-header">
                <el-icon><User /></el-icon>
                <span>快捷操作</span>
              </div>
            </template>

            <div class="actions-grid">
              <div class="action-item" @click="$router.push('/')">
                <div class="action-icon action-blue">📖</div>
                <span>开始学习</span>
              </div>
              <div class="action-item" @click="$router.push('/questions')">
                <div class="action-icon action-green">✏️</div>
                <span>题库练习</span>
              </div>
              <div class="action-item" @click="$router.push('/agent')">
                <div class="action-icon action-purple">🤖</div>
                <span>AI助教</span>
              </div>
              <div class="action-item" @click="$router.push('/visualize')">
                <div class="action-icon action-orange">📊</div>
                <span>知识图谱</span>
              </div>
            </div>
          </ElCard>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.profile-page {
  min-height: 100%;
}

.loading-container,
.error-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.profile-grid {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 20px;
  align-items: start;
}

.profile-sidebar {
  display: flex;
  flex-direction: column;
  gap: 20px;
  position: sticky;
  top: 0;
}

.profile-card,
.password-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.avatar-section {
  text-align: center;
  padding: 20px 0 16px;
  border-bottom: 1px solid #ebeef5;
  margin-bottom: 16px;
}

.profile-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  margin-bottom: 12px;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
}

.avatar-text {
  font-size: 36px;
  font-weight: 600;
  color: white;
}

.user-name {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px;
}

.role-tag {
  font-size: 12px;
}

.info-list :deep(.el-descriptions__label) {
  width: 80px;
  color: #909399;
  font-size: 13px;
}

.info-list :deep(.el-descriptions__content) {
  color: #303133;
  font-size: 14px;
}

.info-list :deep(.el-descriptions__body) {
  background: transparent;
}

.info-value {
  color: #303133;
  font-weight: 500;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.password-form {
  margin-top: 8px;
}

.password-form :deep(.el-form-item__label) {
  font-weight: 500;
}

.form-error {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #f56c6c;
  font-size: 13px;
  margin-bottom: 12px;
}

.form-success {
  color: #67c23a;
  font-size: 13px;
  margin-bottom: 12px;
}

.submit-btn {
  width: 100%;
}

.profile-main {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stats-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.stat-block {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  background: linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%);
  border-radius: 12px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-block:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.stat-icon-wrap {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.stat-primary {
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.stat-success {
  background: linear-gradient(135deg, #11998e, #38ef7d);
}

.stat-warning {
  background: linear-gradient(135deg, #f2994a, #f2c94c);
}

.stat-info {
  background: linear-gradient(135deg, #4facfe, #00f2fe);
}

.stat-details {
  flex: 1;
  min-width: 0;
}

.stat-number {
  font-size: 18px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.modules-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.modules-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.module-item {
  padding: 14px 16px;
  background: #f8f9fb;
  border-radius: 10px;
  transition: background 0.2s;
}

.module-item:hover {
  background: #f0f2f5;
}

.module-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.module-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.module-percent {
  font-size: 14px;
  font-weight: 700;
  color: #667eea;
}

.module-progress {
  margin-bottom: 8px;
}

.module-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #909399;
}

.actions-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px 12px;
  background: #f8f9fb;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 13px;
  color: #606266;
}

.action-item:hover {
  background: #f0f4ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
  color: #667eea;
}

.action-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.action-blue {
  background: linear-gradient(135deg, #e0e7ff, #c7d2fe);
}

.action-green {
  background: linear-gradient(135deg, #d1fae5, #a7f3d0);
}

.action-purple {
  background: linear-gradient(135deg, #ede9fe, #ddd6fe);
}

.action-orange {
  background: linear-gradient(135deg, #fed7aa, #fdba74);
}

/* 响应式 */
@media (max-width: 1024px) {
  .profile-grid {
    grid-template-columns: 280px 1fr;
    gap: 16px;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }

  .profile-sidebar {
    position: static;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .actions-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .stat-block {
    padding: 12px;
  }

  .stat-icon-wrap {
    width: 48px;
    height: 48px;
  }

  .stat-number {
    font-size: 16px;
  }
}

@media (max-width: 480px) {
  .actions-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .module-meta {
    flex-direction: column;
    gap: 4px;
  }
}
</style>
