import { ref } from 'vue'

export function useBorrowSort(borrowRecords: any) {
  const currentSort = ref('')

  const sortByStatus = () => {
    borrowRecords.value.sort((a: any, b: any) => {
      if (a.status === b.status) return 0
      return a.status === 'returned' ? 1 : -1
    })
    currentSort.value = 'status'
  }

  const sortByDate = () => {
    borrowRecords.value.sort((a: any, b: any) => {
      return b.borrow_date - a.borrow_date
    })
    currentSort.value = 'date'
  }

  return {
    currentSort,
    sortByStatus,
    sortByDate
  }
}