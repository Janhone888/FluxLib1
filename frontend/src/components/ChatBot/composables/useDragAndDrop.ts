import { ref } from 'vue'

export function useDragAndDrop() {
  const windowPosition = ref({ x: 100, y: 100 })
  const windowSize = ref({ width: 400, height: 600 })
  const isDragging = ref(false)

  let dragStartX = 0
  let dragStartY = 0

  const startDrag = (e: MouseEvent) => {
    isDragging.value = true
    dragStartX = e.clientX - windowPosition.value.x
    dragStartY = e.clientY - windowPosition.value.y

    document.addEventListener('mousemove', onDrag)
    document.addEventListener('mouseup', stopDrag)
  }

  const onDrag = (e: MouseEvent) => {
    if (!isDragging.value) return

    // 限制在窗口范围内
    const newX = Math.max(0, Math.min(
      window.innerWidth - windowSize.value.width,
      e.clientX - dragStartX
    ))
    const newY = Math.max(0, Math.min(
      window.innerHeight - windowSize.value.height,
      e.clientY - dragStartY
    ))

    windowPosition.value = { x: newX, y: newY }
  }

  const stopDrag = () => {
    isDragging.value = false
    document.removeEventListener('mousemove', onDrag)
    document.removeEventListener('mouseup', stopDrag)
  }

  return {
    windowPosition,
    windowSize,
    isDragging,
    startDrag,
    stopDrag,
    onDrag
  }
}