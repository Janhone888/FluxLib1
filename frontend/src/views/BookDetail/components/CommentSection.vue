<template>
  <el-card class="comments-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <h3>读者评论</h3>
        <el-tag type="primary">{{ totalCommentsCount }} 条评论（含子评论）</el-tag>
      </div>
    </template>

    <!-- 评论输入框 -->
    <div class="comment-input-section">
      <el-input
        v-model="newComment"
        type="textarea"
        :rows="3"
        placeholder="分享您对这本书的看法..."
        resize="none"
        maxlength="500"
        show-word-limit
      />
      <div class="comment-actions">
        <el-button
          type="primary"
          @click="$emit('submit-comment', newComment)"
          :loading="submittingComment"
          :disabled="!newComment.trim()"
        >
          发表评论
        </el-button>
      </div>
    </div>

    <!-- 评论列表 -->
    <div class="comments-list">
      <div v-if="comments.length === 0" class="empty-comments">
        <el-empty description="暂无评论，快来发表第一条评论吧！" />
      </div>

      <div v-else>
        <CommentItem
          v-for="comment in comments"
          :key="comment.comment_id"
          :comment="comment"
          @like-comment="$emit('like-comment', $event)"
          @reply-comment="$emit('reply-comment', $event)"
        />
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import CommentItem from './CommentItem.vue'

interface Props {
  bookId: string
  comments: any[]
  totalCommentsCount: number
}

defineProps<Props>()
defineEmits(['submit-comment', 'like-comment', 'reply-comment'])

const newComment = ref('')
const submittingComment = ref(false)
</script>

<style scoped>
.comments-card {
  border-radius: 12px;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.comment-input-section {
  margin-bottom: 24px;
}

.comment-actions {
  margin-top: 12px;
  text-align: right;
}

.comments-list {
  space-y: 20px;
}

.empty-comments {
  padding: 40px 0;
}
</style>