let groups = [];

async function loadGroups() {
    try {
        const response = await axios.get(`${API_BASE}/core/groups/`);
        groups = response.data || [];
        renderGroups();
    } catch (error) {
        console.error('Failed to load groups:', error);
    }
}

function renderGroups() {
    const types = ['script', 'action_set', 'task'];
    const typeNames = {
        'script': 'script-groups',
        'action_set': 'action-set-groups',
        'task': 'task-groups'
    };
    
    types.forEach(type => {
        const container = document.getElementById(typeNames[type]);
        const typeGroups = groups.filter(g => g.type === type);
        
        if (typeGroups.length === 0) {
            container.innerHTML = '<div class="text-muted">暂无分组</div>';
            return;
        }
        
        const rootGroups = typeGroups.filter(g => !g.parent);
        container.innerHTML = renderGroupTree(rootGroups, typeGroups, 0);
    });
}

function renderGroupTree(rootGroups, allGroups, level) {
    let html = '<ul class="list-unstyled">';
    
    rootGroups.forEach(group => {
        const children = allGroups.filter(g => g.parent === group.id);
        const indent = level * 20;
        
        html += `
            <li class="mb-2" style="padding-left: ${indent}px;">
                <div class="d-flex align-items-center justify-content-between p-2 border rounded">
                    <div>
                        ${children.length > 0 ? '<i class="bi bi-folder-fill text-warning me-2"></i>' : '<i class="bi bi-folder text-secondary me-2"></i>'}
                        <strong>${group.name}</strong>
                        <small class="text-muted ms-2">(${group.code})</small>
                        ${group.description ? `<br><small class="text-muted">${group.description}</small>` : ''}
                    </div>
                    <div>
                        <button class="btn btn-outline-primary btn-sm" onclick="editGroup(${group.id})" title="编辑">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-outline-danger btn-sm" onclick="deleteGroup(${group.id})" title="删除">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
                ${children.length > 0 ? renderGroupTree(children, allGroups, level + 1) : ''}
            </li>
        `;
    });
    
    html += '</ul>';
    return html;
}

function openGroupModal(id = null) {
    document.getElementById('group-id').value = id || '';
    document.getElementById('group-name').value = '';
    document.getElementById('group-code').value = '';
    document.getElementById('group-type').value = 'script';
    document.getElementById('group-parent').innerHTML = '<option value="">无</option>';
    document.getElementById('group-description').value = '';
    document.getElementById('group-order').value = '0';
    
    if (id) {
        const group = groups.find(g => g.id === id);
        if (group) {
            document.getElementById('groupModalTitle').textContent = '编辑分组';
            document.getElementById('group-name').value = group.name;
            document.getElementById('group-code').value = group.code;
            document.getElementById('group-type').value = group.type;
            document.getElementById('group-description').value = group.description || '';
            document.getElementById('group-order').value = group.order;
            
            updateParentSelect(group.type, group.parent, group.id);
        }
    } else {
        document.getElementById('groupModalTitle').textContent = '创建分组';
        updateParentSelect('script');
    }
}

function updateParentSelect(type, selectedParent = null, excludeId = null) {
    const select = document.getElementById('group-parent');
    const typeGroups = groups.filter(g => g.type === type && g.id !== excludeId);
    
    let html = '<option value="">无</option>';
    typeGroups.forEach(g => {
        const selected = g.id === selectedParent ? 'selected' : '';
        html += `<option value="${g.id}" ${selected}>${g.full_path}</option>`;
    });
    
    select.innerHTML = html;
}

document.getElementById('group-type').addEventListener('change', function() {
    updateParentSelect(this.value);
});

async function saveGroup() {
    const id = document.getElementById('group-id').value;
    const name = document.getElementById('group-name').value;
    const code = document.getElementById('group-code').value;
    const type = document.getElementById('group-type').value;
    const parent = document.getElementById('group-parent').value;
    const description = document.getElementById('group-description').value;
    const order = document.getElementById('group-order').value;
    
    if (!name || !code || !type) {
        showToast('请填写必填项', 'error');
        return;
    }
    
    const data = {
        name: name,
        code: code,
        type: type,
        parent: parent || null,
        description: description,
        order: parseInt(order) || 0
    };
    
    try {
        if (id) {
            await axios.put(`${API_BASE}/core/groups/${id}/`, data);
            showToast('更新成功');
        } else {
            await axios.post(`${API_BASE}/core/groups/`, data);
            showToast('创建成功');
        }
        
        bootstrap.Modal.getInstance(document.getElementById('groupModal')).hide();
        loadGroups();
    } catch (error) {
        console.error('Failed to save group:', error);
        showToast('保存失败: ' + (error.response?.data?.detail || error.message), 'error');
    }
}

function editGroup(id) {
    openGroupModal(id);
    new bootstrap.Modal(document.getElementById('groupModal')).show();
}

async function deleteGroup(id) {
    const group = groups.find(g => g.id === id);
    if (!group) return;
    
    if (group.children_count > 0) {
        showToast('该分组下有子分组，无法删除', 'error');
        return;
    }
    
    if (!confirm('确定删除此分组？')) return;
    
    try {
        await axios.delete(`${API_BASE}/core/groups/${id}/`);
        showToast('删除成功');
        loadGroups();
    } catch (error) {
        console.error('Failed to delete group:', error);
        showToast('删除失败: ' + (error.response?.data?.error || error.message), 'error');
    }
}

loadGroups();