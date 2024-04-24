from rest_framework import serializers
from .models import Machines, Department, CustomUser, MachineIssue, Employee


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class meta:
        model = CustomUser
        fields = ['username', 'email']


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']

class EmployeeSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer()
    # user = UserSerializer()
    class Meta:
        model= Employee
        fields = "__all__"

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

class IssueSerializer(serializers.ModelSerializer):
    user = EmployeeSerializer()
    class Meta:
        model = MachineIssue
        fields = ('id', 'user', 'equipment', 'ticket_num', 'machine_id', 'machine_hours',
                   'description_user', 'status', 'image', 'date_time')

