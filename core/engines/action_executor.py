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
from .error_message_manager import error_message_manager

logger = logging.getLogger(__name__)


class ActionExecutorMixin:
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
            original_error = traceback.format_exc()
            context = {}
            if action_type == 'navigate':
                context['url'] = value or '未知页面'
            elif element_config:
                context['element_config'] = element_config
            
            formatted_error = error_message_manager.format_error_message(
                str(e), 
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
            logger.error(f"Action {action_type} failed:\n{original_error}")

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
