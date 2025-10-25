// types/borrow.ts
export interface BorrowRecord {
  borrow_id: string
  book_id: string
  book_title: string
  book_author?: string
  book_cover?: string
  borrower: string
  borrow_date: number
  due_date: number
  return_date?: number
  status: 'borrowed' | 'returned'
  returning?: boolean
}

export interface BatchReturnRequest {
  borrow_ids: string[]
}

export interface BatchReturnResponse {
  success: boolean
  returned_count: number
  error?: string
}