<template>
  <div class="step-complete">
    <div class="success-icon">
      <i class="el-icon-success"></i>
    </div>
    <h3>密码重置成功</h3>
    <p>您的密码已成功重置，请使用新密码登录</p>
    <div class="complete-actions">
      <el-button type="primary" @click="$emit('navigate-login')" class="action-btn">
        立即登录
      </el-button>
      <el-button @click="$emit('navigate-home')" class="secondary-btn">返回首页</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Emits {
  (e: 'navigate-login'): void
  (e: 'navigate-home'): void
}

defineEmits<Emits>()
</script>

<style scoped>
.step-complete {
  padding: 30px 0;
  text-align: center;
}

.success-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
}

.success-icon i {
  font-size: 48px;
  color: white;
}

.step-complete h3 {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 10px 0;
  color: white;
}

.step-complete p {
  font-size: 16px;
  color: #94a3b8;
  margin: 0 0 30px 0;
}

.complete-actions {
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
  .complete-actions {
    flex-direction: column;
    gap: 8px;
  }
}
</style>