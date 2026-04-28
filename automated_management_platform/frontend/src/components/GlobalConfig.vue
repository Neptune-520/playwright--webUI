<template>
  <div class="global-config">
    <div class="page-header">
      <h2><span>⚙️</span> 全局配置</h2>
    </div>

    <div class="config-card">
      <h3 class="card-title"><span>🔗</span> 数据上传配置</h3>
      <div class="config-section">
        <div class="form-group">
          <label class="form-label">自动化管理平台API地址</label>
          <input type="text" class="form-input" v-model="config.management_platform_url" placeholder="http://localhost:8001/api/script-results/upload">
          <p class="form-help">脚本执行结果上传的目标地址，用于接收来自 playwright-webui 平台的执行数据</p>
        </div>
      </div>
    </div>

    <div class="action-buttons">
      <button class="btn btn-primary" @click="saveConfig" :disabled="saving">
        {{ saving ? '保存中...' : '保存配置' }}
      </button>
      <button class="btn btn-secondary" @click="loadConfig" :disabled="loading">
        {{ loading ? '加载中...' : '重置' }}
      </button>
    </div>

    <div class="config-info" v-if="savedAt">
      <p>最后保存时间：{{ savedAt }}</p>
    </div>
  </div>
</template>

<script>
import api from '../api/index.js'

export default {
  name: 'GlobalConfig',
  data() {
    return {
      config: {
        management_platform_url: '',
        username: ''
      },
      originalConfig: {},
      loading: false,
      saving: false,
      savedAt: null
    }
  },
  mounted() {
    this.loadConfig()
  },
  methods: {
    async loadConfig() {
      this.loading = true
      try {
        const response = await api.get('/config')
        this.config = { ...response.data }
        this.originalConfig = { ...response.data }
        this.savedAt = null
      } catch (error) {
        console.error('加载配置失败:', error)
        alert('加载配置失败')
      } finally {
        this.loading = false
      }
    },
    async saveConfig() {
      this.saving = true
      try {
        await api.post('/config', this.config)
        this.originalConfig = { ...this.config }
        this.savedAt = new Date().toLocaleString('zh-CN')
        alert('配置保存成功')
      } catch (error) {
        console.error('保存配置失败:', error)
        alert('保存配置失败')
      } finally {
        this.saving = false
      }
    }
  }
}
</script>

<style scoped>
.global-config {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.config-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #e4e7ed;
}

.card-title {
  margin: 0 0 16px;
  font-size: 16px;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.config-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: #606266;
}

.form-input {
  padding: 10px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.form-input:focus {
  border-color: #667eea;
}

.form-help {
  margin: 0;
  font-size: 12px;
  color: #909399;
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #667eea;
  color: #fff;
}

.btn-primary:not(:disabled):hover {
  background: #5568d3;
}

.btn-secondary {
  background: #fff;
  color: #606266;
  border: 1px solid #dcdfe6;
}

.btn-secondary:not(:disabled):hover {
  border-color: #667eea;
  color: #667eea;
}

.config-info {
  background: #f0f9eb;
  border: 1px solid #e1f3d8;
  border-radius: 4px;
  padding: 12px;
}

.config-info p {
  margin: 0;
  font-size: 13px;
  color: #67c23a;
}
</style>
