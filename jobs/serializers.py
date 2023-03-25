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
class GetJobMachineSerializer(serializers.ModelSerializer):
    class Meta:
        model=JobMachine
        fields='__all__'
class JobSahaykSerialiser(serializers.ModelSerializer):
    class Meta:
        model=JobSahayak
        fields='__all__'        

class MachineSerializers(serializers.ModelSerializer):
    class Meta:
        model=MachineType
        fields='__all__'        

 