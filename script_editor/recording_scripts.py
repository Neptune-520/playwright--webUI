import logging

logger = logging.getLogger(__name__)

RECORDING_JS = """
(function() {
    if (window.__rec_active) return;
    window.__rec_active = true;

    function getElementInfo(el) {
        if (!el || !el.tagName) return null;
        var info = {
            tag: el.tagName.toLowerCase(),
            id: el.id || '',
            name: el.getAttribute('name') || '',
            className: el.className || '',
            type: el.getAttribute('type') || '',
            placeholder: el.getAttribute('placeholder') || '',
            href: el.getAttribute('href') || '',
            value: el.value || '',
            dataTestId: el.getAttribute('data-testid') || '',
            dataFixid: el.getAttribute('data-fixid') || '',
            text: ''
        };
        var directText = '';
        for (var i = 0; i < el.childNodes.length; i++) {
            if (el.childNodes[i].nodeType === 3) {
                directText += el.childNodes[i].textContent;
            }
        }
        info.text = directText.trim().substring(0, 100);
        if (!info.text && el.textContent) {
            info.text = el.textContent.trim().substring(0, 100);
        }
        info.ancestorId = '';
        info.ancestorIdSelector = '';
        var ancestor = el.parentElement;
        while (ancestor && ancestor !== document.documentElement) {
            var fixid = ancestor.getAttribute('data-fixid');
            if (fixid) {
                info.ancestorId = fixid;
                info.ancestorIdSelector = '[data-fixid="' + fixid + '"]';
                break;
            }
            if (ancestor.id) {
                info.ancestorId = ancestor.id;
                info.ancestorIdSelector = '#' + CSS.escape(ancestor.id);
                break;
            }
            ancestor = ancestor.parentElement;
        }
        return info;
    }

    function generateCssSelector(el) {
        if (!el || el === document.body || el === document.documentElement) return 'body';
        if (el.id) return '#' + CSS.escape(el.id);
        var parts = [];
        while (el && el !== document.body && el !== document.documentElement) {
            var selector = el.tagName.toLowerCase();
            if (el.id) {
                selector = '#' + CSS.escape(el.id);
                parts.unshift(selector);
                break;
            }
            if (el.className && typeof el.className === 'string') {
                var classes = el.className.trim().split(/\\s+/).filter(function(c) {
                    return c && !c.startsWith('__rec_');
                });
                if (classes.length > 0) {
                    selector += '.' + classes.map(function(c) { return CSS.escape(c); }).join('.');
                }
            }
            var parent = el.parentElement;
            if (parent) {
                var siblings = Array.from(parent.children).filter(function(s) {
                    return s.tagName === el.tagName;
                });
                if (siblings.length > 1) {
                    var idx = siblings.indexOf(el) + 1;
                    selector += ':nth-of-type(' + idx + ')';
                }
            }
            parts.unshift(selector);
            el = el.parentElement;
        }
        return parts.join(' > ');
    }

    document.addEventListener('click', function(e) {
        var el = e.target;
        if (el.closest('[class*="__rec_"]')) return;
        var info = getElementInfo(el);
        if (!info) return;
        var action = {
            action_type: 'click',
            element_info: info,
            value: '',
            timestamp: new Date().toISOString()
        };
        try { window.__rec_recordAction(JSON.stringify(action)); } catch(ex) {}
    }, true);

    document.addEventListener('input', function(e) {
        var el = e.target;
        if (!el.tagName) return;
        var tag = el.tagName.toLowerCase();
        var type = (el.getAttribute('type') || '').toLowerCase();
        if (tag === 'input' && (type === 'checkbox' || type === 'radio')) return;
        if (tag !== 'input' && tag !== 'textarea') return;
        var info = getElementInfo(el);
        if (!info) return;
        var action = {
            action_type: 'fill',
            element_info: info,
            value: el.value || '',
            timestamp: new Date().toISOString()
        };
        try { window.__rec_recordAction(JSON.stringify(action)); } catch(ex) {}
    }, true);

    document.addEventListener('change', function(e) {
        var el = e.target;
        if (!el.tagName) return;
        var tag = el.tagName.toLowerCase();
        var type = (el.getAttribute('type') || '').toLowerCase();

        if (tag === 'select') {
            var info = getElementInfo(el);
            if (!info) return;
            var selected = el.options[el.selectedIndex];
            var action = {
                action_type: 'select',
                element_info: info,
                value: selected ? selected.value : '',
                display_value: selected ? selected.text : '',
                timestamp: new Date().toISOString()
            };
            try { window.__rec_recordAction(JSON.stringify(action)); } catch(ex) {}
        } else if (type === 'checkbox') {
            var info = getElementInfo(el);
            if (!info) return;
            var action = {
                action_type: el.checked ? 'check' : 'uncheck',
                element_info: info,
                value: '',
                timestamp: new Date().toISOString()
            };
            try { window.__rec_recordAction(JSON.stringify(action)); } catch(ex) {}
        }
    }, true);

    document.addEventListener('keydown', function(e) {
        var specialKeys = ['Enter', 'Tab', 'Escape', 'Backspace', 'Delete', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'];
        if (specialKeys.indexOf(e.key) === -1) return;
        var el = e.target;
        var info = getElementInfo(el);
        if (!info) return;
        var action = {
            action_type: 'press',
            element_info: info,
            value: e.key,
            timestamp: new Date().toISOString()
        };
        try { window.__rec_recordAction(JSON.stringify(action)); } catch(ex) {}
    }, true);

    console.log('[Recorder] Recording script injected');
})();
"""

MAX_RECORDING_DURATION = 600
