<template>
  <div class="cover-uploader">
    <ImageUploader v-model="coverValue" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import ImageUploader from '@/components/ImageUploader.vue'

interface Props {
  modelValue: string
}

interface Emits {
  (e: 'update:modelValue', value: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const coverValue = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})
</script>

<style scoped>
.cover-uploader {
  width: 200px;
  height: 280px;
}
</style>