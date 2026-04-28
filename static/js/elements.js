let elements = [];

async function loadElements() {
    try {
        const response = await axios.get(`${API_BASE}/scripts/elements/`);
        elements = response.data;
        renderElements();
    } catch (error) {
        console.error('Failed to load elements:', error);
    }
}

function renderElements() {
    const tbody = document.getElementById('elements-table');
    
    if (elements.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center text-muted">暂无数据</td></tr>';
        return;
    }
    
    tbody.innerHTML = elements.map(el => `
        <tr>
            <td>${el.id}</td>
            <td>${el.name}</td>
            <td><code>${el.code}</code></td>
            <td><span class="badge bg-info">${el.locator_type}</span></td>
            <td><code>${el.locator_value.length > 30 ? el.locator_value.substring(0, 30) + '...' : el.locator_value}</code></td>
            <td>${el.page_url || '-'}</td>
            <td>${el.is_active ? '<span class="badge bg-success">启用</span>' : '<span class="badge bg-secondary">禁用</span>'}</td>
            <td>
                <button class="btn btn-outline-primary btn-sm" onclick="editElement(${el.id})">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-outline-danger btn-sm" onclick="deleteElement(${el.id})">
                    <i class="bi bi-trash"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

function openElementModal(elementId = null) {
    document.getElementById('element-id').value = elementId || '';
    document.getElementById('element-name').value = '';
    document.getElementById('element-code').value = '';
    document.getElementById('element-locator-type').value = 'css';
    document.getElementById('element-locator-value').value = '';
    document.getElementById('element-page-url').value = '';
    document.getElementById('element-description').value = '';
    document.getElementById('element-timeout').value = '10000';
    document.getElementById('element-wait-state').value = 'visible';
    
    if (elementId) {
        const element = elements.find(e => e.id === elementId);
        if (element) {
            document.getElementById('elementModalTitle').textContent = '编辑元素定位器';
            document.getElementById('element-name').value = element.name;
            document.getElementById('element-code').value = element.code;
            document.getElementById('element-locator-type').value = element.locator_type;
            document.getElementById('element-locator-value').value = element.locator_value;
            document.getElementById('element-page-url').value = element.page_url || '';
            document.getElementById('element-description').value = element.description || '';
            document.getElementById('element-timeout').value = element.wait_timeout;
            document.getElementById('element-wait-state').value = element.wait_state;
        }
    } else {
        document.getElementById('elementModalTitle').textContent = '添加元素定位器';
    }
}

async function saveElement() {
    const id = document.getElementById('element-id').value;
    const data = {
        name: document.getElementById('element-name').value,
        code: document.getElementById('element-code').value,
        locator_type: document.getElementById('element-locator-type').value,
        locator_value: document.getElementById('element-locator-value').value,
        page_url: document.getElementById('element-page-url').value,
        description: document.getElementById('element-description').value,
        wait_timeout: parseInt(document.getElementById('element-timeout').value),
        wait_state: document.getElementById('element-wait-state').value,
    };
    
    try {
        if (id) {
            await axios.put(`${API_BASE}/scripts/elements/${id}/`, data);
            showToast('更新成功');
        } else {
            await axios.post(`${API_BASE}/scripts/elements/`, data);
            showToast('添加成功');
        }
        
        bootstrap.Modal.getInstance(document.getElementById('elementModal')).hide();
        loadElements();
    } catch (error) {
        console.error('Failed to save element:', error);
        showToast('保存失败', 'error');
    }
}

function editElement(elementId) {
    openElementModal(elementId);
    new bootstrap.Modal(document.getElementById('elementModal')).show();
}

async function deleteElement(elementId) {
    if (!confirm('确定删除此元素定位器？')) return;
    
    try {
        await axios.delete(`${API_BASE}/scripts/elements/${elementId}/`);
        showToast('删除成功');
        loadElements();
    } catch (error) {
        console.error('Failed to delete element:', error);
        showToast('删除失败', 'error');
    }
}

loadElements();