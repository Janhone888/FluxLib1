<template>
  <div class="comment-item">
    <div class="comment-header">
      <el-avatar :size="40" :src="comment.user_avatar_url" />
      <div class="comment-user">
        <div class="user-name">{{ comment.user_display_name }}</div>
        <div class="comment-time">{{ formatTime(comment.created_at) }}</div>
      </div>
    </div>

    <div class="comment-content">
      {{ comment.content }}
    </div>

    <div class="comment-footer">
      <el-button
        link
        @click="$emit('like-comment', comment.comment_id)"
        :class="{ liked: comment.likes > 0 }"
      >
        <el-icon><Star /></el-icon>
        点赞 ({{ comment.likes }})
      </el-button>
      <el-button link @click="$emit('reply-comment', comment)">
        <el-icon><ChatDotRound /></el-icon>
        回复
      </el-button>
    </div>

    <!-- 回复列表 -->
    <div v-if="comment.replies && comment.replies.length > 0" class="replies-section">
      <CommentItem
        v-for="reply in comment.replies"
        :key="reply.comment_id"
        :comment="reply"
        @like-comment="$emit('like-comment', $event)"
        @reply-comment="$emit('reply-comment', $event)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { Star, ChatDotRound } from '@element-plus/icons-vue'

interface Props {
  comment: any
}

defineProps<Props>()
defineEmits(['like-comment', 'reply-comment'])

const formatTime = (timeString: string) => {
  if (!timeString) return ''
  return new Date(timeString).toLocaleString('zh-CN')
}
</script>

<style scoped>
.comment-item {
  padding: 20px;
  border-radius: 8px;
  background: #f8fafc;
  margin-bottom: 16px;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.comment-user {
  flex: 1;
}

.user-name {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 2px;
}

.comment-time {
  font-size: 12px;
  color: #9ca3af;
}

.comment-content {
  line-height: 1.6;
  color: #4b5563;
  margin-bottom: 12px;
}

.comment-footer {
  display: flex;
  gap: 16px;
}

.comment-footer .el-button {
  padding: 4px 8px;
  color: #6b7280;
}

.comment-footer .liked {
  color: #f59e0b;
}

.replies-section {
  margin-top: 16px;
  padding-left: 20px;
  border-left: 2px solid #e5e7eb;
}
</style>