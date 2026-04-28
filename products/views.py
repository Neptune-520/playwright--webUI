from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import ProductType, ProductParameter, ProductOption
from .serializers import (
    ProductTypeSerializer, ProductTypeListSerializer,
    ProductParameterSerializer, ProductParameterCreateSerializer,
    ProductOptionSerializer
)


class ProductTypeViewSet(viewsets.ModelViewSet):
    queryset = ProductType.objects.all()
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductTypeListSerializer
        return ProductTypeSerializer


class ProductParameterViewSet(viewsets.ModelViewSet):
    queryset = ProductParameter.objects.all()
    serializer_class = ProductParameterSerializer
    permission_classes = [AllowAny]


class ProductOptionViewSet(viewsets.ModelViewSet):
    queryset = ProductOption.objects.all()
    serializer_class = ProductOptionSerializer
    permission_classes = [AllowAny]


@api_view(['GET', 'POST'])
def product_type_list(request):
    if request.method == 'GET':
        products = ProductType.objects.all()
        serializer = ProductTypeListSerializer(products, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = ProductTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def product_type_detail(request, pk):
    product = get_object_or_404(ProductType, pk=pk)
    
    if request.method == 'GET':
        serializer = ProductTypeSerializer(product)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = ProductTypeSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def product_parameter_list(request, product_type_id):
    product_type = get_object_or_404(ProductType, pk=product_type_id)
    
    if request.method == 'GET':
        parameters = ProductParameter.objects.filter(product_type=product_type)
        serializer = ProductParameterSerializer(parameters, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = ProductParameterCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(product_type=product_type)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def product_parameter_detail(request, pk):
    parameter = get_object_or_404(ProductParameter, pk=pk)
    
    if request.method == 'GET':
        serializer = ProductParameterSerializer(parameter)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = ProductParameterCreateSerializer(parameter, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        parameter.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
