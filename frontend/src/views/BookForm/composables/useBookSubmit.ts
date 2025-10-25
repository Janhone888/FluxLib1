import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useBookStore } from '@/stores/books'

export function useBookSubmit(bookStore: any, router: any) {
  const submitting = ref(false)

  const handleSubmit = async (formData: any, action: 'create' | 'update', bookId?: string) => {
    try {
      submitting.value = true

      // 数据验证
      if (!formData.title || !formData.author) {
        ElMessage.warning('请填写必填字段')
        return
      }

      // 创建提交数据对象
      const submitData = {
        cover: formData.cover,
        title: formData.title,
        author: formData.author,
        publisher: formData.publisher,
        isbn: formData.isbn,
        price: Number(formData.price),
        stock: Number(formData.stock),
        category: formData.category,
        description: formData.description,
        summary: formData.summary,
        status: formData.status || 'available'
      }

      console.log("提交的图书数据:", JSON.stringify(submitData, null, 2))

      let result
      if (action === 'create') {
        result = await bookStore.createBook(submitData)

        // 添加成功后触发全局事件
        const event = new CustomEvent('book-added')
        window.dispatchEvent(event)

        ElMessage.success('图书添加成功')
      } else if (action === 'update' && bookId) {
        result = await bookStore.updateBook(bookId, submitData)
        ElMessage.success('图书信息更新成功')
      }

      // 延迟返回列表页
      setTimeout(() => {
        router.push('/books')
      }, 1500)

      return result
    } catch (error: any) {
      ElMessage.error(`${action === 'create' ? '添加' : '更新'}失败: ${error.message}`)
      throw error
    } finally {
      submitting.value = false
    }
  }

  return {
    submitting,
    handleSubmit
  }
}