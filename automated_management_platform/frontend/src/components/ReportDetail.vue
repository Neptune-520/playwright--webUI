<template>
  <div class="report-detail">
    <div class="page-header">
      <h2><i class="bi bi-file-earmark-text"></i> 报告详情</h2>
      <div>
        <button class="btn-copy" @click="copyLink">
          <i class="bi bi-link-45deg"></i> 复制链接
        </button>
        <button class="btn-back" @click="goBack">
          <i class="bi bi-arrow-left"></i> 返回
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <span class="loading-spinner">⏳</span>
      <p>加载中...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <span class="error-icon">⚠</span>
      <p>{{ error }}</p>
      <button class="retry-btn" @click="loadReport">重试</button>
    </div>

    <template v-else-if="report && !loading">
      <div class="stat-grid">
        <div class="stat-card">
          <div class="stat-label">任务名称</div>
          <div class="stat-value">{{ report.task_name || '-' }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">脚本数量</div>
          <div class="stat-value">{{ report.script_count || 1 }}</div>
        </div>
        <div class="stat-card" :class="statusClass">
          <div class="stat-label">状态</div>
          <div class="stat-value">
            <span class="status-badge" :class="'status-' + report.status">
              {{ statusText }}
            </span>
          </div>
        </div>
        <div class="stat-card info">
          <div class="stat-label">通过率</div>
          <div class="stat-value">
            <span :class="passRateClass">{{ report.pass_rate != null ? (report.pass_rate + '%') : 'N/A' }}</span>
          </div>
        </div>
        <div class="stat-card success">
          <div class="stat-label">通过</div>
          <div class="stat-value">{{ report.passed_steps != null ? report.passed_steps : '-' }}</div>
        </div>
        <div class="stat-card danger">
          <div class="stat-label">失败</div>
          <div class="stat-value">{{ report.failed_steps != null ? report.failed_steps : '-' }}</div>
        </div>
        <div class="stat-card warning">
          <div class="stat-label">跳过</div>
          <div class="stat-value">{{ report.skipped_steps != null ? report.skipped_steps : '-' }}</div>
        </div>
        <div class="stat-card info">
          <div class="stat-label">总步骤</div>
          <div class="stat-value">{{ report.total_steps != null ? report.total_steps : '-' }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">执行时间</div>
          <div class="stat-value time-value">{{ formatDate(report.started_at) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">执行时长</div>
          <div class="stat-value">{{ formatDuration(report.total_duration) }}</div>
        </div>
      </div>

      <div class="steps-section">
        <div class="steps-header">
          <h3 class="section-title"><i class="bi bi-list-check"></i> 步骤详情</h3>
          <div class="btn-group">
            <button class="btn-toggle" @click="expandAll">
              <i class="bi bi-arrows-expand"></i> 展开全部
            </button>
            <button class="btn-toggle" @click="collapseAll">
              <i class="bi bi-arrows-collapse"></i> 收起全部
            </button>
          </div>
        </div>
        <div class="accordion">
          <div v-if="groupedSteps.length > 0">
            <div class="accordion-item" v-for="(group, gIndex) in groupedSteps" :key="gIndex">
              <div class="accordion-header" @click="toggleStep(gIndex)">
                <button class="accordion-button" :class="{ collapsed: stepOpenStates[gIndex] === false }">
                  <i class="bi bi-code-slash"></i>
                  {{ group.scriptName }}
                </button>
              </div>
              <div class="accordion-body" v-show="stepOpenStates[gIndex] !== false">
                <div class="steps-table">
                  <table>
                    <thead>
                      <tr>
                        <th>序号</th>
                        <th>步骤名称</th>
                        <th>状态</th>
                        <th>耗时</th>
                        <th>错误信息</th>
                      </tr>
                    </thead>
                    <tbody>
                      <template v-for="step in group.steps" :key="step.step_order">
                        <tr class="step-row" :class="{ 'action-set-step': step.action_values && step.action_values.sub_steps, 'parent-collapsed': stepSubStepOpenStates[step.step_order] === false }" @click="step.action_values && step.action_values.sub_steps && toggleStepGroup(step.step_order)">
                          <td class="step-order-cell">
                            <span v-if="step.action_values && step.action_values.sub_steps" class="expand-icon">
                              <i :class="stepSubStepOpenStates[step.step_order] !== false ? 'bi bi-chevron-down' : 'bi bi-chevron-right'"></i>
                            </span>
                            <span v-else class="expand-placeholder"></span>
                            {{ step.step_order }}
                          </td>
                          <td class="step-name-cell">
                            <span class="step-label" :class="{ 'action-set-label': step.action_values && step.action_values.sub_steps }">
                              <i v-if="step.action_values && step.action_values.sub_steps" class="bi bi-braces"></i>
                              {{ step.step_name.replace(/^\[[^\]]+\]\s*/, '') }}
                            </span>
                          </td>
                          <td>
                            <span class="step-status" :class="'step-' + step.status">
                              {{ step.status === 'passed' ? '通过' : step.status === 'failed' ? '失败' : '跳过' }}
                            </span>
                          </td>
                          <td>{{ step.duration != null ? step.duration.toFixed(2) + 's' : 'N/A' }}</td>
                          <td class="error-cell">
                            <div v-if="step.error" class="error-display-wrapper">
                              <div class="formatted-error-msg">{{ step.error }}</div>
                              <button v-if="step.error_stack && step.error_stack !== step.error" 
                                      class="btn-toggle-console" 
                                      @click.stop="toggleConsoleError(step.step_order)">
                                <i class="bi bi-terminal"></i> 控制台报错
                              </button>
                              <div v-show="consoleOpenStates[step.step_order]" class="console-error-content">
                                <strong>控制台原始报错:</strong><br>
                                <pre>{{ step.error_stack }}</pre>
                              </div>
                            </div>
                            <span v-else>-</span>
                          </td>
                        </tr>
                        <tr v-if="step.action_values && step.action_values.sub_steps && stepSubStepOpenStates[step.step_order] !== false" 
                            v-for="subStep in step.action_values.sub_steps" :key="step.step_order + '-' + subStep.step_name" 
                            class="sub-step-row">
                          <td class="sub-step-order-cell">{{ step.step_order }}-{{ subStep.step_name }}</td>
                          <td class="step-name-cell">
                            <span class="sub-step-label">
                              <i class="bi bi-dash"></i>
                              {{ subStep.step_name }}
                            </span>
                          </td>
                          <td>
                            <span class="step-status" :class="'step-' + subStep.status">
                              {{ subStep.status === 'passed' ? '通过' : subStep.status === 'failed' ? '失败' : '跳过' }}
                            </span>
                          </td>
                          <td>{{ step.duration != null ? step.duration.toFixed(2) + 's' : 'N/A' }}</td>
                          <td class="error-cell">
                            <div v-if="subStep.error" class="error-display-wrapper">
                              <div class="formatted-error-msg">{{ subStep.error }}</div>
                              <button v-if="subStep.error_stack && subStep.error_stack !== subStep.error" 
                                      class="btn-toggle-console" 
                                      @click.stop="toggleConsoleError(step.step_order + '-' + subStep.step_name)">
                                <i class="bi bi-terminal"></i> 控制台报错
                              </button>
                              <div v-show="consoleOpenStates[step.step_order + '-' + subStep.step_name]" class="console-error-content">
                                <strong>控制台原始报错:</strong><br>
                                <pre>{{ subStep.error_stack }}</pre>
                              </div>
                            </div>
                            <span v-else>-</span>
                          </td>
                        </tr>
                      </template>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="empty-steps">
            暂无步骤数据
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import api from '../api/index.js'

export default {
  name: 'ReportDetail',
  props: {
    reportId: {
      type: [Number, String],
      default: null
    }
  },
  data() {
    return {
      report: null,
      loading: false,
      error: null,
      stepOpenStates: {},
      consoleOpenStates: {},
      stepSubStepOpenStates: {}
    }
  },
  computed: {
    statusText() {
      if (!this.report) return '-'
      return this.report.status === 'completed' ? '成功' : '失败'
    },
    statusClass() {
      if (!this.report) return ''
      return this.report.status === 'completed' ? 'success' : 'danger'
    },
    passRateClass() {
      if (!this.report) return ''
      const rate = this.report.pass_rate || 0
      if (rate >= 80) return 'text-success'
      if (rate >= 50) return 'text-warning'
      return 'text-danger'
    },
    groupedSteps() {
      if (!this.report || !this.report.step_results) return []
      const groups = {}
      const order = []
      this.report.step_results.forEach(step => {
        let scriptName = this.report.script_name || '脚本'
        const match = step.step_name.match(/^\[([^\]]+)\]/)
        if (match) {
          scriptName = match[1]
        }
        if (!groups[scriptName]) {
          groups[scriptName] = []
          order.push(scriptName)
        }
        groups[scriptName].push(step)
      })
      return order.map(name => ({
        scriptName: name,
        steps: groups[name]
      }))
    }
  },
  mounted() {
    this.loadReport()
  },
  methods: {
    async loadReport() {
      if (!this.reportId) {
        this.error = '未提供报告ID'
        this.loading = false
        return
      }
      this.loading = true
      this.error = null
      try {
        const response = await api.get(`/script-results/${this.reportId}`)
        this.report = response.data
        this.stepOpenStates = {}
        this.stepSubStepOpenStates = {}
        const steps = this.groupedSteps
        if (steps.length > 0) {
          steps.forEach((_, i) => {
            this.stepOpenStates[i] = true
          })
          steps.forEach(group => {
            group.steps.forEach(step => {
              if (step.action_values && step.action_values.sub_steps) {
                this.stepSubStepOpenStates[step.step_order] = true
              }
            })
          })
        }
      } catch (error) {
        console.error('加载报告失败:', error)
        this.error = '加载报告失败,请检查报告ID是否正确'
      } finally {
        this.loading = false
      }
    },
    goBack() {
      this.$emit('back')
    },
    copyLink() {
      const url = `${window.location.origin}${window.location.pathname}?report=${this.reportId}`
      navigator.clipboard.writeText(url).then(() => {
        alert('链接已复制到剪贴板')
      }).catch(() => {
        alert('复制失败,请手动复制')
      })
    },
    toggleStep(index) {
      this.stepOpenStates[index] = !this.stepOpenStates[index]
    },
    toggleConsoleError(stepOrder) {
      this.consoleOpenStates[stepOrder] = !this.consoleOpenStates[stepOrder]
    },
    toggleStepGroup(stepOrder) {
      this.stepSubStepOpenStates[stepOrder] = !this.stepSubStepOpenStates[stepOrder]
    },
    expandAll() {
      this.groupedSteps.forEach((_, i) => {
        this.stepOpenStates[i] = true
      })
      if (this.report && this.report.step_results) {
        this.report.step_results.forEach(step => {
          if (step.action_values && step.action_values.sub_steps) {
            this.stepSubStepOpenStates[step.step_order] = true
          }
        })
      }
    },
    collapseAll() {
      this.groupedSteps.forEach((_, i) => {
        this.stepOpenStates[i] = false
      })
      if (this.report && this.report.step_results) {
        this.report.step_results.forEach(step => {
          if (step.action_values && step.action_values.sub_steps) {
            this.stepSubStepOpenStates[step.step_order] = false
          }
        })
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
.report-detail {
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

.btn-back, .btn-copy {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  margin-left: 8px;
}

.btn-back {
  background: #fff;
  border: 1px solid #dcdfe6;
  color: #303133;
}

.btn-back:hover {
  border-color: #667eea;
  color: #667eea;
}

.btn-copy {
  background: #667eea;
  color: #fff;
}

.btn-copy:hover {
  background: #5568d3;
}

.loading-state, .error-state {
  text-align: center;
  padding: 60px;
  color: #909399;
}

.loading-spinner {
  font-size: 48px;
  display: block;
  margin-bottom: 12px;
}

.error-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 12px;
  color: #f56c6c;
}

.retry-btn {
  margin-top: 12px;
  padding: 8px 24px;
  background: #667eea;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
}

.retry-btn:hover {
  background: #5568d3;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
}

.stat-card {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #e4e7ed;
  text-align: center;
}

.stat-card .stat-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-card .stat-value {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.time-value {
  font-size: 13px !important;
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

.stat-card.warning .stat-value {
  color: #e6a23c;
}

.text-success {
  color: #67c23a !important;
}

.text-warning {
  color: #e6a23c !important;
}

.text-danger {
  color: #f56c6c !important;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 14px;
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

.steps-section {
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  overflow: hidden;
}

.steps-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #ebeef5;
  background: #fafbfc;
}

.section-title {
  margin: 0;
  font-size: 15px;
  color: #303133;
}

.btn-group {
  display: flex;
  gap: 4px;
}

.btn-toggle {
  padding: 4px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background: #fff;
  cursor: pointer;
  font-size: 12px;
  color: #606266;
  display: flex;
  align-items: center;
  gap: 4px;
}

.btn-toggle:hover {
  border-color: #667eea;
  color: #667eea;
}

.accordion {
  width: 100%;
}

.accordion-item {
  border-bottom: none;
}

.accordion-header {
  background: #fff;
  cursor: pointer;
}

.accordion-button {
  width: 100%;
  padding: 12px 16px;
  border: none;
  background: none;
  text-align: left;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.accordion-button:hover {
  background: #f5f7fa;
}

.accordion-body {
  padding: 0 16px 16px;
}

.steps-table {
  width: 100%;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  overflow: auto;
}

.steps-table table {
  width: 100%;
  border-collapse: collapse;
}

.steps-table thead {
  background: #fafbfc;
  position: sticky;
  top: 0;
}

.steps-table th {
  padding: 10px 12px;
  text-align: left;
  color: #606266;
  font-weight: 500;
  font-size: 13px;
  border-bottom: 1px solid #ebeef5;
}

.steps-table td {
  padding: 10px 12px;
  font-size: 13px;
  color: #303133;
  border-bottom: 1px solid #ebeef5;
}

.steps-table tbody tr:last-child td {
  border-bottom: none;
}

.steps-table tbody tr:hover {
  background: #fafbfc;
}

.step-name-cell {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.empty-steps {
  text-align: center;
  padding: 40px;
  color: #c0c4cc;
}

.step-status {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
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
  max-width: 250px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #f56c6c;
}

.error-cell .error-display-wrapper {
  white-space: normal;
}

.error-cell .formatted-error-msg {
  font-size: 12px;
  line-height: 1.5;
  color: #f56c6c;
  word-break: break-word;
}

.error-cell .btn-toggle-console {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  margin-top: 6px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background: #fff;
  color: #606266;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s;
}

.error-cell .btn-toggle-console:hover {
  border-color: #409eff;
  color: #409eff;
}

.error-cell .console-error-content {
  margin-top: 8px;
  padding: 8px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 4px;
}

.error-cell .console-error-content pre {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 8px;
  border-radius: 4px;
  font-size: 11px;
  max-height: 200px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 4px 0 0 0;
}

@media (max-width: 1024px) {
  .stat-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .stat-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .page-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
}

.action-set-step {
  cursor: pointer;
  background: #f5f7fa;
}

.action-set-step:hover {
  background: #ebecf0;
}

.action-set-step .step-name-cell {
  font-weight: 600;
}

.step-order-cell {
  position: relative;
}

.expand-icon {
  display: inline-block;
  margin-right: 6px;
  font-size: 12px;
  color: #909399;
  transition: transform 0.2s;
}

.expand-placeholder {
  display: inline-block;
  margin-right: 6px;
  width: 12px;
}

.step-label.action-set-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.step-label.action-set-label i {
  color: #909399;
  font-size: 14px;
}

.action-set-label i.bi-braces::before {
  font-size: 12px;
}

.sub-step-row {
  background: #f8f9fb;
}

.sub-step-row:hover {
  background: #f0f2f5;
}

.sub-step-order-cell {
  font-size: 12px;
  color: #909399;
  padding-left: 36px !important;
}

.sub-step-label {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #606266;
}

.sub-step-label i {
  font-size: 10px;
  color: #c0c4cc;
}

.parent-collapsed {
  border-bottom: 1px solid #ebeef5;
}
</style>
