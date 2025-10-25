import { ref, onUnmounted } from 'vue'

export function useCountdown(initialCount: number = 60) {
  const countdown = ref(0)
  let countdownTimer: NodeJS.Timeout | null = null

  const startCountdown = () => {
    countdown.value = initialCount
    clearInterval(countdownTimer as NodeJS.Timeout)

    countdownTimer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(countdownTimer as NodeJS.Timeout)
      }
    }, 1000)
  }

  const stopCountdown = () => {
    if (countdownTimer) {
      clearInterval(countdownTimer)
      countdownTimer = null
    }
  }

  onUnmounted(() => {
    stopCountdown()
  })

  return {
    countdown,
    startCountdown,
    stopCountdown
  }
}