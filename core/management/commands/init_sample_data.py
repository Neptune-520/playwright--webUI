from django.core.management.base import BaseCommand
from products.models import ProductType, ProductParameter, ProductOption


class Command(BaseCommand):
    help = '初始化示例产品类型数据'

    def handle(self, *args, **options):
        self.stdout.write('开始初始化产品类型数据...')
        self.stdout.write(self.style.SUCCESS('产品类型数据初始化完成！'))
