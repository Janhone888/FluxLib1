import { ref, watch } from 'vue'

export function useChatWindow(messages: any, hasNewMessage: any, scrollToBottom: Function) {
  const isMinimized = ref(true)

  // 切换最小化状态
  const toggleMinimize = () => {
    isMinimized.value = !isMinimized.value
    if (!isMinimized.value) {
      hasNewMessage.value = false
      scrollToBottom()
    }
  }

  // 关闭聊天
  const closeChat = () => {
    isMinimized.value = true
  }

  // 监听消息变化
  watch(messages, (newVal) => {
    if (isMinimized.value && newVal.length > 0) {
      const lastMessage = newVal[newVal.length - 1]
      if (lastMessage.role === 'ai') {
        hasNewMessage.value = true
      }
    }
  }, { deep: true })

  return {
    isMinimized,
    toggleMinimize,
    closeChat
  }
}