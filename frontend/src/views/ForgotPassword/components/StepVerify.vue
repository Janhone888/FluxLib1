<template>
  <div class="step-content">
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
        <el-button :disabled="countdown > 0" @click="$emit('resend-code')" class="resend-btn">
          {{ countdown > 0 ? `${countdown}秒后重发` : '重新发送' }}
        </el-button>
      </el-form-item>

      <el-form-item class="btn-group">
        <el-button
          type="primary"
          @click="$emit('verify-code')"
          :loading="verifying"
          class="action-btn"
          size="large"
        >
          <span v-if="!verifying">验证验证码</span>
          <span v-else>验证中...</span>
        </el-button>
        <el-button @click="$emit('previous-step')" size="large" class="secondary-btn">上一步</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import type { ForgotPasswordForm } from '../composables/useForgotPassword'

interface Props {
  form: ForgotPasswordForm
  verifying: boolean
  countdown: number
  rules: any
}

interface Emits {
  (e: 'verify-code'): void
  (e: 'resend-code'): void
  (e: 'previous-step'): void
}

defineProps<Props>()
defineEmits<Emits>()
</script>

<style scoped>
.step-content {
  padding: 0 0 15px;
}

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

.step-form {
  margin-bottom: 20px;
}

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

.btn-group {
  display: flex;
  gap: 10px;
}

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

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
  background: linear-gradient(135deg, #768fea 0%, #865bc2 100%);
}

.secondary-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

@media (max-width: 768px) {
  .step-alert {
    padding: 10px 14px;
  }

  .alert-content h4 {
    font-size: 14px;
  }

  .alert-content p {
    font-size: 13px;
  }

  .btn-group {
    flex-direction: column;
    gap: 8px;
  }
}
</style>