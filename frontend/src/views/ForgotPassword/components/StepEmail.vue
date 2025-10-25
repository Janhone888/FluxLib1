<template>
  <div class="step-content">
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
          @click="$emit('send-code')"
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
      <el-button link @click="$emit('navigate-login')" class="back-link">
        <i class="el-icon-arrow-left"></i>
        返回登录
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ForgotPasswordForm } from '../composables/useForgotPassword'

interface Props {
  form: ForgotPasswordForm
  sendingCode: boolean
  rules: any
}

interface Emits {
  (e: 'send-code'): void
  (e: 'navigate-login'): void
}

defineProps<Props>()
defineEmits<Emits>()
</script>

<style scoped>
.step-content {
  padding: 0 0 15px;
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

.action-btn {
  width: 100%;
  height: 50px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
  background: linear-gradient(135deg, #768fea 0%, #865bc2 100%);
}

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
</style>