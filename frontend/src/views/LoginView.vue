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
      </div>

      <div class="stats">
        <div class="stat-item">
          <div class="stat-value">86ms</div>
          <div class="stat-label">平均响应时间</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">1500+ QPS</div>
          <div class="stat-label">并发能力</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">¥5.3/天</div>
          <div class="stat-label">运营成本</div>
        </div>
      </div>

      <div class="tech-stack">
        <div class="tech-title">技术栈</div>
        <div class="tech-items">
          <span>Vue3</span>
          <span>Vite</span>
          <span>Element Plus</span>
          <span>函数计算</span>
          <span>表格存储</span>
          <span>OSS</span>
        </div>
      </div>
    </div>

    <!-- 右侧登录表单 -->
    <div class="login-form-container">
      <div class="form-wrapper">
        <!-- 登录表单 -->
        <div v-if="activeTab === 'login'" class="login-form">
          <h2>用户登录</h2>
          <el-form ref="loginForm" :model="loginForm" :rules="loginRules">
            <el-form-item prop="email">
              <el-input
                v-model="loginForm.email"
                placeholder="请输入邮箱"
                prefix-icon="Message"
                size="large"
              />
            </el-form-item>

            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="请输入密码"
                prefix-icon="Lock"
                size="large"
                show-password
              />
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                @click="handleLogin"
                :loading="loading"
                class="login-btn"
                size="large"
              >
                登录
              </el-button>
            </el-form-item>
          </el-form>

          <div class="form-footer">
            <el-link type="info" @click="activeTab = 'register'">注册新账号</el-link>
            <el-link type="primary" @click="useDemoAccount">使用演示账号</el-link>
          </div>
        </div>

        <!-- 注册表单 -->
        <div v-if="activeTab === 'register'" class="register-form">
          <h2>注册新账号</h2>
          <el-form ref="registerForm" :model="registerForm" :rules="registerRules">
            <el-form-item prop="email">
              <el-input
                v-model="registerForm.email"
                placeholder="请输入邮箱"
                prefix-icon="Message"
                size="large"
              />
            </el-form-item>

            <el-form-item prop="code" class="code-item">
              <el-input
                v-model="registerForm.code"
                placeholder="请输入验证码"
                prefix-icon="Key"
                size="large"
              />
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
              <el-input
                v-model="registerForm.password"
                type="password"
                placeholder="请输入密码"
                prefix-icon="Lock"
                size="large"
                show-password
              />
            </el-form-item>

            <el-form-item prop="confirmPassword">
              <el-input
                v-model="registerForm.confirmPassword"
                type="password"
                placeholder="请确认密码"
                prefix-icon="Lock"
                size="large"
                show-password
              />
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                @click="handleRegister"
                :loading="loading"
                class="register-btn"
                size="large"
              >
                注册
              </el-button>
            </el-form-item>
          </el-form>

          <div class="form-footer">
            <el-link type="primary" @click="activeTab = 'login'">返回登录</el-link>
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
  '/videos/city4.mp4'
]

// 随机选择一个城市视频
const currentVideo = ref('')
const getRandomVideo = () => {
  const randomIndex = Math.floor(Math.random() * cityVideos.length)
  return cityVideos[randomIndex]
}

onMounted(() => {
  currentVideo.value = getRandomVideo()

  // 确保视频播放
  if (bgVideo.value) {
    bgVideo.value.play().catch(e => {
      console.log('视频自动播放被阻止:', e)
    })
  }
})

const activeTab = ref('login')
const loading = ref(false)
const countdown = ref(0)

// 登录表单
const loginForm = reactive({
  email: '',
  password: ''
})

const loginRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: ['blur', 'change'] }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6位', trigger: 'blur' }
  ]
}

// 注册表单
const registerForm = reactive({
  email: '',
  code: '',
  password: '',
  confirmPassword: ''
})

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

// 发送验证码
const sendVerificationCode = async () => {
  if (!registerForm.email) {
    ElMessage.warning('请输入邮箱')
    return
  }

  try {
    await api.sendVerificationCode(registerForm.email)
    ElMessage.success('验证码已发送，请查收邮件')
    startCountdown()
  } catch (error) {
    ElMessage.error(`发送验证码失败: ${error.message}`)
  }
}

// 验证码倒计时
const startCountdown = () => {
  countdown.value = 60
  const timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(timer)
    }
  }, 1000)
}

// 登录处理
const handleLogin = async () => {
  try {
    loading.value = true
    await userStore.login({
      email: loginForm.email,
      password: loginForm.password
    })
    ElMessage.success('登录成功')
    router.push('/dashboard')
  } catch (error) {
    ElMessage.error(`登录失败: ${error.message}`)
  } finally {
    loading.value = false
  }
}

// 注册处理
const handleRegister = async () => {
  try {
    loading.value = true

    // 调用注册API
    await api.register({
      email: registerForm.email,
      password: registerForm.password,
      code: registerForm.code
    })

    ElMessage.success('注册成功，请登录')
    activeTab.value = 'login'
    loginForm.email = registerForm.email
  } catch (error) {
    ElMessage.error(`注册失败: ${error.message}`)
  } finally {
    loading.value = false
  }
}

// 使用演示账号
const useDemoAccount = () => {
  loginForm.email = '2292974063@qq.com'
  loginForm.password = '123456'
  handleLogin()
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

/* 视频遮罩层 */
.video-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  z-index: 1;
}

/* 左侧系统信息 */
.system-info {
  flex: 1;
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 0 10%;
  color: white;
}

.logo {
  display: flex;
  align-items: center;
  margin-bottom: 40px;
}

.logo i {
  font-size: 48px;
  color: #1890ff;
  margin-right: 15px;
}

.logo h1 {
  font-size: 36px;
  font-weight: 600;
  letter-spacing: 1px;
  margin: 0;
}

.stats {
  display: flex;
  gap: 30px;
  margin-bottom: 50px;
}

.stat-item {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 10px;
  padding: 20px;
  width: 180px;
  text-align: center;
  transition: transform 0.3s ease;
}

.stat-item:hover {
  transform: translateY(-5px);
  background: rgba(24, 144, 255, 0.2);
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 8px;
  color: #1890ff;
}

.stat-label {
  font-size: 14px;
  opacity: 0.8;
}

.tech-stack {
  max-width: 600px;
}

.tech-title {
  font-size: 20px;
  margin-bottom: 15px;
  color: #1890ff;
}

.tech-items {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.tech-items span {
  background: rgba(24, 144, 255, 0.2);
  backdrop-filter: blur(10px);
  padding: 8px 15px;
  border-radius: 20px;
  font-size: 14px;
}

/* 右侧登录表单 */
.login-form-container {
  position: relative;
  z-index: 2;
  width: 450px;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(20px);
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 0 40px;
  box-shadow: -5px 0 30px rgba(0, 0, 0, 0.5);
}

.form-wrapper {
  max-width: 400px;
  width: 100%;
}

.login-form, .register-form {
  color: white;
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

h2 {
  text-align: center;
  margin-bottom: 30px;
  font-size: 24px;
  color: white;
  font-weight: 500;
}

:deep(.el-form-item) {
  margin-bottom: 25px;
}

:deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  box-shadow: none;
  border-radius: 8px;
}

:deep(.el-input__inner) {
  color: white;
}

:deep(.el-input__prefix) {
  color: #1890ff;
}

.code-item {
  position: relative;
}

.code-btn {
  position: absolute;
  right: 0;
  top: 0;
  height: 100%;
  border-radius: 0 8px 8px 0;
  background: rgba(24, 144, 255, 0.3);
  border: none;
  color: white;
  transition: all 0.3s;
}

.code-btn:hover {
  background: rgba(24, 144, 255, 0.5);
}

.login-btn, .register-btn {
  width: 100%;
  height: 50px;
  font-size: 16px;
  margin-top: 10px;
  background: #1890ff;
  border: none;
  border-radius: 8px;
  transition: all 0.3s;
}

.login-btn:hover, .register-btn:hover {
  background: #40a9ff;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(24, 144, 255, 0.4);
}

.form-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

:deep(.el-link) {
  color: #8c9bae;
  transition: color 0.3s;
}

:deep(.el-link:hover) {
  color: #1890ff;
}

/* 响应式调整 */
@media (max-width: 1200px) {
  .system-info {
    padding: 0 5%;
  }

  .stats {
    flex-wrap: wrap;
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
    justify-content: center;
  }

  .stats {
    justify-content: center;
  }

  .login-form-container {
    width: 100%;
    padding: 40px 20px;
    background: rgba(0, 0, 0, 0.9);
  }

  .form-wrapper {
    max-width: 500px;
    margin: 0 auto;
  }
}
</style>