import { ref } from 'vue'
import { Star, Clock, Setting } from '@element-plus/icons-vue'
import api from '@/utils/api'

export interface FavoriteItem {
  book_id: string
  book_title: string
  book_author: string
  book_cover: string
}

export interface HistoryItem {
  history_id: string
  book_id: string
  book_title: string
  book_author: string
  book_cover: string
  view_time: number
}

export function useProfileTabs() {
  const activeTab = ref('favorites')

  const tabs = [
    { id: 'favorites', name: '我的收藏', icon: Star },
    { id: 'history', name: '浏览历史', icon: Clock },
    { id: 'settings', name: '资料设置', icon: Setting }
  ]

  const favoritesPreview = ref<FavoriteItem[]>([])
  const historyPreview = ref<HistoryItem[]>([])

  const fetchFavoritesPreview = async () => {
    try {
      const response = await api.getFavorites()
      let favoritesData: FavoriteItem[] = []

      if (response.data && Array.isArray(response.data)) {
        favoritesData = response.data.slice(0, 6)
      } else if (response.data && response.data.items) {
        favoritesData = response.data.items.slice(0, 6)
      }

      favoritesPreview.value = favoritesData
    } catch (error) {
      console.error('获取收藏预览失败', error)
      favoritesPreview.value = []
    }
  }

  const fetchHistoryPreview = async () => {
    try {
      const response = await api.getViewHistory()
      let historyData: HistoryItem[] = []

      if (response.data && Array.isArray(response.data)) {
        historyData = response.data.slice(0, 6)
      } else if (response.data && response.data.items) {
        historyData = response.data.items.slice(0, 6)
      }

      historyPreview.value = historyData
    } catch (error) {
      console.error('获取历史预览失败', error)
      historyPreview.value = []
    }
  }

  const favoritesCount = computed(() => favoritesPreview.value.length)
  const viewHistoryCount = computed(() => historyPreview.value.length)

  return {
    activeTab,
    tabs,
    favoritesPreview,
    historyPreview,
    favoritesCount,
    viewHistoryCount,
    fetchFavoritesPreview,
    fetchHistoryPreview
  }
}