import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'

export function useImageUpload() {
  const uploading = ref(false)

  const uploadImage = async (file: File, type: 'avatar_url' | 'background_url', name: string): Promise<string> => {
    uploading.value = true
    try {
      // 获取OSS预签名URL
      const uploadUrlRes = await api.getUploadUrl(file.name, file.type)
      if (!uploadUrlRes.data?.presigned_url) throw new Error('获取上传链接失败')
      const { presigned_url, access_url } = uploadUrlRes.data

      // 上传图片到OSS
      const uploadRes = await fetch(presigned_url, {
        method: 'PUT',
        body: file,
        headers: { 'Content-Type': file.type }
      })
      if (!uploadRes.ok) throw new Error(`上传失败：${uploadRes.status}`)

      ElMessage.success(`${name}上传成功`)
      return access_url
    } catch (error) {
      ElMessage.error(`${name}上传失败：${(error as Error).message}`)
      throw error
    } finally {
      uploading.value = false
    }
  }

  const validateImageFile = (file: File): boolean => {
    const isImage = file.type.startsWith('image/')
    const isLt5M = file.size / 1024 / 1024 < 5

    if (!isImage) {
      ElMessage.error('只能上传图片文件')
      return false
    }
    if (!isLt5M) {
      ElMessage.error('图片大小不能超过5MB')
      return false
    }

    return true
  }

  return {
    uploading,
    uploadImage,
    validateImageFile
  }
}