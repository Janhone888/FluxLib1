<template>
  <div class="analytics">
    <el-card>
      <template #header>
        <div class="flex-between">
          <h2>图书数据分析</h2>
          <div>
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
            />
          </div>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="24">
          <el-card shadow="never">
            <div id="borrow-analytics-chart" style="height: 400px;"></div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" class="mt-20">
        <el-col :span="12">
          <el-card shadow="never">
            <div id="popular-books-chart" style="height: 400px;"></div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="never">
            <div id="category-analytics-chart" style="height: 400px;"></div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import dayjs from 'dayjs'

const dateRange = ref([
  dayjs().subtract(30, 'day').format('YYYY-MM-DD'),
  dayjs().format('YYYY-MM-DD')
])

onMounted(() => {
  initCharts()
})

const initCharts = () => {
  // 借阅分析图
  const borrowChart = echarts.init(document.getElementById('borrow-analytics-chart'))
  borrowChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: {
      data: ['总借阅量', '计算机类', '文学类', '经济类', '历史类'],
      bottom: 10
    },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: Array.from({ length: 30 }, (_, i) =>
        dayjs().subtract(30 - i, 'day').format('MM/DD'))
    },
    yAxis: { type: 'value' },
    series: [
      {
        name: '总借阅量',
        type: 'line',
        smooth: true,
        data: Array.from({ length: 30 }, () => Math.floor(Math.random() * 50) + 20)
      },
      {
        name: '计算机类',
        type: 'line',
        smooth: true,
        data: Array.from({ length: 30 }, () => Math.floor(Math.random() * 20) + 10)
      },
      {
        name: '文学类',
        type: 'line',
        smooth: true,
        data: Array.from({ length: 30 }, () => Math.floor(Math.random() * 15) + 5)
      },
      {
        name: '经济类',
        type: 'line',
        smooth: true,
        data: Array.from({ length: 30 }, () => Math.floor(Math.random() * 10) + 3)
      },
      {
        name: '历史类',
        type: 'line',
        smooth: true,
        data: Array.from({ length: 30 }, () => Math.floor(Math.random() * 8) + 2)
      }
    ]
  })

  // 热门图书图
  const popularChart = echarts.init(document.getElementById('popular-books-chart'))
  popularChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'value' },
    yAxis: {
      type: 'category',
      data: [
        '深入理解计算机系统',
        'JavaScript高级程序设计',
        'Python数据分析',
        '云原生架构',
        '设计模式之美',
        '经济学原理',
        '百年孤独',
        '人类简史'
      ]
    },
    series: [
      {
        name: '借阅次数',
        type: 'bar',
        data: [128, 115, 98, 76, 65, 52, 48, 42]
      }
    ]
  })

  // 分类分析图
  const categoryChart = echarts.init(document.getElementById('category-analytics-chart'))
  categoryChart.setOption({
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', right: 10, top: 'center' },
    series: [
      {
        name: '借阅分布',
        type: 'pie',
        radius: '55%',
        center: ['40%', '50%'],
        data: [
          { value: 1048, name: '计算机科学' },
          { value: 735, name: '文学小说' },
          { value: 580, name: '经济管理' },
          { value: 484, name: '历史传记' },
          { value: 300, name: '自然科学' }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  })

  // 响应窗口大小变化
  window.addEventListener('resize', () => {
    borrowChart.resize()
    popularChart.resize()
    categoryChart.resize()
  })
}
</script>

<style scoped>
.analytics {
  padding: 20px;
}

.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.mt-20 {
  margin-top: 20px;
}
</style>