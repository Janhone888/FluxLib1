<template>
  <div class="step-content">
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
          @click="$emit('reset-password')"
          :loading="resetting"
          class="action-btn"
          size="large"
        >
          <span v-if="!resetting">重置密码</span>
          <span v-else>重置中...</span>
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
  resetting: boolean
  passwordRules: any
}

interface Emits {
  (e: 'reset-password'): void
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