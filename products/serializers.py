from rest_framework import serializers
from .models import ProductType, ProductParameter, ProductOption


class ProductOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductOption
        fields = ['id', 'display_value', 'actual_value', 'price_modifier', 'order', 'is_active']


class ProductParameterSerializer(serializers.ModelSerializer):
    options = ProductOptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = ProductParameter
        fields = [
            'id', 'name', 'code', 'input_type', 'is_required',
            'default_value', 'placeholder', 'validation_regex',
            'order', 'is_active', 'options'
        ]


class ProductTypeSerializer(serializers.ModelSerializer):
    parameters = ProductParameterSerializer(many=True, read_only=True)
    parameters_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductType
        fields = [
            'id', 'name', 'code', 'description', 'icon',
            'is_active', 'created_at', 'updated_at',
            'parameters', 'parameters_count'
        ]
    
    def get_parameters_count(self, obj):
        return obj.parameters.filter(is_active=True).count()


class ProductTypeListSerializer(serializers.ModelSerializer):
    parameters_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductType
        fields = ['id', 'name', 'code', 'description', 'is_active', 'parameters_count']
    
    def get_parameters_count(self, obj):
        return obj.parameters.filter(is_active=True).count()


class ProductParameterCreateSerializer(serializers.ModelSerializer):
    options = ProductOptionSerializer(many=True, required=False)
    
    class Meta:
        model = ProductParameter
        fields = [
            'id', 'product_type', 'name', 'code', 'input_type',
            'is_required', 'default_value', 'placeholder',
            'validation_regex', 'order', 'is_active', 'options'
        ]
    
    def create(self, validated_data):
        options_data = validated_data.pop('options', [])
        parameter = ProductParameter.objects.create(**validated_data)
        
        for option_data in options_data:
            ProductOption.objects.create(parameter=parameter, **option_data)
        
        return parameter
    
    def update(self, instance, validated_data):
        options_data = validated_data.pop('options', [])
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if options_data:
            instance.options.all().delete()
            for option_data in options_data:
                ProductOption.objects.create(parameter=instance, **option_data)
        
        return instance
