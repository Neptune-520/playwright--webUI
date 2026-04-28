<template>
  <div class="app">
    <header class="header">
      <h1>自动化管理系统</h1>
    </header>
    <div class="layout">
      <nav class="sidebar">
        <ul class="menu">
          <li class="menu-item" :class="{ active: analysisMenuOpen }" @click="analysisMenuOpen = !analysisMenuOpen">
            <span class="menu-icon">📊</span>
            <span class="menu-text">脚本执行分析</span>
            <span class="menu-arrow" :class="{ rotated: analysisMenuOpen }">▶</span>
          </li>
          <ul class="submenu" v-show="analysisMenuOpen">
            <li class="submenu-item" :class="{ active: currentPage === 'analysis' }" @click="switchPage('analysis')">
              <span class="submenu-icon">📈</span>
              <span>执行概览</span>
            </li>
            <li class="submenu-item" :class="{ active: currentPage === 'reportlist' }" @click="switchPage('reportlist')">
              <span class="submenu-icon">📋</span>
              <span>报告列表</span>
            </li>
          </ul>
          <li class="menu-item" :class="{ active: currentPage === 'file' }" @click="switchPage('file')">
            <span class="menu-icon">📄</span>
            <span>集合文件</span>
          </li>
          <li class="menu-item" :class="{ active: currentPage === 'config' }" @click="switchPage('config')">
            <span class="menu-icon">⚙️</span>
            <span>全局配置</span>
          </li>
        </ul>
      </nav>
      <main class="main-content">
        <template v-if="currentPage === 'file'">
        <!-- Toolbar -->
        <div class="toolbar">
          <div class="toolbar-left">
            <button class="toolbar-btn" @click="showUploadModal = true">
              <span class="btn-icon">📤</span> 上传
            </button>
            <button class="toolbar-btn" @click="showNewFolderDialog">
              <span class="btn-icon">📁</span> 新建文件夹
            </button>
            <button v-if="selectedNames.size > 0" class="toolbar-btn danger" @click="batchDeleteSelected">
              <span class="btn-icon">🗑️</span> 删除已选({{ selectedNames.size }})
            </button>
            <button v-if="selectedNames.size > 0" class="toolbar-btn" @click="batchDownloadSelected">
              <span class="btn-icon">⬇️</span> 下载已选({{ selectedNames.size }})
            </button>
          </div>
          <div class="toolbar-right">
            <div class="search-box">
              <input type="text" v-model="searchKeyword" placeholder="搜索文件名（全局搜索）" class="search-input" @keydown.enter="handleSearchKeyDown" @compositionstart="searchComposing = true" @compositionend="searchComposing = false" />
              <button class="toolbar-btn" @click="performSearch">
                <span class="btn-icon">🔍</span> 搜索
              </button>
              <button class="toolbar-btn" v-if="isSearchMode" @click="clearSearch">
                <span class="btn-icon">↩️</span> 返回
              </button>
            </div>
          </div>
        </div>

        <!-- Breadcrumb -->
        <div class="breadcrumb" v-if="!isSearchMode">
          <span class="breadcrumb-item" @click="navigateTo('')">此电脑</span>
          <template v-for="(seg, idx) in breadcrumbSegments" :key="idx">
            <span class="breadcrumb-sep">></span>
            <span
              v-if="idx < breadcrumbSegments.length - 1"
              class="breadcrumb-item"
              @click="navigateToIndex(idx)"
            >{{ seg }}</span>
            <span v-else class="breadcrumb-item current">{{ seg }}</span>
          </template>
        </div>
        <div class="breadcrumb" v-else>
          <span class="breadcrumb-item current">搜索结果: "{{ searchKeyword }}"</span>
        </div>

        <!-- File/Folder Explorer -->
        <div class="explorer" @contextmenu.prevent="showEmptyContextMenu">
          <table class="explorer-table">
            <thead>
              <tr>
                <th class="col-check">
                  <input type="checkbox" :checked="allSelected" @change="toggleSelectAll" />
                </th>
                <th class="col-name-th">名称</th>
                <th class="col-size-th">大小</th>
                <th class="col-time-th">修改时间</th>
                <th class="col-actions-th">操作</th>
              </tr>
            </thead>
            <tbody>
              <template v-if="displayItems.length === 0">
                <tr>
                  <td colspan="5" class="empty-cell">
                    <span class="empty-icon">📂</span>
                    <p>{{ isSearchMode ? '未找到匹配的文件' : '此文件夹为空' }}</p>
                  </td>
                </tr>
              </template>
              <template v-if="isSearchMode">
                <tr v-for="item in displayItems" :key="item.name + '-' + item.path" class="file-row">
                  <td class="col-check">
                    <input type="checkbox" :checked="selectedNames.has(item.name + '-' + item.path)" @change="toggleSelectByNamePath(item.name + '-' + item.path)" />
                  </td>
                  <td class="col-name-td">
                    <span class="file-icon">📄</span>
                    <span class="file-name-text" :title="item.name">{{ item.name }}</span>
                    <a class="file-path" v-if="item.path" @click="navigateToPath(item.path)">{{ item.path }}</a>
                  </td>
                  <td class="col-size-td">{{ formatFileSize(item.size) }}</td>
                  <td class="col-time-td">{{ formatDate(item.modified_time) }}</td>
                  <td class="col-actions-td">
                    <button class="action-btn preview-btn" @click="handleSearchPreview(item)" title="查看">
                      查看
                    </button>
                    <button class="action-btn download-btn" @click="handleSearchDownload(item)" title="下载">
                      下载
                    </button>
                    <button class="action-btn delete-btn" @click="showDeleteSearchDialog(item)" title="删除">
                      删除
                    </button>
                  </td>
                </tr>
              </template>
              <template v-else>
                <ExplorerItem
                  v-for="item in displayItems"
                  :key="item.name + '-' + currentPath"
                  :item="item"
                  :selected="selectedNames.has(item.name)"
                  @open-folder="handleOpenFolder"
                  @toggle-select="toggleSelect"
                  @preview="handlePreview"
                  @download="handleDownload"
                  @rename="showRenameDialog"
                  @request-delete="showDeleteDialog"
                />
              </template>
            </tbody>
          </table>
        </div>

        <!-- Modals -->
        <FilePreview
          v-if="showPreview"
          :content="previewContent"
          :filename="previewFilename"
          @close="closePreview"
        />
        <UploadModal
          v-if="showUploadModal"
          :path="currentPath"
          @upload-success="onUploadSuccess"
          @close="showUploadModal = false"
        />
        <RenameModal
          v-if="showRenameModal"
          :original-name="renameOriginal"
          :is-folder="renameIsFolder"
          @confirm="executeRename"
          @cancel="closeRenameModal"
        />
        <ConfirmModal
          v-if="showConfirmModal"
          :title="confirmTitle"
          :message="confirmMessage"
          @confirm="executeConfirm"
          @cancel="closeConfirmModal"
        />
        </template>
        <template v-else-if="currentPage === 'analysis'">
          <ScriptAnalysis @view-report="loadReport" />
        </template>
        <template v-else-if="currentPage === 'reportlist'">
          <ReportList :loadReport="loadReport" />
        </template>
        <template v-else-if="currentPage === 'config'">
          <GlobalConfig />
        </template>
        <template v-else-if="currentPage === 'report'">
          <ReportDetail :reportId="currentReportId" @back="handleBackFromReport" />
        </template>
      </main>
    </div>
  </div>
</template>

<script>
import ExplorerItem from './components/ExplorerItem.vue'
import FilePreview from './components/FilePreview.vue'
import UploadModal from './components/UploadModal.vue'
import RenameModal from './components/RenameModal.vue'
import ConfirmModal from './components/ConfirmModal.vue'
import ScriptAnalysis from './components/ScriptAnalysis.vue'
import GlobalConfig from './components/GlobalConfig.vue'
import ReportDetail from './components/ReportDetail.vue'
import ReportList from './components/ReportList.vue'
import api from './api/index.js'

export default {
  name: 'App',
  components: {
    ExplorerItem,
    FilePreview,
    UploadModal,
    RenameModal,
    ConfirmModal,
    ScriptAnalysis,
    GlobalConfig,
    ReportDetail,
    ReportList
  },
  data() {
    return {
      currentPage: 'analysis',
      items: [],
      currentPath: '',
      selectedNames: new Set(),
      showPreview: false,
      previewContent: null,
      previewFilename: '',
      showUploadModal: false,
      showRenameModal: false,
      renameOriginal: '',
      renameIsFolder: false,
      showConfirmModal: false,
      confirmTitle: '',
      confirmMessage: '',
      confirmAction: null,
      searchKeyword: '',
      isSearchMode: false,
      searchResults: [],
      searchDeleteItem: null,
      searchComposing: false,
      currentReportId: null,
      reportLoading: false,
      analysisMenuOpen: true
    }
  },
  computed: {
    breadcrumbSegments() {
      if (!this.currentPath) return []
      return this.currentPath.split('/').filter(Boolean)
    },
    allSelected() {
      if (this.isSearchMode) {
        const files = this.searchResults
        if (files.length === 0) return false
        return files.every(f => this.selectedNames.has(f.name + '-' + f.path))
      }
      const files = this.items.filter(i => !i.is_folder)
      if (files.length === 0) return false
      return files.every(f => this.selectedNames.has(f.name))
    },
    displayItems() {
      if (this.isSearchMode) {
        return this.searchResults
      }
      return this.items
    }
  },
  mounted() {
    this.loadItems()
    // Handle browser back/forward
    window.addEventListener('popstate', () => this.handleUrlChange())
    this.handleUrlChange()
  },
  beforeUnmount() {
    window.removeEventListener('popstate', () => this.handleUrlChange())
  },
  methods: {
    handleUrlChange() {
      const urlParams = new URLSearchParams(window.location.search)
      const reportId = urlParams.get('report')
      const pageParam = urlParams.get('page')
      if (reportId) {
        this.loadReport(reportId)
      } else if (pageParam) {
        this.currentPage = pageParam
        this.currentReportId = null
      } else {
        this.currentPage = 'analysis'
        this.currentReportId = null
      }
    },
    switchPage(page) {
      this.currentPage = page
      this.currentReportId = null
      const url = new URL(window.location)
      url.searchParams.delete('report')
      url.searchParams.set('page', page)
      window.history.pushState({ page }, '', url)
    },
    loadReport(id) {
      this.currentReportId = id
      this.currentPage = 'report'
      const url = new URL(window.location)
      url.searchParams.set('report', id)
      url.searchParams.delete('page')
      window.history.pushState({ report: id }, '', url)
    },
    handleBackFromReport() {
      this.currentPage = 'reportlist'
      this.currentReportId = null
      const url = new URL(window.location)
      url.searchParams.delete('report')
      url.searchParams.set('page', 'reportlist')
      window.history.pushState({ page: 'reportlist' }, '', url)
    },
    async loadItems() {
      try {
        const params = {}
        if (this.currentPath) params.path = this.currentPath
        const response = await api.get('/items', { params })
        this.items = response.data
        this.selectedNames.clear()
      } catch (error) {
        console.error('加载失败:', error)
      }
    },
    handleOpenFolder(name) {
      this.currentPath = this.currentPath ? `${this.currentPath}/${name}` : name
      this.loadItems()
    },
    navigateToPath(path) {
      const cleanPath = path.replace(/^\.\//, '');
      const dirPath = cleanPath.substring(0, cleanPath.lastIndexOf('/'));
      this.isSearchMode = false
      this.searchResults = []
      this.searchKeyword = ''
      this.currentPath = dirPath
      this.loadItems()
    },
    navigateTo(path) {
      this.currentPath = path
      this.loadItems()
    },
    navigateToIndex(idx) {
      const segments = this.breadcrumbSegments.slice(0, idx + 1)
      this.currentPath = segments.join('/')
      this.loadItems()
    },
    onUploadSuccess() {
      this.loadItems()
    },
    toggleSelect(name) {
      if (this.selectedNames.has(name)) {
        this.selectedNames.delete(name)
      } else {
        this.selectedNames.add(name)
      }
      this.selectedNames = new Set(this.selectedNames)
    },
    toggleSelectAll() {
      const files = this.items.filter(i => !i.is_folder)
      if (this.allSelected) {
        files.forEach(f => this.selectedNames.delete(f.name))
      } else {
        files.forEach(f => this.selectedNames.add(f.name))
      }
      this.selectedNames = new Set(this.selectedNames)
    },
    closeContextMenu() {
    },
    showNewFolderDialog() {
      this.renameOriginal = ''
      this.renameIsFolder = true
      this.showRenameModal = true
    },
    showRenameDialog(name) {
      const item = this.items.find(i => i.name === name)
      this.renameOriginal = name
      this.renameIsFolder = item ? item.is_folder : false
      this.showRenameModal = true
    },
    closeRenameModal() {
      this.showRenameModal = false
      this.renameOriginal = ''
    },
    async executeRename(newName) {
      if (!newName || !newName.trim()) {
        this.closeRenameModal()
        return
      }
      try {
        if (this.renameOriginal) {
          await api.put(`/items/${encodeURIComponent(this.renameOriginal)}/rename`, null, {
            params: {
              new_name: newName.trim(),
              path: this.currentPath
            }
          })
        } else {
          await api.post('/folder', null, {
            params: {
              name: newName.trim(),
              path: this.currentPath
            }
          })
        }
        this.closeRenameModal()
        this.loadItems()
      } catch (error) {
        alert(error.response?.data?.detail || (this.renameOriginal ? '重命名失败' : '创建文件夹失败'))
      }
    },
    showDeleteDialog(name) {
      const item = this.items.find(i => i.name === name)
      const type = item?.is_folder ? '文件夹' : '文件'
      this.confirmTitle = '确认删除'
      this.confirmMessage = `确定要删除${type} "${name}" 吗？${item?.is_folder ? '文件夹内的所有内容也将被删除。' : ''}`
      this.confirmAction = async () => {
        await api.delete(`/items/${encodeURIComponent(name)}`, {
          params: { path: this.currentPath }
        })
        this.loadItems()
      }
      this.showConfirmModal = true
    },
    async batchDeleteSelected() {
      if (this.isSearchMode) {
        const files = this.searchResults.filter(f => this.selectedNames.has(f.name + '-' + f.path))
        if (files.length === 0) return
        this.confirmTitle = '批量删除'
        this.confirmMessage = `确定要删除选中的 ${files.length} 个文件吗？`
        this.confirmAction = async () => {
          for (const f of files) {
            const path = f.path.substring(0, f.path.lastIndexOf('/')) || ''
            await api.delete(`/items/${encodeURIComponent(f.name)}`, {
              params: { path }
            })
          }
          this.performSearch()
        }
      } else {
        const files = this.items.filter(i => !i.is_folder && this.selectedNames.has(i.name))
        if (files.length === 0) return
        this.confirmTitle = '批量删除'
        this.confirmMessage = `确定要删除选中的 ${files.length} 个文件吗？`
        this.confirmAction = async () => {
          for (const f of files) {
            await api.delete(`/items/${encodeURIComponent(f.name)}`, {
              params: { path: this.currentPath }
            })
          }
          this.loadItems()
        }
      }
      this.showConfirmModal = true
    },
    async batchDownloadSelected() {
      const files = this.isSearchMode ? this.searchResults : this.items.filter(i => !i.is_folder)
      const selectedFiles = files.filter(f => this.selectedNames.has(this.isSearchMode ? f.name + '-' + f.path : f.name))
      for (const f of selectedFiles) {
        if (this.isSearchMode) {
          const encodedName = encodeURIComponent(f.name)
          const encodedPath = encodeURIComponent(f.path.substring(0, f.path.lastIndexOf('/')) || '')
          const link = document.createElement('a')
          link.href = `/api/items/${encodedName}/download?path=${encodedPath}`
          link.download = f.name
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
        } else {
          this.handleDownload(f.name)
        }
      }
    },
    handleSearchKeyDown(event) {
      if (!this.searchComposing) {
        event.preventDefault()
        this.performSearch()
      }
    },
    async performSearch() {
      if (!this.searchKeyword.trim()) {
        return
      }
      try {
        const response = await api.get('/search', { params: { keyword: this.searchKeyword } })
        this.searchResults = response.data
        this.isSearchMode = true
        this.selectedNames.clear()
      } catch (error) {
        console.error('搜索失败:', error)
      }
    },
    clearSearch() {
      this.isSearchMode = false
      this.searchResults = []
      this.searchKeyword = ''
      this.selectedNames.clear()
    },
    toggleSelectByNamePath(key) {
      if (this.selectedNames.has(key)) {
        this.selectedNames.delete(key)
      } else {
        this.selectedNames.add(key)
      }
      this.selectedNames = new Set(this.selectedNames)
    },
    async handleSearchPreview(item) {
      try {
        const path = item.path.substring(0, item.path.lastIndexOf('/')) || ''
        const response = await api.get(`/items/${encodeURIComponent(item.name)}/preview`, { params: { path } })
        this.previewContent = response.data
        this.previewFilename = item.name
        this.showPreview = true
      } catch (error) {
        console.error('预览失败:', error)
      }
    },
    handleSearchDownload(item) {
      const path = item.path.substring(0, item.path.lastIndexOf('/')) || ''
      const encodedName = encodeURIComponent(item.name)
      const encodedPath = encodeURIComponent(path)
      const link = document.createElement('a')
      link.href = `/api/items/${encodedName}/download?path=${encodedPath}`
      link.download = item.name
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    },
    showDeleteSearchDialog(item) {
      this.searchDeleteItem = item
      this.confirmTitle = '确认删除'
      this.confirmMessage = `确定要删除文件 "${item.name}" 吗？`
      this.confirmAction = async () => {
        const path = item.path.substring(0, item.path.lastIndexOf('/')) || ''
        await api.delete(`/items/${encodeURIComponent(item.name)}`, {
          params: { path }
        })
        if (this.isSearchMode) {
          this.performSearch()
        } else {
          this.loadItems()
        }
      }
      this.showConfirmModal = true
    },
    closeConfirmModal() {
      this.showConfirmModal = false
      this.confirmAction = null
    },
    async executeConfirm() {
      try {
        if (this.confirmAction) await this.confirmAction()
      } catch (error) {
        alert(error.response?.data?.detail || '操作失败')
      }
      this.closeConfirmModal()
    },
    async handlePreview(name) {
      try {
        const params = {}
        if (this.currentPath) params.path = this.currentPath
        const response = await api.get(`/items/${encodeURIComponent(name)}/preview`, { params })
        this.previewContent = response.data
        this.previewFilename = name
        this.showPreview = true
      } catch (error) {
        console.error('预览失败:', error)
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
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    closePreview() {
      this.showPreview = false
      this.previewContent = null
      this.previewFilename = ''
    },
    handleDownload(name) {
      const encodedName = encodeURIComponent(name)
      const encodedPath = encodeURIComponent(this.currentPath)
      const link = document.createElement('a')
      link.href = `/api/items/${encodedName}/download?path=${encodedPath}`
      link.download = name
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
  }
}
</script>

<style scoped>
.app {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 12px 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.layout {
  display: flex;
  min-height: calc(100vh - 56px);
}

.sidebar {
  width: 180px;
  background: #fff;
  border-right: 1px solid #e4e7ed;
  flex-shrink: 0;
  padding: 12px 0;
}

.menu {
  list-style: none;
  padding: 0;
  margin: 0;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  cursor: pointer;
  transition: all 0.2s;
  color: #303133;
  font-size: 13px;
  position: relative;
}

.menu-item:hover:not(.disabled) {
  background: #f5f7fa;
  color: #667eea;
}

.menu-item.active {
  background: #ecf5ff;
  color: #667eea;
  border-right: 3px solid #667eea;
  font-weight: 500;
}

.menu-item.disabled {
  color: #c0c4cc;
  cursor: not-allowed;
}

.menu-icon {
  font-size: 16px;
}

.menu-text {
  flex: 1;
}

.menu-arrow {
  font-size: 10px;
  transition: transform 0.2s;
}

.menu-arrow.rotated {
  transform: rotate(90deg);
}

.submenu {
  list-style: none;
  padding: 0;
  margin: 0;
  background: #fafbfc;
  overflow: hidden;
}

.submenu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px 8px 40px;
  cursor: pointer;
  transition: all 0.2s;
  color: #606266;
  font-size: 13px;
}

.submenu-item:hover:not(.disabled) {
  background: #ecf5ff;
  color: #667eea;
}

.submenu-item.active {
  background: #d9ecff;
  color: #667eea;
  font-weight: 500;
}

.submenu-icon {
  font-size: 14px;
}

.main-content {
  flex: 1;
  padding: 16px;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: space-between;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 6px;
}

.toolbar-right {
  display: flex;
  align-items: center;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 4px;
}

.search-input {
  padding: 6px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 12px;
  width: 200px;
  outline: none;
  transition: border-color 0.2s;
}

.search-input:focus {
  border-color: #667eea;
}

.toolbar-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: #fff;
  border: 1px solid #dcdfe6;
  color: #303133;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.toolbar-btn:hover {
  border-color: #667eea;
  color: #667eea;
}

.toolbar-btn.danger {
  color: #f56c6c;
  border-color: #f56c6c;
}

.toolbar-btn.danger:hover {
  background: #f56c6c;
  color: #fff;
}

.btn-icon {
  font-size: 14px;
}

.breadcrumb {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  background: #fff;
  border-radius: 6px;
  font-size: 13px;
  border: 1px solid #e4e7ed;
}

.breadcrumb-item {
  color: #667eea;
  cursor: pointer;
  transition: color 0.2s;
}

.breadcrumb-item:hover {
  color: #5568d3;
}

.breadcrumb-item.current {
  color: #303133;
  cursor: default;
  font-weight: 500;
}

.breadcrumb-item.current:hover {
  color: #303133;
}

.breadcrumb-sep {
  margin: 0 6px;
  color: #c0c4cc;
}

.explorer {
  flex: 1;
  background: #fff;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
  overflow: auto;
}

.explorer-table {
  width: 100%;
  border-collapse: collapse;
}

.explorer-table thead {
  background: #fafbfc;
  position: sticky;
  top: 0;
  z-index: 1;
}

.explorer-table th {
  padding: 8px 12px;
  text-align: left;
  color: #606266;
  font-weight: 500;
  font-size: 12px;
  border-bottom: 1px solid #ebeef5;
}

.col-check {
  width: 36px;
  text-align: center;
}

.col-name-th {
  width: 50%;
}

.col-size-th {
  width: 100px;
}

.col-time-th {
  width: 170px;
}

.col-actions-th {
  width: 200px;
}

.col-name-td {
  width: 50%;
  display: flex;
  align-items: center;
  gap: 8px;
}

.col-size-td {
  width: 12%;
  color: #909399;
}

.col-time-td {
  width: 22%;
  color: #909399;
}

.col-actions-td {
  width: 26%;
}

.file-path {
  color: #909399;
  font-size: 11px;
  margin-left: 8px;
  cursor: pointer;
  text-decoration: none;
}

.file-path:hover {
  color: #667eea;
  text-decoration: underline;
}

.file-row {
  transition: background-color 0.2s;
}

.file-row:hover {
  background-color: #fafbfc;
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

.empty-cell {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}

.empty-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 8px;
}

.empty-cell p {
  margin: 0;
  font-size: 14px;
}

@media (max-width: 768px) {
  .header h1 { font-size: 16px; }
  .layout { flex-direction: column; }
  .sidebar { width: 100%; padding: 8px 0; }
  .main-content { padding: 10px; }
  .col-size-th, .col-time-th { display: none; }
  .breadcrumb { flex-wrap: wrap; }
}
</style>
