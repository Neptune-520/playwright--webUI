import logging
import requests
from typing import Optional
from pathlib import Path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import TestTask, TestResult, TestReport
from .serializers import (
    TestTaskListSerializer, TestTaskDetailSerializer, TestTaskCreateSerializer,
    TestResultSerializer, TestReportSerializer,
    TestTaskWithReportListSerializer
)
from core.tasks import execute_test_task
from core.script_manager import TestResultExporter
from script_editor.models import GlobalConfig

logger = logging.getLogger(__name__)


def get_management_platform_url():
    try:
        config = GlobalConfig.get_config()
        if config.management_platform_url:
            return config.management_platform_url
    except Exception:
        pass
    return 'http://localhost:8001/api/script-results/upload'


def get_username():
    try:
        config = GlobalConfig.get_config()
        if hasattr(config, 'username') and config.username:
            return config.username
    except Exception:
        pass
    return ''


def upload_result_to_management(task_id: int) -> tuple[bool, Optional[str]]:
    try:
        exporter = TestResultExporter()
        result_data = exporter.load_result(task_id)
        if not result_data:
            logger.error(f"No result data found for task {task_id}")
            return False, None

        task = TestTask.objects.get(pk=task_id)
        report = getattr(task, 'report', None)

        is_multi_script = 'script_count' in result_data and 'step_results' not in result_data

        def build_script_results(task_results):
            script_results = []
            for tr in task_results:
                action_values = getattr(tr, 'action_values', {}) or {}
                sub_steps = action_values.get('sub_steps', [])
                
                entry = {
                    'step_name': tr.step_name,
                    'step_order': len(script_results) + 1,
                    'action_type': getattr(tr, 'action_type', ''),
                    'status': tr.status,
                    'duration': tr.duration,
                    'error': tr.error_message or None,
                    'error_stack': getattr(tr, 'error_stack', '') or None,
                    'screenshot': str(tr.screenshot) if tr.screenshot else None,
                }
                
                if sub_steps:
                    entry['sub_steps'] = [
                        {
                            'step_name': s['step_name'],
                            'status': s['status'],
                            'error': s.get('error'),
                            'error_stack': s.get('error_stack'),
                            'action_values': s.get('values', {}) or {},
                        }
                        for s in sub_steps
                    ]
                    entry['action_values'] = {'sub_steps': entry['sub_steps']}
                
                script_results.append(entry)
            return script_results

        if is_multi_script:
            task_results = task.results.all().order_by('step_order')
            script_results = build_script_results(task_results)

            result_data['script_name'] = task.name
            result_data['step_results'] = script_results

            if report:
                result_data['total_steps'] = report.total_steps
                result_data['passed_steps'] = report.passed_steps
                result_data['failed_steps'] = report.failed_steps
                result_data['skipped_steps'] = report.skipped_steps
                result_data['total_duration'] = report.total_duration
                result_data['pass_rate'] = report.pass_rate
            else:
                result_data['total_steps'] = len(script_results)
                result_data['passed_steps'] = sum(1 for r in script_results if r['status'] == 'passed')
                result_data['failed_steps'] = sum(1 for r in script_results if r['status'] == 'failed')
                result_data['skipped_steps'] = sum(1 for r in script_results if r['status'] == 'skipped')
                result_data['total_duration'] = sum(r['duration'] for r in script_results)
                total = result_data['total_steps']
                result_data['pass_rate'] = round((result_data['passed_steps'] / total * 100) if total > 0 else 0, 2)
        else:
            task_results = task.results.all().order_by('step_order')
            script_results = build_script_results(task_results)
            result_data['step_results'] = script_results

            if report:
                result_data['total_steps'] = report.total_steps
                result_data['passed_steps'] = report.passed_steps
                result_data['failed_steps'] = report.failed_steps
                result_data['skipped_steps'] = report.skipped_steps
                result_data['total_duration'] = report.total_duration
                result_data['pass_rate'] = report.pass_rate

        if 'script_name' not in result_data:
            task_scripts = list(task.task_scripts.all().order_by('order'))
            if task_scripts and hasattr(task_scripts[0], 'script'):
                result_data['script_name'] = task_scripts[0].script.name
            else:
                result_data['script_name'] = task.name

        username = get_username()
        if username:
            result_data['username'] = username

        target_url = get_management_platform_url()
        response = requests.post(
            target_url,
            json=result_data,
            timeout=30,
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code in (200, 201):
            logger.info(f"Successfully uploaded result for task {task_id}")
            report_id = None
            try:
                resp_json = response.json()
                report_id = (
                    resp_json.get('report_id')
                    or resp_json.get('id')
                    or resp_json.get('reportId')
                    or resp_json.get('task_id')
                )
                if report_id is not None:
                    report_id = str(report_id)
            except Exception:
                pass
            return True, report_id
        else:
            logger.error(f"Failed to upload result for task {task_id}: {response.status_code} - {response.text}")
            return False, None
    except Exception as e:
        logger.exception(f"Error uploading result for task {task_id}: {e}")
        return False, None


@api_view(['POST'])
@permission_classes([AllowAny])
def trigger_upload(request, task_id):
    task = get_object_or_404(TestTask, pk=task_id)
    
    if task.status not in ('completed', 'failed'):
        return Response({'error': 'Task not completed yet'}, status=status.HTTP_400_BAD_REQUEST)
    
    task.upload_status = 'uploading'
    task.save()
    
    success, report_id = upload_result_to_management(task_id)

    if success:
        task.upload_status = 'uploaded'
        task.save()
        return Response({'message': 'Upload successful', 'task_id': task_id, 'report_id': report_id})
    else:
        task.upload_status = 'failed'
        task.save()
        return Response({'error': 'Upload failed', 'task_id': task_id}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
def task_list(request):
    if request.method == 'GET':
        tasks = TestTask.objects.filter(task_group__isnull=True)
        serializer = TestTaskWithReportListSerializer(tasks, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = TestTaskCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def task_detail(request, pk):
    task = get_object_or_404(TestTask, pk=pk)
    
    if request.method == 'GET':
        if task.script_count > 1:
            results = task.results.all()
            script_names = [ts.script.name for ts in task.task_scripts.all().order_by('order')]
            
            scripts_passed = 0
            scripts_failed = 0
            
            for script_name in script_names:
                script_results = results.filter(step_name__contains=f'[{script_name}]')
                failed_count = script_results.filter(status='failed').count()
                if failed_count == 0 and script_results.exists():
                    scripts_passed += 1
                else:
                    scripts_failed += 1
            
            task.scripts_passed = scripts_passed
            task.scripts_failed = scripts_failed
        else:
            task.scripts_passed = 0
            task.scripts_failed = 0
        
        serializer = TestTaskDetailSerializer(task)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = TestTaskCreateSerializer(task, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        from django.db import transaction
        
        with transaction.atomic():
            # 先删除关联的测试结果和报告
            task.results.all().delete()
            if hasattr(task, 'report'):
                task.report.delete()
            # 清理已废弃的关联记录
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute('DELETE FROM test_manager_taskgroupitem WHERE task_id=%s', [task.id])
            task.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([AllowAny])
def execute_task_view(request, task_id):
    task = get_object_or_404(TestTask, pk=task_id)
    
    if task.status == 'running':
        return Response({
            'error': 'Task is already running'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    parameters = request.data.get('parameters', task.parameters)
    task.parameters = parameters
    
    upload_to_management = request.data.get('upload_to_management', task.upload_to_management)
    send_email = request.data.get('send_email', task.send_email)
    
    task.upload_to_management = upload_to_management
    task.send_email = send_email
    task.status = 'pending'
    task.upload_status = 'pending' if upload_to_management else 'none'
    task.save()
    
    task_scripts = list(task.task_scripts.all().order_by('order'))
    if len(task_scripts) > 1:
        from core.tasks import execute_multi_script_task
        try:
            result = execute_multi_script_task.apply_async([task_id])
            return Response({
                'task_id': task_id,
                'celery_task_id': result.id,
                'status': 'started',
                'message': 'Multi-script task execution started',
                'script_count': len(task_scripts)
            })
        except Exception as e:
            logger.error(f'Celery failed for multi-script task, using sync: {e}')
            from core.tasks import run_multi_script_task_sync
            run_multi_script_task_sync(task_id)
            return Response({
                'task_id': task_id,
                'status': 'started',
                'message': 'Multi-script task execution started (sync mode)',
                'script_count': len(task_scripts)
            })
    else:
        try:
            result = execute_test_task.apply_async([task_id])
            return Response({
                'task_id': task_id,
                'celery_task_id': result.id,
                'status': 'started',
                'message': 'Test task execution started'
            })
        except Exception as e:
            from core.tasks import run_test_task_sync
            run_test_task_sync(task_id)
            return Response({
                'task_id': task_id,
                'status': 'started',
                'message': 'Test task execution started (sync mode)'
            })


@api_view(['POST'])
@permission_classes([AllowAny])
def stop_task(request, task_id):
    task = get_object_or_404(TestTask, pk=task_id)
    
    if task.status != 'running':
        return Response({
            'error': 'Task is not running'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    from celery.result import AsyncResult
    from automation_test_platform.celery import app
    
    if task.celery_task_id:
        app.control.revoke(task.celery_task_id, terminate=True)
    
    task.status = 'cancelled'
    task.finished_at = timezone.now()
    task.save()
    
    return Response({
        'task_id': task_id,
        'status': 'cancelled',
        'message': 'Test task stopped'
    })


@api_view(['GET'])
def result_list(request):
    task_id = request.query_params.get('task_id')
    if task_id:
        results = TestResult.objects.filter(task_id=task_id)
    else:
        results = TestResult.objects.all()
    serializer = TestResultSerializer(results, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def result_detail(request, pk):
    result = get_object_or_404(TestResult, pk=pk)
    serializer = TestResultSerializer(result)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_test_screenshots(request, result_id):
    result = get_object_or_404(TestResult, pk=result_id)
    
    screenshots = []
    if result.screenshot:
        screenshots.append({
            'id': result.id,
            'step_name': result.step_name,
            'url': result.screenshot.url if result.screenshot else None,
        })
    
    return Response({
        'result_id': result_id,
        'screenshots': screenshots
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def export_test_report(request, task_id):
    format_type = request.query_params.get('format', 'json')
    task = get_object_or_404(TestTask, pk=task_id)
    
    exporter = TestResultExporter()
    filepath = exporter.export_report(task_id, format_type)
    
    return Response({
        'task_id': task_id,
        'report_file': str(filepath),
        'format': format_type
    })
