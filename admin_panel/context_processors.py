from authentication.models import User
from datetime import date,datetime
from booking.models import JobBooking
from jobs.models import JobMachine
from jobs.models import JobSahayak
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

    total_job_post_sahayak = JobSahayak.objects.filter((Q(status='Pending') | Q(status='Accepted') | Q(status='Booked') | Q(status='Ongoing'))).count()
    total_job_post_machine = JobMachine.objects.filter((Q(status='Pending') | Q(status='Accepted') | Q(status='Booked') | Q(status='Ongoing'))).count()
    total_job_post = total_job_post_machine + total_job_post_sahayak

    today_job_post_sahayak = JobSahayak.objects.filter(
    Q(date__startswith=today_str) &
    (Q(status='Pending') | Q(status='Accepted') | Q(status='Booked') | Q(status='Ongoing'))
    ).count()

    today_job_post_machine = JobMachine.objects.filter(
    Q(date__startswith=today_str) &
    (Q(status='Pending') | Q(status='Accepted') | Q(status='Booked') | Q(status='Ongoing'))
    ).count()
    today_job_post = today_job_post_machine + today_job_post_sahayak

    total_job_post_theke = JobSahayak.objects.filter(Q(job_type='theke_pe_kam') & (Q(status='Pending') | Q(status='Accepted') | Q(status='Booked') | Q(status='Ongoing'))).count()
    today_job_post_theke = JobSahayak.objects.filter(Q(job_type='theke_pe_kam') & Q(date__startswith=today_str) & (Q(status='Pending') | Q(status='Accepted') | Q(status='Booked') | Q(status='Ongoing'))).count()

    total_job_post_individual = JobSahayak.objects.filter(Q(job_type='individuals_sahayak') & (Q(status='Pending') | Q(status='Accepted') | Q(status='Booked') | Q(status='Ongoing'))).count()
    today_job_post_individual = JobSahayak.objects.filter(Q(job_type='individuals_sahayak') & Q(date__startswith=today_str) & (Q(status='Pending') | Q(status='Accepted') | Q(status='Booked') | Q(status='Ongoing'))).count()

    total_job_post_machineMalik = JobMachine.objects.filter(Q(status='Pending') | Q(status='Accepted') | Q(status='Booked') | Q(status='Ongoing')).count()
    today_job_post_machineMalik = JobMachine.objects.filter(Q(date__startswith=today_str) & (Q(status='Pending') | Q(status='Accepted') | Q(status='Booked') | Q(status='Ongoing'))).count()

    total_job_completed_sahayak = JobSahayak.objects.filter(Q(status='Completed')).count()
    total_job_completed_machine = JobMachine.objects.filter(Q(status='Completed')).count()
    total_job_completed = total_job_completed_sahayak + total_job_completed_machine

    today_job_completed = JobBooking.objects.filter(Q(status='Completed') & Q(date_completed__startswith=today_str)).count()
    # today_job_completed_machine = JobMachine.objects.filter(Q(status='Completed') & Q(date_completed__startswith=today_str)).count()
    # today_job_completed = today_job_completed_sahayak + today_job_completed_machine

    total_job_cancelled_sahayak = JobSahayak.objects.filter(Q(status='Cancelled')).count()
    total_job_cancelled_machine = JobMachine.objects.filter(Q(status='Cancelled')).count()
    total_job_cancelled = total_job_cancelled_machine + total_job_cancelled_sahayak

    today_job_cancelled = JobBooking.objects.filter(Q(status='Cancelled') & Q(date_cancelled__startswith=today_str)).count()

    total_job_cancelled_AP_sahayak = JobSahayak.objects.filter(Q(status='Cancelled-After-Payment')).count()
    total_job_cancelled_AP_machine = JobMachine.objects.filter(Q(status='Cancelled-After-Payment')).count()
    total_job_cancelled_AP = total_job_cancelled_AP_machine + total_job_cancelled_AP_sahayak

    today_job_cancelled_AP = JobBooking.objects.filter(Q(status='Cancelled-After-Payment') & Q(date_cancelled_after_payment__startswith=today_str)).count()



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
        'today_revenue': today_revenue,
        'total_job_post': total_job_post,
        'today_job_post': today_job_post,
        'total_job_post_theke': total_job_post_theke,
        'today_job_post_theke': today_job_post_theke,
        'total_job_post_individual': total_job_post_individual,
        'today_job_post_individual': today_job_post_individual,
        'total_job_post_machineMalik': total_job_post_machineMalik,
        'today_job_post_machineMalik': today_job_post_machineMalik,
        'total_job_completed': total_job_completed,
        'today_job_completed': today_job_completed,
        'total_job_cancelled': total_job_cancelled,
        'today_job_cancelled': today_job_cancelled,
        'total_job_cancelled_AP': total_job_cancelled_AP,
        'today_job_cancelled_AP': today_job_cancelled_AP
    }
