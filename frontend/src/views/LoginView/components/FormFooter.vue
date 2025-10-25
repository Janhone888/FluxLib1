/* 表单底部链接组件 */
<template>
  <div class="form-footer">
    <div v-if="showQuickActions" class="quick-actions">
      <el-button link @click="$emit('use-demo-account')" class="demo-btn">
        <i class="el-icon-magic-stick"></i>
        使用演示账号
      </el-button>
    </div>

    <div v-if="showAuthLinks" class="auth-links">
      <el-button link @click="$emit('forgot-password')" class="forgot-link">
        忘记密码？
      </el-button>
      <span class="divider">|</span>
      <el-button link @click="$emit('switch-to-register')" class="register-link">
        注册新账号
      </el-button>
    </div>

    <div v-if="showBack" class="back-link">
      <el-button link @click="$emit('back')" class="back-btn">
        <i class="el-icon-arrow-left"></i>
        返回登录
      </el-button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  showQuickActions: {
    type: Boolean,
    default: false
  },
  showAuthLinks: {
    type: Boolean,
    default: false
  },
  showBack: {
    type: Boolean,
    default: false
  }
})

defineEmits(['use-demo-account', 'forgot-password', 'switch-to-register', 'back'])
</script>

<style scoped>
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

/* 响应式适配 */
@media (max-width: 768px) {
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