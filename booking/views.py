from django.shortcuts import render

# Create your views here.
from .models import *
from jobs.models import *
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from jobs.serializers import JobSahaykSerialiser,GetJobMachineSerializer

class JobAcceptMachin(APIView):
    permission_classes=[IsAuthenticated,]
    def post(self,request,format=None):
        if request.user.status == 'MachineMalik':
            job_id=request.data.get('job_id')
            machin_user=request.user
            #check job is exist or not 
            try:
                job = JobMachine.objects.get(pk=job_id)
            except JobMachine.DoesNotExist:
                return Response({'error': 'Job does not exist !'})
            if JobBooking.objects.filter(jobmachine=job, booking_user=machin_user).exists():
                return Response({'error': 'Job is already accepted !'})
            booking=JobBooking.objects.create(jobmachine=job,booking_user=machin_user,status='Accepted')
            update_booking_amount_machine(booking)
            get_job=JobMachine.objects.get(pk=job_id)
            get_job.status= 'Accepted'
            get_job.save()
            serial=JobBookingSerializers(booking)
            return Response({'Success':'Job accepted !','data':serial.data})
        else:
            return Response({'error':'you are not MachineMalik'})    
         
class JobAcceptedSahayakTheka(APIView):
    permission_classes=[IsAuthenticated,]
    def post(self,request,format=None):
        job_id=request.data.get('job_id')
        sahayak_user=request.user
        #check if job is exists or not 
        try:
            job = JobSahayak.objects.get(pk=job_id)
        except JobSahayak.DoesNotExist:
            return Response({'error': 'Job does not exist !'})

        if JobBooking.objects.filter(jobsahayak=job, booking_user=sahayak_user).exists():
            return Response({'error': 'Job is already accepted !'})
        booking=JobBooking.objects.create(
            jobsahayak=job,
            booking_user=sahayak_user,
            status='Accepted',
        )
        # booking.jobsahayak.add(job)
        update_booking_amounts(booking)
        get_job=JobSahayak.objects.get(pk=job_id)    
        get_job.status='Accepted'
        get_job.save()
        serial=JobBookingSerializers(booking)
        return Response({'Success':'Job accepted !','data':serial.data})
        
class JobAcceptIndividuals(APIView):
    permission_classes=[IsAuthenticated,]
    def post(self, request, format=None):
        job_id = request.data.get('job_id')
        count_male = int(request.data.get('count_male'))
        count_female = int(request.data.get('count_female'))
        individual_user = request.user

        # Check if job exists
        try:
            job = JobSahayak.objects.get(pk=job_id)
        except JobSahayak.DoesNotExist:
            return Response({'error': 'Job does not exist !'})

        # Check if job is already booked by the user
        if JobBooking.objects.filter(jobsahayak=job, booking_user=individual_user).exists():
            return Response({'error': 'Job is already accepted !'})

        # Check if there are enough available workers for the job
        if int(job.count_male) < count_male or int(job.count_female) < count_female:
            return Response({'error': 'Not enough sahayak available for this job !'})

        # Update the job count
        job.count_male = int(job.count_male)-count_male
        job.count_female = int(job.count_female)-count_female
        job.save()
        if int(job.count_male) == 0 and int(job.count_female) == 0:
            job.status ='Accepted'
            job.save()
        print(job.count_female,job.count_male)
        # Create the booking object
        booking = JobBooking.objects.create(booking_user=individual_user,
                                            count_male=count_male,
                                            count_female=count_female,
                                            status='Accepted',
                                            jobsahayak=job
                                            )
        # booking.jobsahayak.add(job)
        update_booking_amounts(booking)

        # Serialize the booking object
        serializer = JobBookingSerializers(booking)

        return Response({'success': 'Job accepted !', 'data': serializer.data})
        
        
def update_booking_amounts(booking):
    job_sahayak = booking.jobsahayak
    if job_sahayak.job_type == 'individuals_sahayak':    
    # if booking.jobsahayak.filter(job_type='individuals_sahayak').exists():
    #     job_sahayak = booking.jobsahayak.filter(job_type='individuals_sahayak').first()
        count_male = int(booking.count_male) if booking.count_male else 0
        count_female = int(booking.count_female) if booking.count_female else 0
        pay_amount_male = int(job_sahayak.pay_amount_male) if job_sahayak.pay_amount_male else 0
        pay_amount_female = int(job_sahayak.pay_amount_female) if job_sahayak.pay_amount_female else 0
        num_days = int(job_sahayak.num_days) if job_sahayak.num_days else 0

        # Extract the percentage value from fawda_fee_percentage field
        fawda_fee_percentage_str = job_sahayak.fawda_fee_percentage.fawda_fee_percentage.rstrip('%')
        fawda_fee_percentage = float(fawda_fee_percentage_str) if fawda_fee_percentage_str else 0

        # calculate total amount without fawda_fee
        total_amount_without_fawda = (count_male * pay_amount_male + count_female * pay_amount_female) * num_days

        # calculate fawda_fee amount
        fawda_fee_amount = round(total_amount_without_fawda * (fawda_fee_percentage / 100), 2)

        # calculate total amount with fawda_fee
        total_amount = round(total_amount_without_fawda + fawda_fee_amount, 2)

        # calculate payment_your amount
        payment_your = round(total_amount_without_fawda - fawda_fee_amount, 2)

        # update the booking fields
        booking.fawda_fee=str(fawda_fee_amount)
        booking.total_amount = str(total_amount)
        booking.payment_your = str(payment_your)
        booking.total_amount_sahayak = str(total_amount_without_fawda)
        # booking.save()
    elif job_sahayak.job_type == 'theke_pe_kam':
        total_amount_theka = int(job_sahayak.total_amount_theka) if job_sahayak.total_amount_theka else 0
        fawda_fee_percentage_str = job_sahayak.fawda_fee_percentage.fawda_fee_percentage.rstrip('%')
        fawda_fee_percentage = float(fawda_fee_percentage_str) if fawda_fee_percentage_str else 0
        total_amount_without_fawda = total_amount_theka
        fawda_fee_amount = round(total_amount_without_fawda * (fawda_fee_percentage / 100), 2)
        total_amount = round(total_amount_without_fawda + fawda_fee_amount, 2)
        payment_your = round(total_amount_without_fawda - fawda_fee_amount, 2)
        booking.fawda_fee = str(fawda_fee_amount)
        booking.total_amount = str(total_amount)
        booking.payment_your = str(payment_your)
        booking.total_amount_theka = str(total_amount_without_fawda)
        # booking.fawda_fee_percentage = booking.fawda_fee_percentage  # update the original field value without percentage symbol 
    booking.save()    

def update_booking_amount_machine(booking):
    job_machine=booking.jobmachine
    total_amount_machine = int(job_machine.total_amount_machine) if job_machine.total_amount_machine else 0
    fawda_fee_percentage_str = job_machine.fawda_fee_percentage.fawda_fee_percentage.rstrip('%')
    fawda_fee_percentage = float(fawda_fee_percentage_str) if fawda_fee_percentage_str else 0
    total_amount_without_fawda = total_amount_machine
    fawda_fee_amount = round(total_amount_without_fawda * (fawda_fee_percentage / 100), 2)
    total_amount = round(total_amount_without_fawda + fawda_fee_amount, 2)
    payment_your = round(total_amount_without_fawda - fawda_fee_amount, 2)
    booking.fawda_fee = str(fawda_fee_amount)
    booking.total_amount = str(total_amount)
    booking.payment_your = str(payment_your)
    booking.total_amount_machine = str(total_amount_without_fawda)   
    booking.save()


class MyJobsDetais(APIView):
    permission_classes=[IsAuthenticated,]
    def get(self,request,format=None):
        if request.user.status == 'Sahayak' or request.user.status == 'MachineMalik':
            bookedjob=JobBooking.objects.all().filter(booking_user=request.user)
            serial=JobBookingSerializers(bookedjob,many=True)
            return Response({'success':True,'data':serial.data})
        return Response({'error':'you are not Sahayak or MachineMalik !'})    


class MyBookingDetailsSahayak(APIView):
    def get(self, request):
        bookings = JobBooking.objects.filter(jobsahayak__grahak=request.user, status='Accepted')
        total_amount = 0
        count_male = 0
        count_female = 0
        total_amount_sahayak = 0
        payment_your = 0
        fawda_fee = 0
        booking_data = []
        for booking in bookings:
            if booking.jobsahayak.job_type == 'individuals_sahayak':
                total_amount += float(booking.total_amount) if booking.total_amount else 0
                count_male += int(booking.count_male) if booking.count_male else 0
                count_female += int(booking.count_female) if booking.count_female else 0
                total_amount_sahayak += int(booking.total_amount_sahayak) if booking.total_amount_sahayak else 0
                payment_your += float(booking.payment_your) if booking.payment_your else 0
                fawda_fee += float(booking.fawda_fee) if booking.fawda_fee else 0
                booking_data.append({
                    'id': booking.id,
                    'datetime': booking.jobsahayak.datetime,
                    'status': booking.status,
                    'count_male': booking.count_male,
                    'count_female': booking.count_female,
                    'total_amount': booking.total_amount,
                    'total_amount_sahayak': booking.total_amount_sahayak,
                    # 'total_amount_theka': booking.total_amount_theka,
                    # 'total_amount_machine': booking.total_amount_machine,
                    'payment_your': booking.payment_your,
                    'fawda_fee': booking.fawda_fee,
                    'booking_user_id':booking.booking_user.id,
                    'datetime':booking.jobsahayak.datetime,
                    'discription':booking.jobsahayak.description,
                    'land_area':booking.jobsahayak.land_area,
                    'pay_for_male':booking.jobsahayak.pay_amount_male,
                    'pay_for_female':booking.jobsahayak.pay_amount_female,
                    'num_days':booking.jobsahayak.num_days,
                    'job_type':booking.jobsahayak.job_type,
                    'user_status':booking.booking_user.status,
                    'sahayak_name':booking.booking_user.profile.name,
                    'sahayak_village':booking.booking_user.profile.village,
                    'sahayak_mobile_no':booking.booking_user.mobile_no
                })
            else:
                booking_data.append({
                    'booking_id':booking.id,
                    'status':booking.status,
                    'total_amount':booking.total_amount,
                    'total_amount_theka':booking.total_amount_theka,
                    'payment_your':booking.payment_your,
                    'datetime':booking.jobsahayak.datetime,
                    'land_area':booking.jobsahayak.land_area,
                    'discription':booking.jobsahayak.description,
                    'fawda_fee':booking.fawda_fee,
                    'booking_user_id':booking.booking_user.id,
                    'job_type':booking.jobsahayak.job_type,
                    'user_status':booking.booking_user.status,
                    'thekedar_name':booking.booking_user.profile.name,
                    'thekedar_village':booking.booking_user.profile.village,
                    'thekedar_mobile_no':booking.booking_user.mobile_no
                })    
        response_data = {
            'total_amount': total_amount,
            'count_male': count_male,
            'count_female': count_female,
            'total_amount_sahayak': total_amount_sahayak,
            'payment_your': payment_your,
            'fawda_fee': fawda_fee,
            'bookings': booking_data,
        }
        return Response(response_data)

class MyBookingDetailsMachine(APIView):
    def get(self,request,format=None):
        bookings=JobBooking.objects.filter(jobmachine__grahak=request.user,status='Accepted')
        booking_data=[]
        for booking in bookings:
            booking_data.append({
                'booking_id':booking.id,
                'landprepaation':booking.jobmachine.landpreparation.name,
                'harvesting':booking.jobmachine.harvesting.name,
                'sowing':booking.jobmachine.sowing.name,
                'datetime':booking.jobmachine.datetime,
                'land_area':booking.jobmachine.land_area,
                'total_amount':booking.jobmachine.total_amount,
                'total_amount_machine':booking.jobmachine.total_amount_machine,
                'payment_your':booking.jobmachine.payment_your,
                'status':booking.status,
                'machine_malik_name':booking.booking_user.profile.name,
                'machine_malik_village':booking.booking_user.profile.village,
                'machine_malik_mobile_no':booking.booking_user.mobile_no,
                'booking_user_id':booking.booking_user.id
                
            })
        return Response(booking_data)    

class MyBookingPendingDetailsSahayak(APIView):
    def get(self,request,format=None):
       booking=JobSahayak.objects.filter(grahak=request.user,status='Pending')
       serializer=JobSahaykSerialiser(booking,many=True)
       return Response(serializer.data)
    

class MyBookingPendingDetailsMachine(APIView):
    def get(self,request,format=None):
        booking=JobMachine.objects.filter(grahak=request.user,status='Pending')    
        serializer=GetJobMachineSerializer(booking,many=True)
        return Response(serializer.data)

# class AcceptedJobs(APIView):
#     permission_classes=[IsAuthenticated,]
#     def get(self,request,format=None):
#         bookings = JobBooking.objects.filter(booking_user=request.user, status='Accepted')
#         jobs = []
#         for booking in bookings:
#             job = {
#                 'id': booking.id,
#                 'sahayak_name': booking.jobsahayak.name,
#                 'machine_name': booking.jobmachine.name,
#                 'date_booked': booking.date_booked,
#                 'status': booking.status,
#                 'description': f"Job to operate {booking.jobmachine.name} with {booking.jobsahayak.name} on {booking.date_booked.strftime('%d %B, %Y')}"
#             }
#             jobs.append(job)
#         return Response({'jobs': jobs})

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def my_accepted_jobs(request):
#     bookings = JobBooking.objects.filter(booking_user=request.user, status='Accepted')
#     jobs = []
#     for booking in bookings:
#         job = {
#             'id': booking.id,
#             'sahayak_name': booking.jobsahayak.name,
#             'machine_name': booking.jobmachine.name,
#             'date_booked': booking.date_booked,
#             'status': booking.status,
#             'description': f"Job to operate {booking.jobmachine.name} with {booking.jobsahayak.name} on {booking.date_booked.strftime('%d %B, %Y')}"
#         }
#         jobs.append(job)
#     return Response({'jobs': jobs})