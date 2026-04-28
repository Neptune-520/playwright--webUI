<template>
  <div class="modal-overlay" @click="$emit('cancel')">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>{{ title }}</h3>
        <button class="close-btn" @click="$emit('cancel')">&times;</button>
      </div>
      <div class="modal-body">
        <p v-if="isDelete" class="warning-text">确定要删除目录 "{{ folderName }}" 吗？目录内的所有文件也将被删除。</p>
        <div v-if="!isDelete" class="input-group">
          <label>目录名称</label>
          <input
            ref="nameInput"
            v-model="localName"
            type="text"
            @keydown.enter="handleKeyDown"
            @compositionstart="isComposing = true"
            @compositionend="isComposing = false"
            placeholder="请输入目录名称"
            class="folder-input"
            autofocus
          />
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-cancel" @click="$emit('cancel')">取消</button>
        <button class="btn btn-confirm" :class="isDelete ? 'btn-danger' : 'btn-primary'" @click="$emit('confirm', localName)">
          {{ isDelete ? '确认删除' : '确认' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FolderModal',
  props: {
    title: { type: String, default: '' },
    folderName: { type: String, default: '' },
    isDelete: { type: Boolean, default: false }
  },
  data() {
    return {
      localName: this.folderName,
      isComposing: false
    }
  },
  methods: {
    handleKeyDown(event) {
      if (!this.isComposing) {
        event.preventDefault()
        this.$emit('confirm', this.localName)
      }
    }
  },
  watch: {
    folderName(val) {
      this.localName = val
    }
  },
  mounted() {
    this.$nextTick(() => {
      const input = this.$refs.nameInput
      if (input) input.focus()
    })
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
  width: 420px;
  max-width: 90%;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #ebeef5;
}

.modal-header h3 {
  margin: 0;
  color: #303133;
  font-size: 18px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #909399;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
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
  padding: 24px;
}

.warning-text {
  margin: 0 0 16px 0;
  color: #606266;
  font-size: 15px;
  line-height: 1.6;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-group label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.folder-input {
  padding: 10px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.folder-input:focus {
  outline: none;
  border-color: #667eea;
}

.modal-footer {
  display: flex;
  justify-content: center;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #ebeef5;
}

.btn {
  padding: 10px 24px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
  color: white;
}

.btn-cancel {
  background-color: #909399;
}

.btn-cancel:hover {
  background-color: #82848a;
}

.btn-primary {
  background-color: #667eea;
}

.btn-primary:hover {
  background-color: #5568d3;
}

.btn-danger {
  background-color: #f56c6c;
}

.btn-danger:hover {
  background-color: #e03e3e;
}
</style>
