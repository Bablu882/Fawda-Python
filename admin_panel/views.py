from django.shortcuts import render
from authentication.models import User
from booking.models import JobBooking
from django.http import JsonResponse
from jobs.models import JobMachine,JobSahayak
from rest_framework.response import Response

# Create your views here.
# def job_booking_list(request):
#     status_filter = request.GET.get('status', 'All')
#     jobs = JobBooking.objects.all()
#     if status_filter != 'All':
#         jobs = jobs.filter(status=status_filter)
#     context = {'jobs': jobs, 'status_filter': status_filter}
#     return render(request, 'job_booking_list.html', context)






def job_booking_list(request):
    # job_bookings = JobBooking.objects.filter(status=status)
    # job_bookings = JobBooking.objects.all()
    data = []
    if request.method == 'GET':
        status = request.GET.get('status')
        if status == 'Pending':
            job_sahayak=JobSahayak.objects.filter(status=status)
            job_machine=JobMachine.objects.filter(status=status)
            print(job_sahayak,job_machine)
            for jobs in job_sahayak:
                if jobs.job_type == 'theke_pe_kam':
                    job_number='T-123456'
                else:
                    job_number='S-123456'    
                data.append({
                    'id':jobs.id,
                    'job_number':job_number,
                    'Job_type':jobs.job_type,
                    'Job_posting_date':jobs.date,
                    'Job_booking_date':'Null',
                    'Job_satatus':jobs.status,
                    'payment_to_service_provider':jobs.payment_your,
                    'mobile_no_for_payment':'Null',
                    'Payment_status':jobs.status
                })
            for jobs in job_machine:
                data.append({
                    'id':jobs.id,
                    'job_number':'M-123456',
                    'Job_type':jobs.job_type,
                    'Job_posting_date':jobs.date,
                    'Job_booking_date':'Null',
                    'Job_satatus':jobs.status,
                    'payment_to_service_provider':jobs.payment_your,
                    'mobile_no_for_payment':'Null',
                    'Payment_status':jobs.status

                })
        else:
            job_booking=JobBooking.objects.filter(status=status)
            for jobs in job_booking:
                if jobs.jobsahayak.job_type == 'theke_pe_kam':
                    data.append({
                        'id':jobs.id,
                        'job_number':'t-123456',
                        'Job_type':jobs.jobsahayak.job_type,
                        'Job_posting_date':jobs.jobsahayak.date,
                        'Job_booking_date':jobs.date_booked,
                        'Job_satatus':jobs.status,
                        'payment_to_service_provider':jobs.payment_your,
                        'mobile_no_for_payment':'Null',
                        'Payment_status':jobs.status

                    })
                elif jobs.jobsahayak.job_type == 'individuals_sahayak':
                    data.append({
                        'id':jobs.id,
                        'job_number':'t-123456',
                        'Job_type':jobs.jobsahayak.job,
                        'Job_posting_date':jobs.jobsahayak.date,
                        'Job_booking_date':jobs.date_booked,
                        'Job_satatus':jobs.status,
                        'payment_to_service_provider':jobs.payment_your,
                        'mobile_no_for_payment':'Null',
                        'Payment_status':jobs.status

                    })
                else:
                    data.append({
                        {
                        'id':jobs.id,
                        'job_number':'t-123456',
                        'Job_type':jobs.jobmachine.job,
                        'Job_posting_date':jobs.jobmachine.date,
                        'Job_booking_date':jobs.date_booked,
                        'Job_satatus':jobs.status,
                        'payment_to_service_provider':jobs.payment_your,
                        'mobile_no_for_payment':'Null',
                        'Payment_status':jobs.status

                    }

                    })    

    return JsonResponse({'data': data})
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
class JobDetailsAdmin(APIView):
    permission_classes=[AllowAny,]
    def get(self,request,format=None):
        status = request.GET.get('status')
        print(status)
        data=[]
        if status == 'Pending':
            job_sahayak=JobSahayak.objects.filter(status=status)
            job_machine=JobMachine.objects.filter(status=status)
            # print(job_sahayak,job_machine)
            for jobs in job_sahayak:
                if jobs.job_type == 'theke_pe_kam':
                    job_number='T-123456'
                else:
                    job_number='S-123456'    
                data.append({
                    'id':jobs.id,
                    'job_number':job_number,
                    'Job_type':jobs.job_type,
                    'Job_posting_date':jobs.date,
                    'Job_booking_date':'Null',
                    'Job_satatus':jobs.status,
                    'payment_to_service_provider':jobs.payment_your,
                    'mobile_no_for_payment':'Null',
                    'Payment_status':jobs.status
                })
            for jobs in job_machine:
                data.append({
                    'id':jobs.id,
                    'job_number':'M-123456',
                    'Job_type':jobs.job_type,
                    'Job_posting_date':jobs.date,
                    'Job_booking_date':'Null',
                    'Job_satatus':jobs.status,
                    'payment_to_service_provider':jobs.payment_your,
                    'mobile_no_for_payment':'Null',
                    'Payment_status':jobs.status

                })
        else:
            job_booking=JobBooking.objects.filter(status=status)
            for jobs in job_booking:
                if jobs.jobsahayak:
                    if jobs.jobsahayak.job_type == 'theke_pe_kam':
                        data.append({
                            'id':jobs.id,
                            'job_number':'t-123456',
                            'Job_type':jobs.jobsahayak.job_type,
                            'Job_posting_date':jobs.jobsahayak.date,
                            'Job_booking_date':jobs.date_booked,
                            'Job_satatus':jobs.status,
                            'payment_to_service_provider':jobs.payment_your,
                            'mobile_no_for_payment':'Null',
                            'Payment_status':jobs.status

                        })
                    elif jobs.jobsahayak.job_type == 'individuals_sahayak':
                        data.append({
                            'id':jobs.id,
                            'job_number':'t-123456',
                            'Job_type':jobs.jobsahayak.job_type,
                            'Job_posting_date':jobs.jobsahayak.date,
                            'Job_booking_date':jobs.date_booked,
                            'Job_satatus':jobs.status,
                            'payment_to_service_provider':jobs.payment_your,
                            'mobile_no_for_payment':'Null',
                            'Payment_status':jobs.status

                        })
                else:
                    data.append({
                        'id':jobs.id,
                        'job_number':'t-123456',
                        'Job_type':jobs.jobmachine.job_type,
                        'Job_posting_date':jobs.jobmachine.date,
                        'Job_booking_date':jobs.date_booked,
                        'Job_satatus':jobs.status,
                        'payment_to_service_provider':jobs.payment_your,
                        'mobile_no_for_payment':'Null',
                        'Payment_status':jobs.status


                    })    

        return Response({'data': data})
