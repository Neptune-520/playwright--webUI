import asyncio
import json
import logging
from typing import Dict, Any, List, Optional

from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from django.utils import timezone

from script_editor.recording_scripts import RECORDING_JS

logger = logging.getLogger(__name__)


class RecordingEngine:
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.actions: List[Dict[str, Any]] = []
        self.is_recording = False
        self.session_id: Optional[str] = None
        self._action_index = 0

    async def start_recording(self, target_url: str, session_id: str, viewport_width=1920, viewport_height=1080):
        self.session_id = session_id
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=False,
                slow_mo=0,
            )
            context_options = {
                'viewport': {'width': viewport_width, 'height': viewport_height},
                'locale': 'zh-CN',
                'timezone_id': 'Asia/Shanghai',
            }
            self.context = await self.browser.new_context(**context_options)
            self.context.set_default_timeout(30000)

            self.page = await self.context.new_page()

            await self.page.expose_function('__rec_recordAction', self._on_action)

            self.context.on('page', self._on_new_page)

            self.page.on('close', self._on_page_close)

            await self.page.goto(target_url, wait_until='domcontentloaded')

            await self._inject_recording_script()

            self.is_recording = True
            logger.info(f"Recording session {session_id} started for {target_url}")

        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            self.is_recording = False
            await self.close()
            raise

    async def _on_new_page(self, page: Page):
        try:
            await page.expose_function('__rec_recordAction', self._on_action)
            page.on('load', self._on_page_load)
            page.on('close', lambda: None)
            await page.evaluate(RECORDING_JS)
        except Exception as e:
            logger.warning(f"Failed to set up new page recording: {e}")

    async def _on_page_load(self, page: Page):
        try:
            await asyncio.sleep(0.5)
            try:
                await page.expose_function('__rec_recordAction', self._on_action)
            except Exception:
                pass
            await page.evaluate(RECORDING_JS)
        except Exception as e:
            logger.warning(f"Failed to re-inject recording script after navigation: {e}")

    async def _on_page_close(self):
        logger.info(f"Recording page closed for session {self.session_id}")
        self.is_recording = False

    async def _inject_recording_script(self):
        try:
            await self.page.evaluate(RECORDING_JS)
        except Exception as e:
            logger.warning(f"Failed to inject recording script: {e}")

    async def _on_action(self, action_json: str):
        try:
            action_data = json.loads(action_json) if isinstance(action_json, str) else action_json
        except (json.JSONDecodeError, TypeError):
            logger.warning(f"Invalid action data received: {action_json}")
            return

        action_type = action_data.get('action_type', '')
        element_info = action_data.get('element_info')
        value = action_data.get('value', '')

        if action_type == 'fill' and self.actions:
            last = self.actions[-1]
            if (last['action_type'] == 'fill' and
                    last.get('locators', [{}])[0].get('locator_value') == (self._generate_locator(element_info) or [{}])[0].get('locator_value')):
                last['value'] = value
                last['description'] = self._generate_description(
                    'fill', element_info, value, last.get('locators', []))
                return

        locators = []
        if element_info:
            locators = self._generate_locator(element_info)

        description = self._generate_description(action_type, element_info, value, locators)

        action_record = {
            'index': self._action_index,
            'action_type': action_type,
            'element_info': element_info,
            'value': value,
            'display_value': action_data.get('display_value', ''),
            'description': description,
            'timestamp': action_data.get('timestamp', timezone.now().isoformat()),
            'locators': locators,
        }

        self._action_index += 1
        self.actions.append(action_record)
        logger.debug(f"Recorded action: {action_type} - {description}")

    @staticmethod
    def _escape_css_id(id_value: str) -> str:
        import re
        def escape_char(match):
            ch = match.group(0)
            cp = ord(ch)
            if cp == 0:
                return '\ufffd'
            if 0x20 <= cp <= 0x7e and not re.match(r'[0-9-]', ch):
                return '\\' + ch
            return '\\' + format(cp, 'x') + ' '
        escaped = re.sub(r'[^\w-]', escape_char, id_value)
        if id_value and id_value[0].isdigit():
            escaped = '\\' + format(ord(id_value[0]), 'x') + ' ' + escaped[1:]
        return escaped

    def _generate_locator(self, element_info: Dict[str, Any]) -> list:
        tag = element_info.get('tag', '')
        el_id = element_info.get('id', '')
        data_test_id = element_info.get('dataTestId', '')
        data_fixid = element_info.get('dataFixid', '')
        name = element_info.get('name', '')
        placeholder = element_info.get('placeholder', '')
        text = element_info.get('text', '')
        el_type = element_info.get('type', '')
        class_name = element_info.get('className', '')
        ancestor_id = element_info.get('ancestorId', '')
        ancestor_id_selector = element_info.get('ancestorIdSelector', '')

        MEANINGLESS_TAGS = {'div', 'span', 'p', 'section', 'article', 'main', 'header', 'footer', 'nav', 'aside'}

        description = self._generate_element_description(element_info)

        locators = []

        primary = None

        if data_fixid:
            primary = {
                'locator_type': 'css',
                'locator_value': f'[data-fixid="{data_fixid}"]',
                'locator_description': description,
            }

        if el_id and not primary:
            primary = {
                'locator_type': 'css',
                'locator_value': f'#{self._escape_css_id(el_id)}',
                'locator_description': description,
            }

        if data_test_id and not primary:
            primary = {
                'locator_type': 'css',
                'locator_value': f'[data-testid="{data_test_id}"]',
                'locator_description': description,
            }

        if name and not primary:
            primary = {
                'locator_type': 'css',
                'locator_value': f'[name="{name}"]',
                'locator_description': description,
            }

        if placeholder and tag in ('input', 'textarea') and not primary:
            primary = {
                'locator_type': 'css',
                'locator_value': f'{tag}[placeholder="{placeholder}"]',
                'locator_description': description,
            }

        if text and tag in ('button', 'a', 'span', 'label') and not primary:
            clean_text = text.strip()[:50]
            if clean_text:
                primary = {
                    'locator_type': 'text',
                    'locator_value': clean_text,
                    'locator_description': description,
                }

        if class_name and not primary:
            classes = class_name.strip().split()
            meaningful = [c for c in classes if not c.startswith('__rec_')]
            if meaningful:
                selector = f'{tag}.' + '.'.join(meaningful[:3])
                primary = {
                    'locator_type': 'css',
                    'locator_value': selector,
                    'locator_description': description,
                }

        if not primary:
            if tag not in MEANINGLESS_TAGS:
                primary = {
                    'locator_type': 'css',
                    'locator_value': tag,
                    'locator_description': description,
                }
            else:
                primary = {
                    'locator_type': 'css',
                    'locator_value': f'{tag}:first-child',
                    'locator_description': description,
                }

        locators.append(primary)

        if ancestor_id and not data_fixid:
            if ancestor_id_selector:
                ancestor_prefix = ancestor_id_selector
            else:
                ancestor_prefix = f'#{self._escape_css_id(ancestor_id)}'
            if primary['locator_type'] == 'text':
                combined_value = f'{ancestor_prefix} >> text={primary["locator_value"]}'
            else:
                combined_value = f'{ancestor_prefix} >> {primary["locator_value"]}'
            combined_locator = {
                'locator_type': 'css',
                'locator_value': combined_value,
                'locator_description': description,
            }
            locators.insert(0, combined_locator)

        if el_id and name:
            locators.append({
                'locator_type': 'css',
                'locator_value': f'[name="{name}"]',
                'locator_description': description,
            })

        if name and text and tag in ('button', 'a', 'span', 'label'):
            clean_text = text.strip()[:50]
            if clean_text:
                locators.append({
                    'locator_type': 'text',
                    'locator_value': clean_text,
                    'locator_description': description,
                })

        if placeholder and tag in ('input', 'textarea'):
            if primary and (primary['locator_type'] != 'css' or 'placeholder' not in primary['locator_value']):
                locators.append({
                    'locator_type': 'css',
                    'locator_value': f'{tag}[placeholder="{placeholder}"]',
                    'locator_description': description,
                })

        if class_name:
            classes = class_name.strip().split()
            meaningful = [c for c in classes if not c.startswith('__rec_')]
            if meaningful and primary and primary.get('locator_type') != 'css':
                selector = f'{tag}.' + '.'.join(meaningful[:3])
                locators.append({
                    'locator_type': 'css',
                    'locator_value': selector,
                    'locator_description': description,
                })
            elif meaningful and primary and primary.get('locator_type') == 'css' and primary.get('locator_value') == tag:
                selector = f'{tag}.' + '.'.join(meaningful[:3])
                locators.append({
                    'locator_type': 'css',
                    'locator_value': selector,
                    'locator_description': description,
                })

        if text and tag in ('button', 'a', 'span', 'label'):
            clean_text = text.strip()[:50]
            if clean_text:
                text_locator = {
                    'locator_type': 'text',
                    'locator_value': clean_text,
                    'locator_description': description,
                }
                already_has_text = any(loc.get('locator_type') == 'text' for loc in locators)
                if not already_has_text:
                    locators.append(text_locator)

        if name:
            name_locator = {
                'locator_type': 'name',
                'locator_value': name,
                'locator_description': description,
            }
            already_has_name = any(loc.get('locator_type') == 'name' for loc in locators)
            if not already_has_name:
                locators.append(name_locator)

        if placeholder and tag in ('input', 'textarea'):
            placeholder_locator = {
                'locator_type': 'placeholder',
                'locator_value': placeholder,
                'locator_description': description,
            }
            already_has_placeholder = any(loc.get('locator_type') == 'placeholder' for loc in locators)
            if not already_has_placeholder:
                locators.append(placeholder_locator)

        seen = set()
        unique = []
        used_types = set()
        for loc in locators:
            if loc['locator_value'] not in seen and loc['locator_type'] not in used_types:
                seen.add(loc['locator_value'])
                used_types.add(loc['locator_type'])
                unique.append(loc)

        if not unique:
            if tag not in MEANINGLESS_TAGS:
                unique.append({
                    'locator_type': 'css',
                    'locator_value': tag,
                    'locator_description': f'标签名: {tag}',
                })
            else:
                unique.append({
                    'locator_type': 'css',
                    'locator_value': f'{tag}:first-child',
                    'locator_description': f'标签名: {tag}',
                })

        return unique

    def _generate_element_description(self, element_info: Dict[str, Any]) -> str:
        tag = element_info.get('tag', '')
        el_id = element_info.get('id', '')
        name = element_info.get('name', '')
        placeholder = element_info.get('placeholder', '')
        text = element_info.get('text', '')
        el_type = element_info.get('type', '')

        if text:
            clean = text.strip()[:30]
            if clean:
                return clean

        if placeholder:
            return placeholder[:30]

        if name:
            return name

        if el_id:
            return el_id

        type_names = {
            'submit': '提交按钮', 'button': '按钮', 'email': '邮箱输入框',
            'password': '密码输入框', 'text': '文本输入框', 'search': '搜索框',
            'tel': '电话输入框', 'url': 'URL输入框', 'number': '数字输入框',
        }
        if el_type in type_names:
            return type_names[el_type]

        tag_names = {
            'button': '按钮', 'a': '链接', 'input': '输入框', 'select': '下拉框',
            'textarea': '文本域', 'checkbox': '复选框', 'img': '图片',
        }
        if tag in tag_names:
            return tag_names[tag]

        return tag

    def _generate_description(self, action_type, element_info, value, locators) -> str:
        type_labels = {
            'click': '点击', 'fill': '填充', 'select': '选择',
            'check': '勾选', 'uncheck': '取消勾选', 'press': '按键',
            'navigate': '导航', 'hover': '悬停',
        }
        label = type_labels.get(action_type, action_type)

        if action_type == 'navigate':
            return f"导航到 {value}"
        if action_type == 'press':
            key_labels = {
                'Enter': '回车', 'Tab': 'Tab', 'Escape': 'Esc',
                'Backspace': '退格', 'Delete': '删除',
            }
            key_name = key_labels.get(value, value)
            return f"按键 - {key_name}"

        if locators:
            desc = locators[0].get('locator_description', '') if locators else ''
            if desc:
                return f"{label} - {desc}"

        return label

    async def stop_recording(self):
        self.is_recording = False
        await self.close()
        logger.info(f"Recording session {self.session_id} stopped with {len(self.actions)} actions")
        return self.actions

    def get_actions(self) -> List[Dict[str, Any]]:
        return list(self.actions)

    async def close(self):
        try:
            if self.context:
                await self.context.close()
        except Exception as e:
            logger.warning(f"Error closing context: {e}")
        try:
            if self.browser:
                await self.browser.close()
        except Exception as e:
            logger.warning(f"Error closing browser: {e}")
        try:
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            logger.warning(f"Error stopping playwright: {e}")

        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None
