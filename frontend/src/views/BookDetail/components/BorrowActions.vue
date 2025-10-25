<template>
  <el-card class="action-card" shadow="hover">
    <div class="action-section">
      <div class="action-buttons">
        <!-- 管理员借阅按钮 -->
        <el-button
          v-if="userIsAdmin"
          type="primary"
          size="large"
          :disabled="book.stock <= 0 || hasBorrowed"
          @click="$emit('borrow')"
          class="borrow-btn"
        >
          <template #icon>
            <el-icon><Reading /></el-icon>
          </template>
          立即借阅
        </el-button>

        <!-- 普通用户预约按钮 -->
        <el-button
          v-else
          type="primary"
          size="large"
          :disabled="book.stock <= 0"
          @click="$emit('reserve')"
          class="reserve-btn"
        >
          <template #icon>
            <el-icon><Calendar /></el-icon>
          </template>
          预约借阅
        </el-button>

        <!-- 归还按钮 -->
        <el-button
          v-if="hasBorrowed"
          type="success"
          size="large"
          @click="$emit('return', false)"
          class="return-btn"
        >
          <template #icon>
            <el-icon><Check /></el-icon>
          </template>
          按期归还
        </el-button>

        <el-button
          v-if="hasBorrowed"
          type="warning"
          size="large"
          @click="$emit('return', true)"
          class="early-return-btn"
        >
          <template #icon>
            <el-icon><Clock /></el-icon>
          </template>
          提前归还
        </el-button>
      </div>

      <!-- 库存提示 -->
      <div class="stock-tip" v-if="book.stock <= 0">
        <el-alert
          title="暂无库存"
          type="warning"
          description="当前图书暂无库存，您可以先收藏或预约"
          show-icon
          :closable="false"
        />
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { Reading, Calendar, Check, Clock } from '@element-plus/icons-vue'

interface Props {
  book: any
  hasBorrowed: boolean
  userIsAdmin?: boolean
}

defineProps<Props>()
defineEmits(['borrow', 'return', 'reserve'])
</script>

<style scoped>
.action-card {
  border-radius: 12px;
  overflow: hidden;
}

.action-section {
  padding: 24px;
  background: white;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
}

.action-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.borrow-btn,
.reserve-btn,
.return-btn,
.early-return-btn {
  flex: 1;
  min-width: 140px;
  height: 48px;
  font-weight: 600;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.borrow-btn:hover:not(.is-disabled),
.reserve-btn:hover:not(.is-disabled),
.return-btn:hover:not(.is-disabled),
.early-return-btn:hover:not(.is-disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.borrow-btn:active:not(.is-disabled),
.reserve-btn:active:not(.is-disabled),
.return-btn:active:not(.is-disabled),
.early-return-btn:active:not(.is-disabled) {
  transform: translateY(0);
}

.reserve-btn:hover:not(.is-disabled) {
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.stock-tip {
  margin-top: 16px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .action-buttons {
    flex-direction: column;
  }

  .borrow-btn,
  .reserve-btn,
  .return-btn,
  .early-return-btn {
    width: 100%;
  }
}
</style>