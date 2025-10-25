<template>
  <el-dialog
    v-model="visible"
    title="预约借阅"
    width="500px"
    align-center
  >
    <el-form :model="reserveForm" label-width="100px">
      <el-form-item label="预约日期">
        <el-date-picker
          v-model="reserveForm.reserve_date"
          type="date"
          placeholder="选择预约日期"
          :disabled-date="disabledDate"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="时间段">
        <el-select v-model="reserveForm.time_slot" placeholder="选择时间段" style="width: 100%">
          <el-option
            v-for="slot in timeSlots"
            :key="slot.value"
            :label="slot.label"
            :value="slot.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="借阅天数">
        <el-input-number
          v-model="reserveForm.days"
          :min="1"
          :max="60"
          style="width: 100%"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="handleSubmit">确认预约</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'

interface Props {
  visible: boolean
}

interface Emits {
  (e: 'update:visible', value: boolean): void
  (e: 'submit', value: any): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const visible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

const reserveForm = reactive({
  reserve_date: '',
  time_slot: '',
  days: 7
})

const timeSlots = ref([
  { label: '上午 (9:00-12:00)', value: 'morning' },
  { label: '下午 (14:00-17:00)', value: 'afternoon' },
  { label: '晚上 (19:00-21:00)', value: 'evening' }
])

const disabledDate = (time: Date) => {
  return time.getTime() < Date.now() - 8.64e7
}

const handleSubmit = () => {
  emit('submit', { ...reserveForm })
  visible.value = false
}
</script>