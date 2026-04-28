let actionSets = [];
let currentSteps = [];
let currentParameters = [];
let editingStepIndex = -1;
let groups = [];
let currentPage = 1;
let selectedActionSetIds = new Set();

async function loadGroups() {
    try {
        const response = await axios.get(`${API_BASE}/core/groups/?type=action_set`);
        groups = response.data || [];
        const select = document.getElementById('as-group');
        select.innerHTML = '<option value="">无分组</option>' + 
            groups.map(g => `<option value="${g.id}">${g.name}</option>`).join('');
    } catch (error) {
        console.error('Failed to load groups:', error);
    }
}

async function loadActionSets() {
    try {
        const response = await axios.get(`${API_BASE}/scripts/action-sets/`);
        actionSets = response.data;
        await loadActionSetGroupOptions();
        renderActionSets();
    } catch (error) {
        console.error('Failed to load action sets:', error);
        showToast('加载失败', 'error');
    }
}

async function loadActionSetGroupOptions() {
    try {
        const response = await axios.get(`${API_BASE}/core/groups/?type=action_set`);
        const select = document.getElementById('actionset-group-filter');
        select.innerHTML = '<option value="">全部分组</option><option value="__none__">无分组</option>';
        (response.data || []).forEach(group => {
            const option = document.createElement('option');
            option.value = group.id;
            option.textContent = group.name;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Failed to load groups:', error);
    }
}

function renderActionSets() {
    const keyword = document.getElementById('actionset-search').value.toLowerCase();
    const groupFilter = document.getElementById('actionset-group-filter').value;
    const container = document.getElementById('action-sets-container');
    const countEl = document.getElementById('actionset-count');
    const pageSize = parseInt(document.getElementById('actionset-page-size').value);
    
    let filtered = actionSets.filter(a => {
        const matchKeyword = !keyword || a.name.toLowerCase().includes(keyword);
        let matchGroup = true;
        if (groupFilter === '__none__') {
            matchGroup = !a.group;
        } else if (groupFilter) {
            matchGroup = a.group == groupFilter;
        }
        return matchKeyword && matchGroup;
    });
    
    if (actionSets.length === 0) {
        container.innerHTML = '<div class="text-center text-muted py-5">暂无动作集合</div>';
        countEl.textContent = '';
        return;
    }
    
    const totalPages = Math.ceil(filtered.length / pageSize);
    if (currentPage > totalPages) currentPage = totalPages || 1;
    const start = (currentPage - 1) * pageSize;
    const end = Math.min(start + pageSize, filtered.length);
    const pagedData = filtered.slice(start, end);
    
    countEl.textContent = `显示 ${filtered.length > 0 ? start + 1 : 0}-${end}/${filtered.length} 条`;
    
    if (filtered.length === 0) {
        container.innerHTML = '<div class="text-center text-muted py-5">无匹配结果</div>';
        return;
    }
    
    container.innerHTML = pagedData.map(as => `
        <div class="action-set-card ${as.is_builtin ? 'builtin' : ''}">
            <div class="d-flex justify-content-between align-items-start">
                <div class="d-flex align-items-start gap-2">
                    <div class="form-check mt-1">
                        <input class="form-check-input actionset-checkbox" type="checkbox" value="${as.id}" onchange="toggleActionSetSelection(${as.id})" ${selectedActionSetIds.has(as.id) ? 'checked' : ''}>
                    </div>
                    <div>
                        <h5 class="mb-1">
                            ${as.name}
                            ${as.is_builtin ? '<span class="badge bg-success ms-2">内置</span>' : ''}
                            ${!as.is_active ? '<span class="badge bg-secondary ms-2">禁用</span>' : ''}
                        </h5>
                        <small class="text-muted">${as.code}</small>
                        <p class="mt-2 mb-0">${as.description || '暂无描述'}</p>
                    </div>
                </div>
                <div class="btn-group">
                    <button class="btn btn-outline-success btn-sm" onclick="exportSingleActionSet(${as.id})" title="导出">
                        <i class="bi bi-download"></i>
                    </button>
                    <button class="btn btn-outline-primary btn-sm" onclick="editActionSet(${as.id}, ${as.is_builtin})" title="${as.is_builtin ? '内置动作集合只能查看' : '编辑'}">
                        <i class="bi bi-${as.is_builtin ? 'eye' : 'pencil'}"></i>
                    </button>
                    <button class="btn btn-outline-info btn-sm" onclick="viewActionSet(${as.id})" title="查看详情">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button class="btn btn-outline-danger btn-sm" onclick="deleteActionSet(${as.id})" ${as.is_builtin ? 'disabled title="内置动作集合不能删除"' : 'title="删除"'}>
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
            <div class="mt-3">
                <small class="text-muted">${as.steps_count || 0} 个步骤 | ${as.parameters_count || 0} 个参数</small>
            </div>
        </div>
    `).join('');
    
    updateBatchExportButton();
}

function openCreateModal() {
    document.getElementById('modalTitle').textContent = '创建动作集合';
    document.getElementById('action-set-id').value = '';
    document.getElementById('as-name').value = '';
    document.getElementById('as-code').value = '';
    document.getElementById('as-active').value = 'true';
    document.getElementById('as-description').value = '';
    document.getElementById('as-group').value = '';
    currentSteps = [];
    currentParameters = [];
    renderSteps();
    renderParameters();
    
    const saveBtn = document.querySelector('#actionSetModal .modal-footer .btn-primary');
    saveBtn.disabled = false;
    saveBtn.textContent = '保存';
    document.querySelectorAll('#actionSetModal input, #actionSetModal select, #actionSetModal textarea').forEach(el => {
        el.disabled = false;
    });
    
    new bootstrap.Modal(document.getElementById('actionSetModal')).show();
}

async function editActionSet(id, isBuiltin = false) {
    try {
        const response = await axios.get(`${API_BASE}/scripts/action-sets/${id}/`);
        const as = response.data;
        
        const isReadonly = isBuiltin || as.is_builtin;
        
        document.getElementById('modalTitle').textContent = isReadonly ? '查看动作集合（只读）' : '编辑动作集合';
        document.getElementById('action-set-id').value = id;
        document.getElementById('as-name').value = as.name;
        document.getElementById('as-code').value = as.code;
        document.getElementById('as-active').value = as.is_active ? 'true' : 'false';
        document.getElementById('as-description').value = as.description;
        document.getElementById('as-group').value = as.group || '';
        
        currentSteps = as.steps || [];
        currentParameters = as.parameters || [];
        renderSteps();
        renderParameters();
        
        const saveBtn = document.querySelector('#actionSetModal .modal-footer .btn-primary');
        if (isReadonly) {
            saveBtn.disabled = true;
            saveBtn.textContent = '内置动作集合不可修改';
            document.querySelectorAll('#actionSetModal input, #actionSetModal select, #actionSetModal textarea').forEach(el => {
                el.disabled = true;
            });
        } else {
            saveBtn.disabled = false;
            saveBtn.textContent = '保存';
            document.querySelectorAll('#actionSetModal input, #actionSetModal select, #actionSetModal textarea').forEach(el => {
                el.disabled = false;
            });
        }
        
        new bootstrap.Modal(document.getElementById('actionSetModal')).show();
    } catch (error) {
        console.error('Failed to load action set:', error);
        showToast('加载失败', 'error');
    }
}

async function viewActionSet(id) {
    await editActionSet(id);
}

async function deleteActionSet(id) {
    if (!confirm('确定删除此动作集合？')) return;
    
    try {
        await axios.delete(`${API_BASE}/scripts/action-sets/${id}/`);
        showToast('删除成功');
        loadActionSets();
    } catch (error) {
        console.error('Failed to delete:', error);
        showToast('删除失败', 'error');
    }
}

function addParameter() {
    currentParameters.push({name: '', code: '', default_value: '', is_required: true, order: currentParameters.length});
    renderParameters();
}

function renderParameters() {
    const container = document.getElementById('parameters-container');
    container.innerHTML = currentParameters.map((p, i) => `
        <div class="row mb-2">
            <div class="col-3">
                <input type="text" class="form-control form-control-sm" placeholder="名称" value="${p.name}" onchange="updateParameter(${i}, 'name', this.value)">
            </div>
            <div class="col-3">
                <input type="text" class="form-control form-control-sm" placeholder="代码" value="${p.code}" onchange="updateParameter(${i}, 'code', this.value)">
            </div>
            <div class="col-3">
                <input type="text" class="form-control form-control-sm" placeholder="默认值" value="${p.default_value}" onchange="updateParameter(${i}, 'default_value', this.value)">
            </div>
            <div class="col-2">
                <select class="form-select form-select-sm" onchange="updateParameter(${i}, 'is_required', this.value === 'true')">
                    <option value="true" ${p.is_required ? 'selected' : ''}>必填</option>
                    <option value="false" ${!p.is_required ? 'selected' : ''}>可选</option>
                </select>
            </div>
            <div class="col-1">
                <button class="btn btn-outline-danger btn-sm" onclick="removeParameter(${i})"><i class="bi bi-trash"></i></button>
            </div>
        </div>
    `).join('');
}

function updateParameter(index, field, value) {
    currentParameters[index][field] = value;
}

function removeParameter(index) {
    currentParameters.splice(index, 1);
    renderParameters();
}

let editingStepLocators = [];

function addStep() {
    editingStepIndex = -1;
    editingStepLocators = [{locator_type: 'css', locator_value: '', locator_description: ''}];
    document.getElementById('step-name').value = '';
    document.getElementById('step-action-type').value = 'click';
    document.getElementById('step-value').value = '';
    document.getElementById('step-value-type').value = 'static';
    document.getElementById('step-random-options').value = '';
    document.getElementById('step-random-min').value = '';
    document.getElementById('step-random-max').value = '';
    setStepSelectMode('dropdown');
    document.getElementById('step-enabled').checked = true;
    updateStepFields();
    renderStepLocators();
    new bootstrap.Modal(document.getElementById('stepModal')).show();
}

function editStep(index) {
    editingStepIndex = index;
    const step = currentSteps[index];
    document.getElementById('step-name').value = step.name;
    document.getElementById('step-action-type').value = step.action_type;
    document.getElementById('step-value-type').value = step.action_value_type || 'static';
    document.getElementById('step-value').value = step.action_value || '';
    document.getElementById('step-param-select').value = step.parameter_name || '';
    document.getElementById('step-enabled').checked = step.is_enabled;
    
    if (step.action_config && step.action_config.locators && step.action_config.locators.length > 0) {
        editingStepLocators = step.action_config.locators.map(function(loc) {
            return {
                locator_type: loc.locator_type || 'css',
                locator_value: loc.locator_value || '',
                locator_description: loc.locator_description || ''
            };
        });
    } else {
        editingStepLocators = [{
            locator_type: step.locator_type || 'css',
            locator_value: step.locator_value || '',
            locator_description: step.locator_description || ''
        }];
    }
    
    if (step.random_options && Array.isArray(step.random_options)) {
        document.getElementById('step-random-options').value = step.random_options.join('\n');
    } else {
        document.getElementById('step-random-options').value = '';
    }
    
    document.getElementById('step-random-min').value = step.random_min || '';
    document.getElementById('step-random-max').value = step.random_max || '';
    
    document.getElementById('step-force-click').checked = step.force_click || false;
    
    setStepSelectMode(step.select_mode || 'dropdown');
    
    updateStepFields();
    renderStepLocators();
    new bootstrap.Modal(document.getElementById('stepModal')).show();
}

function renderStepLocators() {
    var container = document.getElementById('step-locators-container');
    var locatorTypes = [
        {value: 'css', label: 'CSS选择器'},
        {value: 'xpath', label: 'XPath'},
        {value: 'id', label: 'ID'},
        {value: 'name', label: 'Name属性'},
        {value: 'class_name', label: 'Class名称'},
        {value: 'tag_name', label: '标签名'},
        {value: 'text', label: '文本内容'},
        {value: 'role', label: 'Role'},
        {value: 'test_id', label: 'Test ID'},
        {value: 'placeholder', label: 'Placeholder'},
        {value: 'label', label: 'Label文本'}
    ];
    var html = '';
    editingStepLocators.forEach(function(loc, idx) {
        var badge = idx === 0 ? '<span class="badge bg-primary me-1">首选</span>' : '<span class="badge bg-secondary me-1">备选' + idx + '</span>';
        html += '<div class="row mb-2 align-items-center">' +
            '<div class="col-auto">' + badge + '</div>' +
            '<div class="col-3">' +
                '<select class="form-select form-select-sm" data-loc-index="' + idx + '" data-loc-field="locator_type" onchange="onStepLocatorChange(' + idx + ', \'locator_type\', this.value)">' +
                    locatorTypes.map(function(t) {
                        return '<option value="' + t.value + '"' + (loc.locator_type === t.value ? ' selected' : '') + '>' + t.label + '</option>';
                    }).join('') +
                '</select>' +
            '</div>' +
            '<div class="col-4">' +
                '<input type="text" class="form-control form-control-sm" data-loc-index="' + idx + '" data-loc-field="locator_value" value="' + (loc.locator_value || '').replace(/"/g, '&quot;') + '" placeholder="定位值" onchange="onStepLocatorChange(' + idx + ', \'locator_value\', this.value)">' +
            '</div>' +
            '<div class="col-3">' +
                '<input type="text" class="form-control form-control-sm" data-loc-index="' + idx + '" data-loc-field="locator_description" value="' + (loc.locator_description || '').replace(/"/g, '&quot;') + '" placeholder="描述" onchange="onStepLocatorChange(' + idx + ', \'locator_description\', this.value)">' +
            '</div>' +
            '<div class="col-auto">' +
                (editingStepLocators.length > 1 ? '<button type="button" class="btn btn-outline-danger btn-sm" onclick="removeStepLocator(' + idx + ')"><i class="bi bi-trash"></i></button>' : '') +
            '</div>' +
        '</div>';
    });
    container.innerHTML = html;
}

function onStepLocatorChange(index, field, value) {
    editingStepLocators[index][field] = value;
}

function addStepLocator() {
    editingStepLocators.push({locator_type: 'css', locator_value: '', locator_description: ''});
    renderStepLocators();
}

function removeStepLocator(index) {
    editingStepLocators.splice(index, 1);
    renderStepLocators();
}

function setStepSelectMode(mode) {
    document.getElementById('step-select-mode').value = mode;
    document.getElementById('step-mode-dropdown-btn').classList.toggle('active', mode === 'dropdown');
    document.getElementById('step-mode-click-btn').classList.toggle('active', mode === 'click');
}

function updateStepFields() {
    const actionType = document.getElementById('step-action-type').value;
    const needsElement = ['click', 'fill', 'select', 'random_select', 'random_number', 'wait_for_selector', 'hover', 'focus', 'assert_text'].includes(actionType);
    const needsValue = ['fill', 'select', 'wait', 'press', 'assert_text'].includes(actionType);
    const needsRandomOptions = actionType === 'random_select';
    const needsRandomNumber = actionType === 'random_number';
    const needsForceClick = actionType === 'click';
    
    document.getElementById('step-locator-section').style.display = needsElement ? 'block' : 'none';
    document.getElementById('step-value-section').style.display = needsValue ? 'block' : 'none';
    document.getElementById('step-random-options-section').style.display = needsRandomOptions ? 'block' : 'none';
    document.getElementById('step-random-number-section').style.display = needsRandomNumber ? 'block' : 'none';
    document.getElementById('step-force-click-section').style.display = needsForceClick ? 'block' : 'none';
}

function updateValueField() {
    const valueType = document.getElementById('step-value-type').value;
    const paramSelect = document.getElementById('step-param-select');
    const valueInput = document.getElementById('step-value');
    
    if (valueType === 'parameter') {
        paramSelect.innerHTML = currentParameters.map(p => `<option value="${p.code}">${p.name}</option>`).join('');
        paramSelect.classList.remove('d-none');
        valueInput.classList.add('d-none');
    } else {
        paramSelect.classList.add('d-none');
        valueInput.classList.remove('d-none');
    }
}

function confirmStep() {
    const actionType = document.getElementById('step-action-type').value;
    var actionConfig = {};
    
    if (editingStepLocators.length > 0) {
        actionConfig.locators = editingStepLocators.filter(function(loc) {
            return loc.locator_value.trim() !== '';
        });
    }

    var primaryLocator = editingStepLocators[0] || {locator_type: 'css', locator_value: '', locator_description: ''};
    
    const step = {
        name: document.getElementById('step-name').value || `步骤 ${currentSteps.length + 1}`,
        order: editingStepIndex >= 0 ? currentSteps[editingStepIndex].order : currentSteps.length,
        action_type: actionType,
        locator_type: primaryLocator.locator_type,
        locator_value: primaryLocator.locator_value,
        locator_description: primaryLocator.locator_description,
        action_value: document.getElementById('step-value').value,
        action_value_type: document.getElementById('step-value-type').value,
        parameter_name: document.getElementById('step-value-type').value === 'parameter' ? document.getElementById('step-param-select').value : '',
        is_enabled: document.getElementById('step-enabled').checked,
        wait_timeout: 10000,
        action_config: actionConfig,
    };
    
    if (actionType === 'random_select') {
        const randomOptionsText = document.getElementById('step-random-options').value;
        step.random_options = randomOptionsText.split('\n')
            .map(line => line.trim())
            .filter(line => line.length > 0);
        step.select_mode = document.getElementById('step-select-mode').value;
    }
    
    if (actionType === 'random_number') {
        step.random_min = parseInt(document.getElementById('step-random-min').value) || 0;
        step.random_max = parseInt(document.getElementById('step-random-max').value) || 100;
    }
    
    if (actionType === 'click') {
        step.force_click = document.getElementById('step-force-click').checked;
    }
    
    if (editingStepIndex >= 0) {
        currentSteps[editingStepIndex] = step;
    } else {
        currentSteps.push(step);
    }
    
    renderSteps();
    bootstrap.Modal.getInstance(document.getElementById('stepModal')).hide();
}

function renderSteps() {
    const container = document.getElementById('steps-container');
    container.innerHTML = currentSteps.map((s, i) => {
        var locators = (s.action_config && s.action_config.locators) || [];
        var locInfo = locators.length > 1 ? locators.length + '个定位器' : (locators.length === 1 || s.locator_value ? '1个定位器' : '无定位器');
        return `
        <div class="step-item d-flex justify-content-between align-items-center">
            <div>
                <span class="step-number">${i + 1}</span>
                <strong>${s.name}</strong>
                <small class="text-muted ms-2">${s.action_type} - ${locInfo}</small>
            </div>
            <div>
                <button class="btn btn-outline-secondary btn-sm" onclick="editStep(${i})"><i class="bi bi-pencil"></i></button>
                <button class="btn btn-outline-danger btn-sm" onclick="removeStep(${i})"><i class="bi bi-trash"></i></button>
            </div>
        </div>
    `;
    }).join('');
}

function removeStep(index) {
    currentSteps.splice(index, 1);
    currentSteps.forEach((s, i) => s.order = i);
    renderSteps();
}

async function saveActionSet() {
    const id = document.getElementById('action-set-id').value;
    const data = {
        name: document.getElementById('as-name').value,
        code: document.getElementById('as-code').value,
        is_active: document.getElementById('as-active').value === 'true',
        description: document.getElementById('as-description').value,
        group: document.getElementById('as-group').value || null,
        steps: currentSteps,
        parameters: currentParameters,
    };
    
    if (!data.name || !data.code) {
        showToast('请填写名称和代码', 'error');
        return;
    }
    
    try {
        if (id) {
            await axios.put(`${API_BASE}/scripts/action-sets/${id}/`, data);
        } else {
            await axios.post(`${API_BASE}/scripts/action-sets/`, data);
        }
        bootstrap.Modal.getInstance(document.getElementById('actionSetModal')).hide();
        showToast('保存成功');
        loadActionSets();
    } catch (error) {
        console.error('Failed to save:', error);
        showToast('保存失败: ' + (error.response?.data?.detail || error.message), 'error');
    }
}

function resetActionSetSearch() {
    document.getElementById('actionset-search').value = '';
    document.getElementById('actionset-group-filter').value = '';
    currentPage = 1;
    renderActionSets();
}

document.getElementById('actionset-search').addEventListener('input', () => { currentPage = 1; renderActionSets(); });
document.getElementById('actionset-group-filter').addEventListener('change', () => { currentPage = 1; renderActionSets(); });
document.getElementById('actionset-page-size').addEventListener('change', () => { currentPage = 1; renderActionSets(); });

loadGroups();
loadActionSets();

window.openRecordingModal = function() {
    recRestart('asRecordingModal');
    new bootstrap.Modal(document.getElementById('asRecordingModal')).show();
};

window.recConfirm = function(modalId) {
    var data = window.getRecData(modalId);
    if (!data.actions || data.actions.length === 0) {
        showToast('没有录制的操作可导入', 'error');
        return;
    }

    var typeMap = {
        click: 'click', fill: 'fill', select: 'select',
        check: 'check', uncheck: 'uncheck', press: 'press',
        scroll: 'scroll', navigate: 'navigate', hover: 'hover',
        random_select: 'random_select', random_number: 'random_number'
    };

    data.actions.forEach(function(action) {
        var actionConfig = {};
        var locatorType = 'css';
        var locatorValue = '';
        var locatorDescription = '';

        if (action.locators && action.locators.length > 0) {
            actionConfig.locators = action.locators.map(function(loc) {
                return {
                    locator_type: loc.locator_type,
                    locator_value: loc.locator_value,
                    locator_description: loc.locator_description || ''
                };
            });
            locatorType = action.locators[0].locator_type;
            locatorValue = action.locators[0].locator_value;
            locatorDescription = action.locators[0].locator_description || '';
        } else if (action.locator) {
            locatorType = action.locator.locator_type;
            locatorValue = action.locator.locator_value;
            locatorDescription = action.locator.locator_description || '';
            actionConfig.locators = [{
                locator_type: locatorType,
                locator_value: locatorValue,
                locator_description: locatorDescription
            }];
        }

        if (action.random_options) {
            actionConfig.random_options = action.random_options;
            actionConfig.select_mode = action.select_mode || 'dropdown';
        }
        if (action.random_min !== undefined) {
            actionConfig.random_min = action.random_min;
            actionConfig.random_max = action.random_max;
        }

        var step = {
            name: action.description || action.action_type,
            order: currentSteps.length,
            action_type: typeMap[action.action_type] || 'click',
            locator_type: locatorType,
            locator_value: locatorValue,
            locator_description: locatorDescription,
            action_value: action.value || '',
            action_value_type: 'static',
            parameter_name: '',
            is_enabled: true,
            wait_timeout: 10000,
            action_config: actionConfig,
        };
        currentSteps.push(step);
    });

    renderSteps();
    data.confirmed = true;
    bootstrap.Modal.getInstance(document.getElementById(modalId)).hide();
    showToast('已导入 ' + data.actions.length + ' 个录制步骤');
};

function toggleActionSetSelection(id) {
    if (selectedActionSetIds.has(id)) {
        selectedActionSetIds.delete(id);
    } else {
        selectedActionSetIds.add(id);
    }
    updateBatchExportButton();
}

function updateBatchExportButton() {
    const btn = document.getElementById('btn-batch-export');
    const countEl = document.getElementById('export-count');
    
    if (selectedActionSetIds.size > 0) {
        btn.style.display = 'inline-block';
        countEl.textContent = `(${selectedActionSetIds.size})`;
    } else {
        btn.style.display = 'none';
    }
}

async function exportSingleActionSet(id) {
    try {
        const response = await axios.get(`${API_BASE}/scripts/action-sets/${id}/export/`);
        const data = response.data;
        downloadJsonFile([data], `${data.code}_${data.name}.json`);
        showToast('导出成功');
    } catch (error) {
        console.error('Failed to export:', error);
        showToast('导出失败', 'error');
    }
}

async function batchExportActionSets() {
    if (selectedActionSetIds.size === 0) {
        showToast('请至少选择一个动作集合', 'error');
        return;
    }
    
    try {
        const ids = Array.from(selectedActionSetIds);
        const response = await axios.post(`${API_BASE}/scripts/action-sets/export/`, { ids: ids });
        const data = response.data;
        downloadJsonFile(data, `action_sets_export_${new Date().toISOString().slice(0,10)}.json`);
        showToast(`已导出 ${data.length} 个动作集合`);
    } catch (error) {
        console.error('Failed to batch export:', error);
        showToast('批量导出失败', 'error');
    }
}

function downloadJsonFile(data, filename) {
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function openImportModal() {
    document.getElementById('import-file-input').click();
}

async function handleImportFile(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    try {
        const text = await file.text();
        const data = JSON.parse(text);
        
        if (!Array.isArray(data) && typeof data !== 'object') {
            showToast('文件格式错误：应为JSON数组或JSON对象', 'error');
            return;
        }
        
        const importData = Array.isArray(data) ? data : [data];
        
        const response = await axios.post(`${API_BASE}/scripts/action-sets/import/`, importData);
        const result = response.data;
        
        let message = result.message;
        if (result.errors && result.errors.length > 0) {
            message += '\n错误详情：' + result.errors.map(e => `${e.item}: ${e.error}`).join('\n');
        }
        
        showToast(message);
        loadActionSets();
    } catch (error) {
        console.error('Failed to import:', error);
        if (error.response && error.response.data && error.response.data.detail) {
            showToast('导入失败: ' + error.response.data.detail, 'error');
        } else {
            showToast('导入失败：文件格式不正确', 'error');
        }
    }
    
    event.target.value = '';
}