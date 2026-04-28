from django.db import models
from django.contrib.auth.models import User


class ElementLocator(models.Model):
    LOCATOR_TYPE_CHOICES = [
        ('css', 'CSS选择器'),
        ('xpath', 'XPath'),
        ('id', 'ID'),
        ('name', 'Name属性'),
        ('class_name', 'Class名称'),
        ('tag_name', '标签名'),
        ('text', '文本内容'),
        ('role', 'ARIA角色'),
        ('test_id', 'Test ID'),
        ('placeholder', 'Placeholder'),
        ('label', 'Label文本'),
    ]

    name = models.CharField('元素名称', max_length=100)
    code = models.CharField('元素代码', max_length=50, unique=True)
    locator_type = models.CharField('定位类型', max_length=20, choices=LOCATOR_TYPE_CHOICES, default='css')
    locator_value = models.CharField('定位值', max_length=500)
    page_url = models.URLField('所在页面URL', max_length=500, blank=True, default='')
    description = models.TextField('描述', blank=True, default='')
    wait_timeout = models.IntegerField('等待超时(毫秒)', default=10000)
    wait_state = models.CharField('等待状态', max_length=20, choices=[('visible', '可见'), ('hidden', '隐藏'), ('attached', '附加到DOM'), ('detached', '从DOM分离')], default='visible')
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '元素定位器'
        verbose_name_plural = '元素定位器'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.locator_type}: {self.locator_value})'

    def to_playwright_locator(self):
        return {'type': self.locator_type, 'value': self.locator_value, 'timeout': self.wait_timeout, 'state': self.wait_state}


class TestScript(models.Model):
    STATUS_CHOICES = [('draft', '草稿'), ('published', '已发布'), ('archived', '已归档')]
    name = models.CharField('脚本名称', max_length=200)
    code = models.CharField('脚本代码', max_length=50, unique=True)
    description = models.TextField('描述', blank=True, default='')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='draft')
    version = models.IntegerField('版本号', default=1)
    target_url = models.URLField('目标网站URL', max_length=500)
    script_data = models.JSONField('脚本数据', default=dict)
    group = models.ForeignKey('core.Group', on_delete=models.SET_NULL, null=True, blank=True, related_name='scripts', verbose_name='分组', limit_choices_to={'type': 'script'})
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_scripts', verbose_name='创建人')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '测试脚本'
        verbose_name_plural = '测试脚本'
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.name} (v{self.version})'


class ScriptVersion(models.Model):
    script = models.ForeignKey(TestScript, on_delete=models.CASCADE, related_name='versions', verbose_name='脚本')
    version_number = models.IntegerField('版本号')
    script_data = models.JSONField('脚本数据')
    change_note = models.TextField('变更说明', blank=True, default='')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='创建人')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '脚本版本'
        verbose_name_plural = '脚本版本'
        ordering = ['-version_number']
        unique_together = ['script', 'version_number']

    def __str__(self):
        return f'{self.script.name} - v{self.version_number}'


class TestStep(models.Model):
    ACTION_TYPE_CHOICES = [
        ('navigate', '导航到URL'), ('click', '点击元素'), ('fill', '填充输入框'),
        ('select', '选择下拉选项'), ('random_select', '随机选择'), ('random_number', '随机数值'), ('check', '勾选复选框'), ('uncheck', '取消勾选'),
        ('wait', '等待'), ('wait_for_selector', '等待元素'), ('screenshot', '截图'),
        ('scroll', '滚动'), ('hover', '悬停'), ('focus', '聚焦'), ('press', '按键'),
        ('upload', '上传文件'), ('assert_text', '断言文本'), ('assert_visible', '断言可见'),
        ('assert_value', '断言值'), ('action_set', '动作集合'), ('custom', '自定义操作'),
    ]
    script = models.ForeignKey(TestScript, on_delete=models.CASCADE, related_name='steps', verbose_name='测试脚本')
    name = models.CharField('步骤名称', max_length=200)
    order = models.IntegerField('执行顺序', default=0)
    action_type = models.CharField('操作类型', max_length=30, choices=ACTION_TYPE_CHOICES)
    element = models.ForeignKey(ElementLocator, on_delete=models.SET_NULL, null=True, blank=True, related_name='test_steps', verbose_name='目标元素')
    action_set_ref = models.ForeignKey('ActionSet', on_delete=models.SET_NULL, null=True, blank=True, related_name='test_steps_ref', verbose_name='动作集合')
    action_set_params = models.JSONField('动作集合参数', default=dict, blank=True)
    action_value = models.TextField('操作值', blank=True, default='')
    action_config = models.JSONField('操作配置', default=dict)
    description = models.TextField('描述', blank=True, default='')
    is_enabled = models.BooleanField('是否启用', default=True)
    continue_on_failure = models.BooleanField('失败时继续', default=False)
    retry_count = models.IntegerField('重试次数', default=0)
    retry_interval = models.IntegerField('重试间隔(毫秒)', default=1000)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '测试步骤'
        verbose_name_plural = '测试步骤'
        ordering = ['order']
        unique_together = ['script', 'order']

    def __str__(self):
        return f'{self.script.name} - {self.order}. {self.name}'


class ActionSet(models.Model):
    CATEGORY_CHOICES = [('input', '输入操作'), ('navigation', '导航操作'), ('form', '表单操作'), ('validation', '验证操作'), ('general', '通用操作')]
    name = models.CharField('动作集合名称', max_length=200)
    code = models.CharField('动作集合代码', max_length=50, unique=True)
    description = models.TextField('描述', blank=True, default='')
    category = models.CharField('分类', max_length=100, choices=CATEGORY_CHOICES, default='general')
    group = models.ForeignKey('core.Group', on_delete=models.SET_NULL, null=True, blank=True, related_name='action_sets', verbose_name='分组', limit_choices_to={'type': 'action_set'})
    is_builtin = models.BooleanField('是否内置', default=False)
    is_active = models.BooleanField('是否启用', default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='action_sets', verbose_name='创建人')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '动作集合'
        verbose_name_plural = '动作集合'
        ordering = ['category', 'name']

    def __str__(self):
        return self.name

    def expand_to_steps(self, parameters=None):
        parameters = parameters or {}
        expanded_steps = []
        for step in self.steps.filter(is_enabled=True).order_by('order'):
            step_data = step.to_playwright_step(parameters)
            step_data['action_set_source'] = {'id': self.id, 'name': self.name, 'code': self.code}
            expanded_steps.append(step_data)
        return expanded_steps


class ActionSetStep(models.Model):
    ACTION_TYPE_CHOICES = [('click', '点击元素'), ('fill', '填充输入框'), ('select', '选择下拉选项'), ('random_select', '随机选择'), ('random_number', '随机数值'), ('check', '勾选复选框'), ('uncheck', '取消勾选'), ('wait', '等待'), ('wait_for_selector', '等待元素'), ('scroll', '滚动'), ('hover', '悬停'), ('focus', '聚焦'), ('press', '按键'), ('assert_text', '断言文本'), ('assert_visible', '断言可见')]
    LOCATOR_TYPE_CHOICES = [('css', 'CSS选择器'), ('xpath', 'XPath'), ('id', 'ID'), ('name', 'Name属性'), ('class_name', 'Class名称'), ('text', '文本内容'), ('placeholder', 'Placeholder'), ('label', 'Label文本')]
    SELECT_MODE_CHOICES = [('dropdown', '下拉框选择'), ('click', '点击卡片')]
    
    action_set = models.ForeignKey(ActionSet, on_delete=models.CASCADE, related_name='steps', verbose_name='动作集合')
    name = models.CharField('步骤名称', max_length=200)
    order = models.IntegerField('执行顺序', default=0)
    action_type = models.CharField('操作类型', max_length=30, choices=ACTION_TYPE_CHOICES)
    locator_type = models.CharField('定位类型', max_length=20, choices=LOCATOR_TYPE_CHOICES, blank=True, default='css')
    locator_value = models.CharField('定位值', max_length=500, blank=True, default='')
    locator_description = models.CharField('定位描述', max_length=200, blank=True, default='')
    action_value = models.TextField('操作值', blank=True, default='')
    action_value_type = models.CharField('值类型', max_length=20, choices=[('static', '静态值'), ('parameter', '参数'), ('expression', '表达式')], default='static')
    parameter_name = models.CharField('参数名称', max_length=100, blank=True, default='')
    action_config = models.JSONField('操作配置', default=dict, blank=True)
    wait_timeout = models.IntegerField('等待超时(ms)', default=10000)
    continue_on_failure = models.BooleanField('失败时继续', default=False)
    retry_count = models.IntegerField('重试次数', default=0)
    retry_interval = models.IntegerField('重试间隔(ms)', default=1000)
    random_options = models.JSONField('随机选项列表', blank=True, null=True, default=list)
    select_mode = models.CharField('选择模式', max_length=20, choices=SELECT_MODE_CHOICES, default='dropdown')
    random_min = models.IntegerField('随机数最小值', blank=True, null=True, default=0)
    random_max = models.IntegerField('随机数最大值', blank=True, null=True, default=100)
    force_click = models.BooleanField('强制点击', default=False)
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
        if self.action_config and self.action_config.get('locators'):
            locators = self.action_config['locators']
            if locators:
                primary = locators[0]
                element_config = {'type': primary.get('locator_type', self.locator_type), 'value': primary.get('locator_value', self.locator_value), 'timeout': self.wait_timeout}
                if len(locators) > 1:
                    element_config['backup_locators'] = [
                        {'type': loc.get('locator_type', 'css'), 'value': loc.get('locator_value', '')}
                        for loc in locators[1:]
                    ]
        elif self.locator_value:
            element_config = {'type': self.locator_type, 'value': self.locator_value, 'timeout': self.wait_timeout}
        config = {'continue_on_failure': self.continue_on_failure, 'retry_count': self.retry_count, 'retry_interval': self.retry_interval}
        if self.action_type == 'random_select':
            config['random_options'] = self.random_options or []
            config['select_mode'] = self.select_mode
        if self.action_type == 'random_number':
            config['random_min'] = self.random_min or 0
            config['random_max'] = self.random_max or 100
        if self.action_type == 'click':
            config['force'] = self.force_click
        return {
            'name': self.name, 'action_type': self.action_type, 'element': element_config,
            'value': str(value), 'config': config,
            'is_enabled': self.is_enabled,
        }


class ActionSetParameter(models.Model):
    action_set = models.ForeignKey(ActionSet, on_delete=models.CASCADE, related_name='parameters', verbose_name='动作集合')
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


class GlobalConfig(models.Model):
    headless_mode = models.BooleanField('无头模式（不显示浏览器）', default=False)
    default_timeout = models.IntegerField('默认超时时间(毫秒)', default=30000)
    step_screenshot = models.BooleanField('每步截图', default=False, help_text='是否在每个步骤执行后截取操作元素的截图')
    slow_mo = models.IntegerField('操作延迟(毫秒)', default=0, help_text='每个操作之间的延迟时间')
    viewport_width = models.IntegerField('视口宽度', default=1920)
    viewport_height = models.IntegerField('视口高度', default=1080)
    scroll_distance = models.IntegerField('默认滚动距离(像素)', default=500)
    scroll_direction = models.CharField('默认滚动方向', max_length=10, choices=[('down', '向下'), ('up', '向上'), ('left', '向左'), ('right', '向右')], default='down')
    marketplace_api_url = models.CharField('集合文件API地址', max_length=500, default='http://127.0.0.1:8000', help_text='集合文件的来源API地址')
    management_platform_url = models.CharField('自动化管理平台API地址', max_length=500, default='http://localhost:8001/api/script-results/upload', help_text='脚本执行结果上传的目标地址')
    username = models.CharField('用户名', max_length=100, default='', blank=True, help_text='用于标识上传的任务结果报告')
    email_smtp_host = models.CharField('SMTP服务器地址', max_length=200, default='', blank=True, help_text='邮件发送服务器地址，如smtp.qq.com')
    email_smtp_port = models.IntegerField('SMTP端口', default=465, help_text='SMTP服务器端口，SSL通常为465，STARTTLS通常为587')
    email_username = models.CharField('发件人邮箱', max_length=200, default='', blank=True, help_text='用于发送邮件的邮箱地址')
    email_password = models.CharField('邮箱密码/授权码', max_length=200, default='', blank=True, help_text='邮箱密码或授权码')
    email_use_ssl = models.BooleanField('使用SSL连接', default=True, help_text='是否使用SSL连接（通常465端口使用SSL，587端口不使用）')
    email_recipients = models.CharField('收件人列表', max_length=1000, default='', blank=True, help_text='收件人邮箱，多个用逗号分隔')
    email_enable = models.BooleanField('启用邮件通知', default=False, help_text='是否启用邮件发送功能')
    report_base_url = models.CharField('报告访问地址', max_length=500, default='', blank=True, help_text='任务结果报告的访问地址前缀，用于邮件中的报告链接')
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='更新人')

    class Meta:
        verbose_name = '全局配置'
        verbose_name_plural = '全局配置'

    def __str__(self):
        return '全局配置'

    @classmethod
    def get_config(cls):
        config, _ = cls.objects.get_or_create(pk=1)
        return config
