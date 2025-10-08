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

      <el-form
        ref="bookForm"
        :model="bookForm"
        :rules="rules"
        label-width="120px"
        label-position="top"
        v-loading="loading"
      >
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="图书封面" prop="cover">
              <image-uploader v-model="bookForm.cover" class="cover-uploader" />
              <div class="form-tip">支持 JPG/PNG 格式，大小不超过 5MB</div>
            </el-form-item>
          </el-col>

          <el-col :span="16">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="书名" prop="title">
                  <el-input
                    v-model="bookForm.title"
                    placeholder="请输入书名"
                    :clearable="true"
                    show-word-limit
                    maxlength="100"
                    @input="(val) => debugInput('title', val)"
                  />
                </el-form-item>
              </el-col>

              <el-col :span="12">
                <el-form-item label="作者" prop="author">
                  <el-input
                    v-model="bookForm.author"
                    placeholder="请输入作者"
                    :clearable="true"
                    show-word-limit
                    maxlength="50"
                    @input="(val) => debugInput('author', val)"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="出版社" prop="publisher">
                  <el-input
                    v-model="bookForm.publisher"
                    placeholder="请输入出版社"
                    :clearable="true"
                    show-word-limit
                    maxlength="100"
                    @input="(val) => debugInput('publisher', val)"
                  />
                </el-form-item>
              </el-col>

              <el-col :span="12">
                <el-form-item label="ISBN" prop="isbn">
                  <el-input
                    v-model="bookForm.isbn"
                    placeholder="请输入 ISBN"
                    :clearable="true"
                    maxlength="20"
                    @input="(val) => debugInput('isbn', val)"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="价格" prop="price">
                  <el-input-number
                    v-model="bookForm.price"
                    :min="0"
                    :precision="2"
                    placeholder="请输入价格"
                    class="w-full"
                    controls-position="right"
                  />
                </el-form-item>
              </el-col>

              <el-col :span="12">
                <el-form-item label="库存数量" prop="stock">
                  <el-input-number
                    v-model="bookForm.stock"
                    :min="0"
                    placeholder="请输入库存数量"
                    class="w-full"
                    controls-position="right"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="分类" prop="category">
              <el-select
                v-model="bookForm.category"
                placeholder="请选择分类"
                class="w-full"
                :clearable="true"
              >
                <el-option
                  v-for="category in categories"
                  :key="category.value"
                  :label="category.label"
                  :value="category.value"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="状态" prop="status">
              <el-radio-group v-model="bookForm.status">
                <el-radio label="available">可借阅</el-radio>
                <el-radio label="borrowed">已借出</el-radio>
                <el-radio label="maintenance">维护中</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 添加图书概述字段 -->
        <el-form-item label="图书概述" prop="summary">
          <el-input
            v-model="bookForm.summary"
            type="textarea"
            :rows="3"
            placeholder="请输入图书概述"
            resize="none"
            show-word-limit
            maxlength="500"
            :clearable="true"
          />
        </el-form-item>

        <el-form-item label="图书描述" prop="description">
          <el-input
            v-model="bookForm.description"
            type="textarea"
            :rows="4"
            placeholder="请输入图书描述"
            resize="none"
            :clearable="true"
          />
        </el-form-item>

        <el-divider />

        <el-form-item>
          <el-button type="primary" @click="submitForm" :loading="submitting">
            <el-icon><Check /></el-icon>
            <span>保存更改</span>
          </el-button>

          <el-button @click="resetForm">
            <el-icon><Refresh /></el-icon>
            <span>重置</span>
          </el-button>

          <el-button @click="goBack">
            <el-icon><Close /></el-icon>
            <span>取消</span>
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <div class="mt-20">
      <el-card shadow="never">
        <template #header>
          <h3>借阅记录</h3>
        </template>

        <el-table :data="borrowHistory" stripe class="w-full">
          <el-table-column prop="borrower" label="借阅人" width="150" />
          <el-table-column prop="borrowDate" label="借阅日期" width="150" />
          <el-table-column prop="returnDate" label="归还日期" width="150" />
          <el-table-column label="状态" width="120">
            <template #default="{ row }">
              <el-tag :type="row.status === '已归还' ? 'success' : 'danger'">
                {{ row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="notes" label="备注" />
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Check, Refresh, Close } from '@element-plus/icons-vue'
import { useBookStore } from '@/stores/books'
import ImageUploader from '@/components/ImageUploader.vue'

const route = useRoute()
const router = useRouter()
const bookStore = useBookStore()

// 使用 reactive 创建响应式表单对象
const bookForm = reactive({
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

const categories = ref([
  { value: 'computer', label: '计算机' },
  { value: 'literature', label: '文学' },
  { value: 'economy', label: '经济' },
  { value: 'history', label: '历史' },
  { value: 'science', label: '自然科学' },
  { value: 'art', label: '艺术' },
  { value: 'management', label: '管理' },
  { value: 'education', label: '教育' }
])

const rules = ref({
  title: [
    { required: true, message: '请输入书名', trigger: 'blur' },
    { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' }
  ],
  author: [
    { required: true, message: '请输入作者', trigger: 'blur' }
  ],
  price: [
    { required: true, message: '请输入价格', trigger: 'blur' },
    { type: 'number', min: 0, message: '价格必须大于0', trigger: 'blur' }
  ],
  stock: [
    { required: true, message: '请输入库存数量', trigger: 'blur' },
    { type: 'number', min: 0, message: '库存不能为负数', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择分类', trigger: 'change' }
  ]
})

const loading = ref(true)
const submitting = ref(false)

// 获取图书ID
const bookId = computed(() => route.params.id)

// 借阅历史数据
const borrowHistory = ref([])

onMounted(async () => {
  if (bookId.value) {
    await fetchBookDetail()
  } else {
    ElMessage.warning('无效的图书ID')
    goBack()
  }
})

const fetchBookDetail = async () => {
  try {
    loading.value = true
    await bookStore.fetchBook(bookId.value)

    // 确保正确填充表单数据
    if (bookStore.currentBook) {
      // 逐个字段赋值，确保响应式更新
      bookForm.cover = bookStore.currentBook.cover || ''
      bookForm.title = bookStore.currentBook.title || ''
      bookForm.author = bookStore.currentBook.author || ''
      bookForm.publisher = bookStore.currentBook.publisher || ''
      bookForm.isbn = bookStore.currentBook.isbn || ''
      bookForm.price = bookStore.currentBook.price || 0
      bookForm.stock = bookStore.currentBook.stock || 1
      bookForm.category = bookStore.currentBook.category || ''
      bookForm.description = bookStore.currentBook.description || ''
      bookForm.status = bookStore.currentBook.status || 'available'
      bookForm.summary = bookStore.currentBook.summary || ''

      console.log("加载的图书数据:", bookForm)
    } else {
      ElMessage.warning('未找到该图书信息')
      goBack()
    }
  } catch (error) {
    ElMessage.error(`获取图书信息失败: ${error.message}`)
  } finally {
    loading.value = false
  }
}

const submitForm = async () => {
  try {
    submitting.value = true

    // 数据验证
    if (!bookForm.title || !bookForm.author) {
      ElMessage.warning('请填写必填字段')
      return
    }

    // 创建更新数据对象
    const updateData = {
      cover: bookForm.cover,
      title: bookForm.title,
      author: bookForm.author,
      publisher: bookForm.publisher,
      isbn: bookForm.isbn,
      price: Number(bookForm.price),
      stock: Number(bookForm.stock),
      category: bookForm.category,
      description: bookForm.description,
      summary: bookForm.summary,
      status: bookForm.status
    }

    console.log("提交的更新数据:", JSON.stringify(updateData, null, 2))

    // 更新图书
    await bookStore.updateBook(bookId.value, updateData)

    ElMessage.success({
      message: '图书信息更新成功',
      duration: 2000,
      showClose: true
    })

    // 延迟返回列表页
    setTimeout(() => {
      router.push('/books')
    }, 1500)

  } catch (error) {
    ElMessage.error(`更新失败: ${error.message}`)
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  ElMessageBox.confirm('确定要重置所有更改吗？', '重置确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    // 重新获取原始数据
    await fetchBookDetail()
    ElMessage.info('表单已重置')
  }).catch(() => {})
}

const goBack = () => {
  router.push('/books')
}

// 调试函数
const debugInput = (field, value) => {
  console.log(`输入字段 ${field}:`, value)
  console.log(`bookForm.${field}:`, bookForm[field])
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

.cover-uploader {
  width: 200px;
  height: 280px;
  border: 1px dashed #dcdfe6;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  overflow: hidden;
}

.cover-uploader:hover {
  border-color: #409EFF;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

.w-full {
  width: 100%;
}

.mt-20 {
  margin-top: 20px;
}

.el-form-item {
  margin-bottom: 20px;
}

.el-input, .el-select, .el-input-number {
  width: 100%;
}
</style>
