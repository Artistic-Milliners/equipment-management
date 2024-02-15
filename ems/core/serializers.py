from rest_framework import serializers
from .models import Machines, Department, CustomUser


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class meta:
        model = CustomUser
        fields = ['username', 'email']

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']
