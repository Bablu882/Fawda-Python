from authentication.models import User
from datetime import date,datetime
from booking.models import JobBooking
from django.db.models import Sum,Q
# Create your views here.

def registration_status(request):
    today = date.today()
    today_str = today.strftime('%Y-%m-%d')

    total_registrations_sahayak = User.objects.filter(user_type='Sahayak').count()
    today_registrations_sahayak = User.objects.filter(date_joined__startswith=today_str, user_type='Sahayak').count()

    total_registrations_grahak = User.objects.filter(user_type='Grahak').count()
    today_registrations_grahak = User.objects.filter(date_joined__startswith=today_str, user_type='Grahak').count()

    total_registrations_machine = User.objects.filter(user_type='MachineMalik').count()
    today_registrations_machine = User.objects.filter(date_joined__startswith=today_str, user_type='MachineMalik').count()

    job_booking_total = JobBooking.objects.filter(status='Booked').count()
    job_booking_today = JobBooking.objects.filter(date_booked__startswith=today_str, status='Booked').count()

    total_revenue = JobBooking.objects.filter(status='Booked').aggregate(Sum('admin_commission'))['admin_commission__sum']
    today_revenue = JobBooking.objects.filter(Q(date_booked__startswith=today_str) & Q(status='Booked')).aggregate(Sum('admin_commission'))['admin_commission__sum']

    return {
        'total_registrations_sahayak': total_registrations_sahayak,
        'today_registrations_sahayak': today_registrations_sahayak,
        'total_registrations_grahak': total_registrations_grahak,
        'today_registrations_grahak': today_registrations_grahak,
        'total_registrations_machine': total_registrations_machine,
        'today_registrations_machine': today_registrations_machine,
        'total_booking': job_booking_total,
        'today_booking': job_booking_today,
        'total_revenue': total_revenue,
        'today_revenue': today_revenue
    }
