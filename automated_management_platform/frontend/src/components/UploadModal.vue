<template>
  <div class="modal-overlay" @click="$emit('close')">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>上传文件</h3>
        <button class="close-btn" @click="$emit('close')">&times;</button>
      </div>
      <div class="modal-body">
        <div 
          class="upload-area"
          :class="{ 'drag-over': isDragOver }"
          @dragover.prevent="onDragOver"
          @dragleave.prevent="onDragLeave"
          @drop.prevent="onDrop"
        >
          <div class="upload-icon">📁</div>
          <p>拖拽 JSON 文件到此处，或</p>
          <input 
            type="file" 
            ref="fileInput"
            accept=".json"
            multiple
            @change="onFileSelect"
            class="file-input"
          />
          <button @click="$refs.fileInput.click()" class="upload-btn">
            选择文件
          </button>
        </div>

        <div v-if="selectedFiles.length" class="selected-files">
          <h3>已选择文件：</h3>
          <ul>
            <li v-for="(file, index) in selectedFiles" :key="index">
              <span class="file-name">{{ file.name }}</span>
              <span class="file-size">{{ formatFileSize(file.size) }}</span>
            </li>
          </ul>
          <button @click="uploadFiles" class="upload-action-btn" :disabled="uploading">
            {{ uploading ? '上传中...' : '开始上传' }}
          </button>
        </div>

        <div v-if="message" :class="['message', messageType]">
          {{ message }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api/index.js'

export default {
  name: 'UploadModal',
  props: {
    path: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      selectedFiles: [],
      uploading: false,
      message: '',
      messageType: '',
      isDragOver: false
    }
  },
  methods: {
    onFileSelect(event) {
      const files = Array.from(event.target.files)
      this.selectedFiles = files
      this.clearMessage()
    },
    onDragOver() {
      this.isDragOver = true
    },
    onDragLeave() {
      this.isDragOver = false
    },
    onDrop(event) {
      this.isDragOver = false
      const files = Array.from(event.dataTransfer.files)
      this.selectedFiles = files
      this.clearMessage()
    },
    async uploadFiles() {
      if (!this.selectedFiles.length) return

      this.uploading = true
      this.clearMessage()

      try {
        for (const file of this.selectedFiles) {
          const formData = new FormData()
          formData.append('file', file)
          await api.post(`/upload?path=${encodeURIComponent(this.path)}`, formData, {
            headers: {
              'Content-Type': 'multipart/form-data'
            }
          })
        }
        this.message = `成功上传 ${this.selectedFiles.length} 个文件！`
        this.messageType = 'success'
        this.selectedFiles = []
        this.$refs.fileInput.value = ''
        setTimeout(() => {
          this.$emit('upload-success')
          this.$emit('close')
        }, 1000)
      } catch (error) {
        this.message = `上传失败：${error.response?.data?.detail || error.message}`
        this.messageType = 'error'
      } finally {
        this.uploading = false
      }
    },
    formatFileSize(bytes) {
      if (bytes === 0) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    },
    clearMessage() {
      this.message = ''
      this.messageType = ''
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1002;
}

.modal-content {
  background-color: white;
  border-radius: 12px;
  width: 480px;
  max-width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
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
  color: #303133;
  font-size: 16px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 22px;
  color: #909399;
  cursor: pointer;
  padding: 0;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.3s;
}

.close-btn:hover {
  background-color: #f5f7fa;
  color: #606266;
}

.modal-body {
  padding: 20px;
}

.upload-area {
  border: 2px dashed #dcdfe6;
  border-radius: 8px;
  padding: 30px 20px;
  text-align: center;
  background-color: #fafbfc;
  transition: all 0.3s ease;
}

.upload-area.drag-over {
  border-color: #667eea;
  background-color: #f0f2ff;
}

.upload-icon {
  font-size: 40px;
  margin-bottom: 12px;
}

.upload-area p {
  color: #606266;
  margin: 8px 0;
  font-size: 14px;
}

.file-input {
  display: none;
}

.upload-btn {
  background: #667eea;
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: background 0.3s;
}

.upload-btn:hover {
  background: #5568d3;
}

.selected-files {
  margin-top: 16px;
  padding: 14px;
  background-color: #fafbfc;
  border-radius: 8px;
}

.selected-files h3 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 14px;
}

.selected-files ul {
  list-style: none;
  padding: 0;
  margin: 0 0 12px 0;
  max-height: 150px;
  overflow-y: auto;
}

.selected-files li {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  color: #606266;
  border-bottom: 1px solid #f0f0f0;
  font-size: 13px;
}

.file-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.file-size {
  color: #909399;
  margin-left: 12px;
  flex-shrink: 0;
}

.upload-action-btn {
  background: #67c23a;
  color: white;
  border: none;
  padding: 10px 24px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
  width: 100%;
}

.upload-action-btn:hover:not(:disabled) {
  background: #5daf34;
}

.upload-action-btn:disabled {
  background: #c0c4cc;
  cursor: not-allowed;
}

.message {
  margin-top: 12px;
  padding: 10px 14px;
  border-radius: 6px;
  font-size: 13px;
}

.message.success {
  background-color: #f0f9ff;
  color: #67c23a;
  border: 1px solid #e1f3d8;
}

.message.error {
  background-color: #fef0f0;
  color: #f56c6c;
  border: 1px solid #fde2e2;
}
</style>
