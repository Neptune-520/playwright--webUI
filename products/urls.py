from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_type_list, name='product-type-list'),
    path('<int:pk>/', views.product_type_detail, name='product-type-detail'),
    path('<int:product_type_id>/parameters/', views.product_parameter_list, name='product-parameter-list'),
    path('parameters/<int:pk>/', views.product_parameter_detail, name='product-parameter-detail'),
]
