import { ref } from 'vue'

export function useResize(windowSize: any) {
  const isResizing = ref(false)

  let resizeStartX = 0
  let resizeStartY = 0
  let startWidth = 0
  let startHeight = 0

  const startResize = (e: MouseEvent) => {
    e.preventDefault()
    isResizing.value = true
    resizeStartX = e.clientX
    resizeStartY = e.clientY
    startWidth = windowSize.value.width
    startHeight = windowSize.value.height

    document.addEventListener('mousemove', onResize)
    document.addEventListener('mouseup', stopResize)
  }

  const onResize = (e: MouseEvent) => {
    if (!isResizing.value) return

    const newWidth = Math.max(300, Math.min(800, startWidth + (e.clientX - resizeStartX)))
    const newHeight = Math.max(400, Math.min(800, startHeight + (e.clientY - resizeStartY)))

    windowSize.value = { width: newWidth, height: newHeight }
  }

  const stopResize = () => {
    isResizing.value = false
    document.removeEventListener('mousemove', onResize)
    document.removeEventListener('mouseup', stopResize)
  }

  return {
    isResizing,
    startResize,
    stopResize,
    onResize
  }
}