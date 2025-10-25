import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useBookStore } from '@/stores/books'
import { useUserStore } from '@/stores/user'
import api from '@/utils/api'

export function useBookDetail(bookId: any, userStore: any, bookStore: any, router: any) {
  const book = ref({})
  const loading = ref(false)
  const isFavorited = ref(false)
  const hasBorrowed = ref(false)
  const borrowRecords = ref([])

  const fetchBookDetail = async () => {
    if (!bookId.value) return
    try {
      loading.value = true
      await bookStore.fetchBook(bookId.value)
      if (bookStore.currentBook) {
        book.value = bookStore.currentBook
      } else {
        ElMessage.error('未查询到该图书信息')
        router.push('/books')
      }
    } catch (error: any) {
      ElMessage.error(`获取详情失败：${error.message}`)
      router.push('/books')
    } finally {
      loading.value = false
    }
  }

  const toggleFavorite = async () => {
    try {
      if (isFavorited.value) {
        await api.delete(`/favorites/${bookId.value}`)
        isFavorited.value = false
        ElMessage.success('已取消收藏')
      } else {
        await api.post('/favorites', { book_id: bookId.value })
        isFavorited.value = true
        ElMessage.success('收藏成功')
      }
    } catch (error) {
      ElMessage.error('操作失败')
    }
  }

  const editBook = () => {
    router.push(`/books/edit/${bookId.value}`)
  }

  const deleteBook = async () => {
    try {
      await ElMessageBox.confirm('确定要删除这本图书吗？', '删除确认', {
        type: 'warning'
      })
      await bookStore.deleteBook(bookId.value)
      ElMessage.success('删除成功')
      router.push('/books')
    } catch (error: any) {
      if (error !== 'cancel') {
        ElMessage.error('删除失败')
      }
    }
  }

  const goBack = () => {
    router.back()
  }

  return {
    book,
    loading,
    isFavorited,
    hasBorrowed,
    borrowRecords,
    fetchBookDetail,
    toggleFavorite,
    editBook,
    deleteBook,
    goBack
  }
}