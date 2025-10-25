import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'

export function useComments(bookId: any) {
  const comments = ref([])
  const newComment = ref('')
  const submittingComment = ref(false)

  const totalCommentsCount = computed(() => {
    let count = 0
    const countComments = (commentList: any[]) => {
      commentList.forEach(comment => {
        count++ // 当前评论
        if (comment.replies && comment.replies.length > 0) {
          countComments(comment.replies) // 递归计算子评论
        }
      })
    }
    countComments(comments.value)
    return count
  })

  const fetchComments = async () => {
    try {
      const response = await api.getBookComments(bookId.value)
      console.log('原始评论数据:', response.data)

      // 简单地为每个评论添加状态，保持原有结构
      const addStateToComments = (commentList: any[]) => {
        return commentList.map(comment => ({
          ...comment,
          showReplies: false,
          visibleRepliesCount: 2,
          hasMoreReplies: comment.replies && comment.replies.length > 2,
          replies: comment.replies ? addStateToComments(comment.replies) : []
        }))
      }

      comments.value = addStateToComments(response.data)
      console.log('处理后的评论数据:', comments.value)
    } catch (error) {
      console.error('获取评论失败:', error)
      ElMessage.error('加载评论失败，请刷新重试')
    }
  }

  const submitComment = async (content: string) => {
    if (!content.trim()) {
      ElMessage.warning('评论内容不能为空')
      return
    }

    submittingComment.value = true
    try {
      await api.createComment(bookId.value, {
        content: content.trim()
      })
      ElMessage.success('评论发表成功')
      newComment.value = ''
      await fetchComments()
    } catch (error: any) {
      ElMessage.error('评论发表失败：' + (error.response?.data?.error || error.message))
    } finally {
      submittingComment.value = false
    }
  }

  const likeComment = async (commentId: string) => {
    try {
      await api.post(`/comments/${commentId}/like`)
      await fetchComments()
    } catch (error) {
      ElMessage.error('点赞失败')
    }
  }

  const handleReply = (replyData: any) => {
    // 处理回复逻辑
    console.log('回复数据:', replyData)
  }

  return {
    comments,
    newComment,
    submittingComment,
    totalCommentsCount,
    fetchComments,
    submitComment,
    likeComment,
    handleReply
  }
}