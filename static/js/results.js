let individualTasks = [];

let individualState = {
    search: '',
    pageSize: 10,
    currentPage: 1
};

async function loadIndividualTasks() {
    try {
        const response = await axios.get(`${API_BASE}/tests/tasks/`);
        individualTasks = response.data || [];
        renderIndividualTasks();
    } catch (error) {
        console.error('Failed to load tasks:', error);
        document.getElementById('individual-tbody').innerHTML = 
            '<tr><td colspan="9" class="text-center text-danger">加载失败</td></tr>';
    }
}

function filterIndividualTasks() {
    if (!individualState.search) return individualTasks;
    return individualTasks.filter(task => 
        task.name && task.name.toLowerCase().includes(individualState.search.toLowerCase())
    );
}

function renderIndividualTasks() {
    const filtered = filterIndividualTasks();
    const tbody = document.getElementById('individual-tbody');
    
    if (filtered.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="text-center text-muted">暂无数据</td></tr>';
        document.getElementById('individual-pagination').innerHTML = '';
        return;
    }
    
    const totalPages = Math.ceil(filtered.length / individualState.pageSize);
    if (individualState.currentPage > totalPages) individualState.currentPage = totalPages;
    
    const start = (individualState.currentPage - 1) * individualState.pageSize;
    const end = start + individualState.pageSize;
    const pageData = filtered.slice(start, end);
    
    tbody.innerHTML = pageData.map(task => {
        const report = task.report;
        const passRate = report && report.total_steps > 0 
            ? report.pass_rate 
            : '-';
        
        const totalSteps = report ? report.total_steps : '-';
        const passedSteps = report ? report.passed_steps : '-';
        const failedSteps = report ? report.failed_steps : '-';
        const skippedSteps = report ? report.skipped_steps : '-';
        const duration = report && report.total_duration 
            ? `${report.total_duration.toFixed(2)}s` 
            : '-';
        
        const passRateHtml = typeof passRate === 'number' 
            ? `<div class="progress" style="width: 100px; height: 20px;">
                   <div class="progress-bar bg-success" style="width: ${passRate}%">${passRate.toFixed(1)}%</div>
               </div>`
            : '-';
        
        return `
            <tr>
                <td>${task.id}</td>
                <td>${task.name || '-'}</td>
                <td>${totalSteps}</td>
                <td class="text-success">${passedSteps}</td>
                <td class="text-danger">${failedSteps}</td>
                <td class="text-warning">${skippedSteps}</td>
                <td>${passRateHtml}</td>
                <td>${duration}</td>
                <td>
                    <button class="btn btn-outline-primary btn-sm" onclick="viewTaskDetail(${task.id})">
                        <i class="bi bi-eye"></i> 详情
                    </button>
                </td>
            </tr>
        `;
    }).join('');
    
    renderIndividualPagination(totalPages, filtered.length);
}

function renderIndividualPagination(totalPages, totalItems) {
    const pagination = document.getElementById('individual-pagination');
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    
    let html = `
        <li class="page-item ${individualState.currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="goToIndividualPage(${individualState.currentPage - 1}); return false;">上一页</a>
        </li>
    `;
    
    for (let i = 1; i <= totalPages; i++) {
        if (totalPages > 7 && Math.abs(i - individualState.currentPage) > 2 && i !== 1 && i !== totalPages) {
            if (i === individualState.currentPage - 3 || i === individualState.currentPage + 3) {
                html += '<li class="page-item disabled"><span class="page-link">...</span></li>';
            }
            continue;
        }
        html += `
            <li class="page-item ${i === individualState.currentPage ? 'active' : ''}">
                <a class="page-link" href="#" onclick="goToIndividualPage(${i}); return false;">${i}</a>
            </li>
        `;
    }
    
    html += `
        <li class="page-item ${individualState.currentPage === totalPages ? 'disabled' : ''}">
            <a class="page-link" href="#" onclick="goToIndividualPage(${individualState.currentPage + 1}); return false;">下一页</a>
        </li>
    `;
    
    html += `<li class="page-item disabled"><span class="page-link">共 ${totalItems} 条</span></li>`;
    
    pagination.innerHTML = html;
}

function goToIndividualPage(page) {
    individualState.currentPage = page;
    renderIndividualTasks();
}

function resetIndividualFilters() {
    document.getElementById('individual-search').value = '';
    document.getElementById('individual-page-size').value = '10';
    individualState = { search: '', pageSize: 10, currentPage: 1 };
    renderIndividualTasks();
}

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('individual-search').addEventListener('input', function(e) {
        individualState.search = e.target.value;
        individualState.currentPage = 1;
        renderIndividualTasks();
    });
    
    document.getElementById('individual-page-size').addEventListener('change', function(e) {
        individualState.pageSize = parseInt(e.target.value);
        individualState.currentPage = 1;
        renderIndividualTasks();
    });
    
    loadIndividualTasks();
});