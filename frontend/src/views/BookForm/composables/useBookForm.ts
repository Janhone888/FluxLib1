import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useBookStore } from '@/stores/books'

export function useBookForm(bookId: any, bookStore: any, router: any) {
  const loading = ref(false)

  // 表单数据
  const formData = reactive({
    cover: '',
    title: '',
    author: '',
    publisher: '',
    isbn: '',
    price: 0,
    stock: 1,
    category: '',
    description: '',
    status: 'available',
    summary: ''
  })

  const fetchBookDetail = async () => {
    try {
      loading.value = true
      await bookStore.fetchBook(bookId.value)

      // 确保正确填充表单数据
      if (bookStore.currentBook) {
        // 逐个字段赋值，确保响应式更新
        Object.assign(formData, {
          cover: bookStore.currentBook.cover || '',
          title: bookStore.currentBook.title || '',
          author: bookStore.currentBook.author || '',
          publisher: bookStore.currentBook.publisher || '',
          isbn: bookStore.currentBook.isbn || '',
          price: bookStore.currentBook.price || 0,
          stock: bookStore.currentBook.stock || 1,
          category: bookStore.currentBook.category || '',
          description: bookStore.currentBook.description || '',
          status: bookStore.currentBook.status || 'available',
          summary: bookStore.currentBook.summary || ''
        })

        console.log("加载的图书数据:", formData)
      } else {
        ElMessage.warning('未找到该图书信息')
        router.push('/books')
      }
    } catch (error: any) {
      ElMessage.error(`获取图书信息失败: ${error.message}`)
    } finally {
      loading.value = false
    }
  }

  return {
    formData,
    loading,
    fetchBookDetail
  }
}