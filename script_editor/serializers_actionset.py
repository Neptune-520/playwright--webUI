from rest_framework import serializers
from .models import (
    ActionSet, ActionSetStep, ActionSetParameter
)


class ActionSetParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActionSetParameter
        fields = ['id', 'name', 'code', 'description', 'default_value', 'is_required', 'order']


class ActionSetStepSerializer(serializers.ModelSerializer):
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)
    locator_type_display = serializers.CharField(source='get_locator_type_display', read_only=True)
    action_value_type_display = serializers.CharField(source='get_action_value_type_display', read_only=True)
    select_mode_display = serializers.CharField(source='get_select_mode_display', read_only=True)
    
    class Meta:
        model = ActionSetStep
        fields = [
            'id', 'action_set', 'name', 'order', 'action_type', 'action_type_display',
            'locator_type', 'locator_type_display', 'locator_value', 'locator_description',
            'action_value', 'action_value_type', 'action_value_type_display', 'parameter_name',
            'action_config',
            'wait_timeout', 'continue_on_failure', 'retry_count', 'retry_interval',
            'random_options', 'select_mode', 'select_mode_display',
            'random_min', 'random_max', 'force_click',
            'description', 'is_enabled', 'created_at', 'updated_at'
        ]


class ActionSetStepNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActionSetStep
        fields = [
            'name', 'order', 'action_type',
            'locator_type', 'locator_value', 'locator_description',
            'action_value', 'action_value_type', 'parameter_name',
            'action_config',
            'wait_timeout', 'continue_on_failure', 'retry_count', 'retry_interval',
            'random_options', 'select_mode', 'random_min', 'random_max', 'force_click',
            'description', 'is_enabled'
        ]


class ActionSetListSerializer(serializers.ModelSerializer):
    steps_count = serializers.SerializerMethodField()
    parameters_count = serializers.SerializerMethodField()
    used_scripts_count = serializers.SerializerMethodField()
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True, allow_null=True)
    group_name = serializers.CharField(source='group.name', read_only=True, allow_null=True)
    
    class Meta:
        model = ActionSet
        fields = [
            'id', 'name', 'code', 'description', 'category', 'category_display',
            'is_builtin', 'is_active', 'steps_count', 'parameters_count', 'used_scripts_count',
            'group', 'group_name',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
    
    def get_steps_count(self, obj):
        return obj.steps.count()
    
    def get_parameters_count(self, obj):
        return obj.parameters.count()
    
    def get_used_scripts_count(self, obj):
        from script_editor.models import TestStep
        return TestStep.objects.filter(action_set_ref=obj).values_list('script', flat=True).distinct().count()


class ActionSetDetailSerializer(serializers.ModelSerializer):
    steps = ActionSetStepSerializer(many=True, read_only=True)
    parameters = ActionSetParameterSerializer(many=True, read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True, allow_null=True)
    group_name = serializers.CharField(source='group.name', read_only=True, allow_null=True)
    
    class Meta:
        model = ActionSet
        fields = [
            'id', 'name', 'code', 'description', 'category', 'category_display',
            'is_builtin', 'is_active', 'steps', 'parameters',
            'group', 'group_name',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]


class ActionSetCreateSerializer(serializers.ModelSerializer):
    steps = ActionSetStepNestedSerializer(many=True, required=False)
    parameters = ActionSetParameterSerializer(many=True, required=False)
    
    class Meta:
        model = ActionSet
        fields = [
            'id', 'name', 'code', 'description', 'category',
            'is_active', 'group', 'steps', 'parameters'
        ]
    
    def to_internal_value(self, data):
        ret = super().to_internal_value(data)
        if ret.get('group') == '':
            ret['group'] = None
        return ret
    
    def create(self, validated_data):
        steps_data = validated_data.pop('steps', [])
        parameters_data = validated_data.pop('parameters', [])
        
        action_set = ActionSet.objects.create(**validated_data)
        
        for i, step_data in enumerate(steps_data):
            if 'order' not in step_data:
                step_data['order'] = i
            ActionSetStep.objects.create(action_set=action_set, **step_data)
        
        for i, param_data in enumerate(parameters_data):
            if 'order' not in param_data:
                param_data['order'] = i
            ActionSetParameter.objects.create(action_set=action_set, **param_data)
        
        return action_set
    
    def update(self, instance, validated_data):
        steps_data = validated_data.pop('steps', None)
        parameters_data = validated_data.pop('parameters', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if steps_data is not None:
            instance.steps.all().delete()
            for i, step_data in enumerate(steps_data):
                if 'order' not in step_data:
                    step_data['order'] = i
                ActionSetStep.objects.create(action_set=instance, **step_data)
        
        if parameters_data is not None:
            instance.parameters.all().delete()
            for i, param_data in enumerate(parameters_data):
                if 'order' not in param_data:
                    param_data['order'] = i
                ActionSetParameter.objects.create(action_set=instance, **param_data)
        
        return instance
