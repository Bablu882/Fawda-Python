from rest_framework import serializers
from .models import *
class ClientInformationsSerializer(serializers.ModelSerializer):
    class Meta:
        model=ClientInformations
        fields='__all__'


class AppVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model=AppVersion
        fields='__all__'        