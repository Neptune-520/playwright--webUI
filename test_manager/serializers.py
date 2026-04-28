from rest_framework import serializers
from .models import TestTask, TestResult, TestReport, TaskGroup, TaskGroupItem, TaskScript


class TaskScriptSerializer(serializers.ModelSerializer):
    script_name = serializers.CharField(source='script.name', read_only=True)
    script_code = serializers.CharField(source='script.code', read_only=True)
    
    class Meta:
        model = TaskScript
        fields = ['id', 'script', 'script_name', 'script_code', 'order', 'parameters']


class TestResultSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    original_error_message = serializers.CharField(source='error_stack', read_only=True)
    
    class Meta:
        model = TestResult
        fields = [
            'id', 'task', 'step_name', 'step_order', 'status', 'status_display',
            'duration', 'error_message', 'error_stack', 'original_error_message', 'screenshot', 'action_values', 
            'logs', 'created_at'
        ]


class TestReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestReport
        fields = [
            'id', 'task', 'total_steps', 'passed_steps', 'failed_steps',
            'skipped_steps', 'total_duration', 'summary', 'pass_rate', 'created_at'
        ]


class TestTaskListSerializer(serializers.ModelSerializer):
    script_name = serializers.CharField(source='script.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True, allow_null=True)
    group_name = serializers.CharField(source='group.name', read_only=True, allow_null=True)
    results_count = serializers.SerializerMethodField()
    report = TestReportSerializer(read_only=True)
    script_count = serializers.ReadOnlyField()
    task_scripts = TaskScriptSerializer(many=True, read_only=True)
    
    class Meta:
        model = TestTask
        fields = [
            'id', 'name', 'script', 'script_name', 'status', 'status_display',
            'group', 'group_name', 'script_count', 'task_scripts',
            'scheduled_time', 'started_at', 'finished_at',
            'created_by', 'created_by_name', 'results_count', 'report', 'created_at', 'updated_at'
        ]
    
    def get_results_count(self, obj):
        return obj.results.count()


class TestTaskWithReportListSerializer(serializers.ModelSerializer):
    script_name = serializers.CharField(source='script.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True, allow_null=True)
    group_name = serializers.CharField(source='group.name', read_only=True, allow_null=True)
    results_count = serializers.SerializerMethodField()
    report = TestReportSerializer(read_only=True)
    script_count = serializers.ReadOnlyField()
    task_scripts = TaskScriptSerializer(many=True, read_only=True)
    
    class Meta:
        model = TestTask
        fields = [
            'id', 'name', 'script', 'script_name', 'status', 'status_display',
            'group', 'group_name', 'script_count', 'task_scripts',
            'scheduled_time', 'started_at', 'finished_at',
            'created_by', 'created_by_name', 'results_count', 'report', 'created_at', 'updated_at'
        ]
    
    def get_results_count(self, obj):
        return obj.results.count()


class TestTaskDetailSerializer(serializers.ModelSerializer):
    script_name = serializers.CharField(source='script.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True, allow_null=True)
    group_name = serializers.CharField(source='group.name', read_only=True, allow_null=True)
    results = TestResultSerializer(many=True, read_only=True)
    report = TestReportSerializer(read_only=True)
    script_count = serializers.ReadOnlyField()
    task_scripts = TaskScriptSerializer(many=True, read_only=True)
    upload_status_display = serializers.CharField(source='get_upload_status_display', read_only=True)
    scripts_passed = serializers.SerializerMethodField()
    scripts_failed = serializers.SerializerMethodField()
    
    class Meta:
        model = TestTask
        fields = [
            'id', 'name', 'script', 'script_name', 'status', 'status_display',
            'parameters', 'group', 'group_name', 'script_count', 'task_scripts',
            'scheduled_time', 'started_at', 'finished_at',
            'celery_task_id', 'created_by', 'created_by_name',
            'upload_to_management', 'upload_status', 'upload_status_display',
            'scripts_passed', 'scripts_failed',
            'results', 'report', 'created_at', 'updated_at'
        ]
    
    def get_scripts_passed(self, obj):
        return getattr(obj, 'scripts_passed', 0)
    
    def get_scripts_failed(self, obj):
        return getattr(obj, 'scripts_failed', 0)


class TestTaskCreateSerializer(serializers.ModelSerializer):
    scripts = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=True,
        help_text='脚本ID列表，支持单选或多选'
    )
    upload_to_management = serializers.BooleanField(required=False, default=False)
    
    class Meta:
        model = TestTask
        fields = ['id', 'name', 'scripts', 'parameters', 'group', 'scheduled_time', 'upload_to_management']
    
    def create(self, validated_data):
        scripts = validated_data.pop('scripts')
        request = self.context.get('request')
        user = None
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
        
        from script_editor.models import TestScript
        first_script = TestScript.objects.get(pk=scripts[0])
        
        task = TestTask.objects.create(
            name=validated_data['name'],
            script=first_script,
            parameters=validated_data.get('parameters', {}),
            group=validated_data.get('group'),
            scheduled_time=validated_data.get('scheduled_time'),
            created_by=user,
            is_aggregate_subtask=False,
            upload_to_management=validated_data.get('upload_to_management', False),
        )
        
        for idx, script_id in enumerate(scripts):
            script = TestScript.objects.get(pk=script_id)
            TaskScript.objects.create(
                task=task,
                script=script,
                order=idx,
                parameters=validated_data.get('parameters', {})
            )
        
        return task


class TestTaskExecuteSerializer(serializers.Serializer):
    parameters = serializers.DictField(required=False, default=dict)


class TaskGroupItemSerializer(serializers.ModelSerializer):
    script_name = serializers.CharField(source='script.name', read_only=True)
    script_code = serializers.CharField(source='script.code', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    task_name = serializers.CharField(source='task.name', read_only=True, allow_null=True)
    
    class Meta:
        model = TaskGroupItem
        fields = [
            'id', 'script', 'script_name', 'script_code', 'order', 'parameters',
            'status', 'status_display', 'task', 'task_name',
            'started_at', 'finished_at', 'error_message'
        ]


class TaskGroupItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskGroupItem
        fields = ['script', 'order', 'parameters']


class TaskGroupListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True, allow_null=True)
    group_name = serializers.CharField(source='group.name', read_only=True, allow_null=True)
    total_scripts = serializers.ReadOnlyField()
    completed_scripts = serializers.ReadOnlyField()
    failed_scripts = serializers.ReadOnlyField()
    
    class Meta:
        model = TaskGroup
        fields = [
            'id', 'name', 'description', 'status', 'status_display',
            'total_scripts', 'completed_scripts', 'failed_scripts',
            'group', 'group_name',
            'scheduled_time', 'started_at', 'finished_at',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]


class TaskGroupDetailSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True, allow_null=True)
    group_name = serializers.CharField(source='group.name', read_only=True, allow_null=True)
    items = TaskGroupItemSerializer(many=True, read_only=True)
    total_scripts = serializers.ReadOnlyField()
    completed_scripts = serializers.ReadOnlyField()
    failed_scripts = serializers.ReadOnlyField()
    
    class Meta:
        model = TaskGroup
        fields = [
            'id', 'name', 'description', 'status', 'status_display',
            'items', 'total_scripts', 'completed_scripts', 'failed_scripts',
            'group', 'group_name',
            'scheduled_time', 'started_at', 'finished_at', 'celery_task_id',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]


class TaskGroupCreateSerializer(serializers.ModelSerializer):
    items = TaskGroupItemCreateSerializer(many=True, required=False)
    
    class Meta:
        model = TaskGroup
        fields = ['id', 'name', 'description', 'group', 'scheduled_time', 'items']
    
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        request = self.context.get('request')
        user = None
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
        
        task_group = TaskGroup.objects.create(**validated_data, created_by=user)
        
        for item_data in items_data:
            TaskGroupItem.objects.create(task_group=task_group, **item_data)
        
        return task_group
    
    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                TaskGroupItem.objects.create(task_group=instance, **item_data)
        
        return instance
