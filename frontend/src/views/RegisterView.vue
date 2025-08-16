<template>
  <div class="register-container">
    <el-card class="register-card">
      <div class="logo">
        <i class="el-icon-notebook-2"></i>
        <h2>注册新账户</h2>
      </div>

      <el-steps :active="activeStep" align-center class="steps">
        <el-step title="账户信息" />
        <el-step title="邮箱验证" />
        <el-step title="完成注册" />
      </el-steps>

      <!-- 步骤1: 账户信息 -->
      <div v-if="activeStep === 1" class="step-content">
        <el-form ref="accountForm" :model="accountForm" :rules="accountRules" label-width="100px">
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="accountForm.email" placeholder="请输入您的邮箱" />
          </el-form-item>

          <el-form-item label="密码" prop="password">
            <el-input v-model="accountForm.password" type="password" placeholder="设置登录密码" show-password />
          </el-form-item>

          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input v-model="accountForm.confirmPassword" type="password" placeholder="再次输入密码" show-password />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="sendVerification" :loading="sendingCode">发送验证码</el-button>
            <el-button @click="$router.push('/login')">返回登录</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 步骤2: 邮箱验证 -->
      <div v-if="activeStep === 2" class="step-content">
        <el-alert type="success" show-icon :closable="false">
          <template #title>
            验证码已发送至 <strong>{{ accountForm.email }}</strong>，请查收邮件
          </template>
        </el-alert>

        <el-form ref="verifyForm" :model="verifyForm" :rules="verifyRules" label-width="100px" class="mt-4">
          <el-form-item label="验证码" prop="code">
            <el-input v-model="verifyForm.code" placeholder="请输入6位验证码">
              <template #append>
                <el-button :disabled="countdown > 0" @click="resendCode">
                  {{ countdown > 0 ? `${countdown}秒后重发` : '重新发送' }}
                </el-button>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="verifyCode" :loading="verifying">验证账户</el-button>
            <el-button @click="activeStep = 1">上一步</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 步骤3: 注册完成 -->
      <div v-if="activeStep === 3" class="step-complete">
        <el-result icon="success" title="注册成功" sub-title="您的账户已成功创建">
          <template #extra>
            <el-button type="primary" @click="$router.push('/login')">立即登录</el-button>
            <el-button @click="$router.push('/')">返回首页</el-button>
          </template>
        </el-result>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()
const activeStep = ref(1)
const sendingCode = ref(false)
const verifying = ref(false)
const countdown = ref(0)
let countdownTimer = null

// 账户表单
const accountForm = reactive({
  email: '',
  password: '',
  confirmPassword: ''
})

// 验证表单
const verifyForm = reactive({
  code: ''
})

// 表单验证规则
const accountRules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: ['blur', 'change'] }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, message: '密码长度至少为8位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== accountForm.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const verifyRules = {
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 6, message: '验证码长度为6位', trigger: 'blur' }
  ]
}

// 发送验证码
const sendVerification = async () => {
  try {
    sendingCode.value = true
    await userStore.sendVerificationCode(accountForm.email, accountForm.password)
    activeStep.value = 2
    startCountdown()
    ElMessage.success('验证码已发送，请查收邮箱')
  } catch (error) {
    ElMessage.error(`发送失败: ${error.message}`)
  } finally {
    sendingCode.value = false
  }
}

// 验证验证码
const verifyCode = async () => {
  try {
    verifying.value = true
    await userStore.verifyAccount(accountForm.email, verifyForm.code)
    activeStep.value = 3
    ElMessage.success('账户验证成功')
  } catch (error) {
    ElMessage.error(`验证失败: ${error.message}`)
  } finally {
    verifying.value = false
  }
}

// 重新发送验证码
const resendCode = async () => {
  try {
    await userStore.sendVerificationCode(accountForm.email, accountForm.password)
    startCountdown()
    ElMessage.success('验证码已重新发送')
  } catch (error) {
    ElMessage.error(`发送失败: ${error.message}`)
  }
}

// 倒计时
const startCountdown = () => {
  countdown.value = 60
  clearInterval(countdownTimer)
  countdownTimer = setInterval(() => {
    if (countdown.value > 0) {
      countdown.value--
    } else {
      clearInterval(countdownTimer)
    }
  }, 1000)
}

// 组件卸载时清除定时器
onUnmounted(() => {
  clearInterval(countdownTimer)
})
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 20px;
}

.register-card {
  width: 100%;
  max-width: 600px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.logo {
  text-align: center;
  margin-bottom: 20px;
}

.logo i {
  font-size: 48px;
  color: #1890ff;
}

.logo h2 {
  margin-top: 10px;
}

.steps {
  margin-bottom: 30px;
}

.step-content {
  padding: 0 20px 20px;
}

.step-complete {
  padding: 40px 20px;
  text-align: center;
}

.mt-4 {
  margin-top: 16px;
}
</style>