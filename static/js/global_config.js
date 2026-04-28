async function loadConfig() {
    try {
        const response = await axios.get(`${API_BASE}/scripts/global-config/`);
        const config = response.data;
        
        if (config.headless_mode) {
            document.getElementById('headless-true').checked = true;
        } else {
            document.getElementById('headless-false').checked = true;
        }
        
        document.getElementById('default-timeout').value = config.default_timeout || 30000;
        document.getElementById('step-screenshot').checked = config.step_screenshot || false;
        document.getElementById('slow-mo').value = config.slow_mo || 0;
        document.getElementById('viewport-width').value = config.viewport_width || 1920;
        document.getElementById('viewport-height').value = config.viewport_height || 1080;
        document.getElementById('scroll-distance').value = config.scroll_distance || 500;
        document.getElementById('scroll-direction').value = config.scroll_direction || 'down';
        
        updateScreenshotInfo();
        
        if (config.updated_at) {
            const updateDate = new Date(config.updated_at);
            document.getElementById('update-info').innerHTML = `
                <p class="mb-1"><strong>最后更新：</strong></p>
                <p class="text-muted small mb-1">${updateDate.toLocaleString('zh-CN')}</p>
                <p class="text-muted small mb-0">更新人：${config.updated_by_name || '系统'}</p>
            `;
        } else {
            document.getElementById('update-info').innerHTML = '<p class="text-muted">暂无更新记录</p>';
        }
    } catch (error) {
        console.error('Failed to load config:', error);
        showToast('加载配置失败', 'error');
    }
}

function updateScreenshotInfo() {
    const checked = document.getElementById('step-screenshot').checked;
    document.getElementById('screenshot-info').style.display = checked ? 'block' : 'none';
}

document.getElementById('step-screenshot').addEventListener('change', updateScreenshotInfo);

async function saveConfig() {
    const headlessMode = document.getElementById('headless-true').checked;
    const defaultTimeout = parseInt(document.getElementById('default-timeout').value) || 30000;
    const stepScreenshot = document.getElementById('step-screenshot').checked;
    const slowMo = parseInt(document.getElementById('slow-mo').value) || 0;
    const viewportWidth = parseInt(document.getElementById('viewport-width').value) || 1920;
    const viewportHeight = parseInt(document.getElementById('viewport-height').value) || 1080;
    const scrollDistance = parseInt(document.getElementById('scroll-distance').value) || 500;
    const scrollDirection = document.getElementById('scroll-direction').value || 'down';
    
    const data = {
        headless_mode: headlessMode,
        default_timeout: defaultTimeout,
        step_screenshot: stepScreenshot,
        slow_mo: slowMo,
        viewport_width: viewportWidth,
        viewport_height: viewportHeight,
        scroll_distance: scrollDistance,
        scroll_direction: scrollDirection
    };
    
    try {
        await axios.put(`${API_BASE}/scripts/global-config/`, data);
        showToast('配置保存成功');
        loadConfig();
    } catch (error) {
        console.error('Failed to save config:', error);
        showToast('保存失败: ' + (error.response?.data?.detail || error.message), 'error');
    }
}

async function clearScreenshots() {
    if (!confirm('确定要删除所有保存的截图吗？此操作不可撤销。')) return;
    try {
        const response = await axios.delete(`${API_BASE}/core/scripts/clear-screenshots/`);
        showToast(response.data.message || '截图清理成功');
    } catch (error) {
        console.error('Failed to clear screenshots:', error);
        showToast('清理截图失败', 'error');
    }
}

async function clearTaskResults() {
    if (!confirm('确定要删除所有任务执行结果吗？此操作不可撤销。')) return;
    try {
        const response = await axios.delete(`${API_BASE}/core/scripts/clear-task-results/`);
        showToast(response.data.message || '任务结果清理成功');
    } catch (error) {
        console.error('Failed to clear task results:', error);
        showToast('清理任务结果失败', 'error');
    }
}

loadConfig();