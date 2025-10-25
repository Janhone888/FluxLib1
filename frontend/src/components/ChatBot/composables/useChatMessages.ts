import { ref, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import api from '@/utils/api'

export function useChatMessages() {
  const userStore = useUserStore()

  const messages = ref<any[]>([])
  const loading = ref(false)
  const inputMessage = ref('')
  const hasNewMessage = ref(false)
  const messagesContainer = ref<HTMLElement>()

  // 快捷问题
  const quickQuestions = ref([
    "推荐几本计算机类的书",
    "图书馆的营业时间是什么？",
    "如何借阅图书？",
    "有哪些文学类图书？"
  ])

  // 获取存储键名
  const getStorageKey = () => {
    if (!userStore.userInfo.user_id) {
      return 'ai_chat_history'
    }
    return `ai_chat_history_${userStore.userInfo.user_id}`
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

  // 保存消息
  const saveMessages = () => {
    const storageKey = getStorageKey()
    localStorage.setItem(storageKey, JSON.stringify(messages.value))
  }

  // 格式化时间
  const formatTime = (timestamp: number) => {
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
  const selectQuickQuestion = (question: string) => {
    inputMessage.value = question
    sendMessage()
  }

  return {
    messages,
    loading,
    inputMessage,
    hasNewMessage,
    quickQuestions,
    messagesContainer,
    sendMessage,
    selectQuickQuestion,
    loadMessages,
    saveMessages,
    scrollToBottom
  }
}