from rest_framework import serializers
from .models import *

class PostJobThekePeKamSerializer(serializers.ModelSerializer):
    class Meta:
        model=JobSahayak
        fields=['datetime',
                'description',
                'land_area',
                'land_type',
                'total_amount_theka'
                ]
        
    def validate(self, data):
        if not data['datetime'] or not data['description'] or not data['land_area'] or not data['land_type'] or not data['total_amount_theka']:
            raise serializers.ValidationError({'error': 'All fields are required!'})
        if not data['land_area'].isdigit():
            raise serializers.ValidationError({'error': 'Land area should be numeric!'})
        return data
class GetJobThekePeKamSerializer(serializers.ModelSerializer):
    class Meta:
        model=JobSahayak
        fields='__all__'

class PostJobIndividualSerializer(serializers.ModelSerializer):
    class Meta:
        model=JobSahayak
        fields=['datetime',
                'description',
                'land_area',
                'land_type',
                'count_male',
                'count_female',
                'pay_amount_male',
                'pay_amount_female',
                'num_days',
                # 'fawda_fee_percentage'
                # 'total_amount'
                ]
   
          
class GetJobIndividualsSerializer(serializers.ModelSerializer):
    class Meta:
        model=JobSahayak
        fields='__all__'        

class JobMachineSerializers(serializers.ModelSerializer):
    others = serializers.CharField(max_length=500, allow_null=True, allow_blank=True)
    class Meta:
        model=JobMachine
        fields= [
            'work_type',
            'machine',
            'others',
            'datetime',
            'land_area',
            'land_type',
            'total_amount_machine',    
        ]
    def validate_work_type(self, value):
        if not WorkType.objects.filter(name=value).exists():
            raise serializers.ValidationError("Invalid work type: {}".format(value))
        return value
    
    def validate_machine(self, value):
        if not MachineType.objects.filter(machine=value).exists():
            raise serializers.ValidationError("Invalid machine: {}".format(value))
        return value    
class GetJobMachineSerializer(serializers.ModelSerializer):
    class Meta:
        model=JobMachine
        fields='__all__'
class JobSahaykSerialiser(serializers.ModelSerializer):
    class Meta:
        model=JobSahayak
        fields='__all__'        
class WorkTypeSerialiser(serializers.ModelSerializer):
    class Meta:
        model=WorkType
        fields='__all__'
class MachineSerializers(serializers.ModelSerializer):
    class Meta:
        model=MachineType
        fields='__all__'        

 