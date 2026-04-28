<template>
  <div class="modal-overlay" @click="handleCancel">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>确认删除</h3>
        <button class="close-btn" @click="handleCancel">&times;</button>
      </div>
      <div class="modal-body">
        <p class="warning-text">确定要删除以下文件吗？</p>
        <p class="filename-text">"{{ filename }}"</p>
        <p class="hint-text">此操作不可撤销。</p>
      </div>
      <div class="modal-footer">
        <button class="btn btn-cancel" @click="handleCancel">取消</button>
        <button class="btn btn-confirm" @click="handleConfirm">确认删除</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DeleteConfirmModal',
  props: {
    filename: {
      type: String,
      default: ''
    }
  },
  methods: {
    handleConfirm() {
      this.$emit('confirm', this.filename)
    },
    handleCancel() {
      this.$emit('cancel')
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
  z-index: 1001;
}

.modal-content {
  background-color: white;
  border-radius: 12px;
  width: 400px;
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
  text-align: center;
}

.warning-text {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 16px;
}

.filename-text {
  margin: 0 0 15px 0;
  color: #667eea;
  font-weight: 600;
  font-size: 15px;
  word-break: break-all;
}

.hint-text {
  margin: 0;
  color: #909399;
  font-size: 13px;
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

.btn-confirm {
  background-color: #f56c6c;
}

.btn-confirm:hover {
  background-color: #e03e3e;
}
</style>
