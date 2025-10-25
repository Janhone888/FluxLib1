<template>
  <el-card class="history-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <h3>借阅历史</h3>
        <el-tag type="info">{{ records.length }} 条记录</el-tag>
      </div>
    </template>

    <el-table :data="records" style="width: 100%">
      <el-table-column prop="borrower" label="借阅人" width="120" />
      <el-table-column prop="borrow_date" label="借阅日期" width="150">
        <template #default="{ row }">
          {{ formatDate(row.borrow_date) }}
        </template>
      </el-table-column>
      <el-table-column prop="return_date" label="归还日期" width="150">
        <template #default="{ row }">
          {{ row.return_date ? formatDate(row.return_date) : '未归还' }}
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'returned' ? 'success' : 'warning'" size="small">
            {{ row.status === 'returned' ? '已归还' : '借阅中' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="duration" label="借阅时长" width="100">
        <template #default="{ row }">
          {{ calculateDuration(row.borrow_date, row.return_date) }}
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup lang="ts">
interface Props {
  records: any[]
}

defineProps<Props>()

const formatDate = (dateString: string) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const calculateDuration = (startDate: string, endDate: string) => {
  if (!startDate) return ''
  const start = new Date(startDate)
  const end = endDate ? new Date(endDate) : new Date()
  const diffTime = Math.abs(end.getTime() - start.getTime())
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return `${diffDays}天`
}
</script>

<style scoped>
.history-card {
  border-radius: 12px;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>