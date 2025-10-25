/* 倒计时逻辑组合式函数 */
import { ref } from 'vue'

export function useCountdown() {
  const countdown = ref(0)
  let countdownTimer = null

  const startCountdown = (seconds = 60) => {
    countdown.value = seconds
    clearInterval(countdownTimer)

    countdownTimer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(countdownTimer)
      }
    }, 1000)
  }

  const stopCountdown = () => {
    clearInterval(countdownTimer)
    countdown.value = 0
  }

  return {
    countdown,
    startCountdown,
    stopCountdown
  }
}