from django.shortcuts import render

# Create your views here.
from .models import *
from jobs.models import *
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from rest_framework.permissions import IsAuthenticated

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
        # booking.fawda_fee = str(fawda_fee_percentage)
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
    # booking.fawda_fee = str(fawda_fee_percentage)
    booking.total_amount = str(total_amount)
    booking.payment_your = str(payment_your)
    booking.total_amount_machine = str(total_amount_without_fawda)   
    booking.save()