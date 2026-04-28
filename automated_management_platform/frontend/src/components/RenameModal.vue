<template>
  <teleport to="body">
    <div class="modal-overlay" @click="$emit('cancel')">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ isFolder ? '新建文件夹' : '重命名' }}</h3>
          <button class="close-btn" @click="$emit('cancel')">&times;</button>
        </div>
        <div class="modal-body">
          <div v-if="isFolder" class="input-group">
            <label>文件夹名称</label>
            <input
              ref="nameInput"
              v-model="localName"
              type="text"
              @keydown.enter="handleKeyDown"
              @compositionstart="isComposing = true"
              @compositionend="isComposing = false"
              placeholder="请输入文件夹名称"
              class="name-input"
              autofocus
            />
          </div>
          <div v-else class="input-group">
            <label>新名称</label>
            <input
              ref="nameInput"
              v-model="localName"
              type="text"
              @keydown.enter="handleKeyDown"
              @compositionstart="isComposing = true"
              @compositionend="isComposing = false"
              class="name-input"
              autofocus
            />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-cancel" @click="$emit('cancel')">取消</button>
          <button class="btn btn-primary" @click="$emit('confirm', localName)">确定</button>
        </div>
      </div>
    </div>
  </teleport>
</template>

<script>
export default {
  name: 'RenameModal',
  props: {
    originalName: { type: String, default: '' },
    isFolder: { type: Boolean, default: false }
  },
  data() {
    return {
      localName: this.originalName,
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
    originalName(val) {
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
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}
.modal-content {
  background: white;
  border-radius: 8px;
  width: 360px;
  max-width: 90%;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  border-bottom: 1px solid #ebeef5;
}
.modal-header h3 { margin: 0; font-size: 15px; color: #303133; }
.close-btn {
  background: none; border: none; font-size: 20px; color: #909399;
  cursor: pointer; width: 28px; height: 28px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 4px;
}
.close-btn:hover { background: #f5f7fa; }
.modal-body { padding: 18px; }
.input-group { display: flex; flex-direction: column; gap: 8px; }
.input-group label { font-size: 13px; color: #606266; font-weight: 500; }
.name-input {
  padding: 8px 10px; border: 1px solid #dcdfe6; border-radius: 4px;
  font-size: 13px;
}
.name-input:focus { outline: none; border-color: #667eea; }
.modal-footer {
  display: flex; justify-content: flex-end; gap: 8px;
  padding: 12px 18px; border-top: 1px solid #ebeef5;
}
.btn {
  padding: 6px 16px; border: none; border-radius: 4px;
  cursor: pointer; font-size: 13px;
}
.btn-cancel { background: #f5f7fa; color: #606266; border: 1px solid #dcdfe6; }
.btn-cancel:hover { background: #e4e7ed; }
.btn-primary { background: #667eea; color: white; }
.btn-primary:hover { background: #5568d3; }
</style>
