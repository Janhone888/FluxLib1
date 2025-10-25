<template>
  <div class="system-info">
    <div class="logo">
      <i class="el-icon-notebook-2"></i>
      <h1>找回密码</h1>
      <p class="slogan">重置密码，重新获得账户访问权限</p>
    </div>

    <div class="feature-cards">
      <div class="feature-card">
        <div class="feature-icon">
          <i class="el-icon-message"></i>
        </div>
        <div class="feature-content">
          <h3>邮箱验证</h3>
          <p>通过注册邮箱接收验证码</p>
        </div>
      </div>

      <div class="feature-card">
        <div class="feature-icon">
          <i class="el-icon-lock"></i>
        </div>
        <div class="feature-content">
          <h3>安全重置</h3>
          <p>保障账户安全，防止未授权访问</p>
        </div>
      </div>

      <div class="feature-card">
        <div class="feature-icon">
          <i class="el-icon-time"></i>
        </div>
        <div class="feature-content">
          <h3>快速完成</h3>
          <p>简单几步，快速重置密码</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 这个组件是静态的，不需要额外的逻辑
</script>

<style scoped>
.system-info {
  flex: 1;
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 0 8%;
  color: white;
}

.logo {
  margin-bottom: 60px;
}

.logo i {
  font-size: 64px;
  color: #1890ff;
  margin-bottom: 20px;
  display: block;
}

.logo h1 {
  font-size: 42px;
  font-weight: 700;
  margin-bottom: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.slogan {
  font-size: 18px;
  opacity: 0.8;
  font-weight: 300;
}

.feature-cards {
  display: flex;
  flex-direction: column;
  gap: 25px;
  max-width: 500px;
}

.feature-card {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 20px;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.feature-card:hover {
  transform: translateY(-5px);
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.2);
}

.feature-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  flex-shrink: 0;
}

.feature-icon i {
  font-size: 24px;
  color: white;
}

.feature-content h3 {
  margin: 0 0 5px 0;
  font-size: 16px;
  font-weight: 600;
}

.feature-content p {
  margin: 0;
  font-size: 14px;
  opacity: 0.8;
}

@media (max-width: 1200px) {
  .system-info {
    padding: 0 5%;
  }

  .feature-cards {
    max-width: 400px;
  }
}

@media (max-width: 992px) {
  .system-info {
    padding: 40px 20px;
    text-align: center;
  }

  .logo {
    margin-bottom: 40px;
  }

  .feature-cards {
    max-width: 100%;
    margin: 0 auto;
  }
}
</style>