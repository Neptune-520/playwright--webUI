<template>
  <div class="report-list">
    <div class="page-header">
      <h2>报告列表</h2>
      <button class="refresh-btn" @click="loadResults">
        <span>🔄</span> 刷新
      </button>
    </div>

    <div class="filter-section">
      <div class="filter-left">
        <input type="text" v-model="filters.keyword" class="search-input" placeholder="搜索任务名称/脚本名称" @keydown.enter="loadResults" />
        <select v-model="filters.status" class="filter-select" @change="loadResults">
          <option value="">全部状态</option>
          <option value="completed">已完成</option>
          <option value="failed">失败</option>
        </select>
        <div class="multi-select-wrapper" @click.stop>
          <div class="multi-select" @click="toggleUserDropdown">
            <span class="multi-select-label">{{ selectedUserLabels }}</span>
            <span class="multi-select-arrow">▼</span>
          </div>
          <div class="multi-select-dropdown" v-if="showUserDropdown">
            <input type="text" v-model="userSearchText" class="dropdown-search" placeholder="搜索用户" @click.stop @keydown.stop />
            <div class="dropdown-options">
              <label class="dropdown-option" @click.stop>
                <input type="checkbox" :checked="isAllSelected" @change="toggleAllUsers" />
                <span>全选</span>
              </label>
              <label v-for="uname in filteredUsernames" :key="uname" class="dropdown-option" @click.stop>
                <input type="checkbox" :value="uname" v-model="selectedUsers" @change="onUserSelectionChange" />
                <span>{{ uname }}</span>
              </label>
            </div>
          </div>
        </div>
        <input type="date" v-model="filters.start_date" class="filter-input" @change="loadResults" />
        <input type="date" v-model="filters.end_date" class="filter-input" @change="loadResults" />
      </div>
      <div class="filter-right">
        <button class="filter-btn" @click="loadResults">搜索</button>
        <button class="filter-btn reset" @click="resetFilters">重置</button>
      </div>
    </div>

    <div class="results-table">
      <table>
        <thead>
          <tr>
            <th>任务名称</th>
            <th>操作员</th>
            <th>脚本数量</th>
            <th>状态</th>
            <th>通过率</th>
            <th>总步骤</th>
            <th>执行时长</th>
            <th>执行时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="results.length === 0">
            <td colspan="9" class="empty-cell">暂无数据</td>
          </tr>
          <tr v-for="item in results" :key="item.id" class="result-row">
            <td>{{ item.task_name }}</td>
            <td>{{ item.username || '-' }}</td>
            <td>{{ item.script_count || 1 }}</td>
            <td>
              <span class="status-badge" :class="'status-' + item.status">
                {{ item.status === 'completed' ? '成功' : '失败' }}
              </span>
            </td>
            <td>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: item.pass_rate + '%' }"></div>
              </div>
              <span class="progress-text">{{ item.pass_rate }}%</span>
            </td>
            <td>{{ item.total_steps }}</td>
            <td>{{ formatDuration(item.total_duration) }}</td>
            <td>{{ formatDate(item.started_at) }}</td>
            <td>
              <button class="action-btn view-btn" @click="viewDetail(item)">详情</button>
              <button class="action-btn copy-link-btn" @click="copyReportLink(item)">复制链接</button>
              <button class="action-btn delete-btn" @click="deleteResult(item)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="pagination" v-if="total > 0">
      <select v-model.number="pageSize" @change="onPageSizeChange" class="page-size-select">
        <option :value="10">10条/页</option>
        <option :value="20">20条/页</option>
        <option :value="50">50条/页</option>
        <option :value="100">100条/页</option>
      </select>
      <button class="page-btn" :disabled="page <= 1" @click="goToPage(page - 1)">上一页</button>
      <span class="page-info">第 {{ page }} 页 / 共 {{ totalPages }} 页 ({{ total }} 条)</span>
      <button class="page-btn" :disabled="page >= totalPages" @click="goToPage(page + 1)">下一页</button>
    </div>

    <div class="detail-modal" v-if="showDetail" @click.self="closeDetail">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ detailData.task_name }} - 执行详情</h3>
          <button class="close-btn" @click="closeDetail">✕</button>
        </div>
        <div class="modal-body">
          <div class="detail-info">
            <div class="info-item">
              <span class="info-label">任务名称：</span>
              <span>{{ detailData.task_name }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">脚本名称：</span>
              <span>{{ detailData.script_name }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">状态：</span>
              <span class="status-badge" :class="'status-' + detailData.status">
                {{ detailData.status === 'completed' ? '成功' : '失败' }}
              </span>
            </div>
            <div class="info-item">
              <span class="info-label">执行时间：</span>
              <span>{{ formatDate(detailData.started_at) }} - {{ formatDate(detailData.finished_at) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">总时长：</span>
              <span>{{ formatDuration(detailData.total_duration) }}</span>
            </div>
          </div>

          <h4 class="steps-title">步骤详情</h4>
          <div class="steps-table">
            <table>
              <thead>
                <tr>
                  <th>序号</th>
                  <th>步骤名称</th>
                  <th>操作类型</th>
                  <th>状态</th>
                  <th>耗时</th>
                  <th>错误信息</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="step in detailData.step_results" :key="step.step_order">
                  <td>{{ step.step_order }}</td>
                  <td>{{ step.step_name }}</td>
                  <td>{{ step.action_type }}</td>
                  <td>
                    <span class="step-status" :class="'step-' + step.status">
                      {{ step.status === 'passed' ? '通过' : step.status === 'failed' ? '失败' : '跳过' }}
                    </span>
                  </td>
                  <td>{{ step.duration.toFixed(2) }}s</td>
                  <td class="error-cell">{{ step.error || '-' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api/index.js'

export default {
  name: 'ReportList',
  props: {
    loadReport: {
      type: Function,
      default: null
    }
  },
  data() {
    return {
      results: [],
      page: 1,
      pageSize: 20,
      total: 0,
      filters: {
        status: '',
        keyword: '',
        start_date: '',
        end_date: ''
      },
      allUsernames: [],
      selectedUsers: [],
      showUserDropdown: false,
      userSearchText: '',
      showDetail: false,
      detailData: {}
    }
  },
  computed: {
    totalPages() {
      return Math.ceil(this.total / this.pageSize)
    },
    selectedUserLabels() {
      if (this.selectedUsers.length === 0) return '全部用户'
      if (this.selectedUsers.length === this.allUsernames.length) return '全部用户'
      if (this.selectedUsers.length <= 3) return this.selectedUsers.join(', ')
      return `${this.selectedUsers.slice(0, 3).join(', ')} 等${this.selectedUsers.length}个用户`
    },
    filteredUsernames() {
      if (!this.userSearchText) return this.allUsernames
      const keyword = this.userSearchText.toLowerCase()
      return this.allUsernames.filter(u => u.toLowerCase().includes(keyword))
    },
    isAllSelected() {
      return this.allUsernames.length > 0 && this.selectedUsers.length === this.allUsernames.length
    }
  },
  mounted() {
    this.loadUsernames()
    this.loadResults()
    document.addEventListener('click', this.handleOutsideClick)
  },
  beforeDestroy() {
    document.removeEventListener('click', this.handleOutsideClick)
  },
  methods: {
    handleOutsideClick() {
      if (this.showUserDropdown) {
        this.showUserDropdown = false
      }
    },
    async loadUsernames() {
      try {
        const response = await api.get('/script-results', { params: { page: 1, page_size: 100 } })
        const allData = response.data.data || []
        const usernameSet = new Set()
        allData.forEach(r => {
          const u = r.get ? r.get('username') : r.username
          if (u) usernameSet.add(u)
        })
        this.allUsernames = Array.from(usernameSet).sort()
      } catch (error) {
        console.error('加载用户名失败:', error)
      }
    },
    async loadResults() {
      try {
        const params = {
          page: this.page,
          page_size: this.pageSize
        }
        if (this.filters.status) params.status = this.filters.status
        if (this.filters.keyword) params.keyword = this.filters.keyword
        if (this.allUsernames.length > 0 && this.selectedUsers.length > 0 && this.selectedUsers.length < this.allUsernames.length) {
          params.username = this.selectedUsers.join(',')
        }
        if (this.filters.start_date) params.start_date = this.filters.start_date
        if (this.filters.end_date) params.end_date = this.filters.end_date

        const response = await api.get('/script-results', { params })
        this.results = response.data.data || []
        this.total = response.data.total || 0
        this.page = response.data.page || 1
      } catch (error) {
        console.error('加载结果失败:', error)
        this.results = []
      }
    },
    goToPage(newPage) {
      if (newPage >= 1 && newPage <= this.totalPages) {
        this.page = newPage
        this.loadResults()
      }
    },
    onPageSizeChange() {
      this.page = 1
      this.loadResults()
    },
    resetFilters() {
      this.filters = { status: '', keyword: '', start_date: '', end_date: '' }
      this.selectedUsers = []
      this.page = 1
      this.loadResults()
    },
    toggleUserDropdown() {
      this.showUserDropdown = !this.showUserDropdown
    },
    toggleAllUsers() {
      if (this.isAllSelected) {
        this.selectedUsers = []
      } else {
        this.selectedUsers = [...this.allUsernames]
      }
      this.onUserSelectionChange()
    },
    onUserSelectionChange() {
      this.loadResults()
    },
    viewDetail(item) {
      if (this.loadReport) {
        this.loadReport(item.id)
      } else {
        this.detailData = item
        this.showDetail = true
      }
    },
    copyReportLink(item) {
      const url = `${window.location.origin}${window.location.pathname}?report=${item.id}`
      navigator.clipboard.writeText(url).then(() => {
        alert('链接已复制到剪贴板')
      }).catch(() => {
        alert('复制失败,请手动复制')
      })
    },
    closeDetail() {
      this.showDetail = false
      this.detailData = {}
    },
    async deleteResult(item) {
      if (!confirm(`确定删除任务 "${item.task_name}" 的执行记录吗？`)) return
      try {
        await api.delete(`/script-results/${item.id}`)
        this.loadResults()
      } catch (error) {
        console.error('删除失败:', error)
        alert('删除失败')
      }
    },
    formatDuration(seconds) {
      if (!seconds) return '0s'
      if (seconds < 60) return seconds.toFixed(1) + 's'
      const minutes = Math.floor(seconds / 60)
      const remaining = (seconds % 60).toFixed(0)
      return `${minutes}m ${remaining}s`
    },
    formatDate(dateString) {
      if (!dateString) return '-'
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
  }
}
</script>

<style scoped>
.report-list {
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

.filter-section {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  background: #fff;
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.filter-left, .filter-right {
  display: flex;
  gap: 8px;
  align-items: center;
}

.multi-select-wrapper {
  position: relative;
}

.multi-select {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  min-width: 160px;
  background: #fff;
}

.multi-select:hover {
  border-color: #667eea;
}

.multi-select-label {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.multi-select-arrow {
  font-size: 10px;
  color: #909399;
  margin-left: 8px;
}

.multi-select-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  z-index: 100;
  background: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  min-width: 200px;
  margin-top: 4px;
}

.dropdown-search {
  width: 100%;
  padding: 8px 12px;
  border: none;
  border-bottom: 1px solid #ebeef5;
  font-size: 13px;
  outline: none;
  box-sizing: border-box;
}

.dropdown-options {
  max-height: 200px;
  overflow-y: auto;
  padding: 4px 0;
}

.dropdown-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  cursor: pointer;
  font-size: 13px;
}

.dropdown-option:hover {
  background: #f5f7fa;
}

.filter-select, .filter-input, .search-input {
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 13px;
  outline: none;
}

.search-input {
  width: 200px;
}

.search-input:focus {
  border-color: #667eea;
}

.filter-btn {
  padding: 8px 16px;
  background: #667eea;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: background 0.2s;
}

.filter-btn:hover {
  background: #5568d3;
}

.filter-btn.reset {
  background: #909399;
}

.filter-btn.reset:hover {
  background: #7c7f85;
}

.results-table {
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  overflow: auto;
}

.results-table table {
  width: 100%;
  border-collapse: collapse;
}

.results-table thead {
  background: #fafbfc;
  position: sticky;
  top: 0;
  z-index: 1;
}

.results-table th {
  padding: 12px;
  text-align: left;
  color: #606266;
  font-weight: 500;
  font-size: 13px;
  border-bottom: 1px solid #ebeef5;
}

.results-table td {
  padding: 12px;
  font-size: 13px;
  color: #303133;
  border-bottom: 1px solid #ebeef5;
}

.result-row:hover {
  background: #fafbfc;
}

.empty-cell {
  text-align: center;
  padding: 60px !important;
  color: #c0c4cc;
}

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-completed {
  background: #f0f9eb;
  color: #67c23a;
}

.status-failed {
  background: #fef0f0;
  color: #f56c6c;
}

.progress-bar {
  display: inline-block;
  width: 80px;
  height: 8px;
  background: #ebeef5;
  border-radius: 4px;
  overflow: hidden;
  margin-right: 8px;
  vertical-align: middle;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #67c23a, #85ce61);
  border-radius: 4px;
}

.progress-text {
  font-size: 12px;
  color: #606266;
  vertical-align: middle;
}

.action-btn {
  padding: 4px 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  color: #fff;
  margin-right: 6px;
}

.view-btn {
  background: #409eff;
}

.view-btn:hover {
  background: #337ecc;
}

.delete-btn {
  background: #f56c6c;
}

.delete-btn:hover {
  background: #e03e3e;
}

.copy-link-btn {
  background: #667eea;
}

.copy-link-btn:hover {
  background: #5568d3;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  padding: 12px;
}

.page-size-select {
  padding: 6px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 13px;
  outline: none;
  cursor: pointer;
}

.page-btn {
  padding: 8px 16px;
  background: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-btn:not(:disabled):hover {
  border-color: #667eea;
  color: #667eea;
}

.page-info {
  font-size: 13px;
  color: #606266;
}

.detail-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: #fff;
  border-radius: 8px;
  width: 80%;
  max-width: 900px;
  max-height: 80vh;
  overflow: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #ebeef5;
}

.modal-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #909399;
}

.close-btn:hover {
  color: #303133;
}

.modal-body {
  padding: 20px;
}

.detail-info {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.info-item {
  font-size: 13px;
}

.info-label {
  color: #909399;
  margin-right: 8px;
}

.steps-title {
  margin: 0 0 12px;
  font-size: 15px;
  color: #303133;
}

.steps-table table {
  width: 100%;
  border-collapse: collapse;
}

.steps-table th, .steps-table td {
  padding: 10px 12px;
  text-align: left;
  border-bottom: 1px solid #ebeef5;
  font-size: 13px;
}

.steps-table thead {
  background: #fafbfc;
}

.step-status {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.step-passed {
  background: #f0f9eb;
  color: #67c23a;
}

.step-failed {
  background: #fef0f0;
  color: #f56c6c;
}

.step-skipped {
  background: #fdf6ec;
  color: #e6a23c;
}

.error-cell {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #f56c6c;
}

@media (max-width: 768px) {
  .filter-section {
    flex-direction: column;
  }
  .filter-left, .filter-right {
    flex-wrap: wrap;
  }
  .detail-info {
    grid-template-columns: 1fr;
  }
}
</style>
