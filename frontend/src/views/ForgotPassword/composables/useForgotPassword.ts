import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import api from '@/utils/api'

export interface ForgotPasswordForm {
  email: string
  code: string
  newPassword: string
  confirmPassword: string
}

export function useForgotPassword() {
  const router = useRouter()

  const activeStep = ref(1)
  const sendingCode = ref(false)
  const verifying = ref(false)
  const resetting = ref(false)

  const form = reactive<ForgotPasswordForm>({
    email: '',
    code: '',
    newPassword: '',
    confirmPassword: ''
  })

  const rules = {
    email: [
      { required: true, message: '请输入邮箱地址', trigger: 'blur' },
      { type: 'email', message: '请输入有效的邮箱地址', trigger: ['blur', 'change'] }
    ],
    code: [
      { required: true, message: '请输入验证码', trigger: 'blur' },
      { len: 6, message: '验证码长度为6位', trigger: 'blur' }
    ]
  }

  const passwordRules = {
    newPassword: [
      { required: true, message: '请输入新密码', trigger: 'blur' },
      { min: 6, message: '密码长度至少为6位', trigger: 'blur' }
    ],
    confirmPassword: [
      { required: true, message: '请确认密码', trigger: 'blur' },
      {
        validator: (rule: any, value: string, callback: any) => {
          if (value !== form.newPassword) {
            callback(new Error('两次输入的密码不一致'))
          } else {
            callback()
          }
        },
        trigger: 'blur'
      }
    ]
  }

  const sendVerificationCode = async () => {
    try {
      sendingCode.value = true
      await api.sendResetCode(form.email)
      ElMessage.success('验证码已发送，请查收邮箱')
      activeStep.value = 2
      return true
    } catch (error: any) {
      ElMessage.error(`发送失败: ${error.response?.data?.error || error.message}`)
      throw error
    } finally {
      sendingCode.value = false
    }
  }

  const verifyCode = async () => {
    try {
      verifying.value = true
      await api.verifyResetCode({
        email: form.email,
        code: form.code
      })
      ElMessage.success('验证码验证成功')
      activeStep.value = 3
    } catch (error: any) {
      ElMessage.error(`验证失败: ${error.response?.data?.error || error.message}`)
      throw error
    } finally {
      verifying.value = false
    }
  }

  const resendCode = async () => {
    try {
      await api.sendResetCode(form.email)
      ElMessage.success('验证码已重新发送')
      return true
    } catch (error: any) {
      ElMessage.error(`发送失败: ${error.response?.data?.error || error.message}`)
      throw error
    }
  }

  const resetPassword = async () => {
    try {
      resetting.value = true
      await api.resetPassword({
        email: form.email,
        code: form.code,
        new_password: form.newPassword
      })
      ElMessage.success('密码重置成功')
      activeStep.value = 4
    } catch (error: any) {
      ElMessage.error(`重置失败: ${error.response?.data?.error || error.message}`)
      throw error
    } finally {
      resetting.value = false
    }
  }

  const navigateToLogin = () => {
    router.push('/login')
  }

  const navigateToHome = () => {
    router.push('/')
  }

  const goToPreviousStep = () => {
    if (activeStep.value > 1) {
      activeStep.value--
    }
  }

  return {
    activeStep,
    sendingCode,
    verifying,
    resetting,
    form,
    rules,
    passwordRules,
    sendVerificationCode,
    verifyCode,
    resendCode,
    resetPassword,
    navigateToLogin,
    navigateToHome,
    goToPreviousStep
  }
}