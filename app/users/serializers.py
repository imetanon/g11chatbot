from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'line_user_id',
            'gender',
            'birth_year',
            'status'
        )
        model = User