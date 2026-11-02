<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { authApi } from '@/api'
import { setAuthData } from '@/utils/auth'

const router = useRouter()
const route = useRoute()

type FormMode = 'login' | 'register'

const mode = ref<FormMode>('login')
const loading = ref(false)
const showPassword = ref(false)
const showRegisterPassword = ref(false)

const loginForm = reactive({
  account: '',
  password: ''
})

const registerForm = reactive({
  student_id: '',
  username: '',
  password: '',
  name: '',
  confirm_password: ''
})

const loginErrors = reactive({
  account: '',
  password: '',
  general: ''
})

const registerErrors = reactive({
  student_id: '',
  username: '',
  password: '',
  name: '',
  confirm_password: '',
  general: ''
})

const studentIdValid = computed(() => {
  if (!registerForm.student_id) return false
  return /^\d{6,20}$/.test(registerForm.student_id)
})

const passwordStrength = computed(() => {
  const pwd = registerForm.password
  if (!pwd) return { level: 0, label: '' }
  let score = 0
  if (pwd.length >= 6) score++
  if (pwd.length >= 10) score++
  if (/[A-Z]/.test(pwd)) score++
  if (/[0-9]/.test(pwd)) score++
  if (/[^A-Za-z0-9]/.test(pwd)) score++
  const levels = [
    { level: 1, label: '弱' },
    { level: 2, label: '一般' },
    { level: 3, label: '较强' },
    { level: 4, label: '强' },
    { level: 5, label: '非常强' }
  ]
  return levels[Math.min(score, 5) - 1] || { level: 0, label: '' }
})

const validateLogin = (): boolean => {
  loginErrors.account = ''
  loginErrors.password = ''
  loginErrors.general = ''
  
  if (!loginForm.account.trim()) {
    loginErrors.account = '请输入学号或用户名'
    return false
  }
  if (!loginForm.password) {
    loginErrors.password = '请输入密码'
    return false
  }
  return true
}

const validateRegister = (): boolean => {
  registerErrors.student_id = ''
  registerErrors.username = ''
  registerErrors.password = ''
  registerErrors.name = ''
  registerErrors.confirm_password = ''
  registerErrors.general = ''
  
  let valid = true
  
  if (!registerForm.student_id.trim()) {
    registerErrors.student_id = '请输入学号'
    valid = false
  } else if (!studentIdValid.value) {
    registerErrors.student_id = '学号应为6-20位数字'
    valid = false
  }
  
  if (!registerForm.username.trim()) {
    registerErrors.username = '请输入用户名'
    valid = false
  } else if (registerForm.username.length < 2) {
    registerErrors.username = '用户名至少2个字符'
    valid = false
  }
  
  if (!registerForm.password) {
    registerErrors.password = '请输入密码'
    valid = false
  } else if (registerForm.password.length < 6) {
    registerErrors.password = '密码至少6位'
    valid = false
  }
  
  if (registerForm.confirm_password !== registerForm.password) {
    registerErrors.confirm_password = '两次密码不一致'
    valid = false
  }
  
  return valid
}

const handleLogin = async () => {
  if (!validateLogin()) return
  
  loading.value = true
  loginErrors.general = ''
  
  try {
    const response = await authApi.login({
      account: loginForm.account.trim(),
      password: loginForm.password
    })
    setAuthData(response)
    const redirect = (route.query.redirect as string) || '/'
    router.push(redirect)
  } catch (error: any) {
    const detail = error?.response?.data?.detail || '登录失败，请检查账号和密码'
    loginErrors.general = detail
  } finally {
    loading.value = false
  }
}

const parseErrorMessage = (error: any): string => {
  const status = error?.response?.status
  const data = error?.response?.data

  if (!error?.response) {
    return '网络连接异常，请检查网络后重试'
  }

  if (status === 422) {
    if (Array.isArray(data?.detail)) {
      const messages: string[] = []
      for (const err of data.detail) {
        if (typeof err === 'object' && err.msg) {
          messages.push(err.msg)
        }
      }
      if (messages.length > 0) {
        return '输入数据有误：' + messages.join('；')
      }
    }
    return '输入数据格式有误，请检查后重试'
  }

  if (status === 400) {
    if (typeof data?.detail === 'string') {
      return data.detail
    }
    return '注册信息有误，请检查后重试'
  }

  if (status === 500) {
    return '服务器内部错误，请稍后重试'
  }

  if (typeof data?.detail === 'string') {
    return data.detail
  }

  return '注册失败，请稍后重试'
}

const handleRegister = async () => {
  if (!validateRegister()) return

  loading.value = true
  registerErrors.general = ''

  try {
    await authApi.register({
      student_id: registerForm.student_id.trim(),
      username: registerForm.username.trim(),
      password: registerForm.password,
      name: registerForm.name.trim()
    })

    ElMessage.success('注册成功，请登录')
    mode.value = 'login'
    loginForm.account = registerForm.student_id
    loginForm.password = ''
    registerForm.student_id = ''
    registerForm.username = ''
    registerForm.password = ''
    registerForm.confirm_password = ''
    registerForm.name = ''
  } catch (error: any) {
    registerErrors.general = parseErrorMessage(error)
  } finally {
    loading.value = false
  }
}

const switchMode = (newMode: FormMode) => {
  mode.value = newMode
  loginErrors.general = ''
  registerErrors.general = ''
}

const fillTestAccount = () => {
  loginForm.account = '2024001'
  loginForm.password = 'admin123'
}

onMounted(() => {
})
</script>

<template>
  <div class="login-page">
    <div class="login-bg-decoration">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
    </div>

    <div class="login-container">
      <div class="login-left">
        <div class="brand-section">
          <div class="logo">📊</div>
          <h1>数据库系统</h1>
          <h2>智能学习平台</h2>
          <div class="features-list">
            <div class="feature-item">
              <span class="feature-icon">🎯</span>
              <span>知识可视化学习</span>
            </div>
            <div class="feature-item">
              <span class="feature-icon">🤖</span>
              <span>AI智能助教</span>
            </div>
            <div class="feature-item">
              <span class="feature-icon">📈</span>
              <span>学习进度追踪</span>
            </div>
            <div class="feature-item">
              <span class="feature-icon">💡</span>
              <span>个性化学习路径</span>
            </div>
          </div>
        </div>
      </div>

      <div class="login-right">
        <div class="login-box">
          <div class="form-tabs">
            <button 
              :class="['tab-btn', { active: mode === 'login' }]"
              @click="switchMode('login')"
            >
              登录
            </button>
            <button 
              :class="['tab-btn', { active: mode === 'register' }]"
              @click="switchMode('register')"
            >
              注册
            </button>
            <div 
              class="tab-indicator"
              :class="{ 'tab-right': mode === 'register' }"
            ></div>
          </div>

          <transition name="fade" mode="out-in">
            <div v-if="mode === 'login'" key="login" class="form-content">
              <div class="form-header">
                <h3>欢迎回来</h3>
                <p>请使用学号或用户名登录系统</p>
              </div>

              <div v-if="loginErrors.general" class="error-banner">
                <span class="error-icon">⚠️</span>
                {{ loginErrors.general }}
              </div>

              <form @submit.prevent="handleLogin" class="login-form">
                <div class="form-group" :class="{ hasError: loginErrors.account }">
                  <label>学号 / 用户名</label>
                  <div class="input-wrapper">
                    <span class="input-icon">👤</span>
                    <input
                      v-model="loginForm.account"
                      type="text"
                      placeholder="请输入学号或用户名"
                      autocomplete="username"
                      @blur="validateLogin"
                    />
                  </div>
                  <span v-if="loginErrors.account" class="error-message">
                    {{ loginErrors.account }}
                  </span>
                </div>

                <div class="form-group" :class="{ hasError: loginErrors.password }">
                  <label>密码</label>
                  <div class="input-wrapper">
                    <span class="input-icon">🔒</span>
                    <input
                      v-model="loginForm.password"
                      :type="showPassword ? 'text' : 'password'"
                      placeholder="请输入密码"
                      autocomplete="current-password"
                    />
                    <button 
                      type="button"
                      class="toggle-password"
                      @click="showPassword = !showPassword"
                    >
                      {{ showPassword ? '🙈' : '👁️' }}
                    </button>
                  </div>
                  <span v-if="loginErrors.password" class="error-message">
                    {{ loginErrors.password }}
                  </span>
                </div>

                <button 
                  type="submit" 
                  class="submit-btn"
                  :class="{ loading: loading }"
                  :disabled="loading"
                >
                  <span v-if="loading" class="spinner"></span>
                  <span class="btn-text">{{ loading ? '登录中...' : '登 录' }}</span>
                </button>
              </form>

              <div class="form-footer">
                <button type="button" class="fill-test-btn" @click="fillTestAccount">
                  💡 使用测试账号
                </button>
                <div class="test-hint">
                  管理员：2024001 / admin123<br/>
                  学生：2024002-2024005 / student123
                </div>
              </div>
            </div>

            <div v-else key="register" class="form-content">
              <div class="form-header">
                <h3>创建账号</h3>
                <p>注册学号后即可开始学习</p>
              </div>

              <div v-if="registerErrors.general" class="error-banner">
                <span class="error-icon">⚠️</span>
                {{ registerErrors.general }}
              </div>

              <form @submit.prevent="handleRegister" class="login-form">
                <div class="form-group" :class="{ hasError: registerErrors.student_id }">
                  <label>学号 <span class="required">*</span></label>
                  <div class="input-wrapper">
                    <span class="input-icon">🆔</span>
                    <input
                      v-model="registerForm.student_id"
                      type="text"
                      placeholder="6-20位数字学号"
                      maxlength="20"
                      @blur="validateRegister"
                    />
                  </div>
                  <div v-if="registerErrors.student_id" class="error-message">
                    {{ registerErrors.student_id }}
                  </div>
                  <div v-else-if="registerForm.student_id && studentIdValid" class="success-message">
                    ✓ 学号格式正确
                  </div>
                </div>

                <div class="form-group" :class="{ hasError: registerErrors.username }">
                  <label>用户名 <span class="required">*</span></label>
                  <div class="input-wrapper">
                    <span class="input-icon">👤</span>
                    <input
                      v-model="registerForm.username"
                      type="text"
                      placeholder="2-50个字符"
                      @blur="validateRegister"
                    />
                  </div>
                  <span v-if="registerErrors.username" class="error-message">
                    {{ registerErrors.username }}
                  </span>
                </div>

                <div class="form-group" :class="{ hasError: registerErrors.name }">
                  <label>姓名（选填）</label>
                  <div class="input-wrapper">
                    <span class="input-icon">📝</span>
                    <input
                      v-model="registerForm.name"
                      type="text"
                      placeholder="真实姓名"
                    />
                  </div>
                </div>

                <div class="form-group" :class="{ hasError: registerErrors.password }">
                  <label>密码 <span class="required">*</span></label>
                  <div class="input-wrapper">
                    <span class="input-icon">🔒</span>
                    <input
                      v-model="registerForm.password"
                      :type="showRegisterPassword ? 'text' : 'password'"
                      placeholder="至少6位"
                      @input="validateRegister"
                    />
                    <button 
                      type="button"
                      class="toggle-password"
                      @click="showRegisterPassword = !showRegisterPassword"
                    >
                      {{ showRegisterPassword ? '🙈' : '👁️' }}
                    </button>
                  </div>
                  <div class="password-strength" v-if="registerForm.password">
                    <span class="strength-label">密码强度：</span>
                    <span 
                      class="strength-badge"
                      :class="['level-' + passwordStrength.level]"
                    >
                      {{ passwordStrength.label }}
                    </span>
                  </div>
                  <span v-if="registerErrors.password" class="error-message">
                    {{ registerErrors.password }}
                  </span>
                </div>

                <div class="form-group" :class="{ hasError: registerErrors.confirm_password }">
                  <label>确认密码 <span class="required">*</span></label>
                  <div class="input-wrapper">
                    <span class="input-icon">✅</span>
                    <input
                      v-model="registerForm.confirm_password"
                      :type="showRegisterPassword ? 'text' : 'password'"
                      placeholder="再次输入密码"
                      @blur="validateRegister"
                    />
                  </div>
                  <span v-if="registerErrors.confirm_password" class="error-message">
                    {{ registerErrors.confirm_password }}
                  </span>
                </div>

                <button 
                  type="submit" 
                  class="submit-btn register"
                  :class="{ loading: loading }"
                  :disabled="loading"
                >
                  <span v-if="loading" class="spinner"></span>
                  <span class="btn-text">{{ loading ? '注册中...' : '注 册 账 号' }}</span>
                </button>
              </form>
            </div>
          </transition>
        </div>
      </div>
    </div>

    
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  position: relative;
  overflow: hidden;
  padding: 20px;
}

.login-bg-decoration {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}

.circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.1;
  background: white;
}

.circle-1 {
  width: 400px;
  height: 400px;
  top: -100px;
  left: -100px;
  animation: float 20s ease-in-out infinite;
}

.circle-2 {
  width: 300px;
  height: 300px;
  bottom: -50px;
  right: -50px;
  animation: float 15s ease-in-out infinite reverse;
}

.circle-3 {
  width: 200px;
  height: 200px;
  top: 50%;
  left: 50%;
  animation: float 25s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(30px, -30px) scale(1.1); }
}

.login-container {
  display: flex;
  width: 100%;
  max-width: 960px;
  min-height: 560px;
  background: white;
  border-radius: 24px;
  box-shadow: 0 30px 80px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  position: relative;
  z-index: 1;
}

.login-left {
  flex: 1;
  background: linear-gradient(135deg, #3b4cca 0%, #667eea 100%);
  padding: 50px 40px;
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.login-left::before {
  content: '';
  position: absolute;
  inset: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.08'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
  opacity: 0.5;
}

.brand-section {
  position: relative;
  z-index: 1;
}

.logo {
  font-size: 3.5rem;
  margin-bottom: 20px;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2));
}

.brand-section h1 {
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 8px 0;
  letter-spacing: 2px;
}

.brand-section h2 {
  font-size: 1.5rem;
  font-weight: 400;
  margin: 0 0 20px 0;
  opacity: 0.9;
}

.brand-desc {
  font-size: 0.95rem;
  line-height: 1.8;
  opacity: 0.85;
  margin-bottom: 30px;
}

.features-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 10px;
  backdrop-filter: blur(10px);
  font-size: 0.95rem;
  transition: all 0.3s ease;
}

.feature-item:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateX(5px);
}

.feature-icon {
  font-size: 1.3rem;
}

.login-right {
  flex: 1.2;
  padding: 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: white;
}

.login-box {
  width: 100%;
  max-width: 380px;
  margin: 0 auto;
}

.form-tabs {
  display: flex;
  position: relative;
  margin-bottom: 30px;
  background: #f5f7fa;
  border-radius: 12px;
  padding: 4px;
}

.tab-btn {
  flex: 1;
  padding: 12px 20px;
  background: none;
  border: none;
  font-size: 0.95rem;
  font-weight: 500;
  color: #666;
  cursor: pointer;
  border-radius: 10px;
  transition: all 0.3s ease;
  position: relative;
  z-index: 1;
}

.tab-btn.active {
  color: #667eea;
  background: white;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
}

.tab-indicator {
  position: absolute;
  top: 4px;
  left: 4px;
  width: calc(50% - 4px);
  height: calc(100% - 8px);
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.15);
  transition: transform 0.3s ease;
  z-index: 0;
}

.tab-indicator.tab-right {
  transform: translateX(100%);
}

.form-content {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.form-header {
  margin-bottom: 25px;
}

.form-header h3 {
  font-size: 1.5rem;
  color: #1a1a2e;
  margin: 0 0 8px 0;
}

.form-header p {
  color: #888;
  font-size: 0.9rem;
  margin: 0;
}

.error-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #fff5f5;
  border: 1px solid #fed7d7;
  border-radius: 10px;
  color: #c53030;
  font-size: 0.9rem;
  margin-bottom: 20px;
}

.error-icon {
  font-size: 1.1rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 0.85rem;
  font-weight: 500;
  color: #555;
}

.required {
  color: #e53e3e;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 14px;
  font-size: 1.1rem;
  pointer-events: none;
}

.input-wrapper input {
  width: 100%;
  padding: 12px 45px 12px 45px;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  background: #f8fafc;
  box-sizing: border-box;
}

.input-wrapper input:focus {
  outline: none;
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.input-wrapper input::placeholder {
  color: #a0aec0;
}

.toggle-password {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.1rem;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s ease;
}

.toggle-password:hover {
  transform: scale(1.2);
}

.hasError .input-wrapper input {
  border-color: #e53e3e;
  background: #fff5f5;
}

.hasError .input-wrapper input:focus {
  box-shadow: 0 0 0 3px rgba(229, 62, 62, 0.1);
}

.error-message {
  font-size: 0.8rem;
  color: #e53e3e;
}

.success-message {
  font-size: 0.8rem;
  color: #38a169;
}

.password-strength {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.8rem;
}

.strength-label {
  color: #888;
}

.strength-badge {
  padding: 2px 10px;
  border-radius: 12px;
  font-weight: 500;
}

.strength-badge.level-1 { background: #fed7d7; color: #c53030; }
.strength-badge.level-2 { background: #feebc8; color: #dd6b20; }
.strength-badge.level-3 { background: #fefcbf; color: #d69e2e; }
.strength-badge.level-4 { background: #c6f6d5; color: #38a169; }
.strength-badge.level-5 { background: #9ae6b4; color: #276749; }

.submit-btn {
  width: 100%;
  padding: 14px 24px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-top: 10px;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.submit-btn:active:not(:disabled) {
  transform: translateY(0);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.submit-btn.loading {
  background: linear-gradient(135deg, #a0aec0 0%, #718096 100%);
}

.submit-btn.register {
  background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
}

.submit-btn.register:hover:not(:disabled) {
  box-shadow: 0 8px 25px rgba(72, 187, 120, 0.4);
}

.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.form-footer {
  margin-top: 20px;
  text-align: center;
}

.fill-test-btn {
  background: none;
  border: 1px dashed #cbd5e0;
  color: #667eea;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 10px;
}

.fill-test-btn:hover {
  background: #f0f4ff;
  border-color: #667eea;
}

.test-hint {
  font-size: 0.75rem;
  color: #a0aec0;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
    max-width: 400px;
    min-height: auto;
  }

  .login-left {
    padding: 30px;
  }

  .brand-section h1 {
    font-size: 1.5rem;
  }

  .brand-section h2 {
    font-size: 1.2rem;
  }

  .features-list {
    display: none;
  }

  .login-right {
    padding: 30px 25px;
  }

  .login-box {
    max-width: 100%;
  }
}

@media (max-width: 480px) {
  .login-page {
    padding: 10px;
  }

  .login-container {
    border-radius: 16px;
  }

  .login-left {
    padding: 25px 20px;
  }

  .login-right {
    padding: 25px 20px;
  }

  .form-tabs {
    margin-bottom: 20px;
  }

  .form-header h3 {
    font-size: 1.25rem;
  }
}
</style>
