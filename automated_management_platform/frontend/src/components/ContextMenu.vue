<template>
  <teleport to="body">
    <div v-show="visible" class="context-menu-wrapper" :style="{ left: position.x + 'px', top: position.y + 'px' }" @click.stop>
      <!-- 空白区域右键 -->
      <template v-if="targetItem === null">
        <div class="context-menu-item" @click="$emit('create-folder')">
          <span class="item-icon">📁</span>
          <span>新建文件夹</span>
        </div>
      </template>
      <!-- 文件夹右键 -->
      <template v-else-if="targetItem && targetItem.is_folder">
        <div class="context-menu-item" @click="$emit('open-folder', targetItem.name)">
          <span class="item-icon">📂</span>
          <span>打开</span>
        </div>
        <div class="context-menu-item" @click="$emit('rename', targetItem.name)">
          <span class="item-icon">✏️</span>
          <span>重命名</span>
        </div>
        <div class="context-menu-separator"></div>
        <div class="context-menu-item danger" @click="$emit('delete', targetItem.name)">
          <span class="item-icon">🗑️</span>
          <span>删除</span>
        </div>
      </template>
      <!-- 文件右键 -->
      <template v-else-if="targetItem">
        <div class="context-menu-item" @click="$emit('preview', targetItem.name)">
          <span class="item-icon">👁️</span>
          <span>查看</span>
        </div>
        <div class="context-menu-item" @click="$emit('download', targetItem.name)">
          <span class="item-icon">⬇️</span>
          <span>下载</span>
        </div>
        <div class="context-menu-item" @click="$emit('rename', targetItem.name)">
          <span class="item-icon">✏️</span>
          <span>重命名</span>
        </div>
        <div class="context-menu-separator"></div>
        <div class="context-menu-item danger" @click="$emit('delete', targetItem.name)">
          <span class="item-icon">🗑️</span>
          <span>删除</span>
        </div>
      </template>
    </div>
  </teleport>
</template>

<script>
export default {
  name: 'ContextMenu',
  props: {
    position: { type: Object, required: true },
    targetItem: { type: Object, default: null }
  },
  data() {
    return {
      visible: true
    }
  },
  mounted() {
    this.boundClick = () => this.close()
    this.boundContextMenu = () => this.close()
    setTimeout(() => {
      document.addEventListener('click', this.boundClick)
      document.addEventListener('contextmenu', this.boundContextMenu)
    }, 0)
  },
  beforeUnmount() {
    document.removeEventListener('click', this.boundClick)
    document.removeEventListener('contextmenu', this.boundContextMenu)
  },
  methods: {
    close() {
      this.visible = false
      this.$emit('close')
    }
  }
}
</script>

<style>
.context-menu-wrapper {
  position: fixed;
  z-index: 2000;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  padding: 6px 0;
  min-width: 160px;
  max-width: 200px;
}
.context-menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 13px;
  color: #303133;
  transition: background-color 0.15s;
}
.context-menu-item:hover {
  background-color: #f5f7fa;
}
.context-menu-item.danger {
  color: #f56c6c;
}
.context-menu-item.danger:hover {
  background-color: #fef0f0;
}
.context-menu-item .item-icon {
  font-size: 14px;
}
.context-menu-separator {
  height: 1px;
  background-color: #ebeef5;
  margin: 4px 0;
}
</style>
