<template>
  <div class="add-book">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <h2>添加新书</h2>
        </div>
      </template>

      <BookForm
        ref="bookFormRef"
        :form-data="formData"
        :submitting="submitting"
        @submit="handleSubmit"
        @reset="handleReset"
        @cancel="handleCancel"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useBookStore } from '@/stores/books'

import BookForm from './components/BookForm.vue'
import { useBookSubmit } from './composables/useBookSubmit'

const router = useRouter()
const bookStore = useBookStore()

// 表单引用
const bookFormRef = ref()

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
  summary: '',
  status: 'available'
})

// 使用组合式函数
const { submitting, handleSubmit: submitBook } = useBookSubmit(bookStore, router)

// 处理表单提交
const handleSubmit = async (formData: any) => {
  await submitBook(formData, 'create')
}

// 处理表单重置
const handleReset = () => {
  Object.assign(formData, {
    cover: '',
    title: '',
    author: '',
    publisher: '',
    isbn: '',
    price: 0,
    stock: 1,
    category: '',
    description: '',
    summary: '',
    status: 'available'
  })
}

// 处理取消操作
const handleCancel = () => {
  router.push('/books')
}
</script>

<style scoped>
.add-book {
  padding: 20px;
}

.box-card {
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .add-book {
    padding: 16px;
  }
}
</style>