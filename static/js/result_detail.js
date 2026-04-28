const taskId = {{ task_id }};
let globalConfig = null;

async function loadGlobalConfig() {
    try {
        const response = await axios.get(`${API_BASE}/scripts/global-config/`);
        globalConfig = response.data;
    } catch (error) {
        console.error('Failed to load global config:', error);
    }
}

async function loadResultDetail() {
    try {
        await loadGlobalConfig();
        
        const response = await axios.get(`${API_BASE}/tests/tasks/${taskId}/`);
        const data = response.data;
        
        renderTaskInfo(data);
        
        if (data.report) {
            document.getElementById('total-steps').textContent = data.report.total_steps;
            document.getElementById('passed-steps').textContent = data.report.passed_steps;
            document.getElementById('failed-steps').textContent = data.report.failed_steps;
            document.getElementById('skipped-steps').textContent = data.report.skipped_steps || 0;
            document.getElementById('pass-rate').textContent = data.report.pass_rate.toFixed(1) + '%';
            document.getElementById('duration').textContent = formatDuration(data.report.total_duration);
        }
        
        renderTimeInfo(data);
        renderParameters(data);
        
        const scriptCount = data.script_count || 1;
        if (scriptCount > 1 && data.task_scripts) {
            renderMultiScriptInfo(data);
            renderMultiScriptResults(data.results, data.task_scripts);
        } else {
            renderSteps(data.results);
        }
    } catch (error) {
        console.error('Failed to load result detail:', error);
        showToast('加载失败', 'error');
    }
}

function renderTaskInfo(data) {
    const container = document.getElementById('task-info-container');
    const statusClass = {
        'pending': 'secondary',
        'running': 'primary',
        'completed': 'success',
        'failed': 'danger',
        'cancelled': 'warning'
    }[data.status] || 'secondary';
    
    const statusText = {
        'pending': '待执行',
        'running': '执行中',
        'completed': '已完成',
        'failed': '失败',
        'cancelled': '已取消'
    }[data.status] || data.status;
    
    container.innerHTML = `
        <div class="card mb-4">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h4 class="mb-2">${data.name}</h4>
                        <div>
                            <span class="badge bg-${statusClass} me-2">${statusText}</span>
                            <span class="text-muted"><i class="bi bi-person me-1"></i>${data.created_by_name || '未知'}</span>
                        </div>
                    </div>
                    <div>
                        <span class="badge bg-info me-2">脚本: ${data.script_name}</span>
                        ${data.script_count > 1 ? `<span class="badge bg-primary">多脚本任务 (${data.script_count}个)</span>` : ''}
                    </div>
                </div>
            </div>
        </div>
    `;
}

function renderTimeInfo(data) {
    document.getElementById('created-at').textContent = formatDate(data.created_at);
    document.getElementById('started-at').textContent = data.started_at ? formatDate(data.started_at) : '-';
    document.getElementById('finished-at').textContent = data.finished_at ? formatDate(data.finished_at) : '-';
}

function renderParameters(data) {
    const container = document.getElementById('parameters-display');
    
    if (!data.parameters || Object.keys(data.parameters).length === 0) {
        container.innerHTML = '<div class="text-muted">暂无参数</div>';
        return;
    }
    
    let html = '<div class="parameters-section">';
    Object.entries(data.parameters).forEach(([key, value]) => {
        let displayValue = value;
        if (typeof value === 'object') {
            displayValue = JSON.stringify(value, null, 2);
        }
        html += `
            <div class="param-row">
                <span class="param-label">${key}:</span>
                <span class="param-value">${displayValue}</span>
            </div>
        `;
    });
    html += '</div>';
    container.innerHTML = html;
}

function formatDuration(seconds) {
    if (seconds < 60) {
        return seconds.toFixed(2) + 's';
    }
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds.toFixed(2)}s`;
}

function formatDate(dateStr) {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleString('zh-CN', { 
        year: 'numeric', 
        month: '2-digit', 
        day: '2-digit',
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit' 
    });
}

function renderMultiScriptInfo(data) {
    const container = document.getElementById('multi-script-info-container');
    const scriptNames = data.task_scripts.map(ts => ts.script_name).join('、');
    
    container.innerHTML = `
        <div class="multi-script-header">
            <h5><i class="bi bi-layers me-2"></i>多脚本任务</h5>
            <div class="mt-2">
                <span class="badge bg-light text-dark me-2">共 ${data.task_scripts.length} 个脚本</span>
                <span class="badge bg-light text-dark">${scriptNames}</span>
            </div>
        </div>
    `;
}

function renderMultiScriptResults(results, taskScripts) {
    const container = document.getElementById('steps-detail');
    
    if (!results || results.length === 0) {
        container.innerHTML = '<div class="text-center text-muted py-4">暂无执行结果</div>';
        return;
    }
    
    const scriptResults = {};
    taskScripts.forEach(ts => {
        scriptResults[ts.script_name] = {
            script: ts,
            results: []
        };
    });
    
    results.forEach(r => {
        let matched = false;
        for (const scriptName in scriptResults) {
            if (r.step_name && r.step_name.includes(`[${scriptName}]`)) {
                scriptResults[scriptName].results.push(r);
                matched = true;
                break;
            }
        }
        if (!matched) {
            const firstKey = Object.keys(scriptResults)[0];
            if (firstKey) scriptResults[firstKey].results.push(r);
        }
    });
    
    const scriptEntries = Object.entries(scriptResults);
    if (scriptEntries.length <= 1) {
        renderSteps(results);
        return;
    }
    
    let accordionHtml = '<div class="accordion script-accordion" id="scriptAccordion">';
    
    scriptEntries.forEach(([scriptName, scriptData], idx) => {
        const collapseId = `script-collapse-${idx}`;
        const headerId = `script-heading-${idx}`;
        
        const scriptResults = scriptData.results;
        const passedCount = scriptResults.filter(r => r.status === 'passed').length;
        const failedCount = scriptResults.filter(r => r.status === 'failed').length;
        const totalCount = scriptResults.length;
        
        const isExpanded = idx === 0 ? 'show' : '';
        const buttonClass = idx === 0 ? '' : 'collapsed';
        
        accordionHtml += `
            <div class="accordion-item">
                <h2 class="accordion-header" id="${headerId}">
                    <button class="accordion-button ${buttonClass}" type="button" data-bs-toggle="collapse" data-bs-target="#${collapseId}" aria-expanded="${idx === 0}" aria-controls="${collapseId}">
                        <div class="w-100 d-flex justify-content-between align-items-center">
                            <div>
                                <i class="bi bi-code-slash me-2"></i>
                                ${scriptName}
                            </div>
                            <div class="text-muted small">
                                <span class="me-3">步骤: ${totalCount}</span>
                                <span class="me-3 text-success">通过: ${passedCount}</span>
                                <span class="text-danger">失败: ${failedCount}</span>
                            </div>
                        </div>
                    </button>
                </h2>
                <div id="${collapseId}" class="accordion-collapse collapse ${isExpanded}" aria-labelledby="${headerId}" data-bs-parent="#scriptAccordion">
                    <div class="accordion-body">
                        ${renderResults(scriptResults, idx)}
                    </div>
                </div>
            </div>
        `;
    });
    
    accordionHtml += '</div>';
    container.innerHTML = accordionHtml;
}

function renderResults(results, groupIndex) {
    if (!results || results.length === 0) {
        return '<div class="text-center text-muted py-3">暂无步骤结果</div>';
    }
    
    return results.map((result, index) => {
        const globalIndex = groupIndex * 1000 + index;
        const statusClass = {
            'passed': 'success',
            'failed': 'danger',
            'skipped': 'warning',
            'error': 'danger'
        }[result.status] || 'secondary';
        
        const statusText = {
            'passed': '通过',
            'failed': '失败',
            'skipped': '跳过',
            'error': '错误'
        }[result.status] || result.status;
        
        let stepNameDisplay = result.step_name;
        const match = result.step_name.match(/^\[([^\]]+)\]\s*(.*)/);
        if (match) {
            stepNameDisplay = match[2];
        }
        
        const actionValuesHtml = renderActionValues(result.action_values, globalIndex);
        
        let screenshotHtml = '';
        if (result.status === 'failed' && result.screenshot) {
            screenshotHtml = `
                <div class="mt-2">
                    <a href="${result.screenshot}" target="_blank" class="btn btn-sm btn-outline-danger">
                        <i class="bi bi-image"></i> 查看错误截图
                    </a>
                </div>
            `;
        } else if (globalConfig && globalConfig.step_screenshot && result.element_screenshot) {
            screenshotHtml = `
                <div class="mt-2">
                    <a href="${result.element_screenshot}" target="_blank" class="btn btn-sm btn-outline-secondary">
                        <i class="bi bi-image"></i> 查看截图
                    </a>
                </div>
            `;
        }
        
        return `
            <div class="step-item border-${statusClass}">
                ${match ? `<div class="script-label-badge">${match[1]}</div>` : ''}
                <div class="d-flex justify-content-between align-items-start">
                    <div class="d-flex align-items-center">
                        <span class="step-number bg-${statusClass}">${index + 1}</span>
                        <div>
                            <div class="fw-bold">${stepNameDisplay}</div>
                            <small class="text-muted">耗时: ${result.duration.toFixed(2)}s</small>
                        </div>
                    </div>
                    <span class="badge bg-${statusClass}">${statusText}</span>
                </div>
                ${result.error_message ? `
                <div class="error-display-container mt-2" data-step-index="${globalIndex}">
                    <div class="alert alert-danger mb-0">
                        <strong>错误信息:</strong><br>
                        <div class="formatted-error-msg">${result.error_message}</div>
                        ${result.error_stack && result.error_stack !== result.error_message ? `
                            <button class="btn btn-sm btn-outline-secondary mt-2 toggle-console-error-btn" onclick="toggleConsoleError(${globalIndex})">
                                <i class="bi bi-terminal"></i> 控制台报错
                            </button>
                            <div class="console-error-content mt-2" id="console-error-${globalIndex}" style="display: none;">
                                <hr>
                                <strong>控制台原始报错:</strong><br>
                                <pre class="mb-0">${result.error_stack}</pre>
                            </div>
                        ` : ''}
                    </div>
                </div>
            ` : ''}
                ${result.error_stack ? `
                    <div class="mt-2">
                        <div class="accordion" id="error-stack-${globalIndex}">
                            <div class="accordion-item">
                                <h2 class="accordion-header">
                                    <button class="accordion-button collapsed py-2 bg-danger text-white" type="button" data-bs-toggle="collapse" data-bs-target="#error-stack-collapse-${globalIndex}">
                                        <i class="bi bi-file-earmark-code me-2"></i>查看错误堆栈
                                    </button>
                                </h2>
                                <div id="error-stack-collapse-${globalIndex}" class="accordion-collapse collapse" data-bs-parent="#error-stack-${globalIndex}">
                                    <div class="accordion-body py-2">
                                        <pre class="error-stack-content">${result.error_stack}</pre>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                ` : ''}
                ${renderLogs(result.logs, globalIndex)}
                ${actionValuesHtml}
                ${screenshotHtml}
            </div>
        `;
    }).join('');
}

function renderActionValues(actionValues, stepIndex) {
    if (!actionValues || Object.keys(actionValues).length === 0) {
        return '';
    }
    
    if (actionValues.sub_steps) {
        let subStepsHtml = actionValues.sub_steps.map((sub, subIdx) => {
            const subErrorKey = `sub-${stepIndex}-${subIdx}`;
            const statusClass = {
                'passed': 'success',
                'failed': 'danger',
                'skipped': 'warning',
                'error': 'danger'
            }[sub.status] || 'secondary';
            const statusText = {
                'passed': '通过',
                'failed': '失败',
                'skipped': '跳过',
                'error': '错误'
            }[sub.status] || sub.status || '';

            let valuesHtml = '';
            if (sub.values && Object.keys(sub.values).length > 0) {
                valuesHtml = Object.entries(sub.values).map(([key, value]) => {
                    let displayValue = value;
                    if (Array.isArray(value)) {
                        displayValue = value.join(', ');
                    }
                    return `
                        <div class="action-value-item">
                            <span class="action-value-label">${key}:</span>
                            <span class="action-value-content">${displayValue}</span>
                        </div>
                    `;
                }).join('');
            }

            let errorHtml = '';
            if (sub.error) {
                const hasStack = sub.error_stack && sub.error_stack !== sub.error;
                errorHtml = `
                    <div class="alert alert-danger py-1 px-2 mt-2 mb-0" style="font-size: 0.875rem;" data-step-index="${subErrorKey}">
                        <div class="formatted-error-msg">${sub.error}</div>
                        ${hasStack ? `
                            <button class="btn btn-sm btn-outline-secondary mt-1 toggle-console-error-btn" onclick="toggleConsoleError('${subErrorKey}')">
                                <i class="bi bi-terminal"></i> 控制台报错
                            </button>
                            <div class="console-error-content mt-1" id="console-error-${subErrorKey}" style="display: none;">
                                <hr>
                                <strong>控制台原始报错:</strong><br>
                                <pre class="mb-0">${sub.error_stack}</pre>
                            </div>
                        ` : ''}
                    </div>
                `;
            }

            return `
                <div class="sub-step-item">
                    <div class="d-flex align-items-center">
                        <span class="fw-bold">${sub.step_name}</span>
                        ${statusText ? `<span class="badge bg-${statusClass} ms-2">${statusText}</span>` : ''}
                    </div>
                    ${valuesHtml ? `<div class="action-values-section mt-2">${valuesHtml}</div>` : ''}
                    ${errorHtml}
                </div>
            `;
        }).join('');
        
        return `
            <div class="sub-steps-section">
                <div class="fw-bold mb-2"><i class="bi bi-list-nested me-1"></i>子步骤执行值</div>
                ${subStepsHtml}
            </div>
        `;
    }
    
    let valuesHtml = Object.entries(actionValues).map(([key, value]) => {
        let displayValue = value;
        if (Array.isArray(value)) {
            displayValue = value.join(', ');
        }
        return `
            <div class="action-value-item">
                <span class="action-value-label">${key}:</span>
                <span class="action-value-content">${displayValue}</span>
            </div>
        `;
    }).join('');
    
    return `
        <div class="accordion mt-2" id="accordion-${stepIndex}">
            <div class="accordion-item">
                <h2 class="accordion-header">
                    <button class="accordion-button collapsed py-2" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-${stepIndex}">
                        <i class="bi bi-list-check me-2"></i>查看执行值
                    </button>
                </h2>
                <div id="collapse-${stepIndex}" class="accordion-collapse collapse" data-bs-parent="#accordion-${stepIndex}">
                    <div class="accordion-body py-2">
                        <div class="action-values-section">
                            ${valuesHtml}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function renderLogs(logs, stepIndex) {
    if (!logs || logs.length === 0) {
        return '';
    }
    
    const logItems = logs.map((log, idx) => {
        const timestamp = log.timestamp || '';
        const level = log.level || 'INFO';
        const message = log.message || log;
        const levelClass = {
            'DEBUG': 'text-muted',
            'INFO': 'text-primary',
            'WARNING': 'text-warning',
            'ERROR': 'text-danger'
        }[level] || 'text-secondary';
        
        return `<div class="log-line"><span class="text-muted">[${timestamp}]</span> <span class="${levelClass}">[${level}]</span> ${message}</div>`;
    }).join('');
    
    return `
        <div class="accordion mt-2" id="logs-accordion-${stepIndex}">
            <div class="accordion-item">
                <h2 class="accordion-header">
                    <button class="accordion-button collapsed py-2" type="button" data-bs-toggle="collapse" data-bs-target="#logs-collapse-${stepIndex}">
                        <i class="bi bi-terminal me-2"></i>执行日志 (${logs.length}条)
                    </button>
                </h2>
                <div id="logs-collapse-${stepIndex}" class="accordion-collapse collapse" data-bs-parent="#logs-accordion-${stepIndex}">
                    <div class="accordion-body py-2">
                        <div class="log-container">
                            ${logItems}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function renderSteps(results) {
    const container = document.getElementById('steps-detail');
    
    if (!results || results.length === 0) {
        container.innerHTML = '<div class="text-center text-muted py-4">暂无执行结果</div>';
        return;
    }
    
    container.innerHTML = results.map((result, index) => {
        const statusClass = {
            'passed': 'success',
            'failed': 'danger',
            'skipped': 'warning'
        }[result.status] || 'secondary';
        
        const statusText = {
            'passed': '通过',
            'failed': '失败',
            'skipped': '跳过'
        }[result.status] || result.status;
        
        let stepNameDisplay = result.step_name;
        const match = result.step_name.match(/^\[([^\]]+)\]\s*(.*)/);
        if (match) {
            stepNameDisplay = match[2];
        }
        
        const actionValuesHtml = renderActionValues(result.action_values, index);
        
        let screenshotHtml = '';
        if (result.status === 'failed' && result.screenshot) {
            screenshotHtml = `
                <div class="mt-2">
                    <a href="${result.screenshot}" target="_blank" class="btn btn-sm btn-outline-danger">
                        <i class="bi bi-image"></i> 查看错误截图
                    </a>
                </div>
            `;
        } else if (globalConfig && globalConfig.step_screenshot && result.element_screenshot) {
            screenshotHtml = `
                <div class="mt-2">
                    <a href="${result.element_screenshot}" target="_blank" class="btn btn-sm btn-outline-secondary">
                        <i class="bi bi-image"></i> 查看截图
                    </a>
                </div>
            `;
        }
        
        return `
            <div class="step-item border-${statusClass}">
                ${match ? `<div class="script-label-badge">${match[1]}</div>` : ''}
                <div class="d-flex justify-content-between align-items-start">
                    <div class="d-flex align-items-center">
                        <span class="step-number bg-${statusClass}">${index + 1}</span>
                        <div>
                            <div class="fw-bold">${stepNameDisplay}</div>
                            <small class="text-muted">耗时: ${result.duration.toFixed(2)}s</small>
                        </div>
                    </div>
                    <span class="badge bg-${statusClass}">${statusText}</span>
                </div>
                ${result.error_message ? `
                    <div class="alert alert-danger mt-2 mb-0">
                        <strong>错误信息:</strong><br>
                        <pre class="mb-0">${result.error_message}</pre>
                    </div>
                ` : ''}
                ${result.error_stack ? `
                    <div class="mt-2">
                        <div class="accordion" id="error-stack-${index}">
                            <div class="accordion-item">
                                <h2 class="accordion-header">
                                    <button class="accordion-button collapsed py-2 bg-danger text-white" type="button" data-bs-toggle="collapse" data-bs-target="#error-stack-collapse-${index}">
                                        <i class="bi bi-file-earmark-code me-2"></i>查看错误堆栈
                                    </button>
                                </h2>
                                <div id="error-stack-collapse-${index}" class="accordion-collapse collapse" data-bs-parent="#error-stack-${index}">
                                    <div class="accordion-body py-2">
                                        <pre class="error-stack-content">${result.error_stack}</pre>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                ` : ''}
                ${renderLogs(result.logs, index)}
                ${actionValuesHtml}
                ${screenshotHtml}
            </div>
        `;
    }).join('');
}

async function exportReport(format) {
    try {
        const response = await axios.get(`${API_BASE}/tests/results/${taskId}/export/?format=${format}`);
        showToast('报告导出成功');
    } catch (error) {
        console.error('Failed to export report:', error);
        showToast('导出失败', 'error');
    }
}

function expandAllSteps() {
    document.querySelectorAll('.accordion-collapse').forEach(el => {
        el.classList.add('show');
    });
    document.querySelectorAll('.accordion-button.collapsed').forEach(el => {
        el.classList.remove('collapsed');
    });
}

function collapseAllSteps() {
    document.querySelectorAll('.accordion-collapse.show').forEach(el => {
        el.classList.remove('show');
    });
    document.querySelectorAll('.accordion-button:not(.collapsed)').forEach(el => {
        el.classList.add('collapsed');
    });
}

function toggleConsoleError(stepIndex) {
    const errorContent = document.getElementById(`console-error-${stepIndex}`);
    const button = document.querySelector(`[data-step-index="${stepIndex}"] .toggle-console-error-btn`);
    if (errorContent.style.display === 'none') {
        errorContent.style.display = 'block';
        button.innerHTML = '<i class="bi bi-terminal"></i> 收起控制台报错';
    } else {
        errorContent.style.display = 'none';
        button.innerHTML = '<i class="bi bi-terminal"></i> 控制台报错';
    }
}

loadResultDetail();
