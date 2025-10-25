// types/books.ts
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

export interface Category {
  value: string
  label: string
}

export interface Pagination {
  currentPage: number
  pageSize: number
  total: number
}