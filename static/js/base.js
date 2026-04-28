const API_BASE = '/api';

function showToast(message, type = 'success') {
    const toastContainer = document.querySelector('.toast-container');
    const toast = document.createElement('div');
    toast.className = `toast show align-items-center text-white bg-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info'}`;
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    toastContainer.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN');
}

function getStatusBadge(status) {
    const statusMap = {
        'pending': { class: 'status-pending', text: '待执行' },
        'running': { class: 'status-running', text: '执行中' },
        'completed': { class: 'status-completed', text: '已完成' },
        'failed': { class: 'status-failed', text: '失败' },
        'cancelled': { class: 'status-cancelled', text: '已取消' },
        'draft': { class: 'status-pending', text: '草稿' },
        'published': { class: 'status-completed', text: '已发布' },
        'archived': { class: 'status-cancelled', text: '已归档' },
    };
    const info = statusMap[status] || { class: 'status-pending', text: status };
    return `<span class="status-badge ${info.class}">${info.text}</span>`;
}

// 全局中文输入法支持
(function() {
    // 为所有输入框和文本框添加 composition 状态跟踪
    document.addEventListener('compositionstart', function(e) {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
            e.target.isComposing = true;
        }
    }, true);

    document.addEventListener('compositionend', function(e) {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
            e.target.isComposing = false;
        }
    }, true);
    
    // 全局覆盖 Bootstrap Modal 默认配置，禁用自动聚焦（干扰中文输入）
    if (typeof bootstrap !== 'undefined' && bootstrap.Modal && bootstrap.Modal.Default) {
        bootstrap.Modal.Default.focus = false;
    }
})();
