from authentication.models import User
from datetime import date
from booking.models import JobBooking
# Create your views here.
def registration_status(request):
    today = date.today()
    total_registrations_sahayak = User.objects.filter(user_type='Sahayak').count()
    today_registrations_sahayak = User.objects.filter(date_joined__date=today,user_type='Sahayak').count()
    total_registrations_grahak = User.objects.filter(user_type='Grahak').count()
    today_registrations_grahak = User.objects.filter(date_joined__date=today,user_type='Grahak').count()
    total_registrations_machine = User.objects.filter(user_type='MachineMalik').count()
    today_registrations_machine = User.objects.filter(date_joined__date=today,user_type='MachineMalik').count()
    job_booking_total=JobBooking.objects.filter(status='Booked').count()
    job_booking_today=JobBooking.objects.filter(date_booked__date=today,status='Booked').count()
    return {
        'total_registrations_sahayak': total_registrations_sahayak,
        'today_registrations_sahayak': today_registrations_sahayak,
        'total_registrations_grahak': total_registrations_grahak,
        'today_registrations_grahak': today_registrations_grahak,
        'total_registrations_machine': total_registrations_machine,
        'today_registrations_machine': today_registrations_machine,
        'total_booking':job_booking_total,
        'today_booking':job_booking_today
    }