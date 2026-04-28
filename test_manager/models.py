from django.db import models
from django.contrib.auth.models import User
from script_editor.models import TestScript
import uuid


class TestTask(models.Model):
    STATUS_CHOICES = [
        ('pending', '待执行'),
        ('running', '执行中'),
        ('completed', '已完成'),
        ('failed', '失败'),
        ('cancelled', '已取消'),
    ]

    name = models.CharField('任务名称', max_length=200)
    script = models.ForeignKey(
        TestScript, 
        on_delete=models.CASCADE, 
        related_name='tasks',
        verbose_name='主测试脚本'
    )
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    parameters = models.JSONField('测试参数', default=dict)
    group = models.ForeignKey('core.Group', on_delete=models.SET_NULL, null=True, blank=True, related_name='test_tasks', verbose_name='分组', limit_choices_to={'type': 'task'})
    scheduled_time = models.DateTimeField('计划执行时间', null=True, blank=True)
    started_at = models.DateTimeField('开始时间', null=True, blank=True)
    finished_at = models.DateTimeField('结束时间', null=True, blank=True)
    celery_task_id = models.CharField('Celery任务ID', max_length=100, blank=True, default='')
    task_group = models.ForeignKey(
        'TaskGroup',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='test_tasks',
        verbose_name='任务组'
    )
    is_aggregate_subtask = models.BooleanField(
        '是否为聚合任务子任务',
        default=False,
        help_text='标记此任务是否由聚合任务创建的子任务'
    )
    upload_to_management = models.BooleanField(
        '是否上传至自动化管理平台',
        default=False,
        help_text='勾选后任务执行结果将自动上传至自动化管理平台'
    )
    management_platform_url = models.CharField(
        '自动化管理平台API地址',
        max_length=500,
        blank=True,
        default='',
        help_text='留空则使用全局默认配置'
    )
    upload_status = models.CharField(
        '上传状态',
        max_length=20,
        choices=[
            ('none', '未上传'),
            ('uploading', '上传中'),
            ('uploaded', '已上传'),
            ('failed', '上传失败'),
            ('pending', '待上传'),
        ],
        default='none',
        help_text='结果上传到JSON管理平台的状态'
    )
    send_email = models.BooleanField(
        '是否发送邮件通知',
        default=False,
        help_text='勾选后任务完成后自动发送邮件通知'
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='test_tasks',
        verbose_name='创建人'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '测试任务'
        verbose_name_plural = '测试任务'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.get_status_display()})'

    @property
    def script_count(self):
        return self.task_scripts.count()

    def get_all_scripts(self):
        if self.task_scripts.exists():
            return TestScript.objects.filter(task_scripts__task=self)
        return TestScript.objects.filter(pk=self.script_id)


class TaskScript(models.Model):
    task = models.ForeignKey(
        TestTask,
        on_delete=models.CASCADE,
        related_name='task_scripts',
        verbose_name='测试任务'
    )
    script = models.ForeignKey(
        TestScript,
        on_delete=models.CASCADE,
        related_name='task_scripts',
        verbose_name='测试脚本'
    )
    order = models.IntegerField('执行顺序', default=0)
    parameters = models.JSONField('测试参数', default=dict, blank=True)

    class Meta:
        verbose_name = '任务脚本'
        verbose_name_plural = '任务脚本'
        ordering = ['order']
        unique_together = ['task', 'script']

    def __str__(self):
        return f'{self.task.name} - {self.script.name}'


class TaskGroup(models.Model):
    """
    @deprecated 任务组功能已废弃，请使用测试任务多选功能
    此模型保留用于数据向后兼容
    """
    STATUS_CHOICES = [
        ('pending', '待执行'),
        ('running', '执行中'),
        ('completed', '已完成'),
        ('partial', '部分成功'),
        ('failed', '失败'),
        ('cancelled', '已取消'),
    ]

    name = models.CharField('任务组名称', max_length=200)
    description = models.TextField('描述', blank=True, default='')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    group = models.ForeignKey('core.Group', on_delete=models.SET_NULL, null=True, blank=True, related_name='task_groups', verbose_name='分组', limit_choices_to={'type': 'task'})
    scheduled_time = models.DateTimeField('计划执行时间', null=True, blank=True)
    started_at = models.DateTimeField('开始时间', null=True, blank=True)
    finished_at = models.DateTimeField('结束时间', null=True, blank=True)
    celery_task_id = models.CharField('Celery 任务 ID', max_length=100, blank=True, default='')
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='task_groups',
        verbose_name='创建人'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '任务组'
        verbose_name_plural = '任务组'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.get_status_display()})'

    @property
    def total_scripts(self):
        return self.items.count()

    @property
    def completed_scripts(self):
        return self.items.filter(status='completed').count()

    @property
    def failed_scripts(self):
        return self.items.filter(status='failed').count()


class TaskGroupItem(models.Model):
    """
    @deprecated 任务组功能已废弃
    此模型保留用于数据向后兼容
    """
    STATUS_CHOICES = [
        ('pending', '待执行'),
        ('running', '执行中'),
        ('completed', '已完成'),
        ('failed', '失败'),
        ('skipped', '跳过'),
    ]

    task_group = models.ForeignKey(
        TaskGroup,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='任务组'
    )
    script = models.ForeignKey(
        TestScript,
        on_delete=models.CASCADE,
        related_name='task_group_items',
        verbose_name='测试脚本'
    )
    order = models.IntegerField('执行顺序', default=0)
    parameters = models.JSONField('测试参数', default=dict)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    task = models.ForeignKey(
        TestTask,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='task_group_item',
        verbose_name='关联任务'
    )
    started_at = models.DateTimeField('开始时间', null=True, blank=True)
    finished_at = models.DateTimeField('结束时间', null=True, blank=True)
    error_message = models.TextField('错误信息', blank=True, default='')

    class Meta:
        verbose_name = '任务组项'
        verbose_name_plural = '任务组项'
        ordering = ['order']
        unique_together = ['task_group', 'order']

    def __str__(self):
        return f'{self.task_group.name} - {self.order}. {self.script.name}'


class TestResult(models.Model):
    STATUS_CHOICES = [
        ('passed', '通过'),
        ('failed', '失败'),
        ('skipped', '跳过'),
        ('error', '错误'),
    ]

    task = models.ForeignKey(
        TestTask, 
        on_delete=models.CASCADE, 
        related_name='results',
        verbose_name='测试任务'
    )
    step_name = models.CharField('步骤名称', max_length=200)
    step_order = models.IntegerField('步骤顺序')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES)
    duration = models.FloatField('执行时长(秒)', default=0)
    error_message = models.TextField('错误信息', blank=True, default='')
    error_stack = models.TextField('错误堆栈', blank=True, default='')
    screenshot = models.ImageField('截图', upload_to='screenshots/', blank=True, null=True)
    action_values = models.JSONField('操作值', default=dict, blank=True, help_text='存储步骤执行时的操作值，如输入值、随机选择的值等')
    logs = models.JSONField('执行日志', default=list)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '测试结果'
        verbose_name_plural = '测试结果'
        ordering = ['step_order']

    def __str__(self):
        return f'{self.task.name} - {self.step_name} ({self.get_status_display()})'


class TestReport(models.Model):
    task = models.OneToOneField(
        TestTask, 
        on_delete=models.CASCADE, 
        related_name='report',
        verbose_name='测试任务'
    )
    total_steps = models.IntegerField('总步骤数', default=0)
    passed_steps = models.IntegerField('通过步骤数', default=0)
    failed_steps = models.IntegerField('失败步骤数', default=0)
    skipped_steps = models.IntegerField('跳过步骤数', default=0)
    total_duration = models.FloatField('总执行时长(秒)', default=0)
    summary = models.JSONField('汇总数据', default=dict)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '测试报告'
        verbose_name_plural = '测试报告'

    def __str__(self):
        return f'{self.task.name} 测试报告'

    @property
    def pass_rate(self):
        if self.total_steps == 0:
            return 0
        return round((self.passed_steps / self.total_steps) * 100, 2)
