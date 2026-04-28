<template>
  <div class="script-analysis">
    <div class="page-header">
      <h2>执行概览</h2>
      <button class="refresh-btn" @click="refreshData">
        <span>🔄</span> 刷新
      </button>
    </div>

    <div class="stats-grid" v-if="stats">
      <div class="stat-card">
        <div class="stat-value">{{ stats.total }}</div>
        <div class="stat-label">总任务数</div>
      </div>
      <div class="stat-card success">
        <div class="stat-value">{{ stats.success_rate }}%</div>
        <div class="stat-label">成功率</div>
      </div>
      <div class="stat-card danger">
        <div class="stat-value">{{ stats.fail_rate }}%</div>
        <div class="stat-label">失败率</div>
      </div>
      <div class="stat-card info">
        <div class="stat-value">{{ formatDuration(stats.avg_duration) }}</div>
        <div class="stat-label">平均时长</div>
      </div>
    </div>

    <div class="recent-tasks-section">
      <h3 class="section-title">最近任务</h3>
      <div class="recent-tasks-table">
        <table class="data-table" v-if="recentTasks.length > 0">
          <thead>
            <tr>
              <th>任务名称</th>
              <th>脚本数量</th>
              <th>操作员</th>
              <th>状态</th>
              <th>执行时间</th>
              <th>持续时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(task, index) in recentTasks" :key="index">
              <td class="task-name">{{ task.task_name }}</td>
              <td>{{ task.script_count || 1 }}</td>
              <td>{{ task.username || '-' }}</td>
              <td>
                <span class="status-badge" :class="'status-' + task.status">
                  {{ task.status === 'completed' ? '成功' : task.status === 'failed' ? '失败' : task.status }}
                </span>
              </td>
              <td>{{ formatTime(task.started_at) }}</td>
              <td>{{ formatDuration(task.total_duration) }}</td>
              <td>
                <button class="view-btn" @click="viewTaskDetail(task)">查看</button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-else class="empty-data">暂无最近任务数据</div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api/index.js'

export default {
  name: 'ScriptAnalysis',
  data() {
    return {
      stats: null,
      recentTasks: []
    }
  },
  mounted() {
    this.loadData()
  },
  methods: {
    async loadData() {
      await Promise.all([
        this.loadStats(),
        this.loadRecentTasks()
      ])
    },
    async refreshData() {
      await this.loadData()
    },
    async loadStats() {
      try {
        const response = await api.get('/script-results/stats')
        this.stats = response.data
      } catch (error) {
        console.error('加载统计失败:', error)
        this.stats = null
      }
    },
    async loadRecentTasks() {
      try {
        const response = await api.get('/script-results?page=1&page_size=10')
        this.recentTasks = response.data.data || []
      } catch (error) {
        console.error('加载最近任务失败:', error)
        this.recentTasks = []
      }
    },
    formatDuration(seconds) {
      if (!seconds || seconds === 0) return '0s'
      if (seconds < 60) return seconds.toFixed(1) + 's'
      const minutes = Math.floor(seconds / 60)
      const remaining = (seconds % 60).toFixed(0)
      return `${minutes}m ${remaining}s`
    },
    formatTime(isoString) {
      if (!isoString) return '-'
      const d = new Date(isoString)
      const month = String(d.getMonth() + 1).padStart(2, '0')
      const day = String(d.getDate()).padStart(2, '0')
      const hours = String(d.getHours()).padStart(2, '0')
      const mins = String(d.getMinutes()).padStart(2, '0')
      return `${month}-${day} ${hours}:${mins}`
    },
    viewTaskDetail(task) {
      this.$emit('view-report', task.id)
    }
  }
}
</script>

<style scoped>
.script-analysis {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.refresh-btn:hover {
  border-color: #667eea;
  color: #667eea;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  border: 1px solid #e4e7ed;
}

.stat-card .stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.stat-card.success .stat-value {
  color: #67c23a;
}

.stat-card.danger .stat-value {
  color: #f56c6c;
}

.stat-card.info .stat-value {
  color: #409eff;
}

.stat-card .stat-label {
  margin-top: 8px;
  color: #909399;
  font-size: 13px;
}

.section-title {
  margin: 0 0 12px;
  font-size: 15px;
  color: #303133;
}

.recent-tasks-section {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #e4e7ed;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.data-table th {
  text-align: left;
  padding: 10px 12px;
  background: #f5f7fa;
  color: #606266;
  font-weight: 500;
  border-bottom: 1px solid #ebeef5;
}

.data-table td {
  padding: 10px 12px;
  border-bottom: 1px solid #ebeef5;
  color: #303133;
}

.data-table tbody tr:hover {
  background: #f5f7fa;
}

.task-name, .script-name {
  max-width: 200px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.status-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-completed {
  background: #f0f9ff;
  color: #67c23a;
}

.status-failed {
  background: #fef0f0;
  color: #f56c6c;
}

.view-btn {
  padding: 4px 12px;
  background: #409eff;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.view-btn:hover {
  background: #66b1ff;
}

.empty-data {
  text-align: center;
  padding: 40px;
  color: #c0c4cc;
  font-size: 14px;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
