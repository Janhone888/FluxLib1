<template>
  <el-dialog
    v-model="showDialog"
    title="裁剪封面图片"
    width="800px"
    :close-on-click-modal="false"
    class="crop-dialog"
  >
    <div class="crop-container">
      <div class="crop-preview">
        <vue-cropper
          ref="cropperRef"
          :src="cropImageSrc"
          :aspect-ratio="3 / 1"
          :view-mode="1"
          :guides="true"
          :background="false"
          :auto-crop-area="0.8"
          class="cropper"
        />
      </div>
      <div class="crop-actions">
        <el-button @click="rotateImage(-90)">
          <el-icon><RefreshLeft /></el-icon>
          向左旋转
        </el-button>
        <el-button @click="rotateImage(90)">
          <el-icon><RefreshRight /></el-icon>
          向右旋转
        </el-button>
        <el-button @click="resetCrop">
          <el-icon><Refresh /></el-icon>
          重置
        </el-button>
        <el-button type="primary" @click="handleConfirm">
          <el-icon><Check /></el-icon>
          确认裁剪
        </el-button>
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { RefreshLeft, RefreshRight, Refresh, Check } from '@element-plus/icons-vue'
import 'cropperjs/dist/cropper.css'
import VueCropper from 'vue-cropperjs'

interface Props {
  modelValue: boolean
  cropImageSrc: string
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'confirm', file: File): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const showDialog = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const cropperRef = ref()

const rotateImage = (degrees: number) => {
  if (cropperRef.value) {
    cropperRef.value.rotate(degrees)
  }
}

const resetCrop = () => {
  if (cropperRef.value) {
    cropperRef.value.reset()
  }
}

const handleConfirm = () => {
  if (!cropperRef.value) return

  const canvas = cropperRef.value.getCroppedCanvas({
    width: 1200,
    height: 400,
    imageSmoothingQuality: 'high'
  })

  canvas.toBlob((blob: Blob | null) => {
    if (blob) {
      const croppedFile = new File([blob], 'cropped-cover.jpg', {
        type: 'image/jpeg',
        lastModified: Date.now()
      })
      emit('confirm', croppedFile)
      showDialog.value = false
    }
  }, 'image/jpeg')
}
</script>

<style scoped>
.crop-dialog {
  border-radius: 12px;
}

.crop-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.crop-preview {
  width: 100%;
  height: 400px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  overflow: hidden;
}

.cropper {
  width: 100%;
  height: 100%;
}

.crop-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}

@media (max-width: 768px) {
  .crop-dialog {
    width: 95% !important;
  }

  .crop-preview {
    height: 300px;
  }

  .crop-actions {
    flex-wrap: wrap;
  }
}
</style>