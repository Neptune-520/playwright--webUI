from django.contrib import admin
from .models import TestTask, TestResult, TestReport


class TestResultInline(admin.TabularInline):
    model = TestResult
    extra = 0
    readonly_fields = ['step_name', 'step_order', 'status', 'duration', 'error_message']
    fields = ['step_name', 'step_order', 'status', 'duration', 'error_message']


@admin.register(TestTask)
class TestTaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'script', 'status', 'created_at', 'started_at', 'finished_at']
    list_filter = ['status', 'script']
    search_fields = ['name']
    inlines = [TestResultInline]


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ['task', 'step_name', 'step_order', 'status', 'duration', 'created_at']
    list_filter = ['status', 'task']
    search_fields = ['step_name']


@admin.register(TestReport)
class TestReportAdmin(admin.ModelAdmin):
    list_display = ['task', 'total_steps', 'passed_steps', 'failed_steps', 'pass_rate', 'created_at']
    readonly_fields = ['pass_rate']
