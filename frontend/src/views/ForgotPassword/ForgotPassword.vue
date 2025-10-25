<template>
  <div class="forgot-password-container">
    <!-- 视频背景 -->
    <video ref="bgVideo" class="bg-video" autoplay muted loop>
      <source :src="currentVideo" type="video/mp4">
    </video>

    <div class="video-overlay"></div>

    <!-- 左侧信息区域 -->
    <SystemInfo />

    <!-- 右侧表单区域 -->
    <ForgotPasswordForm
      :active-step="activeStep"
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
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

// Components
import SystemInfo from './components/SystemInfo.vue'
import ForgotPasswordForm from './components/ForgotPasswordForm.vue'

// Composables
import { useVideoBackground } from './composables/useVideoBackground'
import { useCountdown } from './composables/useCountdown'
import { useForgotPassword } from './composables/useForgotPassword'

// 视频背景逻辑
const bgVideo = ref<HTMLVideoElement | null>(null)
const { currentVideo, initializeVideo } = useVideoBackground()

// 倒计时逻辑
const { countdown, startCountdown } = useCountdown()

// 密码重置逻辑
const {
  activeStep,
  sendingCode,
  verifying,
  resetting,
  form,
  rules,
  passwordRules,
  sendVerificationCode,
  verifyCode,
  resendCode,
  resetPassword,
  navigateToLogin,
  navigateToHome,
  goToPreviousStep
} = useForgotPassword()

// 初始化
onMounted(() => {
  initializeVideo(bgVideo.value)
})

// 事件处理
const handleSendCode = async () => {
  try {
    await sendVerificationCode()
    startCountdown()
  } catch (error) {
    // 错误已经在 composable 中处理
  }
}

const handleVerifyCode = async () => {
  try {
    await verifyCode()
  } catch (error) {
    // 错误已经在 composable 中处理
  }
}

const handleResendCode = async () => {
  try {
    await resendCode()
    startCountdown()
  } catch (error) {
    // 错误已经在 composable 中处理
  }
}

const handleResetPassword = async () => {
  try {
    await resetPassword()
  } catch (error) {
    // 错误已经在 composable 中处理
  }
}

// 暴露规则给模板（如果需要的话）
defineExpose({
  rules,
  passwordRules
})
</script>

<style scoped>
.forgot-password-container {
  display: flex;
  height: 100vh;
  position: relative;
  overflow: hidden;
}

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

.video-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  z-index: 1;
}

@media (max-width: 992px) {
  .forgot-password-container {
    flex-direction: column;
  }
}
</style>