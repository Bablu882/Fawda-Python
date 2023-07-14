from .models import *
from rest_framework import serializers
from django.core.validators import RegexValidator
from rest_framework import status


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


from rest_framework import serializers
import re

class RegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    gender = serializers.CharField(max_length=10)
    phone = serializers.CharField(max_length=10)
    mohalla = serializers.CharField(max_length=100)
    village = serializers.CharField(max_length=100)
    user_type = serializers.CharField(max_length=20)
    state = serializers.CharField(max_length=100)
    district = serializers.CharField(max_length=100)
    latitude = serializers.CharField(max_length=20)
    longitude = serializers.CharField(max_length=20)
    age = serializers.CharField(max_length=2)
    pincode = serializers.CharField(max_length=6)
    upiid = serializers.CharField(max_length=100)

    def validate_phone(self, value):
        if not value:
            raise serializers.ValidationError('Phone number is required.')
        if not re.match(r'^\d{10}$', value):
            raise serializers.ValidationError('Phone number should be 10 digits.')
        return value

    def validate_age(self, value):
        if not value:
            raise serializers.ValidationError('Age is required.')
        try:
            Intage = int(value)
            if 18 <= Intage <= 70 :
               return value
            else :
                raise serializers.ValidationError('Age must be greater or equal than 18 and less or equal than 70.')
        except ValueError :
            raise serializers.ValidationError('Age must be a whole number')

    def validate_pincode(self, value):
        if not value:
            raise serializers.ValidationError('Pin code is required.')
        if not re.match(r'^\d{6}$', value):
            raise serializers.ValidationError('Pin code should be 6 digits')
        return value

    def validate_upiid(self, value):
        if not value:
            raise serializers.ValidationError('Upi Id is required.')
        if not re.match(r'^.{1,100}$', value):
            raise serializers.ValidationError('Please enter a valid Upi Id')
        return value    

    def validate_user_type(self, value):
        if not value:
            raise serializers.ValidationError('User type is required.')
        if value not in ["Grahak", "Sahayak", "MachineMalik"]:
            raise serializers.ValidationError('User type should be one of the following: Grahak, Sahayak, MachineMalik.')
        return value

    def validate_gender(self, value):
        if not value:
            raise serializers.ValidationError('Gender is required.')
        if value not in ["Male", "Female"]:
            raise serializers.ValidationError('Gender should be Male or Female')
        return value

    def validate_latitude(self, value):
        if not value:
            raise serializers.ValidationError('Latitude is required.')
        try:
            float_value = float(value)
            if -90 <= float_value <= 90:
                return value
            else:
                raise serializers.ValidationError('Latitude must be between -90 and 90.')
        except ValueError:
            raise serializers.ValidationError('Latitude must be a valid float.')

    def validate_longitude(self, value):
        if not value:
            raise serializers.ValidationError('Longitude is required.')
        try:
            float_value = float(value)
            if -180 <= float_value <= 180:
                return value
            else:
                raise serializers.ValidationError('Longitude must be between -180 and 180.')
        except ValueError:
            raise serializers.ValidationError('Longitude must be a valid float.')

    def validate(self, data):
        state = data.get('state')
        district = data.get('district')
        phone = data.get('phone')

        # Validate state
        try:
            state_obj = State.objects.get(name=state)
        except State.DoesNotExist:
            raise serializers.ValidationError(f'State with name {state} does not exist in the database.')
        data['state'] = state_obj

        # Validate district within state
        try:
            district_obj = District.objects.get(name=district, state=state_obj)
        except District.DoesNotExist:
            raise serializers.ValidationError(f'District with name {district} does not exist within the state {state}.')
        data['district'] = district_obj

        # Check if user already exists
        if User.objects.filter(mobile_no=phone).exists():
            raise serializers.ValidationError({'message':'User already exists'})
        return data


class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=10, error_messages={
            'max_length': 'Phone number should be 10 digits.'
        })

    def validate_phone(self, value):
        if not re.match(r'^\d{10}$', value):
            raise serializers.ValidationError('Phone number should be digits only.')
        return value