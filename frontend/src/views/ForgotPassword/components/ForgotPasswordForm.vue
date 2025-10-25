<template>
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

        <!-- 步骤内容 -->
        <component
          :is="currentStepComponent"
          :form="form"
          :sending-code="sendingCode"
          :verifying="verifying"
          :resetting="resetting"
          :countdown="countdown"
          @send-code="handleSendCode"
          @verify-code="handleVerifyCode"
          @resend-code="handleResendCode"
          @reset-password="handleResetPassword"
          @previous-step="goToPreviousStep"
          @navigate-login="navigateToLogin"
          @navigate-home="navigateToHome"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import StepEmail from './StepEmail.vue'
import StepVerify from './StepVerify.vue'
import StepReset from './StepReset.vue'
import StepComplete from './StepComplete.vue'
import type { ForgotPasswordForm } from '../composables/useForgotPassword'

interface Props {
  activeStep: number
  form: ForgotPasswordForm
  sendingCode: boolean
  verifying: boolean
  resetting: boolean
  countdown: number
}

interface Emits {
  (e: 'send-code'): void
  (e: 'verify-code'): void
  (e: 'resend-code'): void
  (e: 'reset-password'): void
  (e: 'previous-step'): void
  (e: 'navigate-login'): void
  (e: 'navigate-home'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const stepComponents = {
  1: StepEmail,
  2: StepVerify,
  3: StepReset,
  4: StepComplete
}

const currentStepComponent = computed(() => {
  return stepComponents[props.activeStep as keyof typeof stepComponents] || StepEmail
})

const handleSendCode = () => emit('send-code')
const handleVerifyCode = () => emit('verify-code')
const handleResendCode = () => emit('resend-code')
const handleResetPassword = () => emit('reset-password')
const goToPreviousStep = () => emit('previous-step')
const navigateToLogin = () => emit('navigate-login')
const navigateToHome = () => emit('navigate-home')
</script>

<style scoped>
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

.steps {
  margin-bottom: 30px;
}

/* 步骤条样式 */
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

@media (max-width: 992px) {
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
}
</style>