let scripts = [];
let selectedFile = null;
let exportScriptId = null;
let currentPage = 1;

async function loadScripts() {
    try {
        const response = await axios.get(`${API_BASE}/scripts/`);
        scripts = response.data;
        await loadScriptGroupOptions();
        renderScripts();
    } catch (error) {
        console.error('Failed to load scripts:', error);
        const tbody = document.getElementById('scripts-table');
        const errorMsg = error.response?.data?.detail || error.response?.data?.error || '加载脚本列表失败，请稍后重试';
        tbody.innerHTML = `<tr><td colspan="7" class="text-center text-danger">
            <i class="bi bi-exclamation-triangle"></i> ${errorMsg}
            <br><button class="btn btn-sm btn-outline-danger mt-2" onclick="loadScripts()">
                <i class="bi bi-arrow-clockwise"></i> 重试
            </button>
        </td></tr>`;
        showToast(errorMsg, 'error');
    }
}

async function loadScriptGroupOptions() {
    try {
        const response = await axios.get(`${API_BASE}/core/groups/?type=script`);
        const select = document.getElementById('script-group-filter');
        response.data.forEach(group => {
            const option = document.createElement('option');
            option.value = group.id;
            option.textContent = group.name;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Failed to load groups:', error);
    }
}

function renderScripts() {
    const keyword = document.getElementById('script-search').value.toLowerCase();
    const groupFilter = document.getElementById('script-group-filter').value;
    const statusFilter = document.getElementById('script-status-filter').value;
    const pageSize = parseInt(document.getElementById('script-page-size').value);

    let filtered = scripts.filter(s => {
        const matchKeyword = !keyword || 
            s.name.toLowerCase().includes(keyword) || 
            s.code.toLowerCase().includes(keyword) || 
            String(s.id).includes(keyword);
        const matchGroup = !groupFilter || s.group_id == groupFilter;
        const matchStatus = !statusFilter || s.status === statusFilter;
        return matchKeyword && matchGroup && matchStatus;
    });

    const tbody = document.getElementById('scripts-table');
    const countEl = document.getElementById('script-count');

    if (scripts.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">暂无数据</td></tr>';
        countEl.textContent = '';
        return;
    }

    const totalFiltered = filtered.length;
    const totalScripts = scripts.length;
    const startIndex = (currentPage - 1) * pageSize + 1;
    const endIndex = Math.min(currentPage * pageSize, totalFiltered);

    if (totalFiltered === 0) {
        countEl.textContent = '显示 0/0 条';
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">无匹配结果</td></tr>';
        return;
    }

    if (startIndex > totalFiltered) {
        currentPage = 1;
    }

    const paginatedStart = (currentPage - 1) * pageSize;
    const paginatedEnd = currentPage * pageSize;
    const paginatedData = filtered.slice(paginatedStart, paginatedEnd);

    countEl.textContent = `显示 ${startIndex}-${endIndex}/${totalFiltered} 条`;

    tbody.innerHTML = paginatedData.map(script => `
        <tr>
            <td>${script.id}</td>
            <td>
                <div class="fw-bold">${script.name}</div>
                <small class="text-muted">${script.code}</small>
            </td>
            <td>v${script.version}</td>
            <td>${getStatusBadge(script.status)}</td>
            <td>${script.steps_count || 0}</td>
            <td>${formatDate(script.created_at)}</td>
            <td>
                <div class="btn-group">
                    <button class="btn btn-outline-primary btn-sm" onclick="editScript(${script.id})" title="编辑">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-outline-success btn-sm" onclick="createTask(${script.id})" title="创建任务">
                        <i class="bi bi-play-fill"></i>
                    </button>
                    <button class="btn btn-outline-secondary btn-sm" onclick="duplicateScript(${script.id})" title="复制">
                        <i class="bi bi-files"></i>
                    </button>
                    <button class="btn btn-outline-info btn-sm" onclick="showExportModal(${script.id})" title="导出">
                        <i class="bi bi-download"></i>
                    </button>
                    <button class="btn btn-outline-danger btn-sm" onclick="deleteScript(${script.id})" title="删除">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

function resetScriptSearch() {
    currentPage = 1;
    document.getElementById('script-search').value = '';
    document.getElementById('script-group-filter').value = '';
    document.getElementById('script-status-filter').value = '';
    renderScripts();
}

document.getElementById('script-search').addEventListener('input', renderScripts);
document.getElementById('script-group-filter').addEventListener('change', renderScripts);
document.getElementById('script-status-filter').addEventListener('change', renderScripts);
document.getElementById('script-page-size').addEventListener('change', () => { currentPage = 1; renderScripts(); });

function showExportModal(scriptId) {
    exportScriptId = scriptId;
    new bootstrap.Modal(document.getElementById('exportModal')).show();
}

async function doExport(format) {
    if (!exportScriptId) return;

    try {
        if (format === 'json') {
            const response = await axios.get(`${API_BASE}/scripts/${exportScriptId}/export/?export_format=json`);
            const script = scripts.find(s => s.id === exportScriptId);
            const filename = `script_${script?.code || exportScriptId}_export.json`;
            downloadJson(response.data, filename);
        } else {
            const response = await axios.get(`${API_BASE}/scripts/${exportScriptId}/export/?export_format=excel`, {
                responseType: 'blob'
            });
            const script = scripts.find(s => s.id === exportScriptId);
            const filename = `script_${script?.code || exportScriptId}_export.xlsx`;
            downloadBlob(response.data, filename,
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
        }
        bootstrap.Modal.getInstance(document.getElementById('exportModal')).hide();
        showToast('导出成功');
    } catch (error) {
        console.error('Export failed:', error);
        showToast('导出失败', 'error');
    }
}

function downloadJson(data, filename) {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function downloadBlob(blobData, filename, mimeType) {
    const blob = new Blob([blobData], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function showImportModal() {
    resetImportModal();
    new bootstrap.Modal(document.getElementById('importModal')).show();
}

function handleDrop(event) {
    event.preventDefault();
    event.target.closest('#drop-zone').classList.remove('border-primary');
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        setSelectedFile(files[0]);
    }
}

function handleFileSelect(event) {
    const files = event.target.files;
    if (files.length > 0) {
        setSelectedFile(files[0]);
    }
}

function setSelectedFile(file) {
    const ext = file.name.toLowerCase();
    if (!ext.endsWith('.json') && !ext.endsWith('.xlsx') && !ext.endsWith('.xls')) {
        showToast('请选择 .json 或 .xlsx 格式的文件', 'error');
        return;
    }
    selectedFile = file;
    document.getElementById('selected-file-name').textContent = file.name;
    document.getElementById('selected-file-info').style.display = 'block';
    document.getElementById('import-submit-btn').disabled = false;
}

function clearSelectedFile() {
    selectedFile = null;
    document.getElementById('import-file').value = '';
    document.getElementById('selected-file-info').style.display = 'none';
    document.getElementById('import-submit-btn').disabled = true;
}

async function doImport() {
    if (!selectedFile) {
        showToast('请先选择文件', 'error');
        return;
    }

    const conflictStrategy = document.querySelector('input[name="conflict-strategy"]:checked').value;

    document.getElementById('import-upload-section').style.display = 'none';
    document.getElementById('import-progress-section').style.display = 'block';
    document.getElementById('import-submit-btn').disabled = true;

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('format', 'auto');
    formData.append('conflict_strategy', conflictStrategy);

    try {
        const response = await axios.post(`${API_BASE}/scripts/import/`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });

        showImportResult(response.data);
    } catch (error) {
        console.error('Import failed:', error);
        let errorMsg = '导入失败';
        if (error.response?.data?.error) {
            errorMsg = error.response.data.error;
        } else if (error.response?.data?.detail) {
            errorMsg = error.response.data.detail;
        }
        document.getElementById('import-progress-section').style.display = 'none';
        document.getElementById('import-result-section').style.display = 'block';
        const alertEl = document.getElementById('import-result-alert');
        alertEl.className = 'alert alert-danger';
        document.getElementById('import-result-title').textContent = errorMsg;
        document.getElementById('import-again-btn').style.display = 'inline-block';
        document.getElementById('import-submit-btn').style.display = 'none';
    }
}

function showImportResult(result) {
    document.getElementById('import-progress-section').style.display = 'none';
    document.getElementById('import-result-section').style.display = 'block';

    const alertEl = document.getElementById('import-result-alert');
    const hasErrors = result.failed > 0;
    alertEl.className = hasErrors ? 'alert alert-warning' : 'alert alert-success';
    document.getElementById('import-result-title').textContent =
        hasErrors ? '导入完成（部分失败）' : '导入成功';

    document.getElementById('result-scripts-created').textContent =
        (result.scripts_created || 0) + (result.scripts_overwritten || 0);
    document.getElementById('result-scripts-skipped').textContent = result.scripts_skipped || 0;
    document.getElementById('result-actionsets-created').textContent =
        (result.action_sets_created || 0) + (result.action_sets_overwritten || 0);
    document.getElementById('result-elements-created').textContent = result.elements_created || 0;

    const errorsSection = document.getElementById('import-errors-section');
    const errorsList = document.getElementById('import-errors-list');
    if (result.errors && result.errors.length > 0) {
        errorsSection.style.display = 'block';
        errorsList.innerHTML = result.errors.map(err => `
            <div class="list-group-item list-group-item-${err.type === 'warning' ? 'warning' : 'danger'} py-2">
                <small><strong>${err.type === 'warning' ? '警告' : '错误'}:</strong> ${err.message}</small>
            </div>
        `).join('');
    } else {
        errorsSection.style.display = 'none';
    }

    document.getElementById('import-again-btn').style.display = 'inline-block';
    document.getElementById('import-submit-btn').style.display = 'none';

    loadScripts();
}

function resetImportModal() {
    selectedFile = null;
    document.getElementById('import-file').value = '';
    document.getElementById('selected-file-info').style.display = 'none';
    document.getElementById('import-upload-section').style.display = 'block';
    document.getElementById('import-progress-section').style.display = 'none';
    document.getElementById('import-result-section').style.display = 'none';
    document.getElementById('import-submit-btn').disabled = true;
    document.getElementById('import-submit-btn').style.display = 'inline-block';
    document.getElementById('import-again-btn').style.display = 'none';
    document.getElementById('strategy-skip').checked = true;
}

function editScript(scriptId) {
    window.location.href = `/editor/?script_id=${scriptId}`;
}

function createTask(scriptId) {
    window.location.href = `/tasks/?create_task=${scriptId}`;
}

async function duplicateScript(scriptId) {
    try {
        await axios.post(`${API_BASE}/scripts/${scriptId}/duplicate/`);
        showToast('脚本复制成功');
        loadScripts();
    } catch (error) {
        console.error('Failed to duplicate script:', error);
        showToast('复制失败', 'error');
    }
}

async function deleteScript(scriptId) {
    if (!confirm('确定删除此脚本？')) return;

    try {
        await axios.delete(`${API_BASE}/scripts/${scriptId}/`);
        showToast('删除成功');
        loadScripts();
    } catch (error) {
        console.error('Failed to delete script:', error);
        showToast('删除失败', 'error');
    }
}

loadScripts();