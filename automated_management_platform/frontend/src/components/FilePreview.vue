<template>
  <div class="modal-overlay" @click="close">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>文件预览：{{ filename }}</h3>
        <button class="close-btn" @click="close">&times;</button>
      </div>
      <div class="modal-body">
        <pre><code v-html="formattedJson"></code></pre>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FilePreview',
  props: {
    content: {
      type: [Object, String],
      default: null
    },
    filename: {
      type: String,
      default: ''
    }
  },
  computed: {
    formattedJson() {
      try {
        const jsonStr = typeof this.content === 'string' 
          ? this.content 
          : JSON.stringify(this.content, null, 2)
        return this.syntaxHighlight(jsonStr)
      } catch (error) {
        return 'JSON 格式化失败'
      }
    }
  },
  methods: {
    close() {
      this.$emit('close')
    },
    syntaxHighlight(json) {
      json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      return json.replace(
        /("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g,
        function (match) {
          let color = '#e83e8c' // numbers
          if (/^"/.test(match)) {
            if (/:$/.test(match)) {
              color = '#0d6efd' // keys
            } else {
              color = '#6c757d' // strings
            }
          } else if (/true|false/.test(match)) {
            color = '#28a745' // booleans
          } else if (/null/.test(match)) {
            color = '#6c757d' // null
          }
          return '<span style="color: ' + color + '">' + match + '</span>'
        }
      )
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
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 12px;
  width: 80%;
  max-width: 900px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
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
  word-break: break-all;
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
  overflow-y: auto;
  flex: 1;
}

pre {
  margin: 0;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  overflow-x: auto;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.6;
}

code {
  font-family: inherit;
}

@media (max-width: 768px) {
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
  
  .modal-header {
    padding: 15px 20px;
  }
  
  .modal-body {
    padding: 15px;
  }
  
  pre {
    padding: 15px;
    font-size: 12px;
  }
}
</style>