// types/chat.ts
export interface ChatMessage {
  role: 'user' | 'ai'
  content: string
  timestamp: number
}

export interface WindowPosition {
  x: number
  y: number
}

export interface WindowSize {
  width: number
  height: number
}

export interface DragState {
  isDragging: boolean
  startX: number
  startY: number
}

export interface ResizeState {
  isResizing: boolean
  startX: number
  startY: number
  startWidth: number
  startHeight: number
}