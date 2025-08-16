<template>
  <div class="settings">
    <el-card>
      <template #header>
        <h2>系统设置</h2>
      </template>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="基本设置" name="basic">
          <el-form :model="basicSettings" label-width="150px">
            <el-form-item label="系统名称">
              <el-input v-model="basicSettings.systemName" />
            </el-form-item>
            <el-form-item label="图书借阅期限">
              <el-input-number v-model="basicSettings.borrowPeriod" :min="7" :max="90" />
              <span class="ml-10">天</span>
            </el-form-item>
            <el-form-item label="逾期罚款率">
              <el-input-number v-model="basicSettings.fineRate" :min="0.1" :max="10" :step="0.1" />
              <span class="ml-10">元/天</span>
            </el-form-item>
            <el-form-item label="最大借阅数量">
              <el-input-number v-model="basicSettings.maxBorrow" :min="1" :max="20" />
              <span class="ml-10">本</span>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveBasicSettings">保存设置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="用户管理" name="users">
          <el-table :data="users" style="width: 100%">
            <el-table-column prop="username" label="用户名" />
            <el-table-column prop="name" label="姓名" />
            <el-table-column prop="role" label="角色">
              <template #default="scope">
                <el-tag :type="scope.row.role === 'admin' ? 'danger' : 'primary'">
                  {{ scope.row.role === 'admin' ? '管理员' : '普通用户' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="lastLogin" label="最后登录" />
            <el-table-column label="操作" width="180">
              <template #default="scope">
                <el-button size="small" @click="editUser(scope.row)">编辑</el-button>
                <el-button
                  size="small"
                  type="danger"
                  @click="deleteUser(scope.row)"
                  v-if="scope.row.role !== 'admin'"
                >删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="mt-20 text-right">
            <el-button type="primary" @click="addUser">添加用户</el-button>
          </div>
        </el-tab-pane>

        <el-tab-pane label="系统日志" name="logs">
          <el-table :data="logs" style="width: 100%">
            <el-table-column prop="time" label="时间" width="180" />
            <el-table-column prop="user" label="用户" width="120" />
            <el-table-column prop="action" label="操作" />
            <el-table-column prop="detail" label="详情" />
            <el-table-column prop="ip" label="IP地址" width="140" />
          </el-table>

          <div class="mt-20 flex-between">
            <div>
              <el-pagination
                background
                layout="prev, pager, next"
                :total="1000"
                :page-size="10"
                v-model:current-page="currentPage"
              />
            </div>
            <el-button type="primary">导出日志</el-button>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const activeTab = ref('basic')

const basicSettings = ref({
  systemName: '阿里云图书管理系统',
  borrowPeriod: 30,
  fineRate: 0.5,
  maxBorrow: 5
})

const users = ref([
  { id: 1, username: 'admin', name: '管理员', role: 'admin', lastLogin: '2023-10-18 14:30:22' },
  { id: 2, username: 'zhangsan', name: '张三', role: 'user', lastLogin: '2023-10-18 10:15:45' },
  { id: 3, username: 'lisi', name: '李四', role: 'user', lastLogin: '2023-10-17 16:20:33' },
  { id: 4, username: 'wangwu', name: '王五', role: 'user', lastLogin: '2023-10-16 09:42:11' }
])

const logs = ref([
  { time: '2023-10-18 14:30:22', user: 'admin', action: '登录系统', detail: '登录成功', ip: '192.168.1.100' },
  { time: '2023-10-18 14:28:15', user: 'admin', action: '修改设置', detail: '更新了借阅期限为30天', ip: '192.168.1.100' },
  { time: '2023-10-18 14:25:40', user: 'admin', action: '删除图书', detail: '删除了《旧版图书》', ip: '192.168.1.100' },
  { time: '2023-10-18 10:15:45', user: 'zhangsan', action: '借阅图书', detail: '借阅了《JavaScript高级程序设计》', ip: '192.168.1.101' },
  { time: '2023-10-18 09:42:11', user: 'wangwu', action: '归还图书', detail: '归还了《Python数据分析》', ip: '192.168.1.103' },
  { time: '2023-10-17 16:20:33', user: 'lisi', action: '借阅图书', detail: '借阅了《云原生架构》', ip: '192.168.1.102' }
])

const currentPage = ref(1)

const saveBasicSettings = () => {
  ElMessage.success('系统设置已保存')
}

const addUser = () => {
  ElMessage.info('添加用户功能')
}

const editUser = (user) => {
  ElMessage.info(`编辑用户: ${user.name}`)
}

const deleteUser = (user) => {
  ElMessage.warning(`删除用户: ${user.name}`)
}
</script>

<style scoped>
.settings {
  padding: 20px;
}

.mt-20 {
  margin-top: 20px;
}

.text-right {
  text-align: right;
}

.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ml-10 {
  margin-left: 10px;
}
</style>