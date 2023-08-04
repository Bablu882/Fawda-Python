from rest_framework import serializers
from .models import *
from booking.models import JobBooking
from django.utils import timezone
from datetime import datetime
import re

class PostJobThekePeKamSerializer(serializers.ModelSerializer):
    land_type = serializers.CharField()
    def validate_datetime(self, value):
        current_datetime = timezone.localtime(timezone.now())
        if value <= current_datetime + timezone.timedelta(hours=3):
            raise serializers.ValidationError('Datetime should be at least 3 hours greater than the current datetime')
        print('serializer----',value)    
        return value
    
    class Meta:
        model = JobSahayak
        fields = ['datetime', 'description', 'land_area', 'land_type', 'total_amount_theka']

    def validate_land_type(self, value):
        allowed_choices = ['Bigha', 'Killa', 'None']
        if value not in allowed_choices:
            raise serializers.ValidationError('land_type should be Bigha or Killa or None')
        return value
    
    def validate_land_area(self, value):
        try:
            land_area = int(value)
        except ValueError:
            raise serializers.ValidationError('land_area should be a valid integer')

        # if land_area <= 0:
        #     raise serializers.ValidationError('land_area should be greater than 0')
        if land_area >= 100:
            raise serializers.ValidationError('land_area should be less than 100')
        return land_area
    
class GetJobThekePeKamSerializer(serializers.ModelSerializer):
    class Meta:
        model=JobSahayak
        fields='__all__'
        
class PostJobIndividualSerializer(serializers.ModelSerializer):
    datetime = serializers.DateTimeField(required=True)
    description = serializers.CharField(required=True)
    land_type = serializers.CharField(required=True)
    land_area = serializers.CharField(required=True)
    count_male = serializers.CharField(required=False,error_messages={'blank': 'This field may not be blank. if you not need than pass 0'})
    count_female = serializers.CharField(required=False,error_messages={'blank': 'This field may not be blank. if you not need than pass 0'})
    pay_amount_male = serializers.CharField(required=False,error_messages={'blank': 'This field may not be blank. if you not need than pass 0'})
    pay_amount_female = serializers.CharField(required=False,error_messages={'blank': 'This field may not be blank. if you not need than pass 0'})
    num_days = serializers.CharField(required=True)

    class Meta:
        model = JobSahayak
        fields = ['datetime',
                  'description',
                  'land_area',
                  'land_type',
                  'count_male',
                  'count_female',
                  'pay_amount_male',
                  'pay_amount_female',
                  'num_days']
        
    def validate_land_type(self, value):
        allowed_choices = ['Bigha', 'Killa', 'None']
        if value not in allowed_choices:
            raise serializers.ValidationError('land_type should be Bigha or Killa or None')
        return value
        
    # def validate_land_type(self, value):
    #     allowed_choices = ['Bigha', 'Killa']
    #     if value not in allowed_choices:
    #         raise serializers.ValidationError('land_type should be Bigha or Killa')
    #     return value
    
    def validate_land_area(self, value):
        try:
            land_area = int(value)
        except ValueError:
            raise serializers.ValidationError('land_area should be a valid integer')

        # if land_area <= 0:
        #     raise serializers.ValidationError('land_area should be greater than 0')
        if land_area >= 100:
            raise serializers.ValidationError('land_area should be less than 100')
        return land_area
    def validate_datetime(self, value):
        current_datetime = timezone.localtime(timezone.now())
        if value <= current_datetime + timezone.timedelta(hours=3):
            raise serializers.ValidationError('Datetime should be at least 3 hours greater than the current datetime')
        return value
    
    

class GetJobIndividualsSerializer(serializers.ModelSerializer):
    class Meta:
        model=JobSahayak
        fields='__all__'        

class JobMachineSerializers(serializers.ModelSerializer):
    land_type = serializers.CharField()
    others = serializers.CharField(max_length=500, allow_null=True, allow_blank=True)
    class Meta:
        model=JobMachine
        fields= [
            'work_type',
            'machine',
            'others',
            'datetime',
            'status',
            'job_type',
            'job_number',
            'payment_your',
            'total_amount',
            'land_area',
            'land_type',
            'total_amount_machine',    
        ]
    def validate_land_type(self, value):
        allowed_choices = ['Bigha', 'Killa', 'None']
        if value not in allowed_choices:
            raise serializers.ValidationError('land_type should be Bigha or Killa or None')
        return value    
    def validate_work_type(self, value):
        if not re.match(r'^[a-zA-Z\s\u0900-\u097F]+$', value):
            raise serializers.ValidationError(("Invalid work_type, only letters, spaces, and Hindi characters allowed"))
        return value
    
    def validate_machine(self, value):
        if not re.match(r'^[a-zA-Z\s\u0900-\u097F]+$', value):
            raise serializers.ValidationError(("Invalid machine, only letters, spaces, and Hindi characters allowed"))
        return value    
    
    def validate_land_area(self, value):
        try:
            land_area = int(value)
        except ValueError:
            raise serializers.ValidationError('land_area should be a valid integer')

        # if land_area <= 0:
        #     raise serializers.ValidationError('land_area should be greater than 0')
        if land_area >= 100:
            raise serializers.ValidationError('land_area should be less than 100')
        return land_area
    def validate_datetime(self, value):
        current_datetime = timezone.localtime(timezone.now())
        if value <= current_datetime + timezone.timedelta(hours=3):
            raise serializers.ValidationError('Datetime should be at least 3 hours greater than the current datetime')
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

 
class JobBookingSerializers(serializers.ModelSerializer):
    jobsahayak=JobSahaykSerialiser(many=False,read_only=True)
    jobmachine=JobMachineSerializers(many=False,read_only=True)
    class Meta:
        model=JobBooking
        fields='__all__'

    # Product=ProductSerializers(many=False,read_only=True)



