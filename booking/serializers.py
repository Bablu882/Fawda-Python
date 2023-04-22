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
        try:
            rating = int(rating)
        except ValueError:
            raise serializers.ValidationError("rating should be a number")

        if rating > 10:
            raise serializers.ValidationError("rating should not be greater than 10")

        # Check if rating already exists for the given booking_job
        if Rating.objects.filter(booking_job=booking_job).exists():
            raise serializers.ValidationError("Rating already exists for this booking_job")

        return data


class JobAcceptSerializer(serializers.Serializer):
    job_id = serializers.IntegerField(required=True)
    count_male = serializers.IntegerField(required=True, min_value=0)
    count_female = serializers.IntegerField(required=True, min_value=0)


class CancellationBookingJobSerializer(serializers.Serializer):
    job_id = serializers.IntegerField()
    job_number = serializers.CharField()
    status = serializers.ChoiceField(choices=['Cancelled', 'Cancelled-After-Payment'])


class RejectedBookingSerializer(serializers.Serializer):
    booking_id = serializers.IntegerField()
    status = serializers.ChoiceField(choices=[('Rejected', 'Rejected'), ('Rejected-After-Payment', 'Rejected-After-Payment')])

    def validate_booking_id(self, value):
        if not str(value).isdigit():
            raise serializers.ValidationError('Booking ID must be numeric.')
        return value

    def validate(self, attrs):
        status = attrs.get('status')

        if not status:
            raise serializers.ValidationError('Status is required.')
        elif status not in ['Rejected', 'Rejected-After-Payment']:
            raise serializers.ValidationError('Invalid status.')

        return attrs
