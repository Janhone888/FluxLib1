import { defineStore } from 'pinia'
import api from '@/utils/api'

export const useBookStore = defineStore('books', {
  state: () => ({
    books: [],
    currentBook: null,
    loading: false,
    error: null,
    total: 0
  }),

  actions: {
    // 获取图书列表（添加分类参数）
    async fetchBooks(page = 1, pageSize = 10, category = '') {
      this.loading = true
      try {
        // 添加分类参数
        const response = await api.getBooks(page, pageSize, category)

        // 关键修复：确保使用正确的数据结构
        if (response.data && response.data.items) {
          this.books = response.data.items
          this.total = response.data.total
          return response.data
        } else {
          this.error = '返回数据结构错误'
          console.error('无效的响应结构:', response)
          return { items: [], total: 0 }
        }
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    // 获取单本图书详情
    async fetchBook(id) {
      this.loading = true
      try {
        const response = await api.getBook(id)

        // 关键修复：确保使用正确的数据结构
        if (response.data) {
          this.currentBook = response.data
          return response.data
        } else {
          this.error = '返回数据结构错误'
          console.error('无效的响应结构:', response)
          return null
        }
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    // 创建新书
    async createBook(bookData) {
      this.loading = true
      try {
        const response = await api.createBook(bookData)

        // 关键修复：确保使用正确的数据结构
        if (response.data) {
          this.books.push(response.data)
          this.total += 1

          // 触发全局事件
          const event = new CustomEvent('book-added')
          window.dispatchEvent(event)

          return response.data
        } else {
          throw new Error('创建图书失败：无效的响应')
        }
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    // 更新图书信息
    async updateBook(id, bookData) {
      this.loading = true
      try {
        const response = await api.updateBook(id, bookData)

        // 关键修复：确保使用正确的数据结构
        if (response.data) {
          const index = this.books.findIndex(book => book.id === id)
          if (index !== -1) {
            this.books[index] = { ...this.books[index], ...bookData }
          }
          return response.data
        } else {
          throw new Error('更新图书失败：无效的响应')
        }
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    // 删除图书
    async deleteBook(id) {
      this.loading = true
      try {
        const response = await api.deleteBook(id)

        if (response.status === 200) {
          this.books = this.books.filter(book => book.id !== id)
          this.total -= 1
          return true
        } else {
          throw new Error('删除图书失败')
        }
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    // 借阅图书 - 修复：保留封面信息
    async borrowBook(bookId, days = 30) {
      this.loading = true
      try {
        // 调用后端借阅API
        const response = await api.borrowBook(bookId, days)

        if (response.data && response.data.success) {
          // 更新本地库存和状态
          const bookIndex = this.books.findIndex(book => book.book_id === bookId)
          if (bookIndex !== -1) {
            // 保留封面信息
            const cover = this.books[bookIndex].cover
            this.books[bookIndex] = {
              ...this.books[bookIndex],
              stock: this.books[bookIndex].stock - 1,
              status: this.books[bookIndex].stock - 1 === 0 ? 'borrowed' : 'available',
              cover // 保留封面信息
            }
          }

          // 如果当前正在查看这本书，也更新状态
          if (this.currentBook && this.currentBook.book_id === bookId) {
            this.currentBook.stock -= 1
            if (this.currentBook.stock === 0) {
              this.currentBook.status = 'borrowed'
            }
            // 保留封面
            this.currentBook.cover = this.currentBook.cover
          }

          return true
        } else {
          throw new Error('借阅失败：' + (response.data?.error || '未知错误'))
        }
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    // 归还图书 - 修复状态更新问题
    async returnBook(bookId) {
      this.loading = true
      try {
        // 调用后端归还API
        const response = await api.returnBook(bookId)

        if (response.data && response.data.success) {
          // 更新本地库存和状态
          const bookIndex = this.books.findIndex(book => book.book_id === bookId)
          if (bookIndex !== -1) {
            // 增加库存
            this.books[bookIndex].stock += 1

            // 更新状态为"可借阅"
            this.books[bookIndex].status = 'available'
          }

          // 如果当前正在查看这本书，也更新状态
          if (this.currentBook && this.currentBook.book_id === bookId) {
            this.currentBook.stock += 1
            this.currentBook.status = 'available'
          }

          return true
        } else {
          throw new Error('归还失败：' + (response.data?.error || '未知错误'))
        }
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    }
  }
})