/* 登陆页面主组件 */
<template>
  <div class="login-container">
    <BackgroundVideo />

    <div class="login-content">
      <SystemInfo />

      <div class="login-form-container">
        <div class="form-wrapper">
          <LoginForm
            v-if="activeTab === 'login'"
            @switch-to-register="activeTab = 'register'"
          />
          <RegisterForm
            v-else
            @switch-to-login="activeTab = 'login'"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import BackgroundVideo from './components/BackgroundVideo.vue'
import SystemInfo from './components/SystemInfo.vue'
import LoginForm from './components/LoginForm.vue'
import RegisterForm from './components/RegisterForm.vue'

const activeTab = ref('login')
</script>

<style scoped>
.login-container {
  display: flex;
  height: 100vh;
  position: relative;
  overflow: hidden;
}

.login-content {
  display: flex;
  width: 100%;
  position: relative;
  z-index: 2;
}

.login-form-container {
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

/* 响应式适配 */
@media (max-width: 992px) {
  .login-content {
    flex-direction: column;
  }

  .login-form-container {
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
</style>