<template>
<div class="image-uploader">
<el-upload
action=""
:show-file-list="false"
:http-request="handleUpload"
:before-upload="beforeUpload"
:disabled="uploading"
>
<template v-if="imageUrl">
<el-image
:src="imageUrl"
fit="cover"
class="uploaded-image"
:preview-src-list="[imageUrl]"
>
<template #error>
<div class="image-error">
<el-icon><Picture /></el-icon>
<span>图片加载失败</span>
</div>
</template>
</el-image>
</template>

<div v-else class="uploader-placeholder">
<el-icon class="uploader-icon"><Plus /></el-icon>
<div class="uploader-text">上传图书封面</div>
<div class="uploader-tip">建议尺寸：300×400px</div>
</div>
</el-upload>

<div v-if="uploading" class="upload-progress">
<el-progress
:percentage="progress"
:status="uploadStatus"
:stroke-width="12"
/>
<div class="progress-text">{{ progress }}%</div>
<el-button
v-if="progress < 100"
size="small"
@click="cancelUpload"
class="cancel-btn"
>
取消上传
</el-button>
</div>
</div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Plus, Picture } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'

const props = defineProps({
modelValue: String
})

const emit = defineEmits(['update:modelValue'])

const imageUrl = ref(props.modelValue)
const uploading = ref(false)
const progress = ref(0)
const uploadAbortController = ref(null)
const xhr = ref(null)

const uploadStatus = computed(() => {
if (progress.value === 100) return 'success'
if (progress.value < 0) return 'exception'
return ''
})

const beforeUpload = (file) => {
const validTypes = ['image/jpeg', 'image/png', 'image/webp']
const isImage = validTypes.includes(file.type)
const isLt5M = file.size / 1024 / 1024 < 5

if (!isImage) {
ElMessage.error('请上传 JPG/PNG/WEBP 格式的图片')
return false
}

if (!isLt5M) {
ElMessage.error('图片大小不能超过 5MB')
return false
}

return true
}

const handleUpload = async ({ file }) => {
try {
uploading.value = true
progress.value = 0
uploadAbortController.value = new AbortController()

// 1. 获取预签名URL
const { data } = await api.getUploadUrl(
file.name,
file.type
)

// 2. 上传到OSS
await uploadToOSS(file, data.presigned_url)

// 3. 使用后端返回的access_url
const newImageUrl = data.access_url
imageUrl.value = newImageUrl
emit('update:modelValue', newImageUrl)

ElMessage.success('图片上传成功')
} catch (error) {
if (error.name !== 'AbortError') {
ElMessage.error(`图片上传失败: ${error.message}`)
}
} finally {
uploading.value = false
uploadAbortController.value = null
}
}

const uploadToOSS = (file, presignedUrl) => {
return new Promise((resolve, reject) => {
const xhr = new XMLHttpRequest()
xhr.value = xhr

xhr.upload.addEventListener('progress', (e) => {
if (e.lengthComputable) {
progress.value = Math.round((e.loaded / e.total) * 100)
}
})

xhr.addEventListener('load', () => {
if (xhr.status >= 200 && xhr.status < 300) {
resolve()
} else {
progress.value = -1
reject(new Error(`上传失败 (${xhr.status}: ${xhr.statusText})`))
}
})

xhr.addEventListener('error', () => {
progress.value = -1
reject(new Error('网络错误，请检查连接'))
})

xhr.addEventListener('abort', () => {
progress.value = -1
reject(new DOMException('上传已取消', 'AbortError'))
})

xhr.open('PUT', presignedUrl, true)
xhr.setRequestHeader('Content-Type', file.type)

if (uploadAbortController.value) {
uploadAbortController.value.signal.addEventListener('abort', () => {
xhr.abort()
})
}

xhr.send(file)
})
}

const cancelUpload = () => {
if (uploadAbortController.value) {
uploadAbortController.value.abort()
}
if (xhr.value) {
xhr.value.abort()
}
}
</script>

<style scoped>
.image-uploader {
position: relative;
width: 100%;
height: 280px;
border-radius: 6px;
overflow: hidden;
box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
border: 1px dashed #dcdfe6;
}

.uploaded-image {
width: 100%;
height: 100%;
display: block;
}

.uploader-placeholder {
display: flex;
flex-direction: column;
align-items: center;
justify-content: center;
width: 100%;
height: 100%;
background-color: #f5f7fa;
cursor: pointer;
transition: border-color 0.3s;
color: #606266;
}

.uploader-placeholder:hover {
border-color: #409EFF;
background-color: #ecf5ff;
}

.uploader-icon {
font-size: 60px;
color: #c0c4cc;
margin-bottom: 10px;
}

.uploader-text {
font-size: 16px;
font-weight: 500;
margin-bottom: 5px;
}

.uploader-tip {
font-size: 12px;
color: #909399;
}

.upload-progress {
position: absolute;
bottom: 0;
left: 0;
right: 0;
background: rgba(255, 255, 255, 0.9);
padding: 10px;
text-align: center;
border-top: 1px solid #eee;
}

.progress-text {
margin-top: 5px;
font-size: 12px;
color: #606266;
}

.cancel-btn {
margin-top: 10px;
}

.image-error {
display: flex;
flex-direction: column;
align-items: center;
justify-content: center;
height: 100%;
color: #c0c4cc;
background-color: #f5f7fa;
}
</style>