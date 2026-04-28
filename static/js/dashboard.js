async function loadDashboard() {
    try {
        const response = await axios.get(`${API_BASE}/core/dashboard/`);
        const data = response.data;
        
        document.getElementById('total-tasks').textContent = data.statistics.total_tasks;
        document.getElementById('running-tasks').textContent = data.statistics.running_tasks;
        document.getElementById('completed-tasks').textContent = data.statistics.completed_tasks;
        document.getElementById('failed-tasks').textContent = data.statistics.failed_tasks;
        document.getElementById('total-scripts').textContent = data.statistics.total_scripts;
        document.getElementById('published-scripts').textContent = data.statistics.published_scripts;
        document.getElementById('total-elements').textContent = data.statistics.total_elements || 0;
        document.getElementById('pass-rate').textContent = data.statistics.pass_rate + '%';
        
        const recentTasksHtml = data.recent_tasks.length > 0 
            ? data.recent_tasks.map(task => `
                <div class="d-flex justify-content-between align-items-center py-2 border-bottom">
                    <div>
                        <div class="fw-bold">${task.name}</div>
                        <small class="text-muted">${formatDate(task.created_at)}</small>
                    </div>
                    ${getStatusBadge(task.status)}
                </div>
            `).join('')
            : '<div class="text-center text-muted py-4">暂无数据</div>';
        
        document.getElementById('recent-tasks').innerHTML = recentTasksHtml;
    } catch (error) {
        console.error('Failed to load dashboard:', error);
        showToast('加载数据失败', 'error');
    }
}

function refreshDashboard() {
    loadDashboard();
    showToast('数据已刷新');
}

loadDashboard();