from rest_framework import serializers
from core.models import Group


class GroupSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    full_path = serializers.ReadOnlyField()
    children_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Group
        fields = [
            'id', 'name', 'code', 'type', 'type_display', 'description',
            'parent', 'order', 'full_path', 'children_count',
            'created_by', 'created_at', 'updated_at'
        ]
    
    def get_children_count(self, obj):
        return obj.children.count()


class GroupCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name', 'code', 'type', 'description', 'parent', 'order']
    
    def create(self, validated_data):
        request = self.context.get('request')
        user = None
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
        return Group.objects.create(**validated_data, created_by=user)
