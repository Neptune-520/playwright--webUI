from django.db import models
from django.contrib.auth.models import User


class Group(models.Model):
    TYPE_CHOICES = [
        ('script', '脚本分组'),
        ('action_set', '动作集合分组'),
        ('task', '任务分组'),
    ]
    
    name = models.CharField('分组名称', max_length=100)
    code = models.CharField('分组代码', max_length=50)
    type = models.CharField('分组类型', max_length=20, choices=TYPE_CHOICES)
    description = models.TextField('描述', blank=True, default='')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children', verbose_name='父分组')
    order = models.IntegerField('排序', default=0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_groups', verbose_name='创建人')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '分组'
        verbose_name_plural = '分组'
        ordering = ['type', 'order', 'name']
        unique_together = ['code', 'type']
    
    def __str__(self):
        return f'{self.get_type_display()} - {self.name}'
    
    @property
    def full_path(self):
        if self.parent:
            return f'{self.parent.full_path} / {self.name}'
        return self.name
