from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.conf import settings
from test_manager.models import TestTask, TestReport
from script_editor.models import TestScript, ElementLocator
from core.models import Group
from core.serializers import GroupSerializer, GroupCreateSerializer
import os
import json
import glob
import logging

logger = logging.getLogger(__name__)

ERROR_CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'error_config.json')

def load_error_config():
    if os.path.exists(ERROR_CONFIG_FILE):
        try:
            with open(ERROR_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_error_config(config_list):
    with open(ERROR_CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config_list, f, ensure_ascii=False, indent=2)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({
        'status': 'ok',
        'message': 'Automation Test Platform is running',
    })


@api_view(['GET'])
def dashboard(request):
    total_tasks = TestTask.objects.count()
    running_tasks = TestTask.objects.filter(status='running').count()
    completed_tasks = TestTask.objects.filter(status='completed').count()
    failed_tasks = TestTask.objects.filter(status='failed').count()
    
    total_scripts = TestScript.objects.count()
    published_scripts = TestScript.objects.filter(status='published').count()
    
    total_elements = ElementLocator.objects.filter(is_active=True).count()
    
    recent_tasks = TestTask.objects.order_by('-created_at')[:5]
    recent_tasks_data = []
    for task in recent_tasks:
        recent_tasks_data.append({
            'id': task.id,
            'name': task.name,
            'status': task.status,
            'created_at': task.created_at,
        })
    
    pass_rate = 0
    reports = TestReport.objects.all()
    total_passed = sum(r.passed_steps for r in reports)
    total_steps = sum(r.total_steps for r in reports)
    if total_steps > 0:
        pass_rate = round((total_passed / total_steps) * 100, 2)
    
    return Response({
        'statistics': {
            'total_tasks': total_tasks,
            'running_tasks': running_tasks,
            'completed_tasks': completed_tasks,
            'failed_tasks': failed_tasks,
            'total_scripts': total_scripts,
            'published_scripts': published_scripts,
            'total_elements': total_elements,
            'pass_rate': pass_rate,
        },
        'recent_tasks': recent_tasks_data,
    })


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def group_list(request):
    if request.method == 'GET':
        group_type = request.query_params.get('type')
        groups = Group.objects.all()
        if group_type:
            groups = groups.filter(type=group_type)
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = GroupCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def group_detail(request, pk):
    group = get_object_or_404(Group, pk=pk)
    
    if request.method == 'GET':
        serializer = GroupSerializer(group)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = GroupCreateSerializer(group, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(GroupSerializer(group).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        if group.children.exists():
            return Response({'error': 'Cannot delete group with children'}, status=status.HTTP_400_BAD_REQUEST)
        group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def clear_screenshots(request):
    screenshots_dir = settings.SCREENSHOTS_DIR
    deleted_count = 0
    if screenshots_dir.exists():
        image_patterns = ['*.png', '*.jpg', '*.jpeg', '*.gif', '*.webp', '*.bmp']
        for pattern in image_patterns:
            for filepath in glob.glob(str(screenshots_dir / pattern)):
                try:
                    os.remove(filepath)
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"Failed to delete screenshot {filepath}: {e}")
    return Response({
        'message': f'成功清理 {deleted_count} 个截图文件',
        'deleted_count': deleted_count,
    }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def clear_task_results(request):
    results_dir = settings.TEST_RESULTS_DIR
    deleted_count = 0
    if results_dir.exists():
        json_files = glob.glob(str(results_dir / '*.json'))
        for filepath in json_files:
            try:
                os.remove(filepath)
                deleted_count += 1
            except Exception as e:
                logger.error(f"Failed to delete result file {filepath}: {e}")
    return Response({
        'message': f'成功清理 {deleted_count} 个任务结果文件',
        'deleted_count': deleted_count,
    }, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def error_config_list(request):
    from core.engines.error_message_manager import error_message_manager
    
    if request.method == 'POST':
        config_list = load_error_config()
        new_id = max([c.get('id', 0) for c in config_list], default=0) + 1
        new_config = {
            'id': new_id,
            'name': request.data.get('name', ''),
            'pattern': request.data.get('pattern', ''),
            'message_template': request.data.get('message_template', ''),
            'action_type': request.data.get('action_type', ''),
        }
        config_list.append(new_config)
        save_error_config(config_list)
        return Response(new_config, status=status.HTTP_201_CREATED)
    
    builtin_rules = error_message_manager.get_all_rules()
    custom_rules = load_error_config()
    
    return Response({
        'builtin_rules': builtin_rules,
        'custom_rules': custom_rules,
    })


@api_view(['PUT'])
@permission_classes([AllowAny])
def update_error_config(request, config_id):
    config_list = load_error_config()
    for i, config in enumerate(config_list):
        if config.get('id') == config_id:
            config_list[i] = {
                'id': config_id,
                'name': request.data.get('name', config.get('name', '')),
                'pattern': request.data.get('pattern', config.get('pattern', '')),
                'message_template': request.data.get('message_template', config.get('message_template', '')),
                'action_type': request.data.get('action_type', config.get('action_type', '')),
            }
            save_error_config(config_list)
            return Response(config_list[i])
    return Response({'error': 'Config not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_error_config(request, config_id):
    config_list = load_error_config()
    new_list = [config for config in config_list if config.get('id') != config_id]
    if len(new_list) == len(config_list):
        return Response({'error': 'Config not found'}, status=status.HTTP_404_NOT_FOUND)
    save_error_config(new_list)
    return Response(status=status.HTTP_204_NO_CONTENT)
