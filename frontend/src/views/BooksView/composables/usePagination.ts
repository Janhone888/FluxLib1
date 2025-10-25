import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'

export function usePagination(bookStore: any, selectedCategory: any) {
  const currentPage = ref(1)
  const pageSize = ref(12)
  const totalBooks = ref(0)
  const loading = ref(true)

  const paginatedBooks = computed(() => {
    return bookStore.books
  })

  const fetchBooks = async () => {
    try {
      loading.value = true
      const response = await bookStore.fetchBooks(
        currentPage.value,
        pageSize.value,
        selectedCategory.value
      )
      totalBooks.value = response.total
    } catch (error: any) {
      ElMessage.error('获取图书数据失败: ' + error.message)
    } finally {
      loading.value = false
    }
  }

  const handlePageChange = (page: number) => {
    currentPage.value = page
    fetchBooks()
  }

  const handleSizeChange = (size: number) => {
    pageSize.value = size
    currentPage.value = 1
    fetchBooks()
  }

  return {
    currentPage,
    pageSize,
    totalBooks,
    paginatedBooks,
    loading,
    handlePageChange,
    handleSizeChange,
    fetchBooks
  }
}