// types/bookForm.ts
export interface BookFormData {
  cover: string
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
}

export interface BookFormRules {
  title: Array<{ required: boolean; message: string; trigger: string }>
  author: Array<{ required: boolean; message: string; trigger: string }>
  price: Array<{ required: boolean; message: string; trigger: string }>
  stock: Array<{ required: boolean; message: string; trigger: string }>
  category: Array<{ required: boolean; message: string; trigger: string }>
}

export interface CategoryOption {
  value: string
  label: string
}