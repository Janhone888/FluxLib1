<template>
  <div class="book-detail">
    <el-card class="book-card">
      <div class="book-header">
        <el-button icon="el-icon-arrow-left" @click="goBack">返回</el-button>
        <h2>{{ book.title }}</h2>
        <div class="book-actions" v-if="userStore.userInfo.is_admin">
          <el-button type="primary" @click="editBook">编辑</el-button>
          <el-button type="danger" @click="deleteBook">删除</el-button>
        </div>
      </div>

      <div class="book-content">
        <div class="book-cover">
          <el-image :src="book.cover" fit="contain" style="height: 300px" v-if="book.cover">
            <template #error>
              <div class="image-error">
                <el-icon><Picture /></el-icon>
                <span>图片加载失败</span>
              </div>
            </template>
          </el-image>
          <div class="no-cover" v-else>
            无封面
          </div>
        </div>

        <div class="book-info">
          <div class="info-row">
            <span class="label">作者：</span>
            <span>{{ book.author }}</span>
          </div>
          <div class="info-row">
            <span class="label">出版社：</span>
            <span>{{ book.publisher }}</span>
          </div>
          <div class="info-row">
            <span class="label">ISBN：</span>
            <span>{{ book.isbn }}</span>
          </div>
          <div class="info-row">
            <span class="label">分类：</span>
            <el-tag :type="getCategoryTagType(book.category)">
              {{ getCategoryName(book.category) }}
            </el-tag>
          </div>
          <div class="info-row">
            <span class="label">价格：</span>
            <span>¥{{ book.price?.toFixed(2) }}</span>
          </div>
          <div class="info-row">
            <span class="label">库存：</span>
            <el-tag :type="book.stock > 0 ? 'success' : 'danger'">
              {{ book.stock }} 本
            </el-tag>
          </div>
          <div class="info-row">
            <span class="label">状态：</span>
            <el-tag :type="getStatusTagType(book.status)">
              {{ getStatusName(book.status) }}
            </el-tag>
          </div>

          <!-- 添加图书概述 -->
          <div class="info-row" v-if="book.summary">
            <span class="label">图书概述：</span>
            <p>{{ book.summary }}</p>
          </div>

          <div class="info-row">
            <span class="label">描述：</span>
            <p>{{ book.description }}</p>
          </div>
        </div>
      </div>

      <div class="book-borrow-actions">
        <!-- 添加收藏按钮 -->
        <el-button
          :type="isFavorited ? 'warning' : 'default'"
          @click="toggleFavorite"
          :icon="isFavorited ? 'StarFilled' : 'Star'"
        >
          {{ isFavorited ? '已收藏' : '收藏' }}
        </el-button>

        <!-- 管理员显示立即借阅按钮 -->
        <el-button
          v-if="userStore.userInfo.is_admin"
          type="primary"
          :disabled="book.stock <= 0 || hasBorrowed"
          @click="borrowBook"
        >
          立即借阅
        </el-button>

        <!-- 普通用户显示预约按钮 -->
        <el-button
          v-else
          type="primary"
          :disabled="book.stock <= 0"
          @click="reserveDialogVisible = true"
        >
          预约借阅
        </el-button>

        <el-button
          type="success"
          v-if="hasBorrowed"
          @click="confirmReturn(true)"
        >
          提前归还
        </el-button>

        <el-button
          type="success"
          v-if="hasBorrowed && !isEarlyReturn(borrowRecord)"
          @click="confirmReturn(false)"
        >
          按期归还
        </el-button>
      </div>

      <div class="borrow-history" v-if="borrowRecords.length > 0">
        <h3>借阅历史</h3>
        <el-table :data="borrowRecords" style="width: 100%">
          <el-table-column prop="borrower" label="借阅人" />
          <el-table-column prop="borrow_date" label="借阅日期">
            <template #default="{ row }">
              {{ formatDate(row.borrow_date) }}
            </template>
          </el-table-column>
          <el-table-column prop="return_date" label="归还日期">
            <template #default="{ row }">
              {{ row.return_date ? formatDate(row.return_date) : '未归还' }}
            </template>
          </el-table-column>
          <el-table-column label="状态">
            <template #default="{ row }">
              <el-tag :type="row.status === 'returned' ? 'success' : 'warning'">
                {{ row.status === 'returned' ? '已归还' : '借阅中' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- 评论区 -->
    <el-card class="comments-section">
      <template #header>
        <h3>评论区</h3>
      </template>

      <!-- 评论输入框 -->
      <div class="comment-input">
        <el-input
          v-model="newComment"
          type="textarea"
          :rows="3"
          placeholder="留下你的友善评论吧"
          resize="none"
        />
        <div class="comment-actions">
          <el-button type="primary" @click="submitComment" :loading="submittingComment">
            发表评论
          </el-button>
        </div>
      </div>

      <!-- 评论列表 -->
      <div class="comments-list">
        <div v-for="comment in comments" :key="comment.comment_id" class="comment-item">
          <div class="comment-header">
            <el-avatar :size="40" :src="comment.user_avatar_url" />
            <div class="comment-author">
              <div class="author-name">{{ comment.user_display_name }}</div>
              <div class="comment-time">{{ formatTime(comment.created_at) }}</div>
            </div>
          </div>

          <div class="comment-content">
            {{ comment.content }}
          </div>

          <div class="comment-actions">
            <el-button link @click="likeComment(comment.comment_id)">
              <el-icon><Star /></el-icon>
              点赞 ({{ comment.likes }})
            </el-button>
            <el-button link @click="startReply(comment)">
              回复
            </el-button>
          </div>

          <!-- 回复输入框（点击回复时显示） -->
          <div v-if="replyingTo === comment.comment_id" class="reply-input">
            <el-input
              v-model="replyContent"
              type="textarea"
              :rows="2"
              placeholder="写下你的回复..."
              resize="none"
            />
            <div class="reply-actions">
              <el-button size="small" @click="cancelReply">取消</el-button>
              <el-button type="primary" size="small" @click="submitReply" :loading="submittingReply">
                回复
              </el-button>
            </div>
          </div>

          <!-- 回复列表 -->
          <div v-if="comment.replies && comment.replies.length > 0" class="replies-list">
            <div v-for="reply in comment.replies" :key="reply.comment_id" class="reply-item">
              <div class="reply-header">
                <el-avatar :size="32" :src="reply.user_avatar_url" />
                <div class="reply-author">
                  <div class="author-name">{{ reply.user_display_name }}</div>
                  <div class="reply-time">{{ formatTime(reply.created_at) }}</div>
                </div>
              </div>

              <div class="reply-content">
                {{ reply.content }}
              </div>

              <div class="reply-actions">
                <el-button link @click="likeComment(reply.comment_id)">
                  <el-icon><Star /></el-icon>
                  点赞 ({{ reply.likes }})
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="comments.length === 0" class="empty-comments">
          暂无评论，快来发表第一条评论吧！
        </div>
      </div>
    </el-card>

    <!-- 添加预约对话框 -->
    <el-dialog v-model="reserveDialogVisible" title="预约借阅" width="500px">
      <el-form :model="reserveForm" label-width="80px">
        <el-form-item label="预约日期">
          <el-date-picker
            v-model="reserveForm.reserve_date"
            type="date"
            placeholder="选择预约日期"
            :disabled-date="disabledDate"
          />
        </el-form-item>
        <el-form-item label="时间段">
          <el-select v-model="reserveForm.time_slot" placeholder="选择时间段">
            <el-option
              v-for="slot in timeSlots"
              :key="slot.value"
              :label="slot.label"
              :value="slot.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="借阅天数">
          <el-input-number v-model="reserveForm.days" :min="1" :max="60" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reserveDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitReservation">确认预约</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Picture, Star } from '@element-plus/icons-vue'
import { useBookStore } from '@/stores/books'
import { useUserStore } from '@/stores/user'
import api from '@/utils/api'

const route = useRoute()
const router = useRouter()
const bookStore = useBookStore()
const userStore = useUserStore()

const bookId = route.params.id
const book = ref({})
const borrowRecords = ref([])
const hasBorrowed = ref(false)
const loading = ref(false)
const selectedDays = ref(30)
const isFavorited = ref(false)

// 评论区相关状态
const comments = ref([])
const newComment = ref('')
const submittingComment = ref(false)
const replyingTo = ref(null)
const replyContent = ref('')
const submittingReply = ref(false)

// 添加预约对话框状态
const reserveDialogVisible = ref(false)
const reserveForm = reactive({
  reserve_date: '',
  time_slot: '',
  days: 7
})

// 时间段选项
const timeSlots = ref([
  { value: '08:00-10:00', label: '08:00-10:00' },
  { value: '10:00-12:00', label: '10:00-12:00' },
  { value: '13:00-15:00', label: '13:00-15:00' },
  { value: '15:00-17:00', label: '15:00-17:00' },
  { value: '17:00-19:00', label: '17:00-19:00' }
])

// 状态和分类映射函数
const statusMap = {
  available: { name: '可借阅', type: 'success' },
  borrowed: { name: '已借出', type: 'warning' },
  maintenance: { name: '维护中', type: 'danger' }
}

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

const getStatusName = (status) => statusMap[status]?.name || status
const getStatusTagType = (status) => statusMap[status]?.type || ''
const getCategoryName = (category) => categoryMap[category]?.name || category
const getCategoryTagType = (category) => categoryMap[category]?.type || ''

const fetchBookDetail = async () => {
  try {
    loading.value = true
    await bookStore.fetchBook(bookId)
    book.value = bookStore.currentBook

    // 获取借阅记录
    // 这里需要根据实际API调整
    // const response = await api.getBorrowHistory(bookId)
    // borrowRecords.value = response.data

    // 检查当前用户是否借阅了此书
    // 暂时模拟
    hasBorrowed.value = false

    // 检查收藏状态
    await checkFavoriteStatus()
  } catch (error) {
    ElMessage.error('获取图书详情失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 检查收藏状态
const checkFavoriteStatus = async () => {
  try {
    const response = await api.checkFavorite(bookId)
    isFavorited.value = response.data.is_favorited
  } catch (error) {
    console.error('检查收藏状态失败', error)
  }
}

// 切换收藏状态
const toggleFavorite = async () => {
  try {
    if (isFavorited.value) {
      await api.removeFavorite(bookId)
      ElMessage.success('已取消收藏')
    } else {
      await api.addFavorite(bookId)
      ElMessage.success('已收藏')
    }
    isFavorited.value = !isFavorited.value
  } catch (error) {
    ElMessage.error('操作失败: ' + error.message)
  }
}

// 修改borrowBook方法，传入selectedDays
const borrowBook = async () => {
  try {
    await bookStore.borrowBook(bookId, selectedDays.value)
    ElMessage.success('借阅成功')
    fetchBookDetail() // 刷新数据
  } catch (error) {
    // 添加详细的错误提示
    const errorMessage = error.response?.data?.error || error.message
    ElMessage.error(`借阅失败: ${errorMessage}`)

    // 如果是认证问题，提示用户重新登录
    if (error.response?.status === 401) {
      ElMessage.warning('认证已过期，请重新登录')
      router.push('/login')
    }
  }
}

// 确认归还（区分提前归还和按期归还）
const confirmReturn = (isEarly) => {
  if (isEarly) {
    ElMessageBox.confirm('确定要提前归还这本书吗？', '提前归还确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      returnBook(true)
    }).catch(() => {})
  } else {
    returnBook(false)
  }
}

// 执行归还操作
const returnBook = async (isEarly) => {
  try {
    let response
    if (isEarly) {
      response = await api.returnBookEarly(bookId)
    } else {
      response = await api.returnBook(bookId)
    }

    if (response.data.success) {
      ElMessage.success(response.data.message || '归还成功')
      // 刷新页面数据
      fetchBookDetail()
    } else {
      ElMessage.error(response.data.error || '归还失败')
    }
  } catch (error) {
    ElMessage.error('归还失败: ' + error.message)
  }
}

// 检查是否为提前归还
const isEarlyReturn = (record) => {
  if (!record || !record.due_date) return false
  const currentTime = Math.floor(Date.now() / 1000)
  return currentTime < record.due_date
}

const editBook = () => {
  router.push({ name: 'EditBook', params: { id: bookId } })
}

const deleteBook = () => {
  ElMessageBox.confirm('确定要删除这本书吗？删除后无法恢复', '删除确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await bookStore.deleteBook(bookId)
      ElMessage.success('删除成功')
      router.push('/books')
    } catch (error) {
      ElMessage.error('删除失败: ' + error.message)
    }
  }).catch(() => {})
}

const goBack = () => {
  router.go(-1)
}

const formatDate = (timestamp) => {
  return new Date(timestamp * 1000).toLocaleDateString()
}

// 评论区相关方法

// 获取评论
const fetchComments = async () => {
  try {
    const response = await api.getBookComments(bookId)
    comments.value = response.data
  } catch (error) {
    ElMessage.error('获取评论失败')
  }
}

// 发表评论
const submitComment = async () => {
  if (!newComment.value.trim()) {
    ElMessage.warning('评论内容不能为空')
    return
  }

  try {
    submittingComment.value = true
    await api.createComment(bookId, { content: newComment.value })
    ElMessage.success('评论发表成功')
    newComment.value = ''
    // 重新获取评论
    await fetchComments()
  } catch (error) {
    ElMessage.error('发表评论失败')
  } finally {
    submittingComment.value = false
  }
}

// 开始回复
const startReply = (comment) => {
  replyingTo.value = comment.comment_id
  replyContent.value = ''
}

// 取消回复
const cancelReply = () => {
  replyingTo.value = null
  replyContent.value = ''
}

// 提交回复
const submitReply = async () => {
  if (!replyContent.value.trim()) {
    ElMessage.warning('回复内容不能为空')
    return
  }

  try {
    submittingReply.value = true
    await api.createComment(bookId, {
      content: replyContent.value,
      parent_id: replyingTo.value
    })
    ElMessage.success('回复成功')
    replyingTo.value = null
    replyContent.value = ''
    // 重新获取评论
    await fetchComments()
  } catch (error) {
    ElMessage.error('回复失败')
  } finally {
    submittingReply.value = false
  }
}

// 点赞评论
const likeComment = async (commentId) => {
  try {
    await api.likeComment(commentId)
    ElMessage.success('点赞成功')
    // 重新获取评论
    await fetchComments()
  } catch (error) {
    ElMessage.error('点赞失败')
  }
}

// 格式化时间
const formatTime = (timestamp) => {
  return new Date(timestamp * 1000).toLocaleString()
}

// 预约相关方法

// 禁用过去的日期
const disabledDate = (time) => {
  return time.getTime() < Date.now() - 8.64e7 // 禁用今天之前的日期
}

// 提交预约
const submitReservation = async () => {
  try {
    if (!reserveForm.reserve_date || !reserveForm.time_slot) {
      ElMessage.warning('请选择预约日期和时间段')
      return
    }

    // 格式化日期
    const formattedDate = formatDateForReservation(reserveForm.reserve_date)

    const response = await api.reserveBook(bookId, {
      reserve_date: formattedDate,
      time_slot: reserveForm.time_slot,
      days: reserveForm.days
    })

    if (response.data.success) {
      ElMessage.success('预约成功')
      reserveDialogVisible.value = false
      // 刷新页面数据
      fetchBookDetail()
    } else {
      ElMessage.error(response.data.error || '预约失败')
    }
  } catch (error) {
    ElMessage.error('预约失败: ' + error.message)
  }
}

// 格式化日期函数
const formatDateForReservation = (date) => {
  const d = new Date(date)
  let month = '' + (d.getMonth() + 1)
  let day = '' + d.getDate()
  const year = d.getFullYear()

  if (month.length < 2) month = '0' + month
  if (day.length < 2) day = '0' + day

  return [year, month, day].join('-')
}

onMounted(() => {
  fetchBookDetail()
  fetchComments()
})
</script>

<style scoped>
.book-detail {
  padding: 20px;
}

.book-card {
  max-width: 1000px;
  margin: 0 auto;
}

.book-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.book-header h2 {
  margin-left: 15px;
  flex-grow: 1;
}

.book-content {
  display: flex;
  gap: 30px;
  margin-bottom: 30px;
}

@media (max-width: 768px) {
  .book-content {
    flex-direction: column;
  }
}

.book-cover {
  flex: 0 0 300px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
  border-radius: 8px;
  overflow: hidden;
}

.no-cover {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
  font-size: 14px;
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

.book-info {
  flex: 1;
}

.info-row {
  margin-bottom: 15px;
  display: flex;
}

.info-row .label {
  font-weight: bold;
  min-width: 80px;
}

.book-borrow-actions {
  margin: 20px 0;
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
}

.borrow-history {
  margin-top: 30px;
  border-top: 1px solid #eee;
  padding-top: 20px;
}

/* 评论区样式 */
.comments-section {
  margin-top: 30px;
  max-width: 1000px;
  margin: 30px auto 0;
}

.comment-input {
  margin-bottom: 20px;
}

.comment-actions {
  margin-top: 10px;
  text-align: right;
}

.comment-item {
  border-bottom: 1px solid #eee;
  padding: 15px 0;
}

.comment-item:last-child {
  border-bottom: none;
}

.comment-header {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.comment-author {
  margin-left: 10px;
}

.author-name {
  font-weight: bold;
}

.comment-time {
  font-size: 12px;
  color: #999;
}

.comment-content {
  margin-bottom: 10px;
  line-height: 1.6;
}

.comment-actions {
  margin-bottom: 10px;
}

.reply-input {
  margin: 10px 0;
  padding-left: 50px; /* 与头像对齐 */
}

.reply-actions {
  margin-top: 10px;
  text-align: right;
}

.replies-list {
  margin-top: 15px;
  padding-left: 50px; /* 与头像对齐 */
  border-left: 2px solid #f0f0f0;
}

.reply-item {
  padding: 10px 0;
  border-bottom: 1px dashed #eee;
}

.reply-item:last-child {
  border-bottom: none;
}

.reply-header {
  display: flex;
  align-items: center;
  margin-bottom: 5px;
}

.reply-author {
  margin-left: 8px;
}

.reply-time {
  font-size: 11px;
  color: 999;
}

.reply-content {
  font-size: 14px;
  line-height: 1.5;
}

.reply-actions {
  margin-top: 5px;
}

.empty-comments {
  text-align: center;
  color: #999;
  padding: 30px 0;
}
</style>