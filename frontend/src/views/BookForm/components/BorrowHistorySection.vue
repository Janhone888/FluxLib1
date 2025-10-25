<template>
  <div class="mt-20">
    <el-card shadow="never">
      <template #header>
        <h3>借阅记录</h3>
      </template>

      <el-table :data="borrowHistory" stripe class="w-full">
        <el-table-column prop="borrower" label="借阅人" width="150" />
        <el-table-column prop="borrowDate" label="借阅日期" width="150" />
        <el-table-column prop="returnDate" label="归还日期" width="150" />
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.status === '已归还' ? 'success' : 'danger'">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="notes" label="备注" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Props {
  bookId: string
}

defineProps<Props>()

// 借阅历史数据（模拟数据）
const borrowHistory = ref([
  { borrower: '张三', borrowDate: '2023-10-01', returnDate: '2023-10-15', status: '已归还', notes: '按时归还' },
  { borrower: '李四', borrowDate: '2023-10-20', returnDate: '', status: '借阅中', notes: '预计11月归还' }
])

onMounted(() => {
  // 这里可以调用API获取真实的借阅历史
})
</script>

<style scoped>
.mt-20 {
  margin-top: 20px;
}

.w-full {
  width: 100%;
}
</style>