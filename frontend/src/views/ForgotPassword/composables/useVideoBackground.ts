import { ref, onMounted } from 'vue'

export function useVideoBackground() {
  const cityVideos = [
    '/videos/city1.mp4',
    '/videos/city2.mp4',
    '/videos/city3.mp4',
    '/videos/city4.mp4',
    '/videos/city5.mp4'
  ]

  const currentVideo = ref('')

  const getRandomVideo = (): string => {
    const randomIndex = Math.floor(Math.random() * cityVideos.length)
    return cityVideos[randomIndex]
  }

  const initializeVideo = (bgVideo: HTMLVideoElement | null) => {
    currentVideo.value = getRandomVideo()

    if (bgVideo) {
      bgVideo.play().catch(e => {
        console.log('视频自动播放被阻止:', e)
      })
    }
  }

  return {
    currentVideo,
    initializeVideo
  }
}