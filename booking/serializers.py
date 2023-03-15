from rest_framework import serializers
from .models import *
from jobs.serializers import *

class JobBookingSerializers(serializers.ModelSerializer):
    class Meta:
        model=JobBooking
        fields='__all__'

# class JobBookingSerializer(serializers.ModelSerializer):
#     jobsahayak = JobSahaykSerialiser(many=True, read_only=True)
#     jobmachine = GetJobMachineSerializer(many=True, read_only=True)
#     booking_user = serializers.PrimaryKeyRelatedField(read_only=True)

#     class Meta:
#         model = JobBooking
#         fields = ('id', 'total_amount', 'jobsahayak', 'jobmachine', 'booking_user', 'date_booked', 'status')        