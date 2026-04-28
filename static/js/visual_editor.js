var steps = [];
var expandedStepIndex = -1;
var allScripts = [];
var currentScriptId = null;
var actionSets = [];
var groups = [];

var LOCATOR_TYPES = [
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

var ACTION_TYPES = [
    {value: 'navigate', label: '导航', icon: 'bi-globe'},
    {value: 'click', label: '点击', icon: 'bi-cursor'},
    {value: 'fill', label: '填充', icon: 'bi-input-cursor-text'},
    {value: 'select', label: '选择', icon: 'bi-list'},
    {value: 'random_select', label: '随机选择', icon: 'bi-shuffle'},
    {value: 'random_number', label: '随机数值', icon: 'bi-hash'},
    {value: 'wait', label: '等待', icon: 'bi-hourglass-split'},
    {value: 'screenshot', label: '截图', icon: 'bi-camera'},
    {value: 'scroll', label: '滚动', icon: 'bi-arrows-expand'},
    {value: 'hover', label: '悬停', icon: 'bi-hand-index'},
    {value: 'assert_text', label: '断言', icon: 'bi-check2-all'},
    {value: 'action_set', label: '动作集合', icon: 'bi-collection'}
];

function locatorTypeOptions(selected) {
    var types = ['css','xpath','id','name','class_name','tag_name','text','role','test_id','placeholder','label'];
    return types.map(function(t) {
        return '<option value="' + t + '"' + (t === selected ? ' selected' : '') + '>' + t + '</option>';
    }).join('');
}

function needsElement(actionType) {
    return ['click', 'fill', 'select', 'random_select', 'random_number', 'check', 'uncheck', 'hover', 'focus',
            'wait_for_selector', 'scroll', 'assert_text', 'assert_value'].indexOf(actionType) >= 0;
}

function needsValue(actionType) {
    return ['navigate', 'fill', 'select', 'wait', 'press', 'assert_text', 'assert_value'].indexOf(actionType) >= 0;
}

async function initEditor() {
    try {
        await loadActionSets();
        await loadGroups();

        var urlParams = new URLSearchParams(window.location.search);
        var scriptId = urlParams.get('script_id');
        if (scriptId) {
            await loadScriptById(scriptId);
        }
    } catch (error) {
        console.error('Failed to init editor:', error);
    }
}

async function loadGroups() {
    try {
        var response = await axios.get(API_BASE + '/core/groups/?type=script');
        groups = response.data || [];
        var select = document.getElementById('script-group');
        select.innerHTML = '<option value="">无分组</option>' +
            groups.map(function(g) { return '<option value="' + g.id + '">' + g.name + '</option>'; }).join('');
    } catch (error) {
        console.error('Failed to load groups:', error);
    }
}

async function loadActionSets() {
    try {
        var response = await axios.get(API_BASE + '/scripts/action-sets/');
        actionSets = response.data || [];
    } catch (error) {
        console.error('Failed to load action sets:', error);
    }
}

function getCategoryLabel(category) {
    var labels = {
        'input': '输入操作',
        'navigation': '导航操作',
        'form': '表单操作',
        'validation': '验证操作',
        'general': '通用操作'
    };
    return labels[category] || category;
}

function getActionIcon(actionType) {
    var icons = {
        'navigate': 'bi-globe', 'click': 'bi-cursor', 'fill': 'bi-input-cursor-text',
        'select': 'bi-list', 'random_select': 'bi-shuffle', 'random_number': 'bi-hash',
        'check': 'bi-check-square', 'uncheck': 'bi-square', 'wait': 'bi-hourglass-split',
        'screenshot': 'bi-camera', 'scroll': 'bi-arrows-expand', 'hover': 'bi-hand-index',
        'assert_text': 'bi-check2-all', 'action_set': 'bi-collection'
    };
    return icons[actionType] || 'bi-gear';
}

function getActionLabel(actionType) {
    var labels = {
        'navigate': '导航', 'click': '点击', 'fill': '填充',
        'select': '选择', 'random_select': '随机选择', 'random_number': '随机数值',
        'check': '勾选', 'uncheck': '取消勾选', 'wait': '等待',
        'screenshot': '截图', 'scroll': '滚动', 'hover': '悬停',
        'assert_text': '断言文本', 'action_set': '动作集合'
    };
    return labels[actionType] || actionType;
}

async function loadScriptById(scriptId) {
    try {
        var response = await axios.get(API_BASE + '/scripts/' + scriptId + '/');
        var script = response.data;

        currentScriptId = scriptId;
        document.getElementById('script-id').value = scriptId;
        document.getElementById('script-name').value = script.name;
        document.getElementById('script-code').value = script.code;
        document.getElementById('target-url').value = script.target_url;
        document.getElementById('script-description').value = script.description || '';
        document.getElementById('script-status').value = script.status;
        document.getElementById('script-group').value = script.group || '';

        steps = script.steps.map(function(s) {
            var config = s.action_config || {};
            if (!config.locators) {
                config.locators = [];
                if (config.locator_type || config.locator_value) {
                    config.locators.push({
                        locator_type: config.locator_type || 'css',
                        locator_value: config.locator_value || '',
                        locator_description: config.locator_description || ''
                    });
                }
                if (config.backup_locator) {
                    config.locators.push({
                        locator_type: config.backup_locator.locator_type || 'css',
                        locator_value: config.backup_locator.locator_value || '',
                        locator_description: '备用定位器'
                    });
                }
                delete config.locator_type;
                delete config.locator_value;
                delete config.locator_description;
                delete config.backup_locator;
            }
            if (config.locators.length === 0 && s.element) {
                config.locators.push({
                    locator_type: s.element.locator_type || 'css',
                    locator_value: s.element.locator_value || '',
                    locator_description: s.element.name || ''
                });
            }
            return {
                id: s.id,
                name: s.name,
                action_type: s.action_type,
                value: s.action_value,
                config: config,
                is_enabled: s.is_enabled,
                continue_on_failure: s.continue_on_failure,
                retry_count: s.retry_count,
                retry_interval: s.retry_interval,
                action_set_ref: s.action_set_ref || null,
                action_set_params: s.action_set_params || {}
            };
        });

        renderSteps();
        showToast('脚本加载成功');
    } catch (error) {
        console.error('Failed to load script:', error);
        showToast('加载脚本失败', 'error');
    }
}

async function loadScriptList() {
    try {
        var response = await axios.get(API_BASE + '/scripts/');
        allScripts = response.data;
        renderScriptList();
    } catch (error) {
        console.error('Failed to load script list:', error);
    }
}

function renderScriptList() {
    var container = document.getElementById('script-list');

    if (allScripts.length === 0) {
        container.innerHTML = '<div class="text-center text-muted py-4">暂无脚本</div>';
        return;
    }

    container.innerHTML = allScripts.map(function(script) {
        return '<div class="script-list-item" onclick="selectScriptToLoad(' + script.id + ')">' +
            '<div class="fw-bold">' + script.name + '</div>' +
            '<small class="text-muted">' + script.code + ' - v' + script.version + ' - ' + (script.steps_count || 0) + '个步骤</small>' +
        '</div>';
    }).join('');
}

async function selectScriptToLoad(scriptId) {
    bootstrap.Modal.getInstance(document.getElementById('openScriptModal')).hide();
    await loadScriptById(scriptId);
}

function addStep() {
    var step = {
        name: '步骤 ' + (steps.length + 1),
        action_type: 'click',
        value: '',
        config: {
            locators: [{ locator_type: 'css', locator_value: '', locator_description: '' }]
        },
        is_enabled: true,
        continue_on_failure: false,
        retry_count: 0,
        retry_interval: 1000
    };
    steps.push(step);
    renderSteps();
    toggleStep(steps.length - 1);
}

var selectedStepIds = new Set();

function renderSteps() {
    var container = document.getElementById('steps-container');

    if (steps.length === 0) {
        selectedStepIds.clear();
        updateBatchDeleteBtn();
        container.innerHTML =
            '<div class="drop-zone" id="drop-zone">' +
                '<i class="bi bi-plus-circle fs-1"></i>' +
                '<p class="mt-2">点击"添加步骤"开始创建测试流程</p>' +
            '</div>';
        return;
    }

    var html = '';
    steps.forEach(function(step, index) {
        var actionIcon = getActionIcon(step.action_type);
        var isActive = expandedStepIndex === index;
        var activeClass = isActive ? 'active' : '';
        var checked = selectedStepIds.has(index) ? 'checked' : '';

        var summary = getActionLabel(step.action_type);
        if (step.action_type === 'action_set' && step.action_set_ref) {
            var as = actionSets.find(function(a) { return a.id === step.action_set_ref; });
            if (as) summary += ' - ' + as.name;
        } else {
            var locCount = (step.config && step.config.locators) ? step.config.locators.length : 0;
            var locInfo = locCount > 0 ? locCount + '个定位器' : '无定位器';
            summary += ' - ' + locInfo;
        }

        var bpTags = '';
        if (step.config && step.config.breakpoint_start) {
            bpTags += ' <span class="badge bg-warning text-dark" style="font-size:0.7rem">断点开始</span>';
        }
        if (step.config && step.config.breakpoint_end) {
            bpTags += ' <span class="badge bg-danger" style="font-size:0.7rem">断点结束</span>';
        }

        html += '<div class="step-card ' + activeClass + '" data-index="' + index + '"' +
                 ' ondragover="dragOver(event)" ondrop="drop(event, ' + index + ')">' +
            '<div class="step-header" draggable="true" ondragstart="dragStart(event, ' + index + ')" onclick="toggleStep(' + index + ')">' +
                '<div class="step-title">' +
                    '<input type="checkbox" class="form-check-input step-checkbox me-2"' +
                    ' ' + checked + ' onclick="event.stopPropagation(); toggleStepSelect(' + index + ', this.checked)">' +
                    '<span class="step-number">' + (index + 1) + '</span>' +
                    '<div style="min-width:0; flex:1;">' +
                        '<div class="fw-bold">' + escapeHtml(step.name) + '</div>' +
                        '<small class="text-muted step-summary"><i class="bi ' + actionIcon + '"></i> ' + escapeHtml(summary) + bpTags + '</small>' +
                    '</div>' +
                '</div>' +
                '<div class="step-actions">' +
                    '<i class="bi bi-chevron-down expand-icon me-2"></i>' +
                    '<button class="btn btn-outline-secondary btn-sm" onclick="event.stopPropagation(); moveStep(' + index + ', -1)" title="上移"><i class="bi bi-arrow-up"></i></button>' +
                    '<button class="btn btn-outline-secondary btn-sm" onclick="event.stopPropagation(); moveStep(' + index + ', 1)" title="下移"><i class="bi bi-arrow-down"></i></button>' +
                    '<button class="btn btn-outline-danger btn-sm" onclick="event.stopPropagation(); deleteStep(' + index + ')" title="删除"><i class="bi bi-trash"></i></button>' +
                '</div>' +
            '</div>' +
            '<div class="step-config-body">' +
                '<div class="step-config-content">' +
                    renderStepConfig(step, index) +
                '</div>' +
            '</div>' +
        '</div>';
    });

    container.innerHTML = html;
    bindStepConfigEvents();
}

function renderStepConfig(step, index) {
    var html = '';

    html += '<div class="config-field">' +
        '<label>步骤名称</label>' +
        '<input type="text" class="form-control form-control-sm" data-field="name" value="' + escapeAttr(step.name) + '">' +
    '</div>';

    html += '<div class="config-field">' +
        '<label>操作类型</label>' +
        '<div class="action-type-row">';
    ACTION_TYPES.forEach(function(at) {
        html += '<div class="action-type-btn-sm' + (step.action_type === at.value ? ' selected' : '') + '" data-action="' + at.value + '" onclick="setStepActionType(' + index + ', \'' + at.value + '\')">' +
            '<i class="bi ' + at.icon + '"></i> ' + at.label +
        '</div>';
    });
    html += '</div></div>';

    if (needsElement(step.action_type)) {
        var locators = step.config.locators || [];
        var locatorsHtml = '<div class="mb-3"><label class="form-label small fw-bold">定位器</label>';
        locators.forEach(function(loc, locIdx) {
            locatorsHtml += '<div class="d-flex gap-1 mb-1 align-items-center loc-item">'
                + '<select class="form-select form-select-sm" style="max-width:120px" onchange="updateLocator(' + index + ',' + locIdx + ',\'locator_type\',this.value)">'
                + locatorTypeOptions(loc.locator_type || 'css')
                + '</select>'
                + '<input type="text" class="form-control form-control-sm" placeholder="定位值" value="' + (loc.locator_value || '').replace(/"/g, '&quot;') + '" onchange="updateLocator(' + index + ',' + locIdx + ',\'locator_value\',this.value)">'
                + '<input type="text" class="form-control form-control-sm" style="max-width:120px" placeholder="描述" value="' + (loc.locator_description || '').replace(/"/g, '&quot;') + '" onchange="updateLocator(' + index + ',' + locIdx + ',\'locator_description\',this.value)">'
                + (locators.length > 1 ? '<button class="btn btn-sm btn-outline-danger" onclick="removeLocator(' + index + ',' + locIdx + ')"><i class="bi bi-dash"></i></button>' : '')
                + '</div>';
        });
        locatorsHtml += '<button class="btn btn-sm btn-outline-primary" onclick="addLocator(' + index + ')"><i class="bi bi-plus"></i> 添加定位器</button>';
        locatorsHtml += '</div>';
        html += locatorsHtml;
    }

    if (step.action_type === 'action_set') {
        var categories = {};
        actionSets.forEach(function(as) {
            if (!categories[as.category]) categories[as.category] = [];
            categories[as.category].push(as);
        });

        html += '<div class="config-field">' +
            '<label>选择动作集合</label>' +
            '<select class="form-select form-select-sm" data-field="action_set_ref" onchange="onActionSetChange(' + index + ')">' +
                '<option value="">-- 请选择动作集合 --</option>';
        for (var cat in categories) {
            html += '<optgroup label="' + getCategoryLabel(cat) + '">';
            categories[cat].forEach(function(as) {
                html += '<option value="' + as.id + '"' + (step.action_set_ref == as.id ? ' selected' : '') + '>' + as.name + ' (' + as.code + ')</option>';
            });
            html += '</optgroup>';
        }
        html += '</select></div>';

        if (step.action_set_ref) {
            html += '<div id="action-set-params-' + index + '"></div>';
            html += '<div id="action-set-preview-' + index + '"></div>';
        }
    }

    if (needsValue(step.action_type)) {
        html += '<div class="config-field">' +
            '<label>操作值</label>' +
            '<input type="text" class="form-control form-control-sm" data-field="value" value="' + escapeAttr(step.value || '') + '" placeholder="输入值">' +
            '<small class="text-muted">支持参数占位符: {{parameter_name}}</small>' +
        '</div>';
    }

    if (step.action_type === 'random_select') {
        var opts = (step.config && step.config.random_options) ? step.config.random_options.join('\n') : '';
        var mode = (step.config && step.config.select_mode) ? step.config.select_mode : 'dropdown';
        html += '<div class="config-field">' +
            '<label>选择模式</label>' +
            '<div class="btn-group btn-group-sm" role="group">' +
                '<button type="button" class="btn btn-outline-primary' + (mode === 'dropdown' ? ' active' : '') + '" onclick="setStepSelectMode(' + index + ', \'dropdown\')">下拉框选择</button>' +
                '<button type="button" class="btn btn-outline-primary' + (mode === 'click' ? ' active' : '') + '" onclick="setStepSelectMode(' + index + ', \'click\')">点击卡片</button>' +
            '</div>' +
        '</div>';
        html += '<div class="config-field">' +
            '<label>随机选项</label>' +
            '<textarea class="form-control form-control-sm" data-field="random_options" rows="4" placeholder="每行输入一个选项值">' + escapeHtml(opts) + '</textarea>' +
            '<small class="text-muted">每行一个选项，执行时将随机选择其中一个</small>' +
        '</div>';
    }

    if (step.action_type === 'random_number') {
        html += '<div class="config-field">' +
            '<label>随机数值配置</label>' +
            '<div class="config-row">' +
                '<div><label class="small">最小值</label><input type="number" class="form-control form-control-sm" data-field="random_min" value="' + (step.config.random_min || '') + '"></div>' +
                '<div><label class="small">最大值</label><input type="number" class="form-control form-control-sm" data-field="random_max" value="' + (step.config.random_max || '') + '"></div>' +
            '</div>' +
        '</div>';
    }

    html += '<div class="config-field">' +
        '<div class="form-check form-check-inline">' +
            '<input class="form-check-input" type="checkbox" data-field="is_enabled"' + (step.is_enabled ? ' checked' : '') + '>' +
            '<label class="form-check-label">启用</label>' +
        '</div>' +
        '<div class="form-check form-check-inline">' +
            '<input class="form-check-input" type="checkbox" data-field="continue_on_failure"' + (step.continue_on_failure ? ' checked' : '') + '>' +
            '<label class="form-check-label">失败继续</label>' +
        '</div>' +
    '</div>';

    var bpStart = (step.config && step.config.breakpoint_start) ? ' checked' : '';
    var bpEnd = (step.config && step.config.breakpoint_end) ? ' checked' : '';
    html += '<div class="config-field">' +
        '<div class="form-check form-check-inline">' +
            '<input class="form-check-input" type="checkbox" data-field="breakpoint_start"' + bpStart + '>' +
            '<label class="form-check-label">断点开始</label>' +
        '</div>' +
        '<div class="form-check form-check-inline">' +
            '<input class="form-check-input" type="checkbox" data-field="breakpoint_end"' + bpEnd + '>' +
            '<label class="form-check-label">断点结束</label>' +
        '</div>' +
    '</div>';

    html += '<div class="config-row">' +
        '<div class="config-field">' +
            '<label>重试次数</label>' +
            '<input type="number" class="form-control form-control-sm" data-field="retry_count" value="' + step.retry_count + '" min="0">' +
        '</div>' +
        '<div class="config-field">' +
            '<label>重试间隔(ms)</label>' +
            '<input type="number" class="form-control form-control-sm" data-field="retry_interval" value="' + step.retry_interval + '" min="0">' +
        '</div>' +
    '</div>';

    return html;
}

function bindStepConfigEvents() {
    document.querySelectorAll('.step-card[data-index] .step-config-content [data-field]').forEach(function(el) {
        var events = el.tagName === 'SELECT' ? ['change'] : ['input', 'change'];
        events.forEach(function(evt) {
            el.addEventListener(evt, function() {
                var card = el.closest('.step-card');
                var index = parseInt(card.dataset.index);
                syncStepFromUI(index);
            });
        });
    });
}

function syncStepFromUI(index) {
    var card = document.querySelector('.step-card[data-index="' + index + '"]');
    if (!card) return;
    var step = steps[index];
    if (!step) return;

    var nameEl = card.querySelector('[data-field="name"]');
    if (nameEl) step.name = nameEl.value;

    var valueEl = card.querySelector('[data-field="value"]');
    if (valueEl) step.value = valueEl.value;

    var enabledEl = card.querySelector('[data-field="is_enabled"]');
    if (enabledEl) step.is_enabled = enabledEl.checked;

    var cofEl = card.querySelector('[data-field="continue_on_failure"]');
    if (cofEl) step.continue_on_failure = cofEl.checked;

    var rcEl = card.querySelector('[data-field="retry_count"]');
    if (rcEl) step.retry_count = parseInt(rcEl.value) || 0;

    var riEl = card.querySelector('[data-field="retry_interval"]');
    if (riEl) step.retry_interval = parseInt(riEl.value) || 1000;

    var roEl = card.querySelector('[data-field="random_options"]');
    if (roEl) {
        step.config.random_options = roEl.value.split('\n').map(function(l) { return l.trim(); }).filter(function(l) { return l.length > 0; });
    }

    var rmnEl = card.querySelector('[data-field="random_min"]');
    if (rmnEl) step.config.random_min = parseInt(rmnEl.value) || 0;

    var rmxEl = card.querySelector('[data-field="random_max"]');
    if (rmxEl) step.config.random_max = parseInt(rmxEl.value) || 100;

    var asrEl = card.querySelector('[data-field="action_set_ref"]');
    if (asrEl) step.action_set_ref = asrEl.value ? parseInt(asrEl.value) : null;

    var bpStartEl = card.querySelector('[data-field="breakpoint_start"]');
    if (bpStartEl) {
        if (!step.config) step.config = {};
        step.config.breakpoint_start = bpStartEl.checked;
    }

    var bpEndEl = card.querySelector('[data-field="breakpoint_end"]');
    if (bpEndEl) {
        if (!step.config) step.config = {};
        step.config.breakpoint_end = bpEndEl.checked;
    }

    updateStepSummary(index);
}

function updateStepSummary(index) {
    var card = document.querySelector('.step-card[data-index="' + index + '"]');
    if (!card) return;
    var step = steps[index];
    var summaryEl = card.querySelector('.step-summary');
    if (!summaryEl) return;

    var summary = getActionLabel(step.action_type);
    if (step.action_type === 'action_set' && step.action_set_ref) {
        var as = actionSets.find(function(a) { return a.id === step.action_set_ref; });
        if (as) summary += ' - ' + as.name;
    } else {
        var locCount = (step.config && step.config.locators) ? step.config.locators.length : 0;
        var locInfo = locCount > 0 ? locCount + '个定位器' : '无定位器';
        summary += ' - ' + locInfo;
    }

    summaryEl.innerHTML = '<i class="bi ' + getActionIcon(step.action_type) + '"></i> ' + escapeHtml(summary);

    var bpTags = '';
    if (step.config && step.config.breakpoint_start) {
        bpTags += ' <span class="badge bg-warning text-dark" style="font-size:0.7rem">断点开始</span>';
    }
    if (step.config && step.config.breakpoint_end) {
        bpTags += ' <span class="badge bg-danger" style="font-size:0.7rem">断点结束</span>';
    }
    summaryEl.innerHTML = '<i class="bi ' + getActionIcon(step.action_type) + '"></i> ' + escapeHtml(summary) + bpTags;

    var nameEl = card.querySelector('.fw-bold');
    if (nameEl) nameEl.textContent = step.name;
}

function toggleStep(index) {
    if (expandedStepIndex === index) {
        expandedStepIndex = -1;
    } else {
        expandedStepIndex = index;
    }
    renderSteps();

    if (expandedStepIndex >= 0 && steps[expandedStepIndex].action_type === 'action_set' && steps[expandedStepIndex].action_set_ref) {
        loadActionSetDetail(expandedStepIndex);
    }
}

function setStepActionType(index, actionType) {
    steps[index].action_type = actionType;
    if (!steps[index].config) steps[index].config = {};
    if (needsElement(actionType) && (!steps[index].config.locators || steps[index].config.locators.length === 0)) {
        steps[index].config.locators = [{ locator_type: 'css', locator_value: '', locator_description: '' }];
    }
    renderSteps();
}

function setStepSelectMode(index, mode) {
    if (!steps[index].config) steps[index].config = {};
    steps[index].config.select_mode = mode;
    renderSteps();
}

window.updateLocator = function(stepIdx, locIdx, field, value) {
    if (!steps[stepIdx].config.locators) steps[stepIdx].config.locators = [];
    if (!steps[stepIdx].config.locators[locIdx]) return;
    steps[stepIdx].config.locators[locIdx][field] = value;
};

window.addLocator = function(stepIdx) {
    if (!steps[stepIdx].config.locators) steps[stepIdx].config.locators = [];
    steps[stepIdx].config.locators.push({ locator_type: 'css', locator_value: '', locator_description: '' });
    renderSteps();
};

window.removeLocator = function(stepIdx, locIdx) {
    if (!steps[stepIdx].config.locators || steps[stepIdx].config.locators.length <= 1) return;
    steps[stepIdx].config.locators.splice(locIdx, 1);
    renderSteps();
};

function onActionSetChange(index) {
    var card = document.querySelector('.step-card[data-index="' + index + '"]');
    if (!card) return;
    var sel = card.querySelector('[data-field="action_set_ref"]');
    if (!sel) return;
    var val = sel.value;
    steps[index].action_set_ref = val ? parseInt(val) : null;
    if (val) {
        var as = actionSets.find(function(a) { return a.id == val; });
        if (as) steps[index].name = as.name;
    }
    renderSteps();
    if (val) {
        loadActionSetDetail(index);
    }
}

async function loadActionSetDetail(index) {
    var step = steps[index];
    if (!step || !step.action_set_ref) return;

    try {
        var response = await axios.get(API_BASE + '/scripts/action-sets/' + step.action_set_ref + '/');
        var detail = response.data;

        var paramsContainer = document.getElementById('action-set-params-' + index);
        var previewContainer = document.getElementById('action-set-preview-' + index);
        if (!paramsContainer || !previewContainer) return;

        var paramsHtml = '';
        if (detail.parameters && detail.parameters.length > 0) {
            paramsHtml = '<div class="config-field"><label>参数设置</label>';
            detail.parameters.forEach(function(param) {
                var currentValue = step.action_set_params ? (step.action_set_params[param.code] || param.default_value) : param.default_value;
                paramsHtml += '<div class="mb-2">' +
                    '<label class="small">' + param.name + (param.is_required ? ' *' : '') + '</label>' +
                    '<input type="text" class="form-control form-control-sm" data-param-code="' + param.code + '" value="' + escapeAttr(currentValue) + '" placeholder="' + escapeAttr(param.description || '') + '">' +
                '</div>';
            });
            paramsHtml += '</div>';
        }
        paramsContainer.innerHTML = paramsHtml;

        if (detail.steps && detail.steps.length > 0) {
            var previewHtml = '<div class="config-field"><label>包含步骤预览</label><div class="border rounded p-2 bg-light"><small class="text-muted">包含 ' + detail.steps.length + ' 个步骤:</small><ol class="mb-0 mt-1 ps-3">';
            detail.steps.forEach(function(s) {
                previewHtml += '<li><small>' + s.name + ' (' + getActionLabel(s.action_type) + ')</small></li>';
            });
            previewHtml += '</ol></div></div>';
            previewContainer.innerHTML = previewHtml;
        } else {
            previewContainer.innerHTML = '';
        }

        paramsContainer.querySelectorAll('[data-param-code]').forEach(function(el) {
            el.addEventListener('input', function() {
                if (!steps[index].action_set_params) steps[index].action_set_params = {};
                steps[index].action_set_params[el.dataset.paramCode] = el.value;
            });
        });
    } catch (error) {
        console.error('Failed to load action set detail:', error);
    }
}

function toggleStepSelect(index, checked) {
    if (checked) {
        selectedStepIds.add(index);
    } else {
        selectedStepIds.delete(index);
    }
    updateBatchDeleteBtn();
}

function updateBatchDeleteBtn() {
    var btn = document.getElementById('batch-delete-btn');
    var countEl = document.getElementById('selected-count');
    if (selectedStepIds.size > 0) {
        btn.style.display = 'inline-block';
        countEl.textContent = selectedStepIds.size;
    } else {
        btn.style.display = 'none';
    }
}

function batchDeleteSteps() {
    if (selectedStepIds.size === 0) return;
    if (!confirm('确定删除选中的 ' + selectedStepIds.size + ' 个步骤？')) return;

    var indices = Array.from(selectedStepIds).sort(function(a, b) { return b - a; });
    for (var i = 0; i < indices.length; i++) {
        steps.splice(indices[i], 1);
    }

    if (expandedStepIndex !== -1) {
        if (selectedStepIds.has(expandedStepIndex)) {
            expandedStepIndex = -1;
        } else {
            var offset = 0;
            for (var j = 0; j < indices.length; j++) {
                if (indices[j] < expandedStepIndex) offset++;
            }
            expandedStepIndex -= offset;
        }
    }

    selectedStepIds.clear();
    updateBatchDeleteBtn();
    renderSteps();
}

function deleteStep(index) {
    if (confirm('确定删除此步骤？')) {
        steps.splice(index, 1);
        if (expandedStepIndex === index) {
            expandedStepIndex = -1;
        } else if (expandedStepIndex > index) {
            expandedStepIndex--;
        }
        var newSelected = new Set();
        selectedStepIds.forEach(function(idx) {
            if (idx < index) newSelected.add(idx);
            else if (idx > index) newSelected.add(idx - 1);
        });
        selectedStepIds = newSelected;
        updateBatchDeleteBtn();
        renderSteps();
    }
}

function moveStep(index, direction) {
    var newIndex = index + direction;
    if (newIndex < 0 || newIndex >= steps.length) return;

    var temp = steps[index];
    steps[index] = steps[newIndex];
    steps[newIndex] = temp;

    if (expandedStepIndex === index) expandedStepIndex = newIndex;
    else if (expandedStepIndex === newIndex) expandedStepIndex = index;

    renderSteps();
}

function dragStart(e, index) {
    e.dataTransfer.setData('text/plain', index);
}

function dragOver(e) {
    e.preventDefault();
}

function drop(e, targetIndex) {
    e.preventDefault();
    var sourceIndex = parseInt(e.dataTransfer.getData('text/plain'));
    if (sourceIndex === targetIndex) return;

    var step = steps.splice(sourceIndex, 1)[0];
    steps.splice(targetIndex, 0, step);

    if (expandedStepIndex === sourceIndex) expandedStepIndex = targetIndex;
    else if (expandedStepIndex > sourceIndex && expandedStepIndex <= targetIndex) expandedStepIndex--;
    else if (expandedStepIndex < sourceIndex && expandedStepIndex >= targetIndex) expandedStepIndex++;

    renderSteps();
}

async function saveScript() {
    var name = document.getElementById('script-name').value;
    var code = document.getElementById('script-code').value;
    var targetUrl = document.getElementById('target-url').value;

    if (!name || !code || !targetUrl) {
        showToast('请填写脚本名称、代码和目标URL', 'error');
        return;
    }

    if (steps.length === 0) {
        showToast('请至少添加一个测试步骤', 'error');
        return;
    }

    new bootstrap.Modal(document.getElementById('saveModal')).show();
}

async function confirmSave() {
    var scriptId = document.getElementById('script-id').value;
    var groupValue = document.getElementById('script-group').value;
    var data = {
        name: document.getElementById('script-name').value,
        code: document.getElementById('script-code').value,
        description: document.getElementById('script-description').value,
        target_url: document.getElementById('target-url').value,
        status: document.getElementById('script-status').value,
        group: groupValue ? parseInt(groupValue) : null,
        steps: steps.map(function(s, i) {
            return {
                name: s.name,
                order: i,
                action_type: s.action_type,
                element: null,
                action_value: s.value || '',
                action_config: s.config || {},
                description: s.description || '',
                is_enabled: s.is_enabled !== undefined ? s.is_enabled : true,
                continue_on_failure: s.continue_on_failure || false,
                retry_count: s.retry_count || 0,
                retry_interval: s.retry_interval || 1000,
                action_set_ref: s.action_set_ref ? parseInt(s.action_set_ref) : null,
                action_set_params: s.action_set_params || {}
            };
        })
    };

    try {
        if (scriptId) {
            await axios.put(API_BASE + '/scripts/' + scriptId + '/', data);
        } else {
            var response = await axios.post(API_BASE + '/scripts/', data);
            document.getElementById('script-id').value = response.data.id;
            currentScriptId = response.data.id;
        }
        bootstrap.Modal.getInstance(document.getElementById('saveModal')).hide();
        showToast('脚本保存成功');
    } catch (error) {
        console.error('Failed to save script:', error);
        showToast('保存失败: ' + (error.response?.data?.detail || error.message), 'error');
    }
}

function escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function escapeAttr(str) {
    if (!str) return '';
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

document.getElementById('script-search').addEventListener('input', function(e) {
    var search = e.target.value.toLowerCase();
    document.querySelectorAll('.script-list-item').forEach(function(item) {
        var text = item.textContent.toLowerCase();
        item.style.display = text.includes(search) ? 'block' : 'none';
    });
});

document.getElementById('openScriptModal').addEventListener('show.bs.modal', loadScriptList);

initEditor();

window.openEditorRecording = function() {
    var targetUrl = document.getElementById('target-url').value || '';
    document.getElementById('editorRecordingModal-url').value = targetUrl;
    recRestart('editorRecordingModal');
    new bootstrap.Modal(document.getElementById('editorRecordingModal')).show();
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
        var stepConfig = {};
        if (action.locators && action.locators.length > 0) {
            stepConfig.locators = action.locators.map(function(loc) {
                return {
                    locator_type: loc.locator_type,
                    locator_value: loc.locator_value,
                    locator_description: loc.locator_description || ''
                };
            });
        } else if (action.locator && action.action_type !== 'navigate' && action.action_type !== 'scroll') {
            stepConfig.locators = [{
                locator_type: action.locator.locator_type,
                locator_value: action.locator.locator_value,
                locator_description: action.locator.locator_description || action.description || ''
            }];
        }
        if (action.random_options) {
            stepConfig.random_options = action.random_options;
            stepConfig.select_mode = action.select_mode || 'dropdown';
        }
        if (action.random_min !== undefined) {
            stepConfig.random_min = action.random_min;
            stepConfig.random_max = action.random_max;
        }

        var step = {
            name: action.description || action.action_type,
            action_type: typeMap[action.action_type] || 'click',
            value: action.value || '',
            config: stepConfig,
            is_enabled: true,
            continue_on_failure: false,
            retry_count: 0,
            retry_interval: 1000
        };
        steps.push(step);
    });

    renderSteps();
    data.confirmed = true;
    bootstrap.Modal.getInstance(document.getElementById(modalId)).hide();
    showToast('已导入 ' + data.actions.length + ' 个录制步骤');
};