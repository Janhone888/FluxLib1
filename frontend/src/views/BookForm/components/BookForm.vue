<template>
  <el-form
    ref="formRef"
    :model="form"
    :rules="rules"
    label-width="120px"
    label-position="top"
    v-loading="loading"
  >
    <el-row :gutter="20">
      <el-col :span="8">
        <el-form-item label="图书封面" prop="cover">
          <BookCoverUpload v-model="form.cover" />
          <div class="form-tip">支持 JPG/PNG 格式，大小不超过 5MB</div>
        </el-form-item>
      </el-col>

      <el-col :span="16">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="书名" prop="title">
              <el-input
                v-model="form.title"
                placeholder="请输入书名"
                :clearable="true"
                show-word-limit
                maxlength="100"
              />
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item label="作者" prop="author">
              <el-input
                v-model="form.author"
                placeholder="请输入作者"
                :clearable="true"
                show-word-limit
                maxlength="50"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="出版社" prop="publisher">
              <el-input
                v-model="form.publisher"
                placeholder="请输入出版社"
                :clearable="true"
                show-word-limit
                maxlength="100"
              />
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item label="ISBN" prop="isbn">
              <el-input
                v-model="form.isbn"
                placeholder="请输入 ISBN"
                :clearable="true"
                maxlength="20"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="价格" prop="price">
              <el-input-number
                v-model="form.price"
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
                v-model="form.stock"
                :min="1"
                placeholder="请输入库存数量"
                class="w-full"
                controls-position="right"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="分类" prop="category">
          <el-select
            v-model="form.category"
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

        <el-form-item label="状态" prop="status" v-if="showStatusField">
          <el-radio-group v-model="form.status">
            <el-radio label="available">可借阅</el-radio>
            <el-radio label="borrowed">已借出</el-radio>
            <el-radio label="maintenance">维护中</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-col>
    </el-row>

    <!-- 图书概述 -->
    <el-form-item label="图书概述" prop="summary">
      <el-input
        v-model="form.summary"
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
        v-model="form.description"
        type="textarea"
        :rows="4"
        placeholder="请输入图书描述"
        resize="none"
        :clearable="true"
      />
    </el-form-item>

    <!-- 表单操作 -->
    <FormActions
      :is-edit="isEdit"
      :submitting="submitting"
      @submit="handleSubmit"
      @reset="handleReset"
      @cancel="handleCancel"
    />
  </el-form>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import BookCoverUpload from './BookCoverUpload.vue'
import FormActions from './FormActions.vue'

interface Props {
  formData: any
  loading?: boolean
  submitting?: boolean
  isEdit?: boolean
  showStatusField?: boolean
}

interface Emits {
  (e: 'update:formData', value: any): void
  (e: 'submit', value: any): void
  (e: 'reset'): void
  (e: 'cancel'): void
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  submitting: false,
  isEdit: false,
  showStatusField: false
})

const emit = defineEmits<Emits>()

// 表单引用
const formRef = ref()

// 表单数据
const form = ref({ ...props.formData })

// 监听props变化更新表单数据
watch(
  () => props.formData,
  (newData) => {
    form.value = { ...newData }
  },
  { deep: true }
)

// 监听表单变化触发更新
watch(
  form,
  (newForm) => {
    emit('update:formData', newForm)
  },
  { deep: true }
)

// 表单验证规则
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

// 分类选项
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

// 表单提交
const handleSubmit = async () => {
  try {
    const valid = await formRef.value.validate()
    if (valid) {
      emit('submit', form.value)
    }
  } catch (error) {
    console.error('表单验证失败:', error)
  }
}

// 表单重置
const handleReset = () => {
  emit('reset')
}

// 取消操作
const handleCancel = () => {
  emit('cancel')
}

// 暴露方法给父组件
defineExpose({
  validate: () => formRef.value?.validate(),
  resetFields: () => formRef.value?.resetFields()
})
</script>

<style scoped>
.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

.w-full {
  width: 100%;
}

.el-form-item {
  margin-bottom: 20px;
}

.el-input,
.el-select,
.el-input-number {
  width: 100%;
}
</style>