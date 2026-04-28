import asyncio
import time
import json
from typing import Optional, Dict, Any, List
from pathlib import Path
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class ElementLocatorMixin:
    async def _debug_blocking_elements(self, locator) -> None:
        try:
            count = await locator.count()
            if count == 0:
                logger.debug("目标元素不存在 (count=0)")
                return

            box = await locator.bounding_box()
            if not box:
                logger.debug("目标元素没有 bounding box，可能不在视口中")
                return

            cx = box['x'] + box['width'] / 2
            cy = box['y'] + box['height'] / 2

            is_visible = await locator.is_visible()
            logger.debug(f"目标元素可见: {is_visible}, 中心坐标: ({cx}, {cy})")

            elements_at_point = await self.page.evaluate(
                """([x, y]) => {
                    const elements = document.elementsFromPoint(x, y);
                    return elements.slice(0, 10).map(el => ({
                        tag: el.tagName,
                        id: el.id || '',
                        className: el.className || '',
                        style: {
                            position: window.getComputedStyle(el).position,
                            zIndex: window.getComputedStyle(el).zIndex,
                            display: window.getComputedStyle(el).display,
                            visibility: window.getComputedStyle(el).visibility,
                            opacity: window.getComputedStyle(el).opacity,
                            pointerEvents: window.getComputedStyle(el).pointerEvents,
                        },
                        rect: el.getBoundingClientRect().toJSON(),
                        isTarget: el === document.elementFromPoint(x, y),
                    }));
                }""",
                [cx, cy]
            )

            logger.debug(f"坐标 ({cx:.1f}, {cy:.1f}) 处的元素堆栈 (从上到下):")
            for i, el_info in enumerate(elements_at_point):
                tag = el_info['tag']
                el_id = el_info['id']
                cls = el_info['className']
                style = el_info['style']
                rect = el_info['rect']
                marker = " <-- 最顶层元素(接收点击)" if i == 0 else ""
                logger.debug(
                    f"  [{i}] <{tag}>"
                    f" id='{el_id}'"
                    f" class='{cls[:80]}'"
                    f" position={style['position']} z-index={style['zIndex']}"
                    f" display={style['display']} visibility={style['visibility']}"
                    f" opacity={style['opacity']} pointer-events={style['pointerEvents']}"
                    f" rect=({rect['x']:.0f},{rect['y']:.0f},{rect['width']:.0f},{rect['height']:.0f})"
                    f"{marker}"
                )

            top_el = elements_at_point[0] if elements_at_point else None
            if top_el:
                logger.debug(
                    f"阻挡元素: <{top_el['tag']}>"
                    f" id='{top_el['id']}'"
                    f" class='{top_el['className'][:120]}'"
                    f" position={top_el['style']['position']}"
                    f" z-index={top_el['style']['zIndex']}"
                    f" pointer-events={top_el['style']['pointerEvents']}"
                )
        except Exception as debug_err:
            logger.debug(f"调试信息获取失败: {debug_err}")

    async def get_element(self, locator_config: Dict[str, Any]) -> Any:
        if not self.page:
            raise RuntimeError("Page not initialized. Call start() first.")

        locator_type = locator_config.get('type', 'css')
        locator_value = locator_config.get('value', '')
        timeout = locator_config.get('timeout', self.timeout)
        backup_locators = locator_config.get('backup_locators', [])

        primary_locator = self._locate_element(locator_type, locator_value)

        if not backup_locators:
            try:
                await primary_locator.wait_for(timeout=timeout)
            except Exception as wait_error:
                logger.debug(f"get_element wait_for 超时，开始分析...")
                logger.debug(f"定位器类型: {locator_type}, 值: {locator_value}")
                logger.debug(f"wait_for 错误: {wait_error}")
                count = await primary_locator.count()
                logger.debug(f"元素数量: {count}")
                if count > 0:
                    is_visible = await primary_locator.first.is_visible()
                    logger.debug(f"第一个元素是否可见: {is_visible}")
                    if is_visible:
                        await self._debug_blocking_elements(primary_locator.first)
                    else:
                        try:
                            parent_info = await self.page.evaluate(
                                """(selector) => {
                                    const el = document.querySelector(selector);
                                    if (!el) return null;
                                    const rect = el.getBoundingClientRect();
                                    const cs = window.getComputedStyle(el);
                                    const parent = el.parentElement;
                                    return {
                                        el: {
                                            tag: el.tagName, id: el.id, className: el.className,
                                            display: cs.display, visibility: cs.visibility,
                                            opacity: cs.opacity, height: cs.height, width: cs.width,
                                            overflow: cs.overflow, rect: rect.toJSON(),
                                        },
                                        parent: parent ? {
                                            tag: parent.tagName, id: parent.id, className: parent.className,
                                            display: window.getComputedStyle(parent).display,
                                            visibility: window.getComputedStyle(parent).visibility,
                                            opacity: window.getComputedStyle(parent).opacity,
                                            height: window.getComputedStyle(parent).height,
                                            overflow: window.getComputedStyle(parent).overflow,
                                        } : null,
                                    };
                                }""",
                                locator_value if locator_type == 'css' else f'#{locator_value}' if locator_type == 'id' else f'[name="{locator_value}"]'
                            )
                            if parent_info:
                                el_info = parent_info['el']
                                logger.debug(f"元素自身: <{el_info['tag']}> id='{el_info['id']}' class='{el_info['className'][:80]}'")
                                logger.debug(f"  display={el_info['display']} visibility={el_info['visibility']} opacity={el_info['opacity']} height={el_info['height']} width={el_info['width']} overflow={el_info['overflow']}")
                                logger.debug(f"  rect=({el_info['rect']['x']:.0f},{el_info['rect']['y']:.0f},{el_info['rect']['width']:.0f},{el_info['rect']['height']:.0f})")
                                if parent_info['parent']:
                                    p = parent_info['parent']
                                    logger.debug(f"父元素: <{p['tag']}> id='{p['id']}' class='{p['className'][:80]}'")
                                    logger.debug(f"  display={p['display']} visibility={p['visibility']} opacity={p['opacity']} height={p['height']} overflow={p['overflow']}")
                        except Exception as eval_err:
                            logger.debug(f"获取元素/父元素信息失败: {eval_err}")
                raise
            count = await primary_locator.count()
            if count > 1:
                return primary_locator.first
            return primary_locator

        result_locator = primary_locator
        for backup_config in backup_locators:
            backup_type = backup_config.get('type', 'css')
            backup_value = backup_config.get('value', '')
            backup_locator = self._locate_element(backup_type, backup_value)
            result_locator = result_locator.and_(backup_locator)

        try:
            await result_locator.wait_for(timeout=timeout)
        except Exception as wait_error:
            logger.debug(f"get_element (with backup_locators) wait_for 超时")
            logger.debug(f"主定位器类型: {locator_type}, 值: {locator_value}")
            logger.debug(f"wait_for 错误: {wait_error}")
            count = await result_locator.count()
            logger.debug(f"组合定位器元素数量: {count}")
            if count > 0:
                is_visible = await result_locator.first.is_visible()
                logger.debug(f"第一个元素是否可见: {is_visible}")
                if is_visible:
                    await self._debug_blocking_elements(result_locator.first)
            raise
        count = await result_locator.count()
        if count > 1:
            return result_locator.first
        return result_locator

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

    def _locate_element(self, locator_type: str, locator_value: str) -> Any:
        if ' >> ' in locator_value:
            parts = locator_value.split(' >> ', 1)
            ancestor_part = parts[0].strip()
            descendant_part = parts[1].strip()

            ancestor_locator = self._locate_element('css', ancestor_part)

            if descendant_part.startswith('text='):
                text_value = descendant_part[5:]
                descendant_locator = ancestor_locator.get_by_text(text_value, exact=True)
            elif descendant_part.startswith('role='):
                role_value = descendant_part[5:]
                descendant_locator = ancestor_locator.get_by_role(role_value)
            else:
                descendant_locator = ancestor_locator.locator(descendant_part)

            return descendant_locator

        if locator_type == 'css':
            if locator_value.startswith('#'):
                raw_id = locator_value[1:]
                has_backslash = '\\' in raw_id
                if has_backslash:
                    pass
                else:
                    locator_value = '#' + self._escape_css_id(raw_id)
            return self.page.locator(locator_value)
        elif locator_type == 'xpath':
            return self.page.locator(f'xpath={locator_value}')
        elif locator_type == 'id':
            return self.page.locator(f'#{self._escape_css_id(locator_value)}')
        elif locator_type == 'name':
            return self.page.locator(f'[name="{locator_value}"]')
        elif locator_type == 'class_name':
            return self.page.locator(f'.{locator_value}')
        elif locator_type == 'tag_name':
            return self.page.locator(locator_value)
        elif locator_type == 'text':
            return self.page.get_by_text(locator_value, exact=True)
        elif locator_type == 'role':
            return self.page.get_by_role('button', name=locator_value)
        elif locator_type == 'test_id':
            return self.page.get_by_test_id(locator_value)
        elif locator_type == 'placeholder':
            return self.page.get_by_placeholder(locator_value)
        elif locator_type == 'label':
            return self.page.get_by_label(locator_value)
        else:
            return self.page.locator(locator_value)
