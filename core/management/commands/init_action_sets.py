from django.core.management.base import BaseCommand
from script_editor.models import ActionSet, ActionSetStep, ActionSetParameter


class Command(BaseCommand):
    help = '初始化预设动作集合数据'

    def handle(self, *args, **options):
        self.stdout.write('开始初始化动作集合数据...')
        
        self.stdout.write(self.style.SUCCESS('动作集合数据初始化完成！'))
