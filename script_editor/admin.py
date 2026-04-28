from django.contrib import admin
from .models import ElementLocator, TestScript, ScriptVersion, TestStep, ActionSet, ActionSetStep, ActionSetParameter


class TestStepInline(admin.TabularInline):
    model = TestStep
    extra = 1
    fields = ['name', 'order', 'action_type', 'element', 'action_value', 'is_enabled']


class ActionSetStepInline(admin.TabularInline):
    model = ActionSetStep
    extra = 1
    fields = ['name', 'order', 'action_type', 'locator_value', 'action_value', 'is_enabled']


class ActionSetParameterInline(admin.TabularInline):
    model = ActionSetParameter
    extra = 1
    fields = ['name', 'code', 'default_value', 'is_required', 'order']


@admin.register(ElementLocator)
class ElementLocatorAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'locator_type', 'locator_value', 'is_active']
    list_filter = ['locator_type', 'is_active']
    search_fields = ['name', 'code', 'locator_value']


@admin.register(TestScript)
class TestScriptAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'status', 'version', 'created_at']
    list_filter = ['status']
    search_fields = ['name', 'code']
    inlines = [TestStepInline]


@admin.register(ScriptVersion)
class ScriptVersionAdmin(admin.ModelAdmin):
    list_display = ['script', 'version_number', 'created_at']
    list_filter = ['script']


@admin.register(TestStep)
class TestStepAdmin(admin.ModelAdmin):
    list_display = ['name', 'script', 'order', 'action_type', 'is_enabled']
    list_filter = ['script', 'action_type', 'is_enabled']
    search_fields = ['name']


@admin.register(ActionSet)
class ActionSetAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'category', 'is_builtin', 'is_active', 'created_at']
    list_filter = ['category', 'is_builtin', 'is_active']
    search_fields = ['name', 'code']
    inlines = [ActionSetStepInline, ActionSetParameterInline]


@admin.register(ActionSetStep)
class ActionSetStepAdmin(admin.ModelAdmin):
    list_display = ['name', 'action_set', 'order', 'action_type', 'is_enabled']
    list_filter = ['action_set', 'action_type', 'is_enabled']
    search_fields = ['name']


@admin.register(ActionSetParameter)
class ActionSetParameterAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'action_set', 'is_required', 'order']
    list_filter = ['action_set', 'is_required']
    search_fields = ['name', 'code']
