import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'

export function useSearch(bookStore: any) {
  const searchQuery = ref('')
  const selectedCategory = ref('')
  const filteredBooks = ref<any[]>([])

  const handleSearch = () => {
    if (!searchQuery.value) {
      filteredBooks.value = [...bookStore.books]
      return
    }

    const query = searchQuery.value.toLowerCase()
    filteredBooks.value = bookStore.books.filter((book: any) =>
      book.title.toLowerCase().includes(query) ||
      book.author.toLowerCase().includes(query) ||
      book.publisher.toLowerCase().includes(query)
    )
  }

  const handleFilter = () => {
    if (!selectedCategory.value) {
      filteredBooks.value = [...bookStore.books]
      return
    }

    filteredBooks.value = bookStore.books.filter((book: any) =>
      book.category === selectedCategory.value
    )
  }

  // 监听图书库变化
  watch(
    () => bookStore.books,
    (newBooks) => {
      filteredBooks.value = [...newBooks]
      // 重新应用当前的搜索和筛选
      if (searchQuery.value) {
        handleSearch()
      } else if (selectedCategory.value) {
        handleFilter()
      }
    },
    { deep: true }
  )

  return {
    searchQuery,
    selectedCategory,
    filteredBooks,
    handleSearch,
    handleFilter
  }
}