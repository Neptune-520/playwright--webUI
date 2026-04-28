<template>
  <tr
    class="item-row"
    :class="{ selected: selected }"
    @dblclick="handleDblClick"
  >
    <td class="col-check">
      <input v-if="!item.is_folder" type="checkbox" :checked="selected" @change="$emit('toggle-select', item.name)" />
    </td>
    <td class="col-name">
      <span class="item-icon">{{ item.is_folder ? '📁' : '📄' }}</span>
      <span class="item-name" @dblclick.stop="handleDblClick">{{ item.name }}</span>
    </td>
    <td class="col-size">{{ item.is_folder ? '-' : formatFileSize(item.size) }}</td>
    <td class="col-time">{{ formatDate(item.modified_time) }}</td>
    <td class="col-actions">
      <button v-if="item.is_folder" class="action-btn open-btn" @click.stop="$emit('open-folder', item.name)" title="打开">
        打开
      </button>
      <template v-else>
        <button class="action-btn preview-btn" @click.stop="$emit('preview', item.name)" title="查看">
          查看
        </button>
        <button class="action-btn download-btn" @click.stop="$emit('download', item.name)" title="下载">
          下载
        </button>
      </template>
      <button class="action-btn rename-btn" @click.stop="$emit('rename', item.name)" title="重命名">
        重命名
      </button>
      <button class="action-btn delete-btn" @click.stop="$emit('request-delete', item.name)" title="删除">
        删除
      </button>
    </td>
  </tr>
</template>

<script>
export default {
  name: 'ExplorerItem',
  props: {
    item: { type: Object, required: true },
    selected: { type: Boolean, default: false }
  },
  methods: {
    handleDblClick() {
      if (this.item.is_folder) {
        this.$emit('open-folder', this.item.name)
      } else {
        this.$emit('preview', this.item.name)
      }
    },
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
        year: 'numeric', month: '2-digit', day: '2-digit',
        hour: '2-digit', minute: '2-digit', second: '2-digit'
      })
    }
  }
}
</script>

<style scoped>
.item-row {
  cursor: default;
  transition: background-color 0.15s;
  user-select: none;
}
.item-row:hover {
  background-color: #f5f7fa;
}
.item-row.selected {
  background-color: #ecf5ff;
}
.item-row td {
  padding: 6px 12px;
  border-bottom: 1px solid #f0f2f5;
  font-size: 13px;
  color: #303133;
  vertical-align: middle;
}
.col-check {
  width: 36px;
  text-align: center;
}
.col-name {
  display: flex;
  align-items: center;
  gap: 8px;
  overflow: hidden;
}
.item-icon {
  font-size: 16px;
  flex-shrink: 0;
}
.item-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  cursor: default;
}
.col-size {
  width: 80px;
  color: #909399;
  white-space: nowrap;
}
.col-time {
  width: 160px;
  color: #909399;
  white-space: nowrap;
}
.col-actions {
  width: 160px;
  white-space: nowrap;
}
.action-btn {
  padding: 3px 8px;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  font-size: 11px;
  transition: all 0.2s;
  color: white;
  margin-right: 4px;
}
.action-btn:last-child {
  margin-right: 0;
}
.preview-btn { background-color: #409eff; }
.preview-btn:hover { background-color: #337ecc; }
.download-btn { background-color: #67c23a; }
.download-btn:hover { background-color: #5daf34; }
.delete-btn { background-color: #f56c6c; }
.delete-btn:hover { background-color: #e03e3e; }
.open-btn { background-color: #667eea; }
.open-btn:hover { background-color: #5568d3; }
.rename-btn { background-color: #e6a23c; }
.rename-btn:hover { background-color: #d49130; }
</style>
