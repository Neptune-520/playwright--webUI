from django.contrib import admin
from .models import ProductType, ProductParameter, ProductOption


class ProductOptionInline(admin.TabularInline):
    model = ProductOption
    extra = 1


class ProductParameterInline(admin.TabularInline):
    model = ProductParameter
    extra = 1
    show_change_link = True


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'code']
    inlines = [ProductParameterInline]


@admin.register(ProductParameter)
class ProductParameterAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'product_type', 'input_type', 'is_required', 'order']
    list_filter = ['product_type', 'input_type', 'is_required']
    search_fields = ['name', 'code']
    inlines = [ProductOptionInline]


@admin.register(ProductOption)
class ProductOptionAdmin(admin.ModelAdmin):
    list_display = ['display_value', 'actual_value', 'parameter', 'order']
    list_filter = ['parameter']
