from django.db import models
from django.contrib.auth.models import User


class ActionSet(models.Model):
    name = models.CharField('动作集合名称', max_length=200)
    code = models.CharField('动作集合代码', max_length=50, unique=True)
    description = models.TextField('描述', blank=True, default='')
    category = models.CharField('分类', max_length=100, blank=True, default='general')
    is_builtin = models.BooleanField('是否内置', default=False)
    is_active = models.BooleanField('是否启用', default=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='action_sets',
        verbose_name='创建人'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '动作集合'
        verbose_name_plural = '动作集合'
        ordering = ['category', 'name']

    def __str__(self):
        return self.name


class ActionSetStep(models.Model):
    ACTION_TYPE_CHOICES = [
        ('click', '点击元素'),
        ('fill', '填充输入框'),
        ('select', '选择下拉选项'),
        ('random_select', '随机选择'),
        ('random_number', '随机数值'),
        ('check', '勾选复选框'),
        ('uncheck', '取消勾选'),
        ('wait', '等待'),
        ('wait_for_selector', '等待元素'),
        ('scroll', '滚动'),
        ('hover', '悬停'),
        ('focus', '聚焦'),
        ('press', '按键'),
        ('assert_text', '断言文本'),
        ('assert_visible', '断言可见'),
    ]

    LOCATOR_TYPE_CHOICES = [
        ('css', 'CSS选择器'),
        ('xpath', 'XPath'),
        ('id', 'ID'),
        ('name', 'Name属性'),
        ('class_name', 'Class名称'),
        ('text', '文本内容'),
        ('placeholder', 'Placeholder'),
        ('label', 'Label文本'),
    ]

    action_set = models.ForeignKey(
        ActionSet, 
        on_delete=models.CASCADE, 
        related_name='steps',
        verbose_name='动作集合'
    )
    name = models.CharField('步骤名称', max_length=200)
    order = models.IntegerField('执行顺序', default=0)
    action_type = models.CharField('操作类型', max_length=30, choices=ACTION_TYPE_CHOICES)
    
    locator_type = models.CharField('定位类型', max_length=20, choices=LOCATOR_TYPE_CHOICES, blank=True, default='css')
    locator_value = models.CharField('定位值', max_length=500, blank=True, default='')
    locator_description = models.CharField('定位描述', max_length=200, blank=True, default='')
    
    action_value = models.TextField('操作值', blank=True, default='')
    action_value_type = models.CharField(
        '值类型', 
        max_length=20, 
        choices=[
            ('static', '静态值'),
            ('parameter', '参数'),
            ('expression', '表达式'),
        ],
        default='static'
    )
    parameter_name = models.CharField('参数名称', max_length=100, blank=True, default='')
    
    wait_timeout = models.IntegerField('等待超时(ms)', default=10000)
    continue_on_failure = models.BooleanField('失败时继续', default=False)
    retry_count = models.IntegerField('重试次数', default=0)
    retry_interval = models.IntegerField('重试间隔(ms)', default=1000)
    
    random_options = models.JSONField('随机选项列表', blank=True, null=True, default=list)
    select_mode = models.CharField(
        '选择模式',
        max_length=20,
        choices=[
            ('dropdown', '下拉框选择'),
            ('click', '点击卡片'),
        ],
        default='dropdown'
    )
    
    description = models.TextField('描述', blank=True, default='')
    is_enabled = models.BooleanField('是否启用', default=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '动作集合步骤'
        verbose_name_plural = '动作集合步骤'
        ordering = ['order']
        unique_together = ['action_set', 'order']

    def __str__(self):
        return f'{self.action_set.name} - {self.order}. {self.name}'

    def to_playwright_step(self, parameters=None):
        parameters = parameters or {}
        
        value = self.action_value
        if self.action_value_type == 'parameter' and self.parameter_name:
            value = parameters.get(self.parameter_name, self.action_value)
        
        element_config = None
        if self.locator_value:
            element_config = {
                'type': self.locator_type,
                'value': self.locator_value,
                'timeout': self.wait_timeout,
            }
        
        config = {
            'continue_on_failure': self.continue_on_failure,
            'retry_count': self.retry_count,
            'retry_interval': self.retry_interval,
        }
        
        if self.action_type == 'random_select':
            config['random_options'] = self.random_options or []
            config['select_mode'] = self.select_mode
        
        return {
            'name': self.name,
            'action_type': self.action_type,
            'element': element_config,
            'value': value,
            'config': config,
            'is_enabled': self.is_enabled,
        }


class ActionSetParameter(models.Model):
    action_set = models.ForeignKey(
        ActionSet, 
        on_delete=models.CASCADE, 
        related_name='parameters',
        verbose_name='动作集合'
    )
    name = models.CharField('参数名称', max_length=100)
    code = models.CharField('参数代码', max_length=50)
    description = models.TextField('描述', blank=True, default='')
    default_value = models.CharField('默认值', max_length=255, blank=True, default='')
    is_required = models.BooleanField('是否必填', default=True)
    order = models.IntegerField('排序', default=0)
    
    class Meta:
        verbose_name = '动作集合参数'
        verbose_name_plural = '动作集合参数'
        ordering = ['order']
        unique_together = ['action_set', 'code']

    def __str__(self):
        return f'{self.action_set.name} - {self.name}'
