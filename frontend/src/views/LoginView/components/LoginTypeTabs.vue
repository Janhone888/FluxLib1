/* 登录类型切换标签页 */
<template>
  <div class="login-type-tabs">
    <div
      v-for="tab in tabs"
      :key="tab.value"
      class="type-tab"
      :class="{ active: loginType === tab.value }"
      @click="$emit('update:loginType', tab.value)"
    >
      <i :class="tab.icon"></i>
      <span>{{ tab.label }}</span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  loginType: {
    type: String,
    required: true
  }
})

defineEmits(['update:loginType'])

const tabs = [
  {
    value: 'user',
    icon: 'el-icon-user',
    label: '用户登录'
  },
  {
    value: 'admin',
    icon: 'el-icon-s-custom',
    label: '管理员登录'
  }
]
</script>

<style scoped>
.login-type-tabs {
  display: flex;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 4px;
  margin-bottom: 30px;
}

.type-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 500;
}

.type-tab i {
  margin-right: 8px;
  font-size: 16px;
}

.type-tab.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.type-tab:not(.active):hover {
  background: rgba(255, 255, 255, 0.1);
}

/* 响应式适配 */
@media (max-width: 768px) {
  .login-type-tabs {
    flex-direction: column;
    gap: 8px;
  }
}
</style>