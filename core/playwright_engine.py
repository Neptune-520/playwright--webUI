import asyncio
import time
import json
import random
import traceback
from typing import Optional, Dict, Any, List
from pathlib import Path
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from django.conf import settings
import logging
from .engines.error_message_manager import error_message_manager

logger = logging.getLogger(__name__)


class PlaywrightEngine:
    def __init__(
        self,
        headless: bool = None,
        timeout: int = None,
        slow_mo: int = None,
        screenshots_dir: Path = None,
        global_config: Dict[str, Any] = None,
    ):
        self.headless = headless if headless is not None else settings.PLAYWRIGHT_HEADLESS
        self.timeout = timeout if timeout is not None else settings.PLAYWRIGHT_TIMEOUT
        self.slow_mo = slow_mo if slow_mo is not None else settings.PLAYWRIGHT_SLOW_MO
        self.screenshots_dir = screenshots_dir or settings.SCREENSHOTS_DIR
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.global_config = global_config or {}

        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None

    async def start(self, browser_type: str = 'chromium', **context_options):
        self.playwright = await async_playwright().start()

        browser_launcher = getattr(self.playwright, browser_type)
        self.browser = await browser_launcher.launch(
            headless=self.headless,
            slow_mo=self.slow_mo,
        )

        viewport_width = self.global_config.get('viewport_width', 1920) if self.global_config else 1920
        viewport_height = self.global_config.get('viewport_height', 1080) if self.global_config else 1080
        default_context_options = {
            'viewport': {'width': viewport_width, 'height': viewport_height},
            'locale': 'zh-CN',
            'timezone_id': 'Asia/Shanghai',
        }
        default_context_options.update(context_options)

        self.context = await self.browser.new_context(**default_context_options)
        self.context.set_default_timeout(self.timeout)

        self.page = await self.context.new_page()

        logger.info(f"Playwright engine started with {browser_type}")
        return self.page

    async def close(self):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None

        logger.info("Playwright engine closed")

    async def take_screenshot(self, name: str, full_page: bool = False) -> str:
        if not self.page:
            raise RuntimeError("Page not initialized. Call start() first.")

        timestamp = int(time.time() * 1000)
        filename = f"{name}_{timestamp}.png"
        filepath = self.screenshots_dir / filename

        await self.page.screenshot(path=str(filepath), full_page=full_page)

        logger.info(f"Screenshot saved: {filepath}")
        return str(filepath)

    async def take_element_screenshot(self, element, name: str) -> str:
        if not self.page:
            raise RuntimeError("Page not initialized. Call start() first.")

        timestamp = int(time.time() * 1000)
        filename = f"{name}_{timestamp}.png"
        filepath = self.screenshots_dir / filename

        await element.screenshot(path=str(filepath))

        logger.info(f"Element screenshot saved: {filepath}")
        return str(filepath)

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

    async def execute_action(
        self,
        action_type: str,
        element_config: Optional[Dict[str, Any]] = None,
        value: Any = None,
        config: Optional[Dict[str, Any]] = None,
        step_screenshot: bool = False,
    ) -> Dict[str, Any]:
        result = {
            'success': False,
            'action': action_type,
            'value': value,
            'error': None,
            'screenshot': None,
            'element_screenshot': None,
            'duration': 0,
        }

        start_time = time.time()
        config = config or {}
        element = None

        try:
            if action_type == 'navigate':
                await self.page.goto(value, wait_until='networkidle')
                result['success'] = True

            elif action_type == 'click':
                element = await self.get_element(element_config)
                click_options = {
                    'button': config.get('button', 'left'),
                    'click_count': config.get('click_count', 1),
                    'delay': config.get('delay', 0),
                    'force': config.get('force', False),
                }
                try:
                    await element.click(**click_options)
                    result['success'] = True
                except Exception as click_error:
                    logger.debug(f"Click 失败，开始分析阻挡元素...")
                    logger.debug(f"Click 错误信息: {click_error}")
                    await self._debug_blocking_elements(element)
                    raise

            elif action_type == 'fill':
                element = await self.get_element(element_config)
                await element.fill(value or '')
                result['success'] = True

            elif action_type == 'select':
                element = await self.get_element(element_config)
                await element.select_option(value)
                result['success'] = True

            elif action_type == 'random_select':
                random_options = config.get('random_options', [])
                if not random_options:
                    raise ValueError("No random options provided for random_select action")

                select_mode = config.get('select_mode', 'dropdown')
                available_options = list(random_options)
                selected_value = None
                last_error = None

                while available_options and not selected_value:
                    current_choice = random.choice(available_options)

                    try:
                        if select_mode == 'dropdown':
                            element = await self.get_element(element_config)
                            try:
                                await element.select_option(current_choice, timeout=5000)
                                selected_value = current_choice
                            except Exception as e:
                                available_options.remove(current_choice)
                                last_error = str(e)
                                logger.warning(f"Option '{current_choice}' not available in dropdown, trying another option. Error: {e}")
                                continue

                        elif select_mode == 'click':
                            container_locator = element_config.get('value', '') if element_config else ''
                            if not container_locator:
                                raise ValueError("Container locator required for click mode random_select")

                            container = self.page.locator(container_locator)

                            try:
                                option_locator = container.get_by_text(current_choice, exact=True)
                                if await option_locator.count() > 0:
                                    await option_locator.first.click(timeout=5000)
                                    selected_value = current_choice
                                else:
                                    available_options.remove(current_choice)
                                    last_error = f"Option '{current_choice}' not found in container"
                                    logger.warning(f"Option '{current_choice}' not found in container, trying another option")
                                    continue
                            except Exception as e:
                                available_options.remove(current_choice)
                                last_error = str(e)
                                logger.warning(f"Failed to click option '{current_choice}', trying another option. Error: {e}")
                                continue

                        else:
                            element = await self.get_element(element_config)
                            try:
                                await element.select_option(current_choice, timeout=5000)
                                selected_value = current_choice
                            except Exception as e:
                                available_options.remove(current_choice)
                                last_error = str(e)
                                logger.warning(f"Option '{current_choice}' not available, trying another option. Error: {e}")
                                continue

                    except Exception as e:
                        available_options.remove(current_choice)
                        last_error = str(e)
                        logger.warning(f"Error trying option '{current_choice}': {e}")
                        continue

                if not selected_value:
                    raise ValueError(f"No available options found in the page. All options were tried: {random_options}. Last error: {last_error}")

                result['success'] = True
                result['selected_value'] = selected_value
                result['available_options'] = random_options
                result['select_mode'] = select_mode
                logger.info(f"Random select chose: {selected_value} from {len(random_options)} options using {select_mode} mode")

            elif action_type == 'random_number':
                element = await self.get_element(element_config)
                random_min = config.get('random_min', 0)
                random_max = config.get('random_max', 100)
                generated_value = random.randint(random_min, random_max)
                await element.fill(str(generated_value))
                result['success'] = True
                result['generated_value'] = generated_value
                result['random_min'] = random_min
                result['random_max'] = random_max
                logger.info(f"Random number generated: {generated_value} (range: {random_min}-{random_max})")

            elif action_type == 'check':
                element = await self.get_element(element_config)
                await element.check()
                result['success'] = True

            elif action_type == 'uncheck':
                element = await self.get_element(element_config)
                await element.uncheck()
                result['success'] = True

            elif action_type == 'wait':
                wait_time = int(value) if value else 1000
                await asyncio.sleep(wait_time / 1000)
                result['success'] = True

            elif action_type == 'wait_for_selector':
                element = await self.get_element(element_config)
                state = config.get('state', 'visible')
                await element.wait_for(state=state)
                result['success'] = True

            elif action_type == 'screenshot':
                full_page = config.get('full_page', False)
                screenshot_path = await self.take_screenshot(value or 'step', full_page)
                result['screenshot'] = screenshot_path
                result['success'] = True

            elif action_type == 'scroll':
                element = await self.get_element(element_config) if element_config else None
                if element:
                    await element.scroll_into_view_if_needed()
                else:
                    scroll_type = config.get('scroll_type', self.global_config.get('scroll_direction', 'down') if self.global_config else 'down')
                    scroll_amount = config.get('amount', self.global_config.get('scroll_distance', 500) if self.global_config else 500)
                    if scroll_type == 'down':
                        await self.page.mouse.wheel(0, scroll_amount)
                    elif scroll_type == 'up':
                        await self.page.mouse.wheel(0, -scroll_amount)
                    elif scroll_type == 'left':
                        await self.page.mouse.wheel(-scroll_amount, 0)
                    elif scroll_type == 'right':
                        await self.page.mouse.wheel(scroll_amount, 0)
                result['success'] = True

            elif action_type == 'hover':
                element = await self.get_element(element_config)
                await element.hover()
                result['success'] = True

            elif action_type == 'focus':
                element = await self.get_element(element_config)
                await element.focus()
                result['success'] = True

            elif action_type == 'press':
                element = await self.get_element(element_config)
                await element.press(value)
                result['success'] = True

            elif action_type == 'upload':
                element = await self.get_element(element_config)
                file_path = Path(value)
                if file_path.exists():
                    await element.set_input_files(str(file_path))
                else:
                    raise FileNotFoundError(f"File not found: {value}")
                result['success'] = True

            elif action_type == 'assert_text':
                element = await self.get_element(element_config)
                actual_text = await element.text_content()
                expected_text = value
                if expected_text in actual_text:
                    result['success'] = True
                else:
                    raise AssertionError(
                        f"Text assertion failed. Expected: '{expected_text}', Actual: '{actual_text}'"
                    )

            elif action_type == 'assert_visible':
                element = await self.get_element(element_config)
                is_visible = await element.is_visible()
                if is_visible:
                    result['success'] = True
                else:
                    raise AssertionError("Element is not visible")

            elif action_type == 'assert_value':
                element = await self.get_element(element_config)
                actual_value = await element.input_value()
                expected_value = value
                if actual_value == expected_value:
                    result['success'] = True
                else:
                    raise AssertionError(
                        f"Value assertion failed. Expected: '{expected_value}', Actual: '{actual_value}'"
                    )

            elif action_type == 'custom':
                custom_code = value
                if custom_code:
                    exec_globals = {'page': self.page, 'asyncio': asyncio}
                    exec(custom_code, exec_globals)
                result['success'] = True

            else:
                raise ValueError(f"Unknown action type: {action_type}")

            if step_screenshot and element and result['success']:
                try:
                    element_screenshot_path = await self.take_element_screenshot(element, f"step_{action_type}")
                    result['element_screenshot'] = element_screenshot_path
                except Exception as screenshot_error:
                    logger.warning(f"Failed to take element screenshot: {screenshot_error}")

        except Exception as e:
            original_error = str(e)
            context = {}
            if action_type == 'navigate':
                context['url'] = value or '未知页面'
            elif element_config:
                context['element_config'] = element_config
            
            formatted_error = error_message_manager.format_error_message(
                original_error, 
                action_type=action_type,
                context=context
            )
            
            result['error'] = formatted_error
            result['original_error'] = original_error
            result['success'] = False
            try:
                screenshot_path = await self.take_screenshot(f"error_{action_type}")
                result['screenshot'] = screenshot_path
            except:
                pass
            logger.error(f"Action {action_type} failed: {original_error}")

        result['duration'] = time.time() - start_time
        return result

    async def execute_script(
        self,
        steps: List[Dict[str, Any]],
        take_screenshots: bool = True,
        step_screenshot: bool = False,
    ) -> List[Dict[str, Any]]:
        results = []

        for i, step in enumerate(steps):
            if not step.get('is_enabled', True):
                results.append({
                    'step_order': i,
                    'step_name': step.get('name', f'Step {i}'),
                    'status': 'skipped',
                    'duration': 0,
                    'error': None,
                    'screenshot': None,
                    'element_screenshot': None,
                })
                continue

            action_result = await self.execute_action(
                action_type=step.get('action_type'),
                element_config=step.get('element'),
                value=step.get('value'),
                config=step.get('config', {}),
                step_screenshot=step_screenshot,
            )

            result = {
                'step_order': i,
                'step_name': step.get('name', f'Step {i}'),
                'status': 'passed' if action_result['success'] else 'failed',
                'duration': action_result['duration'],
                'error': action_result['error'],
                'original_error': action_result.get('original_error'),
                'screenshot': action_result['screenshot'],
                'element_screenshot': action_result.get('element_screenshot'),
            }

            if take_screenshots and action_result['success'] and not result.get('element_screenshot'):
                try:
                    screenshot_path = await self.take_screenshot(f"step_{i}")
                    result['screenshot'] = screenshot_path
                except:
                    pass

            results.append(result)

            if not action_result['success'] and not step.get('continue_on_failure', False):
                for remaining_step in steps[i+1:]:
                    results.append({
                        'step_order': steps.index(remaining_step),
                        'step_name': remaining_step.get('name', f'Step {steps.index(remaining_step)}'),
                        'status': 'skipped',
                        'duration': 0,
                        'error': 'Skipped due to previous failure',
                        'screenshot': None,
                    })
                break

        return results


class PlaywrightSync:
    @staticmethod
    def run_async(coro):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(coro)
