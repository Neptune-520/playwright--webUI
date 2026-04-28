<template>
  <div class="file-list">
    <div v-if="!files || files.length === 0" class="empty-state">
      <span class="empty-icon">📂</span>
      <p>当前目录下暂无文件</p>
    </div>

    <div v-else class="table-container">
      <table>
        <thead>
          <tr>
            <th class="col-name">文件名</th>
            <th class="col-size">大小</th>
            <th class="col-time">修改时间</th>
            <th class="col-actions">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="file in files" :key="file.name" class="file-row">
            <td class="col-name">
              <span class="file-icon">📄</span>
              <span class="file-name-text" :title="file.name">{{ file.name }}</span>
            </td>
            <td class="col-size">{{ formatFileSize(file.size) }}</td>
            <td class="col-time">{{ formatDate(file.upload_time) }}</td>
            <td class="col-actions">
              <button class="action-btn preview-btn" @click="$emit('preview', file.name)" title="查看">
                查看
              </button>
              <button class="action-btn download-btn" @click="$emit('download', file.name)" title="下载">
                下载
              </button>
              <button class="action-btn delete-btn" @click="$emit('request-delete', file.name)" title="删除">
                删除
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FileList',
  props: {
    files: {
      type: Array,
      default: () => []
    }
  },
  methods: {
    formatFileSize(bytes) {
      if (bytes === 0) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    },
    formatDate(dateString) {
      if (!dateString) return 'N/A'
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
.file-list {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.empty-state {
  text-align: center;
  padding: 50px 20px;
  color: #909399;
}

.empty-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 12px;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
}

.table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background-color: #f5f7fa;
}

th {
  padding: 10px 14px;
  text-align: left;
  color: #606266;
  font-weight: 500;
  font-size: 13px;
  border-bottom: 1px solid #ebeef5;
}

.file-row {
  transition: background-color 0.2s;
}

.file-row:hover {
  background-color: #fafbfc;
}

td {
  padding: 10px 14px;
  border-bottom: 1px solid #f0f2f5;
  font-size: 13px;
  color: #303133;
  vertical-align: middle;
}

.col-name {
  width: 40%;
  display: flex;
  align-items: center;
  gap: 8px;
}

.col-size {
  width: 12%;
  color: #909399;
}

.col-time {
  width: 22%;
  color: #909399;
}

.col-actions {
  width: 26%;
}

.file-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.file-name-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #667eea;
  font-weight: 500;
}

.action-btn {
  padding: 4px 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
  color: white;
  margin-right: 4px;
}

.action-btn:last-child {
  margin-right: 0;
}

.preview-btn {
  background-color: #409eff;
}

.preview-btn:hover {
  background-color: #337ecc;
}

.download-btn {
  background-color: #67c23a;
}

.download-btn:hover {
  background-color: #5daf34;
}

.delete-btn {
  background-color: #f56c6c;
}

.delete-btn:hover {
  background-color: #e03e3e;
}
</style>
