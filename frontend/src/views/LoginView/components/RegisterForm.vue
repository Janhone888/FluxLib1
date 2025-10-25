/* 注册表单组件 */
<template>
  <div class="register-card">
    <div class="card-header">
      <h2>创建账户</h2>
      <p>注册新的用户账户</p>
    </div>

    <el-form ref="registerFormRef" :model="form" :rules="rules" class="register-form">
      <FormInput
        v-model="form.email"
        icon="el-icon-message"
        placeholder="请输入邮箱"
        prop="email"
        type="email"
      />

      <FormInput
        v-model="form.code"
        icon="el-icon-key"
        placeholder="请输入验证码"
        prop="code"
        class="code-item"
      >
        <template #append>
          <el-button
            :disabled="countdown > 0"
            @click="sendVerificationCode"
            class="code-btn"
            size="large"
          >
            {{ countdown > 0 ? `${countdown}秒后重试` : '获取验证码' }}
          </el-button>
        </template>
      </FormInput>

      <FormInput
        v-model="form.password"
        icon="el-icon-lock"
        placeholder="请输入密码"
        prop="password"
        type="password"
        show-password
      />

      <FormInput
        v-model="form.confirmPassword"
        icon="el-icon-lock"
        placeholder="请确认密码"
        prop="confirmPassword"
        type="password"
        show-password
      />

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

    <FormFooter
      :show-back="true"
      @back="$emit('switch-to-login')"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuth } from '../composables/useAuth'
import { useCountdown } from '../composables/useCountdown'
import FormInput from './FormInput.vue'
import FormFooter from './FormFooter.vue'

defineEmits(['switch-to-login'])

const { register, sendVerificationCode: sendCode } = useAuth()
const { countdown, startCountdown } = useCountdown()

const registerFormRef = ref()
const loading = ref(false)

const form = reactive({
  email: '',
  code: '',
  password: '',
  confirmPassword: ''
})

const rules = computed(() => ({
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
        if (value !== form.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}))

const sendVerificationCode = async () => {
  if (!form.email) {
    ElMessage.warning('请输入邮箱')
    return
  }

  try {
    await sendCode(form.email)
    ElMessage.success('验证码已发送，请查收邮件')
    startCountdown(60)
  } catch (error) {
    ElMessage.error(`发送验证码失败: ${error.message}`)
  }
}

const handleRegister = async () => {
  try {
    const valid = await registerFormRef.value.validate()
    if (!valid) return

    loading.value = true

    await register({
      email: form.email,
      password: form.password,
      code: form.code
    })

    ElMessage.success('注册成功，请登录')
    window.location.reload() // 刷新页面以清除表单状态
  } catch (error) {
    ElMessage.error(`注册失败: ${error.message}`)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-card {
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

.register-form {
  margin-bottom: 30px;
}

.code-item {
  position: relative;
}

.code-btn {
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

.register-btn {
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

.register-btn:hover {
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