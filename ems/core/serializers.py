from rest_framework import serializers
from .models import Machines, Department, CustomUser, MachineIssue


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class meta:
        model = CustomUser
        fields = ['username', 'email']

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']

class machineHoursSerializer(serializers.Serializer):
    machine_hours = serializers.IntegerField()

    def to_representation(self, instance):
        if instance is not None:
            return {'machine_hours': instance.machine_hours}
        else:
            return {'error':"No Data"}
        
class MachineCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machines
        fields = ["id", "name"]



    # def to_representation(self, instance):
    #     if instance is not None:
    #         return {'machine_code':instance.id}
    #     else:
    #         return {'error':'No Data'}