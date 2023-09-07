from rest_framework import serializers
from .models import Machines, Department

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']
