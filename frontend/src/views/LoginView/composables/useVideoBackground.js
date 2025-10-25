/* 视频背景逻辑组合式函数 */
import { ref } from 'vue'

const cityVideos = [
  '/videos/city1.mp4',
  '/videos/city2.mp4',
  '/videos/city3.mp4',
  '/videos/city4.mp4',
  '/videos/city5.mp4'
]

export function useVideoBackground() {
  const bgVideo = ref(null)
  const currentVideo = ref('')

  const getRandomVideo = () => {
    const randomIndex = Math.floor(Math.random() * cityVideos.length)
    return cityVideos[randomIndex]
  }

  currentVideo.value = getRandomVideo()

  return {
    bgVideo,
    currentVideo,
    getRandomVideo
  }
}