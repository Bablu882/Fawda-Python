from rest_framework import serializers
from .models import *
from jobs.serializers import *

class JobBookingSerializers(serializers.ModelSerializer):
    class Meta:
        model=JobBooking
        fields='__all__'

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ('id', 'booking_job', 'rating', 'comment')

    def validate(self, data):
        booking_job = data.get('booking_job')
        rating = data.get('rating')
        
        if not booking_job:
            raise serializers.ValidationError("booking_job is required")
        
        if not rating:
            raise serializers.ValidationError("rating is required")
        
        try:
            rating = int(rating)
        except ValueError:
            raise serializers.ValidationError("rating should be a number")
        
        if rating > 5:
            raise serializers.ValidationError("rating should not be greater than 5")
        
        return data




# class JobBookingSerializer(serializers.ModelSerializer):
#     jobsahayak = JobSahaykSerialiser(many=True, read_only=True)
#     jobmachine = GetJobMachineSerializer(many=True, read_only=True)
#     booking_user = serializers.PrimaryKeyRelatedField(read_only=True)

#     class Meta:
#         model = JobBooking
#         fields = ('id', 'total_amount', 'jobsahayak', 'jobmachine', 'booking_user', 'date_booked', 'status')        