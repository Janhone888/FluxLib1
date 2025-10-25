<template>
  <div class="edit-book">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <h2>编辑图书信息</h2>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/books' }">图书管理</el-breadcrumb-item>
            <el-breadcrumb-item>编辑图书</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
      </template>

      <BookForm
        ref="bookFormRef"
        :form-data="formData"
        :loading="loading"
        :submitting="submitting"
        :is-edit="true"
        :show-status-field="true"
        @submit="handleSubmit"
        @reset="handleReset"
        @cancel="handleCancel"
      />
    </el-card>

    <!-- 借阅历史区域 -->
    <BorrowHistorySection v-if="bookId" :book-id="bookId" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useBookStore } from '@/stores/books'

import BookForm from './components/BookForm.vue'
import BorrowHistorySection from './components/BorrowHistorySection.vue'
import { useBookForm } from './composables/useBookForm'
import { useBookSubmit } from './composables/useBookSubmit'

const route = useRoute()
const router = useRouter()
const bookStore = useBookStore()

// 获取图书ID
const bookId = computed(() => route.params.id as string)

// 表单引用
const bookFormRef = ref()

// 使用组合式函数
const { formData, loading, fetchBookDetail } = useBookForm(bookId, bookStore, router)
const { submitting, handleSubmit: submitBook } = useBookSubmit(bookStore, router)

// 页面挂载时加载数据
onMounted(() => {
  if (bookId.value) {
    fetchBookDetail()
  } else {
    ElMessage.warning('无效的图书ID')
    handleCancel()
  }
})

// 处理表单提交
const handleSubmit = async (formData: any) => {
  await submitBook(formData, 'update', bookId.value)
}

// 处理表单重置
const handleReset = async () => {
  try {
    await ElMessageBox.confirm('确定要重置所有更改吗？', '重置确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    // 重新获取原始数据
    await fetchBookDetail()
    ElMessage.info('表单已重置')
  } catch (error) {
    // 用户取消操作
  }
}

// 处理取消操作
const handleCancel = () => {
  router.push('/books')
}
</script>

<style scoped>
.edit-book {
  padding: 20px;
}

.box-card {
  max-width: 1200px;
  margin: 0 auto;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .edit-book {
    padding: 16px;
  }
}
</style>