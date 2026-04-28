from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import ActionSet, ActionSetStep, ActionSetParameter
from .serializers_actionset import (
    ActionSetListSerializer, ActionSetDetailSerializer, ActionSetCreateSerializer,
    ActionSetStepSerializer, ActionSetParameterSerializer
)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def action_set_list(request):
    if request.method == 'GET':
        category = request.query_params.get('category')
        action_sets = ActionSet.objects.filter(is_active=True)
        if category:
            action_sets = action_sets.filter(category=category)
        serializer = ActionSetListSerializer(action_sets, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = ActionSetCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user if request.user.is_authenticated else None)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def action_set_export(request, pk):
    action_set = get_object_or_404(ActionSet, pk=pk)
    serializer = ActionSetDetailSerializer(action_set)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def action_set_batch_export(request):
    ids = request.data.get('ids', [])
    if not ids:
        return Response({'error': '请提供要导出的动作集合ID列表'}, status=status.HTTP_400_BAD_REQUEST)
    
    action_sets = ActionSet.objects.filter(id__in=ids)
    serializer = ActionSetDetailSerializer(action_sets, many=True)
    
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def action_set_import(request):
    import_data = request.data
    if not isinstance(import_data, list):
        import_data = [import_data]
    
    success_count = 0
    skipped_count = 0
    errors = []
    
    # 导出时使用了ActionSetStepSerializer（包含只读显示字段）
    # 导入时需要清理这些字段，使其符合ActionSetStepNestedSerializer格式
    step_readonly_fields = [
        'id', 'action_set', 'action_type_display', 'locator_type_display',
        'action_value_type_display', 'select_mode_display', 'created_at', 'updated_at'
    ]
    param_readonly_fields = [
        'id', 'action_set', 'created_at', 'updated_at'
    ]
    # 动作集合的只读字段
    actionset_readonly_fields = [
        'id', 'created_at', 'updated_at', 'created_by', 'created_by_name',
        'category_display', 'group_name', 'is_builtin', 'steps_count', 'parameters_count'
    ]
    
    for idx, item in enumerate(import_data):
        try:
            if not isinstance(item, dict):
                errors.append({'item': f'第{idx+1}项', 'error': '数据格式错误，应为JSON对象'})
                skipped_count += 1
                continue
                
            item_copy = item.copy()
            code = item_copy.get('code')
            if not code:
                errors.append({'item': item_copy.get('name', f'第{idx+1}项'), 'error': '缺少code字段'})
                skipped_count += 1
                continue
            
            # 如果code已存在，跳过该项
            if ActionSet.objects.filter(code=code).exists():
                skipped_count += 1
                continue
            
            # 提取并清理步骤数据
            steps_data = item_copy.pop('steps', [])
            if isinstance(steps_data, list):
                cleaned_steps = []
                for step in steps_data:
                    if isinstance(step, dict):
                        cleaned_step = {k: v for k, v in step.items() if k not in step_readonly_fields}
                        cleaned_steps.append(cleaned_step)
                steps_data = cleaned_steps
            
            # 提取并清理参数数据
            parameters_data = item_copy.pop('parameters', [])
            if isinstance(parameters_data, list):
                cleaned_params = []
                for param in parameters_data:
                    if isinstance(param, dict):
                        cleaned_param = {k: v for k, v in param.items() if k not in param_readonly_fields}
                        cleaned_params.append(cleaned_param)
                parameters_data = cleaned_params
            
            # 清理动作集合的只读字段
            for field in actionset_readonly_fields:
                item_copy.pop(field, None)
            
            # 处理group字段：如果是空字符串则设为None
            if item_copy.get('group') == '':
                item_copy['group'] = None
            
            # 重新添加清理后的steps和parameters数据
            item_copy['steps'] = steps_data
            item_copy['parameters'] = parameters_data
            
            serializer = ActionSetCreateSerializer(data=item_copy)
            if serializer.is_valid():
                serializer.save(created_by=request.user if request.user.is_authenticated else None)
                success_count += 1
            else:
                error_details = serializer.errors
                errors.append({'item': item_copy.get('name', code), 'error': error_details})
                skipped_count += 1
        except Exception as e:
            errors.append({'item': item.get('name', f'第{idx+1}项'), 'error': str(e)})
            skipped_count += 1
    
    return Response({
        'message': f'导入完成：成功 {success_count} 个，跳过 {skipped_count} 个',
        'success_count': success_count,
        'skipped_count': skipped_count,
        'errors': errors
    })


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def action_set_detail(request, pk):
    action_set = get_object_or_404(ActionSet, pk=pk)
    
    if request.method == 'GET':
        serializer = ActionSetDetailSerializer(action_set)
        return Response(serializer.data)
    elif request.method == 'PUT':
        if action_set.is_builtin:
            return Response({'error': 'Cannot modify builtin action set'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ActionSetCreateSerializer(action_set, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(ActionSetDetailSerializer(action_set).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        if action_set.is_builtin:
            return Response({'error': 'Cannot delete builtin action set'}, status=status.HTTP_400_BAD_REQUEST)
        action_set.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([AllowAny])
def action_set_expand(request, pk):
    action_set = get_object_or_404(ActionSet, pk=pk, is_active=True)
    parameters = request.data.get('parameters', {})
    expanded_steps = action_set.expand_to_steps(parameters)
    
    return Response({
        'action_set': {'id': action_set.id, 'name': action_set.name, 'code': action_set.code},
        'steps': expanded_steps,
        'parameters_used': parameters,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def action_set_categories(request):
    categories = ActionSet.objects.filter(is_active=True).values_list('category', flat=True).distinct()
    return Response(list(categories))


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def action_set_step_list(request, action_set_id):
    action_set = get_object_or_404(ActionSet, pk=action_set_id)
    
    if request.method == 'GET':
        steps = action_set.steps.all()
        serializer = ActionSetStepSerializer(steps, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        if action_set.is_builtin:
            return Response({'error': 'Cannot modify builtin action set'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ActionSetStepSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(action_set=action_set)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def action_set_step_detail(request, pk):
    step = get_object_or_404(ActionSetStep, pk=pk)
    
    if request.method == 'GET':
        serializer = ActionSetStepSerializer(step)
        return Response(serializer.data)
    elif request.method == 'PUT':
        if step.action_set.is_builtin:
            return Response({'error': 'Cannot modify builtin action set'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ActionSetStepSerializer(step, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        if step.action_set.is_builtin:
            return Response({'error': 'Cannot modify builtin action set'}, status=status.HTTP_400_BAD_REQUEST)
        step.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([AllowAny])
def action_set_step_reorder(request, action_set_id):
    action_set = get_object_or_404(ActionSet, pk=action_set_id)
    if action_set.is_builtin:
        return Response({'error': 'Cannot modify builtin action set'}, status=status.HTTP_400_BAD_REQUEST)
    
    step_orders = request.data.get('steps', [])
    for item in step_orders:
        step_id = item.get('id')
        new_order = item.get('order')
        if step_id is not None and new_order is not None:
            ActionSetStep.objects.filter(pk=step_id, action_set=action_set).update(order=new_order)
    return Response({'message': 'Steps reordered successfully'})


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def action_set_parameter_list(request, action_set_id):
    action_set = get_object_or_404(ActionSet, pk=action_set_id)
    
    if request.method == 'GET':
        parameters = action_set.parameters.all()
        serializer = ActionSetParameterSerializer(parameters, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        if action_set.is_builtin:
            return Response({'error': 'Cannot modify builtin action set'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ActionSetParameterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(action_set=action_set)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def action_set_parameter_detail(request, pk):
    parameter = get_object_or_404(ActionSetParameter, pk=pk)
    
    if request.method == 'GET':
        serializer = ActionSetParameterSerializer(parameter)
        return Response(serializer.data)
    elif request.method == 'PUT':
        if parameter.action_set.is_builtin:
            return Response({'error': 'Cannot modify builtin action set'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ActionSetParameterSerializer(parameter, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        if parameter.action_set.is_builtin:
            return Response({'error': 'Cannot modify builtin action set'}, status=status.HTTP_400_BAD_REQUEST)
        parameter.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
