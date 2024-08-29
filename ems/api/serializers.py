from rest_framework import serializers

from core.models import CustomUser

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=150, min_length=8)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, attrs):
        
        print(attrs)
        username = attrs.get('username')
        password = attrs.get('password')

        if not username:
            raise serializers.ValidationError("Please Provide username")
        if not password:
            raise serializers.ValidationError("Please Provide password")

        return attrs
