<template>
  <div class="file-upload">
    <h2>上传 JSON 文件</h2>
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
          {{ file.name }} ({{ formatFileSize(file.size) }})
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
</template>

<script>
import api from '../api/index.js'

export default {
  name: 'FileUpload',
  props: {
    folder: {
      type: String,
      default: '根目录'
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
  watch: {
    folder() {
      this.selectedFiles = []
      this.clearMessage()
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
          await api.post(`/upload?folder=${encodeURIComponent(this.folder)}`, formData, {
            headers: {
              'Content-Type': 'multipart/form-data'
            }
          })
        }
        this.message = `成功上传 ${this.selectedFiles.length} 个文件！`
        this.messageType = 'success'
        this.selectedFiles = []
        this.$refs.fileInput.value = ''
        this.$emit('upload-success')
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
.file-upload {
  margin-bottom: 20px;
}

.file-upload h2 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 18px;
}

.upload-area {
  border: 2px dashed #c0c4cc;
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  background-color: #fafbfc;
  transition: all 0.3s ease;
}

.upload-area.drag-over {
  border-color: #667eea;
  background-color: #f0f2ff;
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.upload-area p {
  color: #606266;
  margin: 10px 0;
}

.file-input {
  display: none;
}

.upload-btn {
  background: #667eea;
  color: white;
  border: none;
  padding: 10px 24px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}

.upload-btn:hover {
  background: #5568d3;
}

.selected-files {
  margin-top: 20px;
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.selected-files h3 {
  margin: 0 0 10px 0;
  color: #303133;
}

.selected-files ul {
  list-style: none;
  padding: 0;
  margin: 0 0 15px 0;
}

.selected-files li {
  padding: 8px 0;
  color: #606266;
  border-bottom: 1px solid #f0f0f0;
}

.upload-action-btn {
  background: #67c23a;
  color: white;
  border: none;
  padding: 12px 32px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
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
  margin-top: 15px;
  padding: 12px 16px;
  border-radius: 6px;
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
