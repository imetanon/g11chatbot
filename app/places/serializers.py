from rest_framework import serializers
from .models import Place, BusinessHour, Category, SubCategory


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
        
        
class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = "__all__"
        
class BusinessHourSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessHour
        fields = "__all__"

class PlaceSerializer(serializers.ModelSerializer):
    # category = serializers.PrimaryKeyRelatedField(many=True, read_only=False, queryset=Category.objects.all())
    category = CategorySerializer(many=True, read_only=True)
    sub_category = SubCategorySerializer(many=True, read_only=True)
    business_hours = BusinessHourSerializer(many=True, read_only=True)
    class Meta:
        model = Place
        fields = "__all__"

