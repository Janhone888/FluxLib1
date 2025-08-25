<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6" v-for="stat in stats" :key="stat.title">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" :style="{ backgroundColor: stat.color }">
              <i :class="stat.icon"></i>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-title">{{ stat.title }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-20">
      <el-col :span="16">
        <el-card>
          <template #header>
            <h3>图书借阅趋势</h3>
          </template>
          <div id="borrow-trend-chart" style="height: 300px;"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>
            <h3>图书分类分布</h3>
          </template>
          <div id="category-distribution-chart" style="height: 300px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="flex-between">
              <h3>借阅记录</h3>
              <el-link type="primary" :underline="false" @click="goToBorrows">查看全部</el-link>
            </div>
          </template>

          <el-table :data="borrowRecords" v-if="borrowRecords.length > 0" style="width: 100%">
            <el-table-column prop="book_title" label="图书名称" />
            <el-table-column prop="borrower" label="借阅人" />
            <el-table-column prop="borrow_date" label="借阅日期" width="180">
              <template #default="{ row }">
                {{ formatDate(row.borrow_date) }}
              </template>
            </el-table-column>
            <el-table-column prop="due_date" label="应还日期" width="180">
              <template #default="{ row }">
                {{ formatDate(row.due_date) }}
              </template>
            </el-table-column>
            <el-table-column label="状态" width="120">
              <template #default="{ row }">
                <el-tag :type="row.status === 'returned' ? 'success' : 'warning'">
                  {{ row.status === 'returned' ? '已归还' : '借阅中' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>

          <div v-else class="empty-tip">
            <p>暂无借阅记录</p>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import dayjs from 'dayjs'
import api from '@/utils/api'

const router = useRouter()

const stats = ref([
  { title: '总图书量', value: 1286, icon: 'el-icon-notebook-2', color: '#1890ff' },
  { title: '可借阅图书', value: 956, icon: 'el-icon-collection', color: '#52c41a' },
  { title: '今日借阅量', value: 42, icon: 'el-icon-timer', color: '#faad14' },
  { title: '逾期未还', value: 18, icon: 'el-icon-warning', color: '#f5222d' }
])

const borrowRecords = ref([])

onMounted(() => {
  initCharts()
  fetchBorrowRecords()
})

const fetchBorrowRecords = async () => {
  try {
    // 获取所有借阅记录
    const response = await api.getBorrowRecords()
    borrowRecords.value = (response.data.items || []).slice(0, 5) // 只取最近5条
  } catch (error) {
    console.error('获取借阅记录失败', error)
  }
}

const formatDate = (timestamp) => {
  return new Date(timestamp * 1000).toLocaleDateString()
}

const initCharts = () => {
  // 借阅趋势图 - 完整初始化代码
  const trendChart = echarts.init(document.getElementById('borrow-trend-chart'))
  trendChart.setOption({
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['借阅量', '归还量']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: ['10/01', '10/05', '10/10', '10/15', '10/20', '10/25', '10/30']
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '借阅量',
        type: 'line',
        smooth: true,
        data: [12, 18, 15, 22, 19, 25, 30],
        lineStyle: {
          width: 3
        },
        itemStyle: {
          color: '#1890ff'
        }
      },
      {
        name: '归还量',
        type: 'line',
        smooth: true,
        data: [8, 12, 10, 15, 20, 18, 22],
        lineStyle: {
          width: 3
        },
        itemStyle: {
          color: '#52c41a'
        }
      }
    ]
  })

  // 分类分布图 - 完整初始化代码
  const categoryChart = echarts.init(document.getElementById('category-distribution-chart'))
  categoryChart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      data: ['计算机科学', '文学小说', '经济管理', '历史传记', '自然科学']
    },
    series: [
      {
        name: '图书分类',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '18',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: [
          { value: 320, name: '计算机科学', itemStyle: { color: '#1890ff' } },
          { value: 240, name: '文学小说', itemStyle: { color: '#52c41a' } },
          { value: 149, name: '经济管理', itemStyle: { color: '#faad14' } },
          { value: 100, name: '历史传记', itemStyle: { color: '#f5222d' } },
          { value: 59, name: '自然科学', itemStyle: { color: '#722ed1' } }
        ]
      }
    ]
  })

  // 响应窗口大小变化
  window.addEventListener('resize', () => {
    trendChart.resize()
    categoryChart.resize()
  })
}

// 跳转到借阅管理
const goToBorrows = () => {
  router.push('/borrows')
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
}

.stat-icon i {
  font-size: 28px;
  color: white;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-title {
  font-size: 14px;
  color: #999;
}

.mt-20 {
  margin-top: 20px;
}

.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty-tip {
  text-align: center;
  padding: 20px;
  color: #999;
}
</style>