/* 系统信息展示组件 */
<template>
  <div class="system-info">
    <div class="logo">
      <i class="el-icon-notebook-2"></i>
      <h1>FluxLib 泛集库</h1>
      <p class="slogan">智慧图书管理，让阅读更简单</p>
    </div>

    <div class="feature-cards">
      <FeatureCard
        v-for="feature in features"
        :key="feature.title"
        :icon="feature.icon"
        :title="feature.title"
        :description="feature.description"
      />
    </div>
  </div>
</template>

<script setup>
import FeatureCard from './FeatureCard.vue'

const features = [
  {
    icon: 'el-icon-collection',
    title: '海量图书资源',
    description: '涵盖计算机、文学、经济等多个领域'
  },
  {
    icon: 'el-icon-timer',
    title: '智能借阅管理',
    description: '一键借阅归还，到期提醒'
  },
  {
    icon: 'el-icon-chat-dot-round',
    title: 'AI智能助手',
    description: '智能推荐，解答疑问'
  }
]
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

/* 响应式适配 */
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
  }
}
</style>