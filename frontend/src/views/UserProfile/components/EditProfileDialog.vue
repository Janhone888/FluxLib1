<template>
  <el-dialog
    v-model="showDialog"
    title="编辑个人资料"
    width="500px"
    :close-on-click-modal="false"
    class="edit-dialog"
  >
    <el-form
      ref="editFormRef"
      :model="editForm"
      :rules="editRules"
      label-width="80px"
      class="edit-form"
    >
      <el-form-item label="显示名称" prop="display_name">
        <el-input
          v-model="editForm.display_name"
          placeholder="请输入显示名称"
          maxlength="20"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="性别" prop="gender">
        <el-select
          v-model="editForm.gender"
          placeholder="请选择性别"
          style="width: 100%"
        >
          <el-option label="男" value="male" />
          <el-option label="女" value="female" />
          <el-option label="其他" value="other" />
          <el-option label="不公开" value="" />
        </el-select>
      </el-form-item>

      <el-form-item label="个性签名" prop="summary">
        <el-input
          v-model="editForm.summary"
          type="textarea"
          :rows="3"
          placeholder="请输入个性签名"
          maxlength="50"
          show-word-limit
          resize="none"
        />
      </el-form-item>

      <!-- 头像预览 -->
      <el-form-item label="头像">
        <div class="preview-section">
          <el-image
            :src="editForm.avatar_url || user.avatar_url"
            fit="cover"
            class="preview-avatar"
          >
            <template #error>
              <div class="preview-error">
                <el-icon><User /></el-icon>
              </div>
            </template>
          </el-image>
          <el-button
            type="text"
            @click="$emit('change-avatar')"
            class="change-btn"
          >
            <el-icon><Camera /></el-icon>
            更换头像
          </el-button>
        </div>
      </el-form-item>

      <!-- 封面预览 -->
      <el-form-item label="封面">
        <div class="preview-section">
          <el-image
            :src="editForm.background_url || user.background_url || defaultCover"
            fit="cover"
            class="preview-cover"
          >
            <template #error>
              <div class="preview-error">
                <el-icon><Picture /></el-icon>
              </div>
            </template>
          </el-image>
          <el-button
            type="text"
            @click="$emit('change-cover')"
            class="change-btn"
          >
            <el-icon><Picture /></el-icon>
            更换封面
          </el-button>
        </div>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="showDialog = false">取消</el-button>
      <el-button
        type="primary"
        @click="handleSave"
        :loading="updating"
      >
        {{ updating ? '保存中...' : '保存' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { User, Camera, Picture } from '@element-plus/icons-vue'
import type { UserProfile } from '../composables/useUserProfile'

interface Props {
  modelValue: boolean
  user: UserProfile
  updating: boolean
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'save', data: any): void
  (e: 'change-avatar'): void
  (e: 'change-cover'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const showDialog = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const editFormRef = ref<FormInstance>()
const editForm = ref({
  display_name: '',
  gender: '',
  summary: '',
  avatar_url: '',
  background_url: ''
})

const editRules: FormRules = reactive({
  display_name: [
    { required: true, message: '请输入显示名称', trigger: 'blur' },
    { min: 1, max: 20, message: '显示名称长度需在1-20个字符之间', trigger: 'blur' }
  ]
})

const defaultCover = 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2340&q=80'

watch(() => props.user, (newUser) => {
  if (newUser) {
    editForm.value = {
      display_name: newUser.display_name || '',
      gender: newUser.gender || '',
      summary: newUser.summary || '',
      avatar_url: newUser.avatar_url || '',
      background_url: newUser.background_url || ''
    }
  }
}, { immediate: true })

const handleSave = async () => {
  if (!editFormRef.value) return

  try {
    await editFormRef.value.validate()

    const updateData = {
      display_name: editForm.value.display_name.trim(),
      gender: editForm.value.gender,
      summary: editForm.value.summary,
      avatar_url: editForm.value.avatar_url || props.user.avatar_url,
      background_url: editForm.value.background_url || props.user.background_url
    }

    emit('save', updateData)
  } catch (error) {
    if (error instanceof Error) {
      ElMessage.error(`资料更新失败：${error.message}`)
    }
  }
}
</script>

<style scoped>
.edit-dialog {
  border-radius: 12px;
}

.edit-form {
  margin-top: 20px;
}

.preview-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.preview-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  border: 2px solid #f0f0f0;
}

.preview-cover {
  width: 120px;
  height: 80px;
  border-radius: 8px;
  border: 2px solid #f0f0f0;
}

.preview-error {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  color: #c0c4cc;
}

.change-btn {
  color: #1890ff;
}
</style>