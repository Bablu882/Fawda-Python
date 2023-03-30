from rest_framework import serializers
from .models import *
class TermsAndConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model=TermsCondition
        fields=['terms_condition','privacy_policy']