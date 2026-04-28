var rec = { recording: false, actions: [], startTs: 0 };
var _recModalId = null;

function recStart(id) {
    _recModalId = id;
    rec = { recording: true, actions: [], startTs: Date.now() };
    document.getElementById(id + '-record').disabled = true;
    document.getElementById(id + '-stop').disabled = false;
    document.getElementById(id + '-log').innerHTML = '<div class="text-info"><i class="bi bi-circle"></i> 正在录制...</div>';
}

function recStop(id) {
    rec.recording = false;
    document.getElementById(id + '-record').disabled = false;
    document.getElementById(id + '-stop').disabled = true;
    var logEl = document.getElementById(id + '-log');
    if (rec.actions.length === 0) {
        logEl.innerHTML = '<div class="text-muted"><i class="bi bi-info-circle"></i> 暂无录制操作</div>';
    } else {
        logEl.innerHTML = rec.actions.map(function(a, i) {
            return '<div>' + (i + 1) + '. ' + a.action_type + (a.locator ? ' [' + a.locator.locator_value + ']' : '') + (a.value ? ' = ' + a.value : '') + (a.description ? ' - ' + a.description : '') + '</div>';
        }).join('');
    }
}

function recRestart(id) {
    _recModalId = id;
    rec = { recording: true, actions: [], startTs: Date.now() };
    document.getElementById(id + '-record').disabled = true;
    document.getElementById(id + '-stop').disabled = false;
    document.getElementById(id + '-log').innerHTML = '<div class="text-info"><i class="bi bi-circle"></i> 正在录制...</div>';
}

function recImport(id) {
    var modal = bootstrap.Modal.getInstance(document.getElementById(id));
    modal.hide();
    if (window.recImportCallback) {
        window.recImportCallback(rec.actions);
        rec = { recording: false, actions: [], startTs: 0 };
    }
}

function recConfirm(id) {
    if (window.recConfirm) {
        window.recConfirm(id);
        rec = { recording: false, actions: [], startTs: 0 };
    }
}

function getRecData(id) {
    return rec;
}

window.recStart = recStart;
window.recStop = recStop;
window.recRestart = recRestart;
window.recImport = recImport;
window.recConfirm = recConfirm;
window.getRecData = getRecData;