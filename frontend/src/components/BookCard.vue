<!-- src/components/ImageUploader.vue -->
<template>
  <div class="image-uploader">
    <el-upload
      action=""
      :show-file-list="false"
      :http-request="handleUpload"
      :before-upload="beforeUpload"
    >
      <el-image
        v-if="imageUrl"
        :src="imageUrl"
        fit="cover"
        class="book-cover"
      />
      <el-icon v-else class="uploader-icon"><Plus /></el-icon>
    </el-upload>

    <div v-if="uploading" class="upload-progress">
      <el-progress :percentage="progress" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import api from '@/utils/api'

const props = defineProps({
  modelValue: String
})

const emit = defineEmits(['update:modelValue'])

const imageUrl = ref(props.modelValue)
const uploading = ref(false)
const progress = ref(0)

const beforeUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt5M = file.size / 1024 / 1024 < 5

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }

  if (!isLt5M) {
    ElMessage.error('图片大小不能超过5MB!')
    return false
  }

  return true
}

const handleUpload = async ({ file }) => {
  try {
    uploading.value = true
    progress.value = 0

    // 获取预签名URL
    const { data } = await api.getUploadUrl(
      file.name,
      file.type
    )

    // 上传文件到OSS
    await uploadToOSS(file, data.url)

    // 更新图片URL
    const imagePath = `https://${import.meta.env.VITE_OSS_BUCKET}.${
      import.meta.env.VITE_OSS_REGION
    }.aliyuncs.com/book-covers/${file.name}`

    imageUrl.value = imagePath
    emit('update:modelValue', imagePath)

    ElMessage.success('图片上传成功!')
  } catch (error) {
    ElMessage.error('图片上传失败: ' + error.message)
  } finally {
    uploading.value = false
  }
}

const uploadToOSS = (file, presignedUrl) => {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()

    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable) {
        progress.value = Math.round((e.loaded / e.total) * 100)
      }
    })

    xhr.addEventListener('load', () => {
      if (xhr.status === 200) resolve()
      else reject(new Error('上传失败'))
    })

    xhr.addEventListener('error', () => {
      reject(new Error('网络错误'))
    })

    xhr.open('PUT', presignedUrl, true)
    xhr.setRequestHeader('Content-Type', file.type)
    xhr.send(file)
  })
}
</script>

<style scoped>
.image-uploader {
  position: relative;
  width: 150px;
  height: 200px;
  border: 1px dashed #dcdfe6;
  border-radius: 6px;
  cursor: pointer;
  overflow: hidden;
}

.uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 150px;
  height: 200px;
  line-height: 200px;
  text-align: center;
}

.book-cover {
  width: 100%;
  height: 100%;
  display: block;
}

.upload-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.8);
  padding: 5px;
}
</style>