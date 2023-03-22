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



class JobDetailsAdminPanel(APIView):
    permission_classes=[AllowAny,]
    def get(self,request,format=None):
        data=request.GET.get('id')
        data_list=[]
        if JobSahayak.objects.filter(id=data,status='Pending').exists():
            details1=JobSahayak.objects.get(id=data)
            data_list.append({
                'grahak_name':details1.grahak.profile.name,
                'grahak_gender':details1.grahak.profile.name,
                'grahak_phone':details1.grahak.mobile_no,
                'grahak_mohalla':details1.grahak.profile.mohalla,
                'grahak_village':details1.grahak.profile.village,
                'grahak_state':details1.grahak.profile.state,
                'grahak_district':details1.grahak.profile.district,
                'status':details1.status,
                'desc':details1.description,
                 
                'heading':"",
                'name':"",
                'gender':"",
                'phone':"",
                'mohalla':"",
                'village':"",
                'state':"",
                'district':"",

            })
        elif JobMachine.objects.filter(id=data,status='Pending').exists():
            details2=JobMachine.objects.get(id=data)
            data_list.append({
                'grahak_name':details2.grahak.profile.name,
                'grahak_gender':details2.grahak.profile.gender,
                'grahak_phone':details2.grahak.mobile_no,
                'grahak_mohalla':details2.grahak.profile.mohalla,
                'grahak_village':details2.grahak.profile.village,
                'grahak_state':details2.grahak.profile.state,
                'grahak_district':details2.grahak.profile.district,
                'status':details2.status,
                'desc':details2.description,
                
                'heading':"",
                'name':"",
                'gender':"",
                'phone':"",
                'mohalla':"",
                'village':"",
                'state':"",
                'district':"",

            })
        elif JobBooking.objects.filter(id=data ,status='Accepted').exists():
            details3=JobBooking.objects.get(id=data)
            if details3.jobsahayak:
                data_list.append({
                    'grahak_name':details3.jobsahayak.grahak.profile.name,
                    'grahak_gender':details3.jobsahayak.grahak.profile.gender,
                    'grahak_phone':details3.jobsahayak.grahak.mobile_no,
                    'grahak_mohalla':details3.jobsahayak.grahak.profile.mohalla,
                    'grahak_village':details3.jobsahayak.grahak.profile.village,
                    'grahak_state':details3.jobsahayak.grahak.profile.state,
                    'grahak_district':details3.jobsahayak.grahak.profile.district,
                    'desc':details3.jobsahayak.description,
                    'status':details3.status,
                    
                    'heading':"Sahayak Details",
                    'name':details3.booking_user.profile.name,
                    'gender':details3.booking_user.profile.gender,
                    'phone':details3.booking_user.mobile_no,
                    'mohalla':details3.booking_user.profile.mohalla,
                    'village':details3.booking_user.profile.village,
                    'state':details3.booking_user.profile.state,
                    'district':details3.booking_user.profile.district,

                })
            else:
                data_list.append({
                    'grahak_name':details3.jobmachine.grahak.profile.name,
                    'grahak_gender':details3.jobmachine.grahak.profile.gender,
                    'grahak_phone':details3.jobmachine.grahak.mobile_no,
                    'grahak_mohalla':details3.jobmachine.grahak.profile.mohalla,
                    'grahak_village':details3.jobmachine.grahak.profile.village,
                    'grahak_state':details3.jobmachine.grahak.profile.state,
                    'grahak_district':details3.jobmachine.grahak.profile.district,
                    'desc':details3.jobmachine.description,
                    'status':details3.status,
                    
                    'heading':"Machine Malik Details",
                    'name':details3.booking_user.profile.name,
                    'gender':details3.booking_user.profile.gender,
                    'phone':details3.booking_user.mobile_no,
                    'mohalla':details3.booking_user.profile.mohalla,
                    'village':details3.booking_user.profile.village,
                    'state':details3.booking_user.profile.state,
                    'district':details3.booking_user.profile.district,
                })  

        else:
            return Response({'Job not exists !'})         
        return Response(data_list)    