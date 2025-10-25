/* 背景视频组件 */
<template>
  <div>
    <video ref="bgVideo" class="bg-video" autoplay muted loop>
      <source :src="currentVideo" type="video/mp4">
    </video>
    <div class="video-overlay"></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useVideoBackground } from '../composables/useVideoBackground'

const { currentVideo, bgVideo } = useVideoBackground()

onMounted(() => {
  if (bgVideo.value) {
    bgVideo.value.play().catch(e => {
      console.log('视频自动播放被阻止:', e)
    })
  }
})
</script>

<style scoped>
.bg-video {
  position: absolute;
  top: 50%;
  left: 50%;
  min-width: 100%;
  min-height: 100%;
  width: auto;
  height: auto;
  transform: translateX(-50%) translateY(-50%);
  object-fit: cover;
  z-index: 0;
}

.video-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  z-index: 1;
}
</style>