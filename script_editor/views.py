from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.http import HttpResponse
from .models import ElementLocator, TestScript, ScriptVersion, TestStep, GlobalConfig
from .serializers import (
    ElementLocatorSerializer, TestScriptListSerializer, TestScriptDetailSerializer,
    TestScriptCreateSerializer, ScriptVersionSerializer, TestStepSerializer,
    TestStepCreateSerializer, GlobalConfigSerializer, ScriptExportSerializer,
    ScriptImportSerializer
)
from .services import ScriptExportImportService
from .recording import RecordingSessionManager
from core.script_manager import ScriptManager
from .models import ActionSet, ActionSetStep, ActionSetParameter
from core.models import Group
import copy
import json


@api_view(['GET', 'POST'])
def script_list(request):
    if request.method == 'GET':
        scripts = TestScript.objects.all()
        serializer = TestScriptListSerializer(scripts, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = TestScriptCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user if request.user.is_authenticated else None)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def script_detail(request, pk):
    script = get_object_or_404(TestScript, pk=pk)
    
    if request.method == 'GET':
        serializer = TestScriptDetailSerializer(script)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = TestScriptCreateSerializer(script, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(TestScriptDetailSerializer(script).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        script.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([AllowAny])
def duplicate_script(request, script_id):
    original_script = get_object_or_404(TestScript, pk=script_id)
    
    original_steps = list(original_script.steps.all())
    
    new_script = TestScript.objects.create(
        name=f"{original_script.name} (Copy)",
        code=f"{original_script.code}_copy_{int(timezone.now().timestamp())}",
        description=original_script.description,
        status='draft',
        version=1,
        target_url=original_script.target_url,
        script_data=copy.deepcopy(original_script.script_data),
        created_by=request.user if request.user.is_authenticated else original_script.created_by,
    )
    
    for step in original_steps:
        TestStep.objects.create(
            script=new_script,
            name=step.name,
            order=step.order,
            action_type=step.action_type,
            element=step.element,
            action_value=step.action_value,
            action_config=copy.deepcopy(step.action_config),
            description=step.description,
            is_enabled=step.is_enabled,
            continue_on_failure=step.continue_on_failure,
            retry_count=step.retry_count,
            retry_interval=step.retry_interval,
        )
    
    return Response({
        'id': new_script.id,
        'name': new_script.name,
        'code': new_script.code,
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def script_versions(request, script_id):
    versions = ScriptVersion.objects.filter(script_id=script_id).order_by('-version_number')
    serializer = ScriptVersionSerializer(versions, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def script_version_detail(request, script_id, version_id):
    version = get_object_or_404(ScriptVersion, script_id=script_id, pk=version_id)
    serializer = ScriptVersionSerializer(version)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
def element_list(request):
    if request.method == 'GET':
        elements = ElementLocator.objects.all()
        serializer = ElementLocatorSerializer(elements, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = ElementLocatorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def element_detail(request, pk):
    element = get_object_or_404(ElementLocator, pk=pk)
    
    if request.method == 'GET':
        serializer = ElementLocatorSerializer(element)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = ElementLocatorSerializer(element, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        element.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def step_list(request):
    if request.method == 'GET':
        steps = TestStep.objects.all()
        serializer = TestStepSerializer(steps, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = TestStepCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def step_detail(request, pk):
    step = get_object_or_404(TestStep, pk=pk)
    
    if request.method == 'GET':
        serializer = TestStepSerializer(step)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = TestStepCreateSerializer(step, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        step.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def visual_editor(request):
    if request.method == 'GET':
        action_types = [
            {'value': choice[0], 'label': choice[1]}
            for choice in TestStep.ACTION_TYPE_CHOICES
        ]
        
        locator_types = [
            {'value': choice[0], 'label': choice[1]}
            for choice in ElementLocator.LOCATOR_TYPE_CHOICES
        ]
        
        return Response({
            'action_types': action_types,
            'locator_types': locator_types,
        })
    
    elif request.method == 'POST':
        from .serializers import VisualScriptSerializer
        
        serializer = VisualScriptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        script = TestScript.objects.create(
            name=data['name'],
            code=data['code'],
            description=data.get('description', ''),
            target_url=data['target_url'],
            script_data={
                'steps': data['steps'],
                'parameters': data.get('parameters', []),
            },
            created_by=request.user if request.user.is_authenticated else None,
        )
        
        for i, step_data in enumerate(data['steps']):
            TestStep.objects.create(
                script=script,
                name=step_data.get('name', f'Step {i+1}'),
                order=i,
                action_type=step_data['action_type'],
                element=None,
                action_value=step_data.get('value', ''),
                action_config=step_data.get('config', {}),
                description=step_data.get('description', ''),
                is_enabled=step_data.get('is_enabled', True),
                continue_on_failure=step_data.get('continue_on_failure', False),
                retry_count=step_data.get('retry_count', 0),
                retry_interval=step_data.get('retry_interval', 1000),
            )
        
        return Response({
            'id': script.id,
            'name': script.name,
            'code': script.code,
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def validate_script(request):
    script_data = request.data
    
    manager = ScriptManager()
    result = manager.validate_script(script_data)
    
    return Response(result)


@api_view(['POST'])
@permission_classes([AllowAny])
def recording_start(request):
    target_url = request.data.get('target_url', '').strip()
    if not target_url:
        return Response(
            {'error': '请输入目标网址'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not target_url.startswith(('http://', 'https://')):
        target_url = 'https://' + target_url

    viewport_width = request.data.get('viewport_width', 1920)
    viewport_height = request.data.get('viewport_height', 1080)

    try:
        session_id = RecordingSessionManager.create_session(
            target_url=target_url,
            user=request.user if request.user.is_authenticated else None,
            viewport_width=int(viewport_width),
            viewport_height=int(viewport_height),
        )
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_409_CONFLICT,
        )
    except Exception as e:
        return Response(
            {'error': f'启动录制失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response({
        'session_id': session_id,
        'status': 'starting',
        'target_url': target_url,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def recording_actions(request, session_id):
    data = RecordingSessionManager.get_session_actions(session_id)
    if data is None:
        return Response(
            {'error': '录制会话不存在'},
            status=status.HTTP_404_NOT_FOUND,
        )
    return Response(data)


@api_view(['POST'])
@permission_classes([AllowAny])
def recording_stop(request, session_id):
    actions = RecordingSessionManager.stop_session(session_id)
    if actions is None:
        return Response(
            {'error': '录制会话不存在'},
            status=status.HTTP_404_NOT_FOUND,
        )
    return Response({
        'session_id': session_id,
        'status': 'stopped',
        'action_count': len(actions),
        'actions': actions,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def recording_convert(request, session_id):
    session_data = RecordingSessionManager.get_session_actions(session_id)
    if session_data is None:
        return Response(
            {'error': '录制会话不存在'},
            status=status.HTTP_404_NOT_FOUND,
        )

    actions = session_data.get('actions', [])
    if not actions:
        return Response(
            {'error': '没有录制的操作可转换'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    mode = request.data.get('mode', 'script')
    name = request.data.get('name', '')
    code = request.data.get('code', '')
    user = request.user if request.user.is_authenticated else None

    try:
        if mode == 'action_set':
            result = _convert_to_action_set(actions, name, code, user, request.data)
        else:
            result = _convert_to_script(actions, name, code, user, request.data)
    except Exception as e:
        return Response(
            {'error': f'转换失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    RecordingSessionManager.cleanup_session(session_id)
    return Response(result)


def _convert_to_action_set(actions, name, code, user, data):
    if not name:
        name = f"录制动作集合_{timezone.now().strftime('%Y%m%d%H%M')}"
    if not code:
        code = f"rec_{timezone.now().strftime('%Y%m%d%H%M%S')}"

    category = data.get('category', 'general')
    group_code = data.get('group_code')
    group = Group.objects.filter(code=group_code, type='action_set').first() if group_code else None

    action_set = ActionSet.objects.create(
        name=name,
        code=code,
        description=f"通过录制生成的动作集合",
        category=category,
        is_builtin=False,
        is_active=True,
        group=group,
        created_by=user,
    )

    for i, action in enumerate(actions):
        locator_type = ''
        locator_value = ''
        locator_description = ''
        action_config = {}
        if action.get('locators') and action['action_type'] not in ('navigate', 'scroll'):
            locators = action['locators']
            if locators:
                action_config['locators'] = [
                    {
                        'locator_type': loc.get('locator_type', 'css'),
                        'locator_value': loc.get('locator_value', ''),
                        'locator_description': loc.get('locator_description', ''),
                    }
                    for loc in locators
                ]
                locator_type = locators[0].get('locator_type', 'css')
                locator_value = locators[0].get('locator_value', '')
                locator_description = locators[0].get('locator_description', '')

        if action.get('random_options'):
            action_config['random_options'] = action['random_options']
            action_config['select_mode'] = action.get('select_mode', 'dropdown')
        if action.get('random_min') is not None:
            action_config['random_min'] = action['random_min']
            action_config['random_max'] = action['random_max']

        ActionSetStep.objects.create(
            action_set=action_set,
            name=action.get('description', f'步骤{i+1}'),
            order=i,
            action_type=action['action_type'],
            locator_type=locator_type,
            locator_value=locator_value,
            locator_description=locator_description,
            action_value=action.get('value', ''),
            action_value_type='static',
            parameter_name='',
            action_config=action_config,
            wait_timeout=10000,
            continue_on_failure=False,
            retry_count=0,
            retry_interval=1000,
            is_enabled=True,
        )

    return {
        'mode': 'action_set',
        'id': action_set.id,
        'name': action_set.name,
        'code': action_set.code,
        'step_count': len(actions),
    }


def _convert_to_script(actions, name, code, user, data):
    if not name:
        name = f"录制脚本_{timezone.now().strftime('%Y%m%d%H%M')}"
    if not code:
        code = f"rec_{timezone.now().strftime('%Y%m%d%H%M%S')}"

    target_url = data.get('target_url', '')
    group_code = data.get('group_code')
    group = Group.objects.filter(code=group_code, type='script').first() if group_code else None

    script = TestScript.objects.create(
        name=name,
        code=code,
        description=f"通过录制生成的脚本",
        status='draft',
        version=1,
        target_url=target_url,
        script_data={},
        group=group,
        created_by=user,
    )

    for i, action in enumerate(actions):
        element = None
        action_config = {}
        if action.get('locators') and action['action_type'] not in ('navigate', 'scroll'):
            locators = action['locators']
            if locators:
                action_config['locators'] = [
                    {
                        'locator_type': loc.get('locator_type', 'css'),
                        'locator_value': loc.get('locator_value', ''),
                    }
                    for loc in locators
                ]

                locator_type = locators[0].get('locator_type', 'css')
                locator_value = locators[0].get('locator_value', '')
                locator_desc = locators[0].get('locator_description', '')

                existing = ElementLocator.objects.filter(
                    locator_type=locator_type,
                    locator_value=locator_value,
                ).first()
                if existing:
                    element = existing
                else:
                    element = ElementLocator.objects.create(
                        name=locator_desc or f"元素_{i+1}",
                        code=f"rec_elem_{timezone.now().strftime('%Y%m%d%H%M%S')}_{i}",
                        locator_type=locator_type,
                        locator_value=locator_value,
                        page_url=target_url,
                        description=locator_desc,
                        wait_timeout=10000,
                        wait_state='visible',
                        is_active=True,
                        created_by=user,
                    )

        action_value = action.get('value', '')
        if action['action_type'] == 'select' and action.get('display_value'):
            action_value = action.get('display_value', action_value)

        TestStep.objects.create(
            script=script,
            name=action.get('description', f'步骤{i+1}'),
            order=i,
            action_type=action['action_type'],
            element=element,
            action_value=action_value,
            action_config=action_config,
            action_set_ref=None,
            action_set_params={},
            description='',
            is_enabled=True,
            continue_on_failure=False,
            retry_count=0,
            retry_interval=1000,
        )

    return {
        'mode': 'script',
        'id': script.id,
        'name': script.name,
        'code': script.code,
        'step_count': len(actions),
    }


@api_view(['GET', 'PUT'])
def global_config(request):
    config = GlobalConfig.get_config()
    
    if request.method == 'GET':
        serializer = GlobalConfigSerializer(config)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = GlobalConfigSerializer(config, data=request.data)
        if serializer.is_valid():
            serializer.save(updated_by=request.user if request.user.is_authenticated else None)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def export_scripts(request):
    serializer = ScriptExportSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    script_ids = serializer.validated_data['script_ids']
    export_format = serializer.validated_data['format']

    service = ScriptExportImportService()

    if export_format == 'json':
        data = service.export_scripts_to_json(script_ids)
        return Response(data)
    elif export_format == 'excel':
        wb = service.export_scripts_to_excel(script_ids)
        from io import BytesIO
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename="scripts_export.xlsx"'
        return response


@api_view(['GET'])
@permission_classes([AllowAny])
def export_script_detail(request, pk):
    script = get_object_or_404(TestScript, pk=pk)
    export_format = request.query_params.get('export_format', 'json')

    service = ScriptExportImportService()

    if export_format == 'json':
        data = service.export_scripts_to_json([script.id])
        return Response(data)
    elif export_format == 'excel':
        wb = service.export_scripts_to_excel([script.id])
        from io import BytesIO
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = f'attachment; filename="script_{script.code}_export.xlsx"'
        return response
    else:
        return Response(
            {'error': f'不支持的导出格式: {export_format}'},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def import_scripts(request):
    file_obj = request.FILES.get('file')
    if not file_obj:
        return Response(
            {'error': '请上传文件'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    conflict_strategy = request.data.get('conflict_strategy', 'skip')
    if conflict_strategy not in ['skip', 'overwrite', 'rename']:
        return Response(
            {'error': '无效的冲突处理策略'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    file_format = request.data.get('format', 'auto')
    filename = file_obj.name.lower()

    if file_format == 'auto':
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            file_format = 'excel'
        elif filename.endswith('.json'):
            file_format = 'json'
        else:
            return Response(
                {'error': '无法识别文件格式，请指定format参数(json/excel)'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    service = ScriptExportImportService()
    user = request.user if request.user.is_authenticated else None

    try:
        if file_format == 'json':
            file_data = file_obj.read()
            result = service.import_scripts_from_json(file_data, conflict_strategy, user)
        elif file_format == 'excel':
            file_data = file_obj.read()
            result = service.import_scripts_from_excel(file_data, conflict_strategy, user)
        else:
            return Response(
                {'error': f'不支持的导入格式: {file_format}'},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except Exception as e:
        return Response(
            {'error': f'导入处理异常: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(result)
