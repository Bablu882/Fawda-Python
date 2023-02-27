from .models import User
from rest_framework import serializers
import random




class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['mobile_no']