/* 表单输入框组件 */
<template>
  <el-form-item :prop="prop">
    <div class="input-with-icon">
      <i :class="icon"></i>
      <el-input
        v-model="modelValue"
        :type="type"
        :placeholder="placeholder"
        :show-password="showPassword"
        size="large"
        v-bind="$attrs"
      >
        <template v-if="$slots.append" #append>
          <slot name="append"></slot>
        </template>
      </el-input>
    </div>
  </el-form-item>
</template>

<script setup>
defineProps({
  modelValue: {
    type: [String, Number],
    required: true
  },
  icon: {
    type: String,
    required: true
  },
  placeholder: {
    type: String,
    default: ''
  },
  prop: {
    type: String,
    default: ''
  },
  type: {
    type: String,
    default: 'text'
  },
  showPassword: {
    type: Boolean,
    default: false
  }
})

defineEmits(['update:modelValue'])
</script>

<style scoped>
.input-with-icon {
  position: relative;
}

.input-with-icon i {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: #64748b;
  z-index: 1;
  font-size: 18px;
}

:deep(.el-input) {
  width: 100%;
}

:deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  box-shadow: none;
  padding-left: 50px;
  transition: all 0.3s ease;
}

:deep(.el-input__wrapper:hover) {
  border-color: rgba(255, 255, 255, 0.2);
}

:deep(.el-input__wrapper.is-focus) {
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
}

:deep(.el-input__inner) {
  color: white;
  background: transparent;
  font-size: 16px;
}

:deep(.el-input__inner::placeholder) {
  color: #64748b;
}
</style>