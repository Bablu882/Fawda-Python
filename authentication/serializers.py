from .models import *
from rest_framework import serializers
import random
from django.core.validators import RegexValidator



class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['mobile_no']

class MobileVerifySerializer(serializers.Serializer):
    mobile_no = serializers.CharField(validators=[RegexValidator(
        regex=r'^\+?1?\d{9,10}$', # define regular expression pattern for mobile number
        message="Mobile number must be entered in the format: '8427262631'. Only 10 digits allowed."
    )])



from rest_framework import serializers
from .models import State, District

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['id', 'name', 'abbreviation', 'slug']

class DistrictSerializer(serializers.ModelSerializer):
    state = StateSerializer()
    class Meta:
        model = District
        fields = ['id', 'name', 'state', 'slug']

class ProfileSerializers(serializers.ModelSerializer):
    class Meta:
        model=Profile
        fields='__all__'