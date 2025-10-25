/* 登陆表单组件 */
<template>
  <div class="login-card">
    <div class="card-header">
      <h2>欢迎回来</h2>
      <p>请登录您的账户</p>
    </div>

    <LoginTypeTabs v-model:login-type="loginType" />

    <el-form ref="loginFormRef" :model="form" :rules="rules" class="login-form">
      <FormInput
        v-model="form.email"
        icon="el-icon-message"
        placeholder="请输入邮箱"
        prop="email"
        type="email"
      />

      <FormInput
        v-model="form.password"
        icon="el-icon-lock"
        placeholder="请输入密码"
        prop="password"
        type="password"
        show-password
      />

      <FormInput
        v-if="loginType === 'admin'"
        v-model="form.adminCode"
        icon="el-icon-key"
        placeholder="请输入管理员码"
        prop="adminCode"
      />

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

    <FormFooter
      :show-quick-actions="true"
      @use-demo-account="useDemoAccount"
      @forgot-password="$router.push('/forgot-password')"
      @switch-to-register="$emit('switch-to-register')"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuth } from '../composables/useAuth'
import LoginTypeTabs from './LoginTypeTabs.vue'
import FormInput from './FormInput.vue'
import FormFooter from './FormFooter.vue'

defineEmits(['switch-to-register'])

const router = useRouter()
const { login } = useAuth()

const loginFormRef = ref()
const loginType = ref('user')
const loading = ref(false)

const form = reactive({
  email: '',
  password: '',
  adminCode: ''
})

const rules = computed(() => ({
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
}))

const handleLogin = async () => {
  try {
    const valid = await loginFormRef.value.validate()
    if (!valid) return

    loading.value = true

    const loginData = {
      email: form.email,
      password: form.password
    }

    if (loginType.value === 'admin') {
      loginData.admin_code = form.adminCode
    }

    const user = await login(loginData)

    ElMessage.success('登录成功')

    if (user.is_admin) {
      router.push('/dashboard')
    } else {
      router.push('/home')
    }
  } catch (error) {
    ElMessage.error(`登录失败: ${error.response?.data?.error || error.message}`)
  } finally {
    loading.value = false
  }
}

const useDemoAccount = () => {
  form.email = '2292974063@qq.com'
  form.password = '123456'
  handleLogin()
}
</script>

<style scoped>
.login-card {
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

.login-form {
  margin-bottom: 30px;
}

.login-btn {
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

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

/* 响应式适配 */
@media (max-width: 768px) {
  .card-header h2 {
    font-size: 24px;
  }
}
</style>