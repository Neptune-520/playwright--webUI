import asyncio
import json
from datetime import datetime
from django.utils import timezone
from celery import shared_task
from django.conf import settings
from test_manager.models import TestTask, TestResult, TestReport
from script_editor.models import TestScript, TestStep, ElementLocator, GlobalConfig
from script_editor.serializers import GlobalConfigSerializer
from core.playwright_engine import PlaywrightEngine
from core.script_manager import TestResultExporter
from core.signals import script_execution_completed
import logging
import uuid

logger = logging.getLogger(__name__)


def run_test_task_sync(task_id: int):
    """
    Synchronous wrapper for test task execution (no Celery required)
    """
    class FakeRequest:
        def __init__(self):
            self.id = f"sync-{task_id}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
    
    class FakeSelf:
        request = FakeRequest()
    
    return execute_test_task.run(FakeSelf(), task_id)


def execute_test_task_sync_for_aggregate(task_id: int, celery_task_id: str):
    """
    Synchronous wrapper for aggregate task execution
    """
    class FakeRequest:
        def __init__(self):
            self.id = celery_task_id
    
    class FakeSelf:
        request = FakeRequest()
    
    return execute_test_task.run(FakeSelf(), task_id)


def _execute_test_task_internal(task_id: int, celery_task_id: str):
    """
    Direct internal execution of test task logic for aggregate tasks.
    Bypasses Celery entirely to avoid parameter passing issues with bind=True.
    """
    try:
        task = TestTask.objects.get(pk=task_id)
    except TestTask.DoesNotExist:
        logger.error(f"Task {task_id} not found")
        return {'status': 'error', 'message': 'Task not found'}
    
    task.results.all().delete()
    if hasattr(task, 'report'):
        task.report.delete()
    
    task.status = 'running'
    task.started_at = timezone.now()
    task.finished_at = None
    task.celery_task_id = celery_task_id
    task.save()
    
    script = task.script
    parameters = task.parameters or {}
    
    global_config = GlobalConfig.get_config()
    
    result_data = {
        'task_id': task_id,
        'task_name': task.name,
        'script_name': script.name,
        'started_at': task.started_at.isoformat(),
        'finished_at': None,
        'status': 'running',
        'step_results': [],
        'parameters': parameters,
    }
    
    engine = None
    try:
        engine = PlaywrightEngine(
            headless=global_config.headless_mode,
            timeout=global_config.default_timeout,
            slow_mo=global_config.slow_mo,
            global_config=GlobalConfigSerializer(global_config).data,
        )
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            page = loop.run_until_complete(
                engine.start(viewport={
                    'width': global_config.viewport_width,
                    'height': global_config.viewport_height,
                })
            )
            
            steps = script.steps.filter(is_enabled=True).order_by('order')
            step_list = list(steps)
            step_results = []
            
            breakpoint_ranges = []
            bp_start_idx = None
            for idx, s in enumerate(step_list):
                action_config = s.action_config or {}
                if action_config.get('breakpoint_start'):
                    bp_start_idx = idx
                if action_config.get('breakpoint_end') and bp_start_idx is not None:
                    breakpoint_ranges.append((bp_start_idx, idx))
                    bp_start_idx = None
            
            for idx, step in enumerate(step_list):
                step_result = execute_step(loop, engine, step, parameters, global_config.step_screenshot, global_config)
                step_results.append(step_result)
                
                TestResult.objects.create(
                    task=task,
                    step_name=step.name,
                    step_order=step.order,
                    status=step_result['status'],
                    duration=step_result['duration'],
                    error_message=step_result.get('error') or '',
                    error_stack=step_result.get('original_error') or step_result.get('error_stack') or '',
                    screenshot=step_result.get('screenshot') or step_result.get('element_screenshot'),
                    action_values=step_result.get('action_values', {}),
                    logs=step_result.get('logs', []),
                )
                
                if step_result['status'] == 'failed' and not step.continue_on_failure:
                    for remaining_step in step_list[idx+1:]:
                        skip_result = {
                            'step_name': remaining_step.name,
                            'step_order': remaining_step.order,
                            'action_type': remaining_step.action_type or '',
                            'status': 'skipped',
                            'duration': 0,
                            'error': '由于之前的失败而跳过',
                            'error_stack': None,
                            'screenshot': None,
                            'element_screenshot': None,
                            'action_values': {},
                            'logs': [],
                        }
                        step_results.append(skip_result)
                        TestResult.objects.create(
                            task=task,
                            step_name=remaining_step.name,
                            step_order=remaining_step.order,
                            status='skipped',
                            duration=0,
                            error_message='由于之前的失败而跳过',
                        )
                    break
            
            result_data['step_results'] = step_results
            
            total_steps = len(step_results)
            passed = sum(1 for r in step_results if r['status'] == 'passed')
            failed = sum(1 for r in step_results if r['status'] == 'failed')
            skipped = sum(1 for r in step_results if r['status'] == 'skipped')
            total_duration = sum(r['duration'] for r in step_results)
            
            result_data['total_steps'] = total_steps
            result_data['passed_steps'] = passed
            result_data['failed_steps'] = failed
            result_data['skipped_steps'] = skipped
            result_data['total_duration'] = total_duration
            result_data['pass_rate'] = round((passed / total_steps * 100) if total_steps > 0 else 0, 2)
            
            if failed > 0:
                task.status = 'failed'
                result_data['status'] = 'failed'
            else:
                task.status = 'completed'
                result_data['status'] = 'completed'
            
            TestReport.objects.create(
                task=task,
                total_steps=total_steps,
                passed_steps=passed,
                failed_steps=failed,
                skipped_steps=skipped,
                total_duration=total_duration,
                summary={
                    'pass_rate': round((passed / total_steps * 100) if total_steps > 0 else 0, 2),
                    'parameters': parameters,
                }
            )
            
        finally:
            if engine:
                try:
                    loop.run_until_complete(engine.close())
                except Exception as e:
                    logger.warning(f"Failed to close Playwright engine: {e}")
            try:
                loop.close()
            except Exception as e:
                logger.warning(f"Failed to close event loop: {e}")
            
    except Exception as e:
        logger.exception(f"Task {task_id} execution failed")
        task.status = 'failed'
        result_data['status'] = 'failed'
        result_data['error'] = str(e)
        
    finally:
        task.finished_at = timezone.now()
        task.save()
        
        result_data['finished_at'] = task.finished_at.isoformat()
        
        exporter = TestResultExporter()
        exporter.save_result(task_id, result_data)
        
        if task.upload_to_management:
            try:
                from test_manager.views import upload_result_to_management
                success, report_id = upload_result_to_management(task_id)
                task.upload_status = 'uploaded' if success else 'failed'
                task.save()
            except Exception as e:
                logger.exception(f"Error during upload for task {task_id}: {e}")
                task.upload_status = 'failed'
                task.save()
                report_id = None

            if task.send_email:
                from test_manager.email_notification import send_task_notification
                send_task_notification(task_id, task.name, task.status, result_data, report_id)
        elif task.send_email:
            from test_manager.email_notification import send_task_notification
            send_task_notification(task_id, task.name, task.status, result_data, None)
    
    return result_data


@shared_task(bind=True)
def execute_test_task(self, task_id: int):
    try:
        task = TestTask.objects.get(pk=task_id)
    except TestTask.DoesNotExist:
        logger.error(f"Task {task_id} not found")
        return {'status': 'error', 'message': 'Task not found'}
    
    task.results.all().delete()
    if hasattr(task, 'report'):
        task.report.delete()
    
    task.status = 'running'
    task.started_at = timezone.now()
    task.finished_at = None
    task.celery_task_id = self.request.id
    task.save()
    
    script = task.script
    parameters = task.parameters or {}
    
    global_config = GlobalConfig.get_config()
    
    result_data = {
        'task_id': task_id,
        'task_name': task.name,
        'script_name': script.name,
        'started_at': task.started_at.isoformat(),
        'finished_at': None,
        'status': 'running',
        'step_results': [],
        'parameters': parameters,
    }
    
    engine = None
    try:
        engine = PlaywrightEngine(
            headless=global_config.headless_mode,
            timeout=global_config.default_timeout,
            slow_mo=global_config.slow_mo,
            global_config=GlobalConfigSerializer(global_config).data,
        )
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            page = loop.run_until_complete(
                engine.start(viewport={
                    'width': global_config.viewport_width,
                    'height': global_config.viewport_height,
                })
            )
            
            steps = script.steps.filter(is_enabled=True).order_by('order')
            step_list = list(steps)
            step_results = []
            
            breakpoint_ranges = []
            bp_start_idx = None
            for idx, s in enumerate(step_list):
                action_config = s.action_config or {}
                if action_config.get('breakpoint_start'):
                    bp_start_idx = idx
                if action_config.get('breakpoint_end') and bp_start_idx is not None:
                    breakpoint_ranges.append((bp_start_idx, idx))
                    bp_start_idx = None
            
            for idx, step in enumerate(step_list):
                step_result = execute_step(loop, engine, step, parameters, global_config.step_screenshot, global_config)
                step_results.append(step_result)
                
                TestResult.objects.create(
                    task=task,
                    step_name=step.name,
                    step_order=step.order,
                    status=step_result['status'],
                    duration=step_result['duration'],
                    error_message=step_result.get('error') or '',
                    error_stack=step_result.get('original_error') or step_result.get('error_stack') or '',
                    screenshot=step_result.get('screenshot') or step_result.get('element_screenshot'),
                    action_values=step_result.get('action_values', {}),
                    logs=step_result.get('logs', []),
                )
                
                if step_result['status'] == 'failed' and not step.continue_on_failure:
                    for remaining_step in step_list[idx+1:]:
                        skip_result = {
                            'step_name': remaining_step.name,
                            'step_order': remaining_step.order,
                            'action_type': remaining_step.action_type or '',
                            'status': 'skipped',
                            'duration': 0,
                            'error': '由于之前的失败而跳过',
                            'error_stack': None,
                            'screenshot': None,
                            'element_screenshot': None,
                            'action_values': {},
                            'logs': [],
                        }
                        step_results.append(skip_result)
                        TestResult.objects.create(
                            task=task,
                            step_name=remaining_step.name,
                            step_order=remaining_step.order,
                            status='skipped',
                            duration=0,
                            error_message='由于之前的失败而跳过',
                        )
                    break
                
                action_config = step.action_config or {}
                if action_config.get('breakpoint_end'):
                    for bp_start, bp_end in breakpoint_ranges:
                        if bp_end == idx:
                            for bp_idx in range(bp_start, bp_end + 1):
                                if bp_idx < len(step_results) and not step_results[bp_idx].get('action_values'):
                                    bp_step = step_list[bp_idx]
                                    retry_result = execute_step(loop, engine, bp_step, parameters, global_config.step_screenshot, global_config)
                                    if retry_result['status'] == 'passed':
                                        step_results[bp_idx] = retry_result
                                        TestResult.objects.filter(task=task, step_order=bp_step.order).update(
                                            status='passed',
                                            duration=retry_result['duration'],
                                            error_message='',
                                            action_values=retry_result.get('action_values', {}),
                                        )
                            break
            
            result_data['step_results'] = step_results
            
            total_steps = len(step_results)
            passed = sum(1 for r in step_results if r['status'] == 'passed')
            failed = sum(1 for r in step_results if r['status'] == 'failed')
            skipped = sum(1 for r in step_results if r['status'] == 'skipped')
            total_duration = sum(r['duration'] for r in step_results)
            
            result_data['total_steps'] = total_steps
            result_data['passed_steps'] = passed
            result_data['failed_steps'] = failed
            result_data['skipped_steps'] = skipped
            result_data['total_duration'] = total_duration
            result_data['pass_rate'] = round((passed / total_steps * 100) if total_steps > 0 else 0, 2)
            
            if failed > 0:
                task.status = 'failed'
                result_data['status'] = 'failed'
            else:
                task.status = 'completed'
                result_data['status'] = 'completed'
            
            TestReport.objects.create(
                task=task,
                total_steps=total_steps,
                passed_steps=passed,
                failed_steps=failed,
                skipped_steps=skipped,
                total_duration=sum(r['duration'] for r in step_results),
                summary={
                    'pass_rate': round((passed / total_steps * 100) if total_steps > 0 else 0, 2),
                    'parameters': parameters,
                }
            )
            
        finally:
            if engine:
                try:
                    loop.run_until_complete(engine.close())
                except Exception as e:
                    logger.warning(f"Failed to close Playwright engine: {e}")
            try:
                loop.close()
            except Exception as e:
                logger.warning(f"Failed to close event loop: {e}")
            
    except Exception as e:
        logger.exception(f"Task {task_id} execution failed")
        task.status = 'failed'
        result_data['status'] = 'failed'
        result_data['error'] = str(e)
        
    finally:
        task.finished_at = timezone.now()
        task.save()
        
        result_data['finished_at'] = task.finished_at.isoformat()
        
        exporter = TestResultExporter()
        exporter.save_result(task_id, result_data)
        
        if getattr(task, 'upload_to_management', False):
            try:
                from test_manager.views import upload_result_to_management
                success, report_id = upload_result_to_management(task_id)
                task.upload_status = 'uploaded' if success else 'failed'
                task.save()
            except Exception as e:
                logger.exception(f"Error during upload for task {task_id}: {e}")
                task.upload_status = 'failed'
                task.save()
                report_id = None

            if getattr(task, 'send_email', False):
                from test_manager.email_notification import send_task_notification
                send_task_notification(task_id, task.name, task.status, result_data, report_id)
        elif getattr(task, 'send_email', False):
            from test_manager.email_notification import send_task_notification
            send_task_notification(task_id, task.name, task.status, result_data, None)
    
    return result_data


def execute_step(loop, engine, step: TestStep, parameters: dict, step_screenshot: bool = False, global_config=None) -> dict:
    result = {
        'step_name': step.name,
        'step_order': step.order,
        'action_type': step.action_type,
        'status': 'pending',
        'duration': 0,
        'error': None,
        'error_stack': None,
        'screenshot': None,
        'element_screenshot': None,
        'action_values': {},
        'logs': [],
    }
    
    import time
    start_time = time.time()
    
    try:
        if step.action_type == 'action_set' and step.action_set_ref:
            action_set = step.action_set_ref
            action_set_params = step.action_set_params or {}
            merged_params = {**parameters, **action_set_params}
            
            action_set_steps = action_set.steps.filter(is_enabled=True).order_by('order')
            sub_results = []
            action_values_list = []
            
            for as_step in action_set_steps:
                sub_result = execute_action_set_step(loop, engine, as_step, merged_params, step_screenshot)
                sub_results.append(sub_result)
                sub_entry = {
                    'step_name': as_step.name,
                    'status': sub_result['status'],
                    'values': sub_result.get('action_values', {}),
                }
                if sub_result.get('error'):
                    sub_entry['error'] = sub_result['error']
                    error_stack = sub_result.get('error_stack') or sub_result.get('original_error')
                    if error_stack and error_stack != sub_result['error']:
                        sub_entry['error_stack'] = error_stack
                action_values_list.append(sub_entry)
                
                if sub_result['status'] == 'failed' and not as_step.continue_on_failure:
                    for remaining_step in action_set_steps:
                        if remaining_step.order > as_step.order:
                            action_values_list.append({
                                'step_name': remaining_step.name,
                                'status': 'skipped',
                                'values': {},
                                'error': '由于之前的失败而跳过',
                            })
                    break
            
            all_passed = all(r['status'] == 'passed' for r in sub_results)
            result['status'] = 'passed' if all_passed else 'failed'
            result['sub_results'] = sub_results
            result['action_values'] = {'sub_steps': action_values_list}
            result['duration'] = time.time() - start_time
            return result
        
        action_value = step.action_value
        
        if parameters:
            for key, value in parameters.items():
                action_value = action_value.replace(f'{{{{{key}}}}}', str(value))
        
        element_config = None
        action_config = step.action_config or {}
        locators = action_config.get('locators', [])
        if locators:
            primary = locators[0]
            element_config = {
                'type': primary.get('locator_type', 'css'),
                'value': primary.get('locator_value', ''),
                'timeout': global_config.default_timeout if global_config else 30000,
            }
            if len(locators) > 1:
                element_config['backup_locators'] = [
                    {
                        'type': loc.get('locator_type', 'css'),
                        'value': loc.get('locator_value', ''),
                    }
                    for loc in locators[1:]
                ]
        elif step.element:
            element_config = step.element.to_playwright_locator()
        
        if step.action_type == 'random_select':
            random_options = action_config.get('random_options', [])
            if not random_options:
                raise ValueError("No random options configured for random_select action")
            action_config['random_options'] = random_options
            action_config['select_mode'] = action_config.get('select_mode', 'dropdown')
        
        if step.action_type == 'random_number':
            action_config['random_min'] = action_config.get('random_min', 0)
            action_config['random_max'] = action_config.get('random_max', 100)
        
        retry_count = step.retry_count
        last_error = None
        
        for attempt in range(retry_count + 1):
            try:
                action_result = loop.run_until_complete(
                    engine.execute_action(
                        action_type=step.action_type,
                        element_config=element_config,
                        value=action_value,
                        config=action_config,
                        step_screenshot=step_screenshot,
                    )
                )
                
                if action_result['success']:
                    result['status'] = 'passed'
                    result['screenshot'] = action_result.get('screenshot')
                    result['element_screenshot'] = action_result.get('element_screenshot')
                    
                    if step.action_type == 'fill':
                        result['action_values'] = {'输入值': action_value}
                    elif step.action_type == 'select':
                        result['action_values'] = {'选择值': action_value}
                    elif step.action_type == 'random_select':
                        result['selected_value'] = action_result.get('selected_value')
                        result['available_options'] = action_result.get('available_options')
                        result['action_values'] = {
                            '随机选择值': action_result.get('selected_value'),
                            '可选值': action_result.get('available_options')
                        }
                    elif step.action_type == 'random_number':
                        result['generated_value'] = action_result.get('generated_value')
                        result['random_min'] = action_result.get('random_min')
                        result['random_max'] = action_result.get('random_max')
                        result['action_values'] = {
                            '随机数值': action_result.get('generated_value'),
                            '范围': f"{action_result.get('random_min')} - {action_result.get('random_max')}"
                        }
                    elif step.action_type == 'click':
                        result['action_values'] = {'操作': '点击'}
                    elif step.action_type == 'navigate':
                        result['action_values'] = {'导航URL': action_value}
                    break
                else:
                    last_error = action_result.get('error')
                    last_original_error = action_result.get('original_error')
                    if attempt < retry_count:
                        time.sleep(step.retry_interval / 1000)
                        continue
                    raise Exception(last_error)
                    
            except Exception as e:
                last_error = str(e)
                if attempt < retry_count:
                    time.sleep(step.retry_interval / 1000)
                    continue
                raise
        
    except Exception as e:
        result['status'] = 'failed'
        result['error'] = str(e)
        result['error_stack'] = last_original_error if 'last_original_error' in locals() and last_original_error else str(e)
        
        try:
            screenshot_path = loop.run_until_complete(
                engine.take_screenshot(f"error_step_{step.order}")
            )
            result['screenshot'] = screenshot_path
        except:
            pass
            
    result['duration'] = time.time() - start_time
    return result


def execute_action_set_step(loop, engine, as_step, parameters: dict, step_screenshot: bool = False) -> dict:
    """
    Execute a single step from an action set
    """
    import time
    
    result = {
        'step_name': as_step.name,
        'step_order': as_step.order,
        'action_type': as_step.action_type,
        'status': 'pending',
        'duration': 0,
        'error': None,
        'element_screenshot': None,
        'action_values': {},
    }
    
    start_time = time.time()
    
    try:
        action_value = as_step.action_value or ''
        
        if as_step.action_value_type == 'parameter' and as_step.parameter_name:
            action_value = parameters.get(as_step.parameter_name, as_step.action_value or '')
        elif parameters:
            for key, value in parameters.items():
                action_value = action_value.replace(f'{{{{{key}}}}}', str(value))
        
        element_config = None
        if hasattr(as_step, 'action_config') and as_step.action_config and as_step.action_config.get('locators'):
            locators = as_step.action_config['locators']
            if locators:
                primary = locators[0]
                element_config = {
                    'type': primary.get('locator_type', as_step.locator_type),
                    'value': primary.get('locator_value', as_step.locator_value),
                    'timeout': as_step.wait_timeout,
                }
                if len(locators) > 1:
                    element_config['backup_locators'] = [
                        {
                            'type': loc.get('locator_type', 'css'),
                            'value': loc.get('locator_value', ''),
                        }
                        for loc in locators[1:]
                    ]
        elif as_step.locator_value:
            element_config = {
                'type': as_step.locator_type,
                'value': as_step.locator_value,
                'timeout': as_step.wait_timeout,
            }
        
        action_config = {
            'continue_on_failure': as_step.continue_on_failure,
            'retry_count': as_step.retry_count,
            'retry_interval': as_step.retry_interval,
        }
        
        if as_step.action_type == 'random_select':
            action_config['random_options'] = as_step.random_options or []
            action_config['select_mode'] = as_step.select_mode or 'dropdown'
        
        if as_step.action_type == 'random_number':
            action_config['random_min'] = getattr(as_step, 'random_min', 0) or 0
            action_config['random_max'] = getattr(as_step, 'random_max', 100) or 100
        
        if as_step.action_type == 'click':
            action_config['force'] = getattr(as_step, 'force_click', False)
        
        retry_count = as_step.retry_count
        last_error = None
        last_original_error = None
        
        for attempt in range(retry_count + 1):
            try:
                action_result = loop.run_until_complete(
                    engine.execute_action(
                        action_type=as_step.action_type,
                        element_config=element_config,
                        value=action_value,
                        config=action_config,
                        step_screenshot=step_screenshot,
                    )
                )
                
                if action_result['success']:
                    result['status'] = 'passed'
                    result['element_screenshot'] = action_result.get('element_screenshot')
                    
                    if as_step.action_type == 'fill':
                        result['action_values'] = {'输入值': action_value}
                    elif as_step.action_type == 'select':
                        result['action_values'] = {'选择值': action_value}
                    elif as_step.action_type == 'random_select':
                        result['action_values'] = {
                            '随机选择值': action_result.get('selected_value'),
                            '可选值': action_result.get('available_options')
                        }
                    elif as_step.action_type == 'random_number':
                        result['action_values'] = {
                            '随机数值': action_result.get('generated_value'),
                            '范围': f"{action_result.get('random_min')} - {action_result.get('random_max')}"
                        }
                    elif as_step.action_type == 'click':
                        result['action_values'] = {'操作': '点击'}
                    break
                else:
                    last_error = action_result.get('error')
                    last_original_error = action_result.get('original_error')
                    if attempt < retry_count:
                        time.sleep(as_step.retry_interval / 1000)
                        continue
                    raise Exception(last_error)
                    
            except Exception as e:
                last_error = str(e)
                if attempt < retry_count:
                    time.sleep(as_step.retry_interval / 1000)
                    continue
                raise
        
    except Exception as e:
        result['status'] = 'failed'
        result['error'] = str(e)
        result['error_stack'] = last_original_error if 'last_original_error' in locals() and last_original_error else str(e)
        
    result['duration'] = time.time() - start_time
    return result


@shared_task
def cleanup_old_results(days: int = 30):
    from datetime import timedelta
    cutoff_date = datetime.now() - timedelta(days=days)
    
    old_tasks = TestTask.objects.filter(
        created_at__lt=cutoff_date,
        status__in=['completed', 'failed', 'cancelled']
    )
    
    count = old_tasks.count()
    old_tasks.delete()
    
    logger.info(f"Cleaned up {count} old test tasks")
    return {'deleted_count': count}


def run_multi_script_task_sync(task_id: int):
    class FakeRequest:
        def __init__(self):
            self.id = f"sync-multi-{task_id}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
    
    class FakeSelf:
        request = FakeRequest()
    
    return execute_multi_script_task.run(FakeSelf(), task_id)


def _execute_single_script_in_task(task_id, script, parameters, step_offset, global_config):
    results = []
    script_steps = script.steps.filter(is_enabled=True).order_by('order')
    step_list = list(script_steps)
    
    from test_manager.models import TestTask
    task = TestTask.objects.get(pk=task_id)
    
    engine = None
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            engine = PlaywrightEngine(
                headless=global_config.headless_mode,
                timeout=global_config.default_timeout,
                slow_mo=global_config.slow_mo,
                global_config=GlobalConfigSerializer(global_config).data,
            )
            loop.run_until_complete(
                engine.start(viewport={
                    'width': global_config.viewport_width,
                    'height': global_config.viewport_height,
                })
            )
            
            for idx, step in enumerate(step_list):
                step_result = execute_step(loop, engine, step, parameters, global_config.step_screenshot, global_config)
                result = {
                    'step_name': f"[{script.name}] {step.name}",
                    'step_order': step_offset + idx + 1,
                    'script_name': script.name,
                    'status': step_result['status'],
                    'duration': step_result['duration'],
                    'error_message': step_result.get('error') or '',
                    'error_stack': step_result.get('original_error') or step_result.get('error_stack') or '',
                    'screenshot': step_result.get('screenshot') or step_result.get('element_screenshot'),
                    'action_values': step_result.get('action_values', {}),
                    'logs': step_result.get('logs', []),
                }
                results.append(result)
                
                TestResult.objects.create(
                    task=task,
                    step_name=result['step_name'],
                    step_order=result['step_order'],
                    status=result['status'],
                    duration=result['duration'],
                    error_message=result['error_message'],
                    error_stack=result['error_stack'],
                    screenshot=result['screenshot'],
                    action_values=result['action_values'],
                    logs=result['logs'],
                )
                
                if step_result['status'] == 'failed' and not step.continue_on_failure:
                    for remaining_step in step_list[idx+1:]:
                        skip_result = {
                            'step_name': f"[{script.name}] {remaining_step.name}",
                            'step_order': step_offset + step_list.index(remaining_step) + 1,
                            'script_name': script.name,
                            'action_type': remaining_step.action_type or '',
                            'status': 'skipped',
                            'duration': 0,
                            'error_message': '由于之前的失败而跳过',
                            'error_stack': '',
                            'screenshot': None,
                            'action_values': {},
                            'logs': [],
                        }
                        results.append(skip_result)
                        TestResult.objects.create(
                            task=task,
                            step_name=skip_result['step_name'],
                            step_order=skip_result['step_order'],
                            status=skip_result['status'],
                            duration=skip_result['duration'],
                            error_message=skip_result['error_message'],
                        )
                    break
        finally:
            if engine:
                try:
                    loop.run_until_complete(engine.close())
                except Exception as e:
                    logger.warning(f"Failed to close Playwright engine: {e}")
            try:
                loop.close()
            except Exception as e:
                logger.warning(f"Failed to close event loop: {e}")
    except Exception as e:
        logger.exception(f"Script {script.id} execution failed in task {task_id}")
        for idx, step in enumerate(step_list):
            fail_result = {
                'step_name': f"[{script.name}] {step.name}",
                'step_order': step_offset + idx + 1,
                'script_name': script.name,
                'status': 'failed',
                'duration': 0,
                'error_message': str(e),
                'error_stack': '',
                'screenshot': None,
                'action_values': {},
                'logs': [],
            }
            results.append(fail_result)
    
    return results


def _execute_multi_script_internal(task_id: int, celery_task_id: str):
    try:
        task = TestTask.objects.get(pk=task_id)
    except TestTask.DoesNotExist:
        logger.error(f"Task {task_id} not found")
        return {'status': 'error', 'message': 'Task not found'}
    
    task.results.all().delete()
    if hasattr(task, 'report'):
        task.report.delete()
    
    task.status = 'running'
    task.started_at = timezone.now()
    task.finished_at = None
    task.celery_task_id = celery_task_id
    task.save()
    
    task_scripts = list(task.task_scripts.all().order_by('order'))
    if not task_scripts:
        task_scripts = [type('Fake', (), {'script': task.script, 'parameters': task.parameters, 'order': 0})()]
    
    global_config = GlobalConfig.get_config()
    
    all_results = []
    step_offset = 0
    any_failed = False

    script_results = []

    for ts in task_scripts:
        script = ts.script
        params = ts.parameters if hasattr(ts, 'parameters') else task.parameters

        results = _execute_single_script_in_task(task_id, script, params or task.parameters, step_offset, global_config)
        all_results.extend(results)
        step_offset += len(results)

        script_passed = sum(1 for r in results if r['status'] == 'passed')
        script_failed = sum(1 for r in results if r['status'] == 'failed')
        script_has_failure = script_failed > 0
        script_all_failed = (script_failed == len(results)) and len(results) > 0

        script_results.append({
            'status': 'failed' if script_has_failure else 'completed',
            'name': script.name,
            'passed_steps': script_passed,
            'failed_steps': script_failed,
        })

        if any(r['status'] == 'failed' for r in results):
            any_failed = True

    total_duration = sum(r['duration'] for r in all_results)
    total_steps_count = len(all_results)
    total_passed = sum(1 for r in all_results if r['status'] == 'passed')
    total_failed = sum(1 for r in all_results if r['status'] == 'failed')
    total_skipped = sum(1 for r in all_results if r['status'] == 'skipped')
    failed_scripts = sum(1 for sr in script_results if sr['failed_steps'] > 0)
    successful_scripts = sum(1 for sr in script_results if sr['failed_steps'] == 0)
    pass_rate = round((successful_scripts / len(task_scripts) * 100) if task_scripts else 0, 2)

    if any_failed:
        task.status = 'failed'
    else:
        task.status = 'completed'
    
    TestReport.objects.create(
        task=task,
        total_steps=len(all_results),
        passed_steps=sum(1 for r in all_results if r['status'] == 'passed'),
        failed_steps=sum(1 for r in all_results if r['status'] == 'failed'),
        skipped_steps=sum(1 for r in all_results if r['status'] == 'skipped'),
        total_duration=sum(r['duration'] for r in all_results),
        summary={
            'pass_rate': pass_rate,
            'parameters': task.parameters or {},
            'script_count': len(task_scripts),
        }
    )
    
    task.finished_at = timezone.now()
    task.save()
    
    result_data = {
        'task_id': task_id,
        'task_name': task.name,
        'started_at': task.started_at.isoformat(),
        'finished_at': task.finished_at.isoformat(),
        'status': task.status,
        'script_count': len(task_scripts),
        'total_duration': total_duration,
        'total_steps': total_steps_count,
        'passed_steps': total_passed,
        'failed_steps': total_failed,
        'skipped_steps': total_skipped,
        'pass_rate': pass_rate,
        'script_results': script_results,
        'successful_scripts': successful_scripts,
        'failed_scripts': failed_scripts,
    }
    
    exporter = TestResultExporter()
    exporter.save_result(task_id, result_data)
    
    if getattr(task, 'upload_to_management', False):
        try:
            from test_manager.views import upload_result_to_management
            success, report_id = upload_result_to_management(task_id)
            task.upload_status = 'uploaded' if success else 'failed'
            task.save()
        except Exception as e:
            logger.exception(f"Error during upload for task {task_id}: {e}")
            task.upload_status = 'failed'
            task.save()
            report_id = None

        if task.send_email:
            from test_manager.email_notification import send_task_notification
            send_task_notification(task_id, task.name, task.status, result_data, report_id)
    elif task.send_email:
        from test_manager.email_notification import send_task_notification
        send_task_notification(task_id, task.name, task.status, result_data, None)
    
    return result_data


@shared_task(bind=True)
def execute_multi_script_task(self, task_id: int):
    return _execute_multi_script_internal(task_id, self.request.id)
