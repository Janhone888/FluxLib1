<template>
<div class="add-book">
  <el-card class="box-card">
    <template #header>
      <div class="card-header">
        <h2>添加新书</h2>
      </div>
    </template>

    <el-form
      ref="bookForm"
      :model="bookForm"
      :rules="rules"
      label-width="120px"
      label-position="top"
    >
      <!-- 封面图片上传 -->
      <el-form-item label="图书封面" prop="cover">
        <!-- 修复：添加固定尺寸容器 -->
        <div style="width:150px; height:200px">
          <image-uploader v-model="bookForm.cover" />
        </div>
        <div class="form-tip">支持JPG/PNG格式，大小不超过5MB</div>
      </el-form-item>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="书名" prop="title">
            <el-input v-model="bookForm.title" placeholder="请输入书名" />
          </el-form-item>
        </el-col>

        <el-col :span="12">
          <el-form-item label="作者" prop="author">
            <el-input v-model="bookForm.author" placeholder="请输入作者" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="出版社" prop="publisher">
            <el-input v-model="bookForm.publisher" placeholder="请输入出版社" />
          </el-form-item>
        </el-col>

        <el-col :span="12">
          <el-form-item label="ISBN" prop="isbn">
            <el-input v-model="bookForm.isbn" placeholder="请输入ISBN" />
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
            />
          </el-form-item>
        </el-col>

        <el-col :span="12">
          <el-form-item label="库存数量" prop="stock">
            <el-input-number
              v-model="bookForm.stock"
              :min="1"
              placeholder="请输入库存数量"
              class="w-full"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="分类" prop="category">
        <el-select v-model="bookForm.category" placeholder="请选择分类" style="width: 100%">
          <el-option
            v-for="category in categories"
            :key="category.value"
            :label="category.label"
            :value="category.value"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="描述" prop="description">
        <el-input
          v-model="bookForm.description"
          type="textarea"
          :rows="4"
          placeholder="请输入图书描述"
        />
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="submitForm" :loading="submitting">提交</el-button>
        <el-button @click="resetForm">重置</el-button>
        <el-button @click="goBack">取消</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useBookStore } from '@/stores/books'
import ImageUploader from '@/components/ImageUploader.vue'

const router = useRouter()
const bookStore = useBookStore()

const bookForm = ref({
  cover: '',
  title: '',
  author: '',
  publisher: '',
  isbn: '',
  price: 0,
  stock: 1,
  category: '',
  description: '',
  status: 'available'
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
    { type: 'number', min: 1, message: '库存至少为1', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择分类', trigger: 'change' }
  ]
})

const submitting = ref(false)

const submitForm = async () => {
  try {
    submitting.value = true

    // 确保封面URL是字符串
    if (typeof bookForm.value.cover !== 'string') {
      bookForm.value.cover = ''
    }

    // 创建纯数据对象
    const bookData = {
      cover: bookForm.value.cover,
      title: bookForm.value.title,
      author: bookForm.value.author,
      publisher: bookForm.value.publisher,
      isbn: bookForm.value.isbn,
      price: Number(bookForm.value.price),
      stock: Number(bookForm.value.stock),
      category: bookForm.value.category,
      description: bookForm.value.description,
      status: 'available'
    }

    console.log("提交的图书数据:", JSON.stringify(bookData, null, 2))

    await bookStore.createBook(bookData)

    // 添加成功后触发全局事件
    const event = new CustomEvent('book-added')
    window.dispatchEvent(event)

    ElMessage.success('图书添加成功')
    router.push('/books')
  } catch (error) {
    ElMessage.error(`添加失败: ${error.message}`)
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  bookForm.value = {
    cover: '',
    title: '',
    author: '',
    publisher: '',
    isbn: '',
    price: 0,
    stock: 1,
    category: '',
    description: '',
    status: 'available'
  }
}

const goBack = () => {
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

.form-tip {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

.w-full {
  width: 100%;
}
</style>