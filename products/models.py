from django.db import models
from django.contrib.auth.models import User


class ProductType(models.Model):
    name = models.CharField('产品类型名称', max_length=100, unique=True)
    code = models.CharField('产品类型代码', max_length=50, unique=True)
    description = models.TextField('描述', blank=True, default='')
    icon = models.ImageField('图标', upload_to='product_icons/', blank=True, null=True)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '产品类型'
        verbose_name_plural = '产品类型'
        ordering = ['name']

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    INPUT_TYPE_CHOICES = [
        ('text', '文本输入'),
        ('select', '下拉选择'),
        ('radio', '单选按钮'),
        ('checkbox', '复选框'),
        ('number', '数字输入'),
        ('color', '颜色选择'),
        ('file', '文件上传'),
    ]

    product_type = models.ForeignKey(
        ProductType, 
        on_delete=models.CASCADE, 
        related_name='parameters',
        verbose_name='产品类型'
    )
    name = models.CharField('参数名称', max_length=100)
    code = models.CharField('参数代码', max_length=50)
    input_type = models.CharField('输入类型', max_length=20, choices=INPUT_TYPE_CHOICES, default='text')
    is_required = models.BooleanField('是否必填', default=True)
    default_value = models.CharField('默认值', max_length=255, blank=True, default='')
    placeholder = models.CharField('占位提示', max_length=100, blank=True, default='')
    validation_regex = models.CharField('验证正则', max_length=255, blank=True, default='')
    order = models.IntegerField('排序', default=0)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '产品参数'
        verbose_name_plural = '产品参数'
        ordering = ['order', 'name']
        unique_together = ['product_type', 'code']

    def __str__(self):
        return f'{self.product_type.name} - {self.name}'


class ProductOption(models.Model):
    parameter = models.ForeignKey(
        ProductParameter, 
        on_delete=models.CASCADE, 
        related_name='options',
        verbose_name='参数'
    )
    display_value = models.CharField('显示值', max_length=100)
    actual_value = models.CharField('实际值', max_length=255)
    price_modifier = models.DecimalField('价格调整', max_digits=10, decimal_places=2, default=0)
    order = models.IntegerField('排序', default=0)
    is_active = models.BooleanField('是否启用', default=True)

    class Meta:
        verbose_name = '参数选项'
        verbose_name_plural = '参数选项'
        ordering = ['order', 'display_value']

    def __str__(self):
        return f'{self.parameter.name} - {self.display_value}'
