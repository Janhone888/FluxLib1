<template>
  <div class="forgot-password-container">
    <!-- 保持原有视频背景 -->
    <video ref="bgVideo" class="bg-video" autoplay muted loop>
      <source :src="currentVideo" type="video/mp4">
    </video>

    <div class="video-overlay"></div>

    <!-- 左侧信息区域 -->
    <div class="system-info">
      <div class="logo">
        <i class="el-icon-notebook-2"></i>
        <h1>找回密码</h1>
        <p class="slogan">重置密码，重新获得账户访问权限</p>
      </div>

      <div class="feature-cards">
        <div class="feature-card">
          <div class="feature-icon">
            <i class="el-icon-message"></i>
          </div>
          <div class="feature-content">
            <h3>邮箱验证</h3>
            <p>通过注册邮箱接收验证码</p>
          </div>
        </div>

        <div class="feature-card">
          <div class="feature-icon">
            <i class="el-icon-lock"></i>
          </div>
          <div class="feature-content">
            <h3>安全重置</h3>
            <p>保障账户安全，防止未授权访问</p>
          </div>
        </div>

        <div class="feature-card">
          <div class="feature-icon">
            <i class="el-icon-time"></i>
          </div>
          <div class="feature-content">
            <h3>快速完成</h3>
            <p>简单几步，快速重置密码</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧表单区域 -->
    <div class="forgot-password-form-container">
      <div class="form-wrapper">
        <div class="forgot-password-card">
          <div class="card-header">
            <h2>重置密码</h2>
            <p>按照步骤重置您的账户密码</p>
          </div>

          <el-steps :active="activeStep" align-center class="steps" simple>
            <el-step title="验证邮箱" />
            <el-step title="验证身份" />
            <el-step title="重置密码" />
            <el-step title="完成" />
          </el-steps>

          <!-- 步骤1: 验证邮箱 -->
          <div v-if="activeStep === 1" class="step-content">
            <el-form ref="emailForm" :model="form" :rules="rules" class="step-form">
              <el-form-item prop="email">
                <div class="input-with-icon">
                  <i class="el-icon-message"></i>
                  <el-input
                    v-model="form.email"
                    placeholder="请输入注册邮箱"
                    size="large"
                  />
                </div>
              </el-form-item>

              <el-form-item>
                <el-button
                  type="primary"
                  @click="sendVerificationCode"
                  :loading="sendingCode"
                  class="action-btn"
                  size="large"
                >
                  <span v-if="!sendingCode">发送验证码</span>
                  <span v-else>发送中...</span>
                </el-button>
              </el-form-item>
            </el-form>

            <div class="form-footer">
              <el-button link @click="$router.push('/login')" class="back-link">
                <i class="el-icon-arrow-left"></i>
                返回登录
              </el-button>
            </div>
          </div>

          <!-- 步骤2: 验证身份 -->
          <div v-if="activeStep === 2" class="step-content">
            <div class="step-alert">
              <i class="el-icon-success"></i>
              <div class="alert-content">
                <h4>验证码已发送</h4>
                <p>已发送至 <strong>{{ form.email }}</strong>，请查收邮件</p>
              </div>
            </div>

            <el-form ref="verifyForm" :model="form" :rules="rules" class="step-form">
              <el-form-item prop="code" class="code-item">
                <div class="input-with-icon">
                  <i class="el-icon-key"></i>
                  <el-input
                    v-model="form.code"
                    placeholder="请输入6位验证码"
                    size="large"
                    maxlength="6"
                  />
                </div>
                <el-button :disabled="countdown > 0" @click="resendCode" class="resend-btn">
                  {{ countdown > 0 ? `${countdown}秒后重发` : '重新发送' }}
                </el-button>
              </el-form-item>

              <el-form-item class="btn-group">
                <el-button
                  type="primary"
                  @click="verifyCode"
                  :loading="verifying"
                  class="action-btn"
                  size="large"
                >
                  <span v-if="!verifying">验证验证码</span>
                  <span v-else>验证中...</span>
                </el-button>
                <el-button @click="activeStep = 1" size="large" class="secondary-btn">上一步</el-button>
              </el-form-item>
            </el-form>
          </div>

          <!-- 步骤3: 重置密码 -->
          <div v-if="activeStep === 3" class="step-content">
            <div class="step-alert">
              <i class="el-icon-success"></i>
              <div class="alert-content">
                <h4>身份验证成功</h4>
                <p>请设置您的新密码</p>
              </div>
            </div>

            <el-form ref="passwordForm" :model="form" :rules="passwordRules" class="step-form">
              <el-form-item prop="newPassword">
                <div class="input-with-icon">
                  <i class="el-icon-lock"></i>
                  <el-input
                    v-model="form.newPassword"
                    type="password"
                    placeholder="请输入新密码"
                    size="large"
                    show-password
                  />
                </div>
              </el-form-item>

              <el-form-item prop="confirmPassword">
                <div class="input-with-icon">
                  <i class="el-icon-lock"></i>
                  <el-input
                    v-model="form.confirmPassword"
                    type="password"
                    placeholder="请确认新密码"
                    size="large"
                    show-password
                  />
                </div>
              </el-form-item>

              <el-form-item class="btn-group">
                <el-button
                  type="primary"
                  @click="resetPassword"
                  :loading="resetting"
                  class="action-btn"
                  size="large"
                >
                  <span v-if="!resetting">重置密码</span>
                  <span v-else>重置中...</span>
                </el-button>
                <el-button @click="activeStep = 2" size="large" class="secondary-btn">上一步</el-button>
              </el-form-item>
            </el-form>
          </div>

          <!-- 步骤4: 完成 -->
          <div v-if="activeStep === 4" class="step-complete">
            <div class="success-icon">
              <i class="el-icon-success"></i>
            </div>
            <h3>密码重置成功</h3>
            <p>您的密码已成功重置，请使用新密码登录</p>
            <div class="complete-actions">
              <el-button type="primary" @click="$router.push('/login')" class="action-btn">
                立即登录
              </el-button>
              <el-button @click="$router.push('/')" class="secondary-btn">返回首页</el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'

const router = useRouter()
const bgVideo = ref(null)

// 城市背景视频列表 - 完全保留原逻辑
const cityVideos = [
  '/videos/city1.mp4',
  '/videos/city2.mp4',
  '/videos/city3.mp4',
  '/videos/city4.mp4',
  '/videos/city5.mp4'
]

// 随机选择视频逻辑 - 完全保留原逻辑
const currentVideo = ref('')
const getRandomVideo = () => {
  const randomIndex = Math.floor(Math.random() * cityVideos.length)
  return cityVideos[randomIndex]
}

onMounted(() => {
  currentVideo.value = getRandomVideo()

  // 视频播放处理 - 完全保留原逻辑
  if (bgVideo.value) {
    bgVideo.value.play().catch(e => {
      console.log('视频自动播放被阻止:', e)
    })
  }
})

// 密码重置核心状态 - 新增verifying状态，调整activeStep最终值为4
const activeStep = ref(1)
const sendingCode = ref(false)
const verifying = ref(false) // 新增：验证码验证加载状态
const resetting = ref(false)
const countdown = ref(0)
let countdownTimer = null

// 表单数据 - 保留原结构
const form = reactive({
  email: '',
  code: '',
  newPassword: '',
  confirmPassword: ''
})

// 表单验证规则 - 分步骤拆分（email/code用于步骤1-2，passwordRules用于步骤3）
const rules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: ['blur', 'change'] }
  ],
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 6, message: '验证码长度为6位', trigger: 'blur' }
  ]
}

// 新增：密码专属验证规则（仅步骤3使用）
const passwordRules = {
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== form.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 发送验证码 - 保留原逻辑（发送后跳转至步骤2）
const sendVerificationCode = async () => {
  try {
    sendingCode.value = true
    await api.sendResetCode(form.email)
    ElMessage.success('验证码已发送，请查收邮箱')
    activeStep.value = 2
    startCountdown()
  } catch (error) {
    ElMessage.error(`发送失败: ${error.response?.data?.error || error.message}`)
  } finally {
    sendingCode.value = false
  }
}

// 新增：验证码验证逻辑（调用verifyResetCode接口，验证成功跳转至步骤3）
const verifyCode = async () => {
  try {
    verifying.value = true
    await api.verifyResetCode({
      email: form.email,
      code: form.code
    })
    ElMessage.success('验证码验证成功')
    activeStep.value = 3 // 验证通过进入密码设置步骤
  } catch (error) {
    ElMessage.error(`验证失败: ${error.response?.data?.error || error.message}`)
  } finally {
    verifying.value = false
  }
}

// 重新发送验证码 - 保留原逻辑
const resendCode = async () => {
  try {
    await api.sendResetCode(form.email)
    ElMessage.success('验证码已重新发送')
    startCountdown()
  } catch (error) {
    ElMessage.error(`发送失败: ${error.response?.data?.error || error.message}`)
  }
}

// 重置密码 - 保留原逻辑（成功后跳转至步骤4）
const resetPassword = async () => {
  try {
    resetting.value = true
    await api.resetPassword({
      email: form.email,
      code: form.code,
      new_password: form.newPassword
    })
    ElMessage.success('密码重置成功')
    activeStep.value = 4 // 调整为步骤4
  } catch (error) {
    ElMessage.error(`重置失败: ${error.response?.data?.error || error.message}`)
  } finally {
    resetting.value = false
  }
}

// 倒计时逻辑 - 完全保留原逻辑
const startCountdown = () => {
  countdown.value = 60
  clearInterval(countdownTimer)
  countdownTimer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(countdownTimer)
    }
  }, 1000)
}

// 组件卸载清除定时器 - 保留原逻辑
onUnmounted(() => {
  clearInterval(countdownTimer)
})
</script>

<style scoped>
/* 容器基础样式 - 同步美化风格 */
.forgot-password-container {
  display: flex;
  height: 100vh;
  position: relative;
  overflow: hidden;
}

/* 全屏背景视频 - 保持原有逻辑 */
.bg-video {
  position: absolute;
  top: 50%;
  left: 50%;
  min-width: 100%;
  min-height: 100%;
  width: auto;
  height: auto;
  transform: translateX(-50%) translateY(-50%);
  object-fit: cover;
  z-index: 0;
}

/* 视频遮罩层 - 调整透明度匹配美化风格 */
.video-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  z-index: 1;
}

/* 左侧系统信息 - 同步美化样式 */
.system-info {
  flex: 1;
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 0 8%;
  color: white;
}

.logo {
  margin-bottom: 60px;
}

.logo i {
  font-size: 64px;
  color: #1890ff;
  margin-bottom: 20px;
  display: block;
}

.logo h1 {
  font-size: 42px;
  font-weight: 700;
  margin-bottom: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.slogan {
  font-size: 18px;
  opacity: 0.8;
  font-weight: 300;
}

/* 功能卡片 - 同步登录页美化风格 */
.feature-cards {
  display: flex;
  flex-direction: column;
  gap: 25px;
  max-width: 500px;
}

.feature-card {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 20px;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.feature-card:hover {
  transform: translateY(-5px);
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.2);
}

.feature-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  flex-shrink: 0;
}

.feature-icon i {
  font-size: 24px;
  color: white;
}

.feature-content h3 {
  margin: 0 0 5px 0;
  font-size: 16px;
  font-weight: 600;
}

.feature-content p {
  margin: 0;
  font-size: 14px;
  opacity: 0.8;
}

/* 右侧表单容器 - 同步美化风格 */
.forgot-password-form-container {
  position: relative;
  z-index: 2;
  width: 480px;
  background: rgba(15, 23, 42, 0.9);
  backdrop-filter: blur(20px);
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 0 40px;
  border-left: 1px solid rgba(255, 255, 255, 0.1);
}

.form-wrapper {
  max-width: 400px;
  width: 100%;
}

/* 密码重置卡片 - 入场动画 */
.forgot-password-card {
  color: white;
  animation: fadeInUp 0.6s ease;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 卡片头部 - 同步美化标题样式 */
.card-header {
  text-align: center;
  margin-bottom: 30px;
}

.card-header h2 {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.card-header p {
  color: #94a3b8;
  font-size: 16px;
}

/* 步骤条 - 调整间距 */
.steps {
  margin-bottom: 30px;
}

/* 步骤条样式 - 黑紫主题（新增） */
:deep(.el-steps) {
  --el-color-primary: #667eea;
}

:deep(.el-step__head) {
  color: #94a3b8;
}

:deep(.el-step__head.is-process) {
  color: #667eea;
  border-color: #667eea;
}

:deep(.el-step__head.is-finish) {
  color: #667eea;
  border-color: #667eea;
}

:deep(.el-step__title) {
  color: #94a3b8;
  font-size: 14px;
}

:deep(.el-step__title.is-process) {
  color: #667eea;
  font-weight: 600;
}

:deep(.el-step__title.is-finish) {
  color: #667eea;
}

:deep(.el-step__line) {
  background-color: rgba(255, 255, 255, 0.1);
}

:deep(.el-step__icon) {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #94a3b8;
  font-size: 16px;
  font-weight: 600;
}

:deep(.el-step__icon.is-text) {
  border: 1px solid rgba(255, 255, 255, 0.1);
}

:deep(.el-step__icon.is-process) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: transparent;
  color: white;
}

:deep(.el-step__icon.is-finish) {
  background: rgba(102, 126, 234, 0.1);
  border-color: #667eea;
  color: #667eea;
}

/* 简单风格步骤条的特殊样式（新增） */
:deep(.el-steps--simple) {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
}

:deep(.el-steps--simple .el-step__title) {
  font-size: 14px;
  color: #94a3b8;
}

:deep(.el-steps--simple .el-step__head.is-process .el-step__title) {
  color: #667eea;
}

:deep(.el-steps--simple .el-step__head.is-finish .el-step__title) {
  color: #667eea;
}

/* 步骤内容容器 - 统一内边距 */
.step-content {
  padding: 0 0 15px;
}

/* 步骤提示框 - 自定义美化样式 */
.step-alert {
  display: flex;
  align-items: flex-start;
  background: rgba(102, 126, 234, 0.1);
  border-left: 4px solid #667eea;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 20px;
}

.step-alert i {
  color: #667eea;
  font-size: 20px;
  margin-right: 12px;
  margin-top: 2px;
}

.alert-content h4 {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 4px 0;
  color: white;
}

.alert-content p {
  font-size: 14px;
  margin: 0;
  color: #94a3b8;
}

.alert-content strong {
  color: #667eea;
  font-weight: 600;
}

/* 步骤表单 - 统一间距 */
.step-form {
  margin-bottom: 20px;
}

/* 带图标的输入框 - 同步登录页样式 */
.input-with-icon {
  position: relative;
}

.input-with-icon i {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: #64748b;
  z-index: 1;
  font-size: 18px;
}

/* 自定义Element Plus输入框样式 */
:deep(.el-input) {
  width: 100%;
}

:deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  box-shadow: none;
  padding-left: 50px;
  transition: all 0.3s ease;
}

:deep(.el-input__wrapper:hover) {
  border-color: rgba(255, 255, 255, 0.2);
}

:deep(.el-input__wrapper.is-focus) {
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
}

:deep(.el-input__inner) {
  color: white;
  background: transparent;
  font-size: 16px;
}

:deep(.el-input__inner::placeholder) {
  color: #64748b;
}

/* 验证码输入项 - 调整按钮位置 */
.code-item {
  position: relative;
}

.resend-btn {
  position: absolute;
  right: 4px;
  top: 50%;
  transform: translateY(-50%);
  background: transparent;
  border: none;
  color: #667eea;
  font-size: 14px;
  padding: 4px 12px;
  cursor: pointer;
  transition: color 0.3s ease;
}

.resend-btn:disabled {
  color: #64748b;
  cursor: not-allowed;
}

/* 按钮组 - 横向排列 */
.btn-group {
  display: flex;
  gap: 10px;
}

/* 主按钮样式 - 同步登录页渐变风格 */
.action-btn {
  flex: 1;
  height: 50px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 12px;
  transition: all 0.3s ease;
}

/* 次要按钮样式 - 浅色背景 */
.secondary-btn {
  flex: 1;
  height: 50px;
  font-size: 16px;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: white;
  transition: all 0.3s ease;
}

/* 按钮 hover 效果 */
.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
  background: linear-gradient(135deg, #768fea 0%, #865bc2 100%);
}

.secondary-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

/* 表单底部链接 - 调整样式 */
.form-footer {
  margin-top: 20px;
  text-align: center;
}

.back-link {
  color: #94a3b8;
  transition: color 0.3s ease;
  font-size: 14px;
}

.back-link:hover {
  color: #667eea;
}

.back-link i {
  margin-right: 5px;
}

/* 完成步骤样式 - 居中布局 */
.step-complete {
  padding: 30px 0;
  text-align: center;
}

.success-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
}

.success-icon i {
  font-size: 48px;
  color: white;
}

.step-complete h3 {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 10px 0;
  color: white;
}

.step-complete p {
  font-size: 16px;
  color: #94a3b8;
  margin: 0 0 30px 0;
}

/* 完成步骤按钮组 - 横向排列 */
.complete-actions {
  display: flex;
  gap: 10px;
}

/* 响应式调整 - 同步登录页适配逻辑 */
@media (max-width: 1200px) {
  .system-info {
    padding: 0 5%;
  }

  .feature-cards {
    max-width: 400px;
  }
}

@media (max-width: 992px) {
  .forgot-password-container {
    flex-direction: column;
  }

  .system-info {
    padding: 40px 20px;
    text-align: center;
  }

  .logo {
    margin-bottom: 40px;
  }

  .feature-cards {
    max-width: 100%;
    margin: 0 auto;
  }

  .forgot-password-form-container {
    width: 100%;
    padding: 40px 20px;
    border-left: none;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }

  .form-wrapper {
    max-width: 500px;
    margin: 0 auto;
  }
}

@media (max-width: 768px) {
  .card-header h2 {
    font-size: 24px;
  }

  .btn-group, .complete-actions {
    flex-direction: column;
    gap: 8px;
  }

  .step-alert {
    padding: 10px 14px;
  }

  .alert-content h4 {
    font-size: 14px;
  }

  .alert-content p {
    font-size: 13px;
  }
}
</style>