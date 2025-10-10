<template>
  <div class="login-container">
    <!-- 全屏背景视频 -->
    <video ref="bgVideo" class="bg-video" autoplay muted loop>
      <source :src="currentVideo" type="video/mp4">
    </video>

    <!-- 视频遮罩层 -->
    <div class="video-overlay"></div>

    <!-- 左侧系统信息 -->
    <div class="system-info">
      <div class="logo">
        <i class="el-icon-notebook-2"></i>
        <h1>FluxLib 泛集库</h1>
        <p class="slogan">智慧图书管理，让阅读更简单</p>
      </div>

      <div class="feature-cards">
        <div class="feature-card">
          <div class="feature-icon">
            <i class="el-icon-collection"></i>
          </div>
          <div class="feature-content">
            <h3>海量图书资源</h3>
            <p>涵盖计算机、文学、经济等多个领域</p>
          </div>
        </div>

        <div class="feature-card">
          <div class="feature-icon">
            <i class="el-icon-timer"></i>
          </div>
          <div class="feature-content">
            <h3>智能借阅管理</h3>
            <p>一键借阅归还，到期提醒</p>
          </div>
        </div>

        <div class="feature-card">
          <div class="feature-icon">
            <i class="el-icon-chat-dot-round"></i>
          </div>
          <div class="feature-content">
            <h3>AI智能助手</h3>
            <p>智能推荐，解答疑问</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧登录表单 -->
    <div class="login-form-container">
      <div class="form-wrapper">
        <!-- 登录卡片 -->
        <div class="login-card" v-if="activeTab === 'login'">
          <div class="card-header">
            <h2>欢迎回来</h2>
            <p>请登录您的账户</p>
          </div>

          <div class="login-type-tabs">
            <div
              class="type-tab"
              :class="{ active: loginType === 'user' }"
              @click="loginType = 'user'"
            >
              <i class="el-icon-user"></i>
              <span>用户登录</span>
            </div>
            <div
              class="type-tab"
              :class="{ active: loginType === 'admin' }"
              @click="loginType = 'admin'"
            >
              <i class="el-icon-s-custom"></i>
              <span>管理员登录</span>
            </div>
          </div>

          <el-form ref="loginForm" :model="loginForm" :rules="loginRules" class="login-form">
            <el-form-item prop="email">
              <div class="input-with-icon">
                <i class="el-icon-message"></i>
                <el-input
                  v-model="loginForm.email"
                  placeholder="请输入邮箱"
                  size="large"
                />
              </div>
            </el-form-item>

            <el-form-item prop="password">
              <div class="input-with-icon">
                <i class="el-icon-lock"></i>
                <el-input
                  v-model="loginForm.password"
                  type="password"
                  placeholder="请输入密码"
                  size="large"
                  show-password
                />
              </div>
            </el-form-item>

            <el-form-item v-if="loginType === 'admin'" prop="adminCode">
              <div class="input-with-icon">
                <i class="el-icon-key"></i>
                <el-input
                  v-model="loginForm.adminCode"
                  placeholder="请输入管理员码"
                  size="large"
                />
              </div>
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                @click="handleLogin"
                :loading="loading"
                class="login-btn"
                size="large"
              >
                <span v-if="!loading">立即登录</span>
                <span v-else>登录中...</span>
              </el-button>
            </el-form-item>
          </el-form>

          <div class="form-footer">
            <div class="quick-actions">
              <el-button link @click="useDemoAccount" class="demo-btn">
                <i class="el-icon-magic-stick"></i>
                使用演示账号
              </el-button>
            </div>
            <div class="auth-links">
              <el-button link @click="$router.push('/forgot-password')" class="forgot-link">
                忘记密码？
              </el-button>
              <span class="divider">|</span>
              <el-button link @click="activeTab = 'register'" class="register-link">
                注册新账号
              </el-button>
            </div>
          </div>
        </div>

        <!-- 注册卡片 -->
        <div class="register-card" v-if="activeTab === 'register'">
          <div class="card-header">
            <h2>创建账户</h2>
            <p>注册新的用户账户</p>
          </div>

          <el-form ref="registerForm" :model="registerForm" :rules="registerRules" class="register-form">
            <el-form-item prop="email">
              <div class="input-with-icon">
                <i class="el-icon-message"></i>
                <el-input
                  v-model="registerForm.email"
                  placeholder="请输入邮箱"
                  size="large"
                />
              </div>
            </el-form-item>

            <el-form-item prop="code" class="code-item">
              <div class="input-with-icon">
                <i class="el-icon-key"></i>
                <el-input
                  v-model="registerForm.code"
                  placeholder="请输入验证码"
                  size="large"
                />
              </div>
              <el-button
                :disabled="countdown > 0"
                @click="sendVerificationCode"
                class="code-btn"
                size="large"
              >
                {{ countdown > 0 ? `${countdown}秒后重试` : '获取验证码' }}
              </el-button>
            </el-form-item>

            <el-form-item prop="password">
              <div class="input-with-icon">
                <i class="el-icon-lock"></i>
                <el-input
                  v-model="registerForm.password"
                  type="password"
                  placeholder="请输入密码"
                  size="large"
                  show-password
                />
              </div>
            </el-form-item>

            <el-form-item prop="confirmPassword">
              <div class="input-with-icon">
                <i class="el-icon-lock"></i>
                <el-input
                  v-model="registerForm.confirmPassword"
                  type="password"
                  placeholder="请确认密码"
                  size="large"
                  show-password
                />
              </div>
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                @click="handleRegister"
                :loading="loading"
                class="register-btn"
                size="large"
              >
                <span v-if="!loading">立即注册</span>
                <span v-else>注册中...</span>
              </el-button>
            </el-form-item>
          </el-form>

          <div class="form-footer">
            <div class="back-link">
              <el-button link @click="activeTab = 'login'" class="back-btn">
                <i class="el-icon-arrow-left"></i>
                返回登录
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import api from '@/utils/api'

const router = useRouter()
const userStore = useUserStore()
const bgVideo = ref(null)

// 城市背景视频列表
const cityVideos = [
  '/videos/city1.mp4',
  '/videos/city2.mp4',
  '/videos/city3.mp4',
  '/videos/city4.mp4',
  '/videos/city5.mp4'
]

// 随机选择一个城市视频
const currentVideo = ref('')
const getRandomVideo = () => {
  const randomIndex = Math.floor(Math.random() * cityVideos.length)
  return cityVideos[randomIndex]
}

// 登录类型（普通用户/管理员）
const loginType = ref('user')
// 表单切换（登录/注册）
const activeTab = ref('login')
// 加载状态
const loading = ref(false)
// 验证码倒计时
const countdown = ref(0)

// 登录表单数据
const loginForm = reactive({
  email: '',
  password: '',
  adminCode: '' // 管理员专属字段
})

// 注册表单数据
const registerForm = reactive({
  email: '',
  code: '',
  password: '',
  confirmPassword: ''
})

// 登录表单验证规则
const loginRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: ['blur', 'change'] }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6位', trigger: 'blur' }
  ],
  adminCode: [
    {
      required: loginType.value === 'admin',
      message: '请输入管理员码',
      trigger: 'blur'
    }
  ]
}

// 注册表单验证规则
const registerRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: ['blur', 'change'] }
  ],
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { pattern: /^\d{6}$/, message: '验证码为6位数字', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 页面挂载时执行
onMounted(() => {
  // 随机设置背景视频
  currentVideo.value = getRandomVideo()
  // 确保视频自动播放（处理浏览器限制）
  if (bgVideo.value) {
    bgVideo.value.play().catch(e => {
      console.log('视频自动播放被阻止:', e)
    })
  }
})

// 发送验证码
const sendVerificationCode = async () => {
  if (!registerForm.email) {
    ElMessage.warning('请输入邮箱')
    return
  }

  try {
    await api.sendVerificationCode(registerForm.email)
    ElMessage.success('验证码已发送，请查收邮件')
    startCountdown() // 启动倒计时
  } catch (error) {
    ElMessage.error(`发送验证码失败: ${error.message}`)
  }
}

// 验证码倒计时逻辑
const startCountdown = () => {
  countdown.value = 60
  const timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(timer) // 倒计时结束清除定时器
    }
  }, 1000)
}

// 处理登录逻辑
const handleLogin = async () => {
  try {
    loading.value = true
    // 构建登录请求数据（根据登录类型添加管理员码）
    const loginData = {
      email: loginForm.email,
      password: loginForm.password
    }
    if (loginType.value === 'admin') {
      loginData.admin_code = loginForm.adminCode
    }

    // 调用登录接口
    const response = await api.login(loginData)
    // 存储用户信息到Pinia和localStorage
    userStore.token = response.data.token
    userStore.userInfo = {
      user_id: response.data.user_id,
      email: response.data.email,
      role: response.data.role,
      is_admin: response.data.is_admin,
      is_temporary_admin: response.data.is_temporary_admin
    }
    userStore.isAuthenticated = true
    localStorage.setItem('token', userStore.token)
    localStorage.setItem('userInfo', JSON.stringify(userStore.userInfo))

    ElMessage.success('登录成功')
    // 根据角色跳转不同页面（管理员→控制台，普通用户→首页）
    if (response.data.is_admin) {
      router.push('/dashboard')
    } else {
      router.push('/home')
    }
  } catch (error) {
    ElMessage.error(`登录失败: ${error.response?.data?.error || error.message}`)
  } finally {
    loading.value = false // 无论成功失败，都关闭加载状态
  }
}

// 处理注册逻辑
const handleRegister = async () => {
  try {
    loading.value = true
    // 调用注册接口
    await api.register({
      email: registerForm.email,
      password: registerForm.password,
      code: registerForm.code
    })

    ElMessage.success('注册成功，请登录')
    activeTab.value = 'login' // 自动切换到登录页
    loginForm.email = registerForm.email // 回显注册邮箱
  } catch (error) {
    ElMessage.error(`注册失败: ${error.message}`)
  } finally {
    loading.value = false
  }
}

// 使用演示账号登录
const useDemoAccount = () => {
  loginForm.email = '2292974063@qq.com'
  loginForm.password = '123456'
  handleLogin() // 自动触发登录
}
</script>

<style scoped>
.login-container {
  display: flex;
  height: 100vh;
  position: relative;
  overflow: hidden;
}

/* 全屏背景视频样式 */
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

/* 视频遮罩层（增强文字可读性） */
.video-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  z-index: 1;
}

/* 左侧系统信息区域 */
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

/* 功能卡片样式 */
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

/* 右侧登录表单容器 */
.login-form-container {
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

/* 登录/注册卡片通用样式 */
.login-card, .register-card {
  color: white;
  animation: fadeInUp 0.6s ease;
}

/* 卡片入场动画 */
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

.card-header {
  text-align: center;
  margin-bottom: 40px;
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

/* 登录类型切换Tabs */
.login-type-tabs {
  display: flex;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 4px;
  margin-bottom: 30px;
}

.type-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 500;
}

.type-tab i {
  margin-right: 8px;
  font-size: 16px;
}

.type-tab.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.type-tab:not(.active):hover {
  background: rgba(255, 255, 255, 0.1);
}

/* 表单通用样式 */
.login-form, .register-form {
  margin-bottom: 30px;
}

/* 带图标的输入框 */
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

/* 验证码按钮样式 */
.code-item {
  position: relative;
}

.code-btn {
  position: absolute;
  right: 4px;
  top: 4px;
  height: calc(100% - 8px);
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.2);
  color: #667eea;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.code-btn:hover {
  background: rgba(102, 126, 234, 0.2);
  border-color: rgba(102, 126, 234, 0.3);
}

.code-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 登录/注册按钮样式 */
.login-btn, .register-btn {
  width: 100%;
  height: 50px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 12px;
  transition: all 0.3s ease;
  margin-top: 10px;
}

.login-btn:hover, .register-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

/* 表单底部链接区域 */
.form-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 30px;
}

.quick-actions, .back-link {
  flex: 1;
}

.auth-links {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 底部链接样式 */
.demo-btn, .forgot-link, .register-link, .back-btn {
  color: #94a3b8;
  transition: color 0.3s ease;
}

.demo-btn:hover, .forgot-link:hover, .register-link:hover, .back-btn:hover {
  color: #667eea;
}

.divider {
  color: #475569;
}

.back-btn i {
  margin-right: 5px;
}

/* 响应式适配（不同屏幕尺寸） */
@media (max-width: 1200px) {
  .system-info {
    padding: 0 5%;
  }

  .feature-cards {
    max-width: 400px;
  }
}

@media (max-width: 992px) {
  .login-container {
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
  }

  .login-form-container {
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

  .login-type-tabs {
    flex-direction: column;
    gap: 8px;
  }

  .form-footer {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }

  .auth-links {
    justify-content: center;
  }
}
</style>