import { ref } from 'vue'

export function useBooks() {
  const categories = ref([
    { value: 'computer', label: '计算机' },
    { value: 'literature', label: '文学' },
    { value: 'economy', label: '经济' },
    { value: 'history', label: '历史' },
    { value: 'science', label: '科学' },
    { value: 'art', label: '艺术' },
    { value: 'management', label: '管理' },
    { value: 'education', label: '教育' }
  ])

  // 图书状态映射
  const statusMap = {
    available: { name: '可借阅', type: 'success' },
    borrowed: { name: '已借出', type: 'warning' },
    maintenance: { name: '维护中', type: 'danger' }
  }

  // 图书分类映射
  const categoryMap = {
    computer: { name: '计算机', type: '' },
    literature: { name: '文学', type: 'success' },
    economy: { name: '经济', type: 'warning' },
    history: { name: '历史', type: 'danger' },
    science: { name: '科学', type: 'info' },
    art: { name: '艺术', type: 'primary' },
    management: { name: '管理', type: 'success' },
    education: { name: '教育', type: 'warning' }
  }

  const getStatusName = (status: string) => statusMap[status as keyof typeof statusMap]?.name || status
  const getStatusTagType = (status: string) => statusMap[status as keyof typeof statusMap]?.type || ''
  const getCategoryName = (category: string) => categoryMap[category as keyof typeof categoryMap]?.name || category
  const getCategoryTagType = (category: string) => categoryMap[category as keyof typeof categoryMap]?.type || ''

  return {
    categories,
    getStatusName,
    getStatusTagType,
    getCategoryName,
    getCategoryTagType
  }
}