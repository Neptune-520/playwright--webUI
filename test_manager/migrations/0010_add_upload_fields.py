from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "test_manager",
            "0009_add_upload_status_to_testtask",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="testtask",
            name="upload_to_management",
            field=models.BooleanField(
                default=False,
                help_text="勾选后任务执行结果将自动上传至自动化管理平台",
                verbose_name="是否上传至自动化管理平台",
            ),
        ),
        migrations.AddField(
            model_name="testtask",
            name="management_platform_url",
            field=models.CharField(
                blank=True,
                default="",
                help_text="留空则使用全局默认配置",
                max_length=500,
                verbose_name="自动化管理平台API地址",
            ),
        ),
    ]
