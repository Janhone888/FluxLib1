<template>
  <div class="chatbot-container">
    <!-- 浮动按钮 -->
    <div class="chatbot-btn" @click="toggleChat" :class="{ 'has-notification': hasNewMessage }">
      <img src="/icons/ai-icon.png" alt="AI助手" class="custom-icon" />
      <span class="notification-dot" v-if="hasNewMessage"></span>
    </div>

    <!-- 聊天窗口 -->
    <el-drawer
      v-model="chatVisible"
      title="FluxLib AI助手"
      direction="rtl"
      size="400px"
      class="chat-drawer"
      :with-header="false"
    >
      <div class="chat-container">
        <!-- 头部 -->
        <div class="chat-header">
          <div class="header-left">
            <img src="/icons/ai-icon.png" alt="AI助手" class="ai-avatar" />
            <div class="header-info">
              <h3>FluxLib AI助手</h3>
              <span class="status">在线</span>
            </div>
          </div>
          <el-button link @click="closeChat">
            <el-icon><Close /></el-icon>
          </el-button>
        </div>

        <!-- 消息区域 -->
        <div class="chat-messages" ref="messagesContainer">
          <div v-for="(msg, index) in messages" :key="index"
               :class="['message', msg.role]">
            <div class="message-avatar">
              <img
                v-if="msg.role === 'ai'"
                src="/icons/ai-icon.png"
                alt="AI助手"
                class="avatar-img"
              />
              <img
                v-else
                src="/icons/user-icon.png"
                alt="用户"
                class="avatar-img"
              />
            </div>
            <div class="message-content-wrapper">
              <div class="message-content">
                <div v-if="msg.role === 'ai'" class="ai-name">FluxLib助手</div>
                <div class="text-content">{{ msg.content }}</div>
              </div>
              <div class="message-time">
                {{ formatTime(msg.timestamp) }}
              </div>
            </div>
          </div>

          <div v-if="loading" class="message ai">
            <div class="message-avatar">
              <img src="/icons/ai-icon.png" alt="AI助手" class="avatar-img" />
            </div>
            <div class="message-content-wrapper">
              <div class="message-content">
                <div class="ai-name">FluxLib助手</div>
                <div class="text-content">
                  <el-icon class="loading"><Loading /></el-icon>
                  思考中...
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="chat-input-area">
          <div class="quick-questions">
            <el-tag
              v-for="(question, index) in quickQuestions"
              :key="index"
              size="small"
              @click="selectQuickQuestion(question)"
              class="question-tag"
            >
              {{ question }}
            </el-tag>
          </div>
          <div class="input-wrapper">
            <el-input
              v-model="inputMessage"
              placeholder="输入您的问题..."
              @keyup.enter="sendMessage"
              :disabled="loading"
              class="message-input"
            >
              <template #append>
                <el-button
                  :icon="Search"
                  @click="sendMessage"
                  :loading="loading"
                  class="send-btn"
                />
              </template>
            </el-input>
          </div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, watch, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  ChatDotRound,
  Close,
  Search,
  Loading
} from '@element-plus/icons-vue'
import api from '@/utils/api'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const chatVisible = ref(false)
const inputMessage = ref('')
const messages = ref([])
const loading = ref(false)
const hasNewMessage = ref(false)
const messagesContainer = ref(null)

// 快捷问题
const quickQuestions = [
  "推荐几本计算机类的书",
  "图书馆的营业时间是什么？",
  "如何借阅图书？",
  "有哪些文学类图书？"
]

// 获取用户特定的存储键
const getStorageKey = () => {
  if (!userStore.userInfo.user_id) {
    return 'ai_chat_history'
  }
  return `ai_chat_history_${userStore.userInfo.user_id}`
}

// 从localStorage加载历史消息
onMounted(() => {
  loadMessages()

  // 监听用户变化
  window.addEventListener('user-changed', handleUserChange)
})

// 组件卸载时移除监听器
onUnmounted(() => {
  window.removeEventListener('user-changed', handleUserChange)
})

// 处理用户变化
const handleUserChange = () => {
  // 用户变化时清除当前消息并加载新用户的消息
  messages.value = []
  loadMessages()
}

// 加载消息
const loadMessages = () => {
  const storageKey = getStorageKey()
  const savedMessages = localStorage.getItem(storageKey)
  if (savedMessages) {
    try {
      messages.value = JSON.parse(savedMessages)
    } catch (e) {
      console.error('解析聊天历史失败:', e)
      initWelcomeMessage()
    }
  } else {
    initWelcomeMessage()
  }
}

// 初始化欢迎消息
const initWelcomeMessage = () => {
  messages.value = [{
    role: 'ai',
    content: '您好！我是FluxLib AI助手，基于DeepSeek技术驱动。我可以帮您查询图书信息、推荐书籍、解答借阅问题等。请问有什么可以帮您？',
    timestamp: Date.now()
  }]
  saveMessages()
}

// 保存消息到localStorage
const saveMessages = () => {
  const storageKey = getStorageKey()
  localStorage.setItem(storageKey, JSON.stringify(messages.value))
}

// 清除当前用户的消息
const clearMessages = () => {
  const storageKey = getStorageKey()
  localStorage.removeItem(storageKey)
  messages.value = []
  initWelcomeMessage()
}

// 格式化时间
const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// 发送消息
const sendMessage = async () => {
  if (!inputMessage.value.trim() || loading.value) return

  const userMessage = inputMessage.value.trim()
  inputMessage.value = ''

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: userMessage,
    timestamp: Date.now()
  })

  saveMessages()
  loading.value = true
  scrollToBottom()

  try {
    const response = await api.sendAIMessage(userMessage)

    // 添加AI回复
    messages.value.push({
      role: 'ai',
      content: response.data.response,
      timestamp: response.data.timestamp * 1000
    })

    saveMessages()
    scrollToBottom()

  } catch (error) {
    console.error('发送消息失败:', error)
    ElMessage.error('发送消息失败，请检查网络连接')

    // 添加错误消息
    messages.value.push({
      role: 'ai',
      content: '抱歉，我现在无法处理您的请求，请稍后再试。',
      timestamp: Date.now()
    })

    saveMessages()
  } finally {
    loading.value = false
  }
}

// 选择快捷问题
const selectQuickQuestion = (question) => {
  inputMessage.value = question
  sendMessage()
}

// 切换聊天窗口
const toggleChat = () => {
  chatVisible.value = !chatVisible.value
  if (chatVisible.value) {
    hasNewMessage.value = false
    scrollToBottom()
  }
}

// 关闭聊天
const closeChat = () => {
  chatVisible.value = false
}

// 监听消息变化
watch(messages, (newVal) => {
  if (!chatVisible.value && newVal.length > 0) {
    const lastMessage = newVal[newVal.length - 1]
    if (lastMessage.role === 'ai') {
      hasNewMessage.value = true
    }
  }
}, { deep: true })
</script>

<style scoped>
.chatbot-container {
  position: fixed;
  right: 20px;
  bottom: 20px;
  z-index: 9999;
}

.chatbot-btn {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1890ff, #722ed1);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
  position: relative;
}

.chatbot-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.custom-icon {
  width: 32px;
  height: 32px;
  object-fit: contain;
}

.notification-dot {
  position: absolute;
  top: 0;
  right: 0;
  width: 12px;
  height: 12px;
  background-color: #ff4d4f;
  border-radius: 50%;
  border: 2px solid white;
}

.chat-drawer {
  :deep(.el-drawer__body) {
    padding: 0;
    display: flex;
    flex-direction: column;
  }
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #e5e5e5;
  background: white;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-info h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.status {
  font-size: 12px;
  color: #52c41a;
}

.ai-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.avatar-img {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background-color: #f9f9f9;
}

.message {
  display: flex;
  margin-bottom: 20px;
  gap: 12px;
}

.message.user {
  flex-direction: row-reverse;
}

.message-content-wrapper {
  max-width: 70%;
}

.message-content {
  padding: 12px 16px;
  border-radius: 18px;
  position: relative;
  line-height: 1.5;
}

.user .message-content {
  background: #1890ff;
  color: white;
  border-bottom-right-radius: 4px;
}

.ai .message-content {
  background: white;
  color: #333;
  border: 1px solid #e5e5e5;
  border-bottom-left-radius: 4px;
}

.ai-name {
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 4px;
  color: #666;
}

.message-time {
  font-size: 11px;
  color: #999;
  margin-top: 4px;
  text-align: right;
}

.user .message-time {
  text-align: left;
}

.chat-input-area {
  padding: 16px;
  border-top: 1px solid #e5e5e5;
  background: white;
}

.quick-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.question-tag {
  cursor: pointer;
  transition: all 0.2s;
}

.question-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.input-wrapper {
  display: flex;
  gap: 8px;
}

.message-input {
  flex: 1;
}

.send-btn {
  background: linear-gradient(135deg, #1890ff, #722ed1);
  color: white;
  border: none;
}

.loading {
  animation: rotating 2s linear infinite;
  margin-right: 8px;
}

@keyframes rotating {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chatbot-btn {
    width: 50px;
    height: 50px;
    right: 10px;
    bottom: 10px;
  }

  .chat-drawer {
    width: 100% !important;
  }

  .message-content-wrapper {
    max-width: 85%;
  }
}
</style>