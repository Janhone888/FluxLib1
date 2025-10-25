// types/book.ts
export interface Book {
  book_id: string
  title: string
  author: string
  publisher: string
  isbn: string
  price: number
  stock: number
  category: string
  description: string
  summary: string
  status: 'available' | 'borrowed' | 'maintenance'
  cover: string
}

export interface Comment {
  comment_id: string
  user_id: string
  user_display_name: string
  user_avatar_url: string
  content: string
  likes: number
  created_at: string
  replies?: Comment[]
  showReplies?: boolean
  visibleRepliesCount?: number
  hasMoreReplies?: boolean
}

export interface BorrowRecord {
  borrow_id: string
  book_id: string
  borrower: string
  borrow_date: string
  return_date: string
  status: 'borrowed' | 'returned'
  duration: string
}