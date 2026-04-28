from rest_framework import serializers
from .models import ElementLocator, TestScript, ScriptVersion, TestStep, GlobalConfig


class ElementLocatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElementLocator
        fields = [
            'id', 'name', 'code', 'locator_type', 'locator_value',
            'page_url', 'description', 'wait_timeout', 'wait_state',
            'is_active', 'created_at', 'updated_at'
        ]


class TestStepSerializer(serializers.ModelSerializer):
    element_name = serializers.CharField(source='element.name', read_only=True, allow_null=True)
    element_locator_type = serializers.CharField(source='element.locator_type', read_only=True, allow_null=True)
    element_locator_value = serializers.CharField(source='element.locator_value', read_only=True, allow_null=True)
    action_set_name = serializers.CharField(source='action_set_ref.name', read_only=True, allow_null=True)
    
    class Meta:
        model = TestStep
        fields = [
            'id', 'script', 'name', 'order', 'action_type',
            'element', 'element_name', 'element_locator_type', 'element_locator_value',
            'action_value', 'action_config',
            'description', 'is_enabled', 'continue_on_failure',
            'retry_count', 'retry_interval', 'action_set_ref', 'action_set_name', 'action_set_params',
            'created_at', 'updated_at'
        ]


class TestStepNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestStep
        fields = [
            'name', 'order', 'action_type', 'element', 'action_value', 
            'action_config', 'description', 'is_enabled', 
            'continue_on_failure', 'retry_count', 'retry_interval',
            'action_set_ref', 'action_set_params'
        ]


class TestScriptListSerializer(serializers.ModelSerializer):
    steps_count = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True, allow_null=True)
    group_name = serializers.CharField(source='group.name', read_only=True, allow_null=True)
    
    class Meta:
        model = TestScript
        fields = [
            'id', 'name', 'code', 'description',
            'status', 'status_display', 'version', 'target_url', 'steps_count',
            'group', 'group_name',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
    
    def get_steps_count(self, obj):
        return obj.steps.count()


class TestScriptDetailSerializer(serializers.ModelSerializer):
    steps = TestStepSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True, allow_null=True)
    group_name = serializers.CharField(source='group.name', read_only=True, allow_null=True)
    
    class Meta:
        model = TestScript
        fields = [
            'id', 'name', 'code', 'description',
            'status', 'status_display', 'version', 'target_url', 'script_data',
            'steps', 'group', 'group_name',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]


class TestScriptCreateSerializer(serializers.ModelSerializer):
    steps = TestStepNestedSerializer(many=True, required=False)
    
    class Meta:
        model = TestScript
        fields = [
            'id', 'name', 'code', 'description',
            'status', 'target_url', 'group', 'steps'
        ]
    
    def create(self, validated_data):
        steps_data = validated_data.pop('steps', [])
        script = TestScript.objects.create(**validated_data)
        
        for step_data in steps_data:
            TestStep.objects.create(script=script, **step_data)
        
        return script
    
    def update(self, instance, validated_data):
        steps_data = validated_data.pop('steps', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if 'status' in validated_data and validated_data['status'] == 'published':
            instance.version += 1
        
        instance.save()
        
        if steps_data is not None:
            instance.steps.all().delete()
            for step_data in steps_data:
                TestStep.objects.create(script=instance, **step_data)
        
        return instance


class ScriptVersionSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True, allow_null=True)
    
    class Meta:
        model = ScriptVersion
        fields = [
            'id', 'script', 'version_number', 'script_data',
            'change_note', 'created_by', 'created_by_name', 'created_at'
        ]


class TestStepCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestStep
        fields = [
            'id', 'script', 'name', 'order', 'action_type',
            'element', 'action_value', 'action_config',
            'description', 'is_enabled', 'continue_on_failure',
            'retry_count', 'retry_interval'
        ]


class VisualScriptSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    code = serializers.CharField(max_length=50)
    description = serializers.CharField(required=False, allow_blank=True, default='')
    product_type_id = serializers.IntegerField(required=False, allow_null=True)
    target_url = serializers.URLField()
    steps = serializers.ListField(
        child=serializers.DictField(),
        allow_empty=False
    )
    parameters = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list
    )


class GlobalConfigSerializer(serializers.ModelSerializer):
    updated_by_name = serializers.CharField(source='updated_by.username', read_only=True, allow_null=True)
    
    class Meta:
        model = GlobalConfig
        fields = [
            'id', 'headless_mode', 'default_timeout', 'step_screenshot',
            'slow_mo', 'viewport_width', 'viewport_height',
            'scroll_distance', 'scroll_direction', 'marketplace_api_url',
            'management_platform_url', 'username',
            'email_smtp_host', 'email_smtp_port', 'email_username', 'email_password',
            'email_use_ssl', 'email_recipients', 'email_enable', 'report_base_url',
            'updated_at', 'updated_by', 'updated_by_name'
        ]


class ScriptExportSerializer(serializers.Serializer):
    script_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
    )
    format = serializers.ChoiceField(choices=['json', 'excel'], default='json')


class ScriptImportSerializer(serializers.Serializer):
    format = serializers.ChoiceField(choices=['json', 'excel', 'auto'], default='auto')
    conflict_strategy = serializers.ChoiceField(
        choices=['skip', 'overwrite', 'rename'],
        default='skip',
    )


class ScriptImportResultSerializer(serializers.Serializer):
    success = serializers.IntegerField()
    failed = serializers.IntegerField()
    skipped = serializers.IntegerField()
    errors = serializers.ListField(child=serializers.DictField())
    action_sets_created = serializers.IntegerField()
    action_sets_skipped = serializers.IntegerField()
    action_sets_overwritten = serializers.IntegerField()
    scripts_created = serializers.IntegerField()
    scripts_skipped = serializers.IntegerField()
    scripts_overwritten = serializers.IntegerField()
    elements_created = serializers.IntegerField()
    elements_reused = serializers.IntegerField()
