from django.shortcuts import render
from django.http import Http404
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
        if request.user.user_type == 'MachineMalik':
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
            job = JobSahayak.objects.get(pk=job_id,job_type='theke_pe_kam')
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
            job = JobSahayak.objects.get(pk=job_id,job_type='individuals_sahayak')
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
                                            jobsahayak=job,
                                            pay_amount_male=job.pay_amount_male,
                                            pay_amount_female=job.pay_amount_female
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
        booking.admin_commission=str(fawda_fee_amount *2)
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
        booking.admin_commission=str(fawda_fee_amount *2)
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
    booking.admin_commission=str(fawda_fee_amount *2)   
    booking.save()


class MyJobsDetais(APIView):
    permission_classes=[IsAuthenticated,]
    def get(self,request,format=None):
        if request.user.user_type == 'Sahayak' or request.user.user_type == 'MachineMalik':
            myjob_list=[]
            bookedjob=JobBooking.objects.all().filter(booking_user=request.user)
            for job in bookedjob:
                if job.jobsahayak:
                    if job.jobsahayak.job_type =='individuals_sahayak':
                        myjob_list.append({
                            "booking_id":job.id,
                            "job_type":job.jobsahayak.job_type,
                            "description":job.jobsahayak.description,
                            "village":job.jobsahayak.grahak.profile.village,
                            "land_area":job.jobsahayak.land_area,
                            "land_type":job.jobsahayak.land_type,
                            "pay_amount_male":job.pay_amount_male,
                            "pay_amount_female":job.pay_amount_female,
                            "fawda_fee":job.fawda_fee,
                            "count_male":job.count_male,
                            "count_female":job.count_female,
                            "payment_your":job.payment_your,
                            "total_amount_sahayak":job.total_amount_sahayak,
                            "num_days":job.jobsahayak.num_days,
                            "datetime":job.jobsahayak.datetime,
                            "grahak_name":job.jobsahayak.grahak.profile.name,
                            "grahak_phone":job.jobsahayak.grahak.mobile_no,
                            "status":job.status
                        })
                    else:
                        myjob_list.append({
                            "booking_id":job.id,
                            "job_type":job.jobsahayak.job_type,
                            "description":job.jobsahayak.description,
                            "village":job.jobsahayak.grahak.profile.village,
                            "datetime":job.jobsahayak.datetime,
                            "land_area":job.jobsahayak.land_area,
                            "land_type":job.jobsahayak.land_type,
                            "fawda_fee":job.fawda_fee,
                            "payment_your":job.payment_your,
                            "total_amount_theka":job.total_amount_theka,
                            "grahak_name":job.jobsahayak.grahak.profile.name,
                            "grahak_phone":job.jobsahayak.grahak.mobile_no,
                            "status":job.status
                        })
                else:
                    myjob_list.append({
                        "booking_id":job.id,
                        "job_type":job.jobmachine.job_type,
                        "description":job.jobmachine.description,
                        "village":job.jobmachine.grahak.profile.village,
                        "datetime":job.jobmachine.datetime,
                        "land_area":job.jobmachine.land_area,
                        "land_type":job.jobmachine.land_type,
                        "fawda_fee":job.fawda_fee,
                        "payment_your":job.payment_your,
                        "total_amount_machine":job.total_amount_machine,
                        "grahak_name":job.jobmachine.grahak.profile.name,
                        "grahak_phone":job.jobmachine.grahak.mobile_no,
                        "status":job.status 
                    })            
            
            return Response({'success':True,'data':myjob_list})
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
                    'user_status':booking.booking_user.user_type,
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
                    'user_status':booking.booking_user.user_type,
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
        bookings1=JobBooking.objects.filter(jobmachine__grahak=request.user,status='Accepted')
        booking_data1=[]
        for booking in bookings1:
            booking_data1.append({
                'booking_id':booking.id,
                'work_type':booking.jobmachine.work_type,
                'machine':booking.jobmachine.machine,
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
        return Response(booking_data1)    

class MyBookingPendingDetailsSahayak(APIView):
    def get(self,request,format=None):
       booking2=JobSahayak.objects.filter(grahak=request.user,status='Pending')
       serializer1=JobSahaykSerialiser(booking2,many=True)
       return Response(serializer1.data)
    

class MyBookingPendingDetailsMachine(APIView):
    def get(self,request,format=None):
        booking3=JobMachine.objects.filter(grahak=request.user,status='Pending')    
        serializer2=GetJobMachineSerializer(booking3,many=True)
        return Response(serializer2.data)



class MyBookingDetails(APIView):
    def get(self,request,format=None):
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
                    'booking_id': booking.id,
                    'id':booking.jobsahayak.id,
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
                    'pay_for_male':booking.pay_amount_male,
                    'pay_for_female':booking.pay_amount_female,
                    'num_days':booking.jobsahayak.num_days,
                    'job_type':booking.jobsahayak.job_type,
                    'user_status':booking.booking_user.user_type,
                    'sahayak_name':booking.booking_user.profile.name,
                    'sahayak_village':booking.booking_user.profile.village,
                    'sahayak_mobile_no':booking.booking_user.mobile_no
                })
            else:
                booking_data.append({
                    'booking_id':booking.id,
                    'id':booking.jobsahayak.id,
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
                    'user_status':booking.booking_user.user_type,
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
        bookings1=JobBooking.objects.filter(jobmachine__grahak=request.user,status='Accepted')
        booking_data1=[]
        for booking in bookings1:
            booking_data1.append({
                'booking_id':booking.id,
                'id':booking.jobmachine.id,
                'work_type':booking.jobmachine.work_type,
                'machine':booking.jobmachine.machine,
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
        booking2=JobSahayak.objects.filter(grahak=request.user,status='Pending')
        serializer1=JobSahaykSerialiser(booking2,many=True)
        booking3=JobMachine.objects.filter(grahak=request.user,status='Pending')    
        serializer2=GetJobMachineSerializer(booking3,many=True)
        return Response({
            'sahayk_booking_details':response_data,
            'machine_malik_booking_details':booking_data1,
            'sahayak_pending_booking_details':serializer1.data,
            'machine_malik_pending_booking_details':serializer2.data
        })



class RatingCreate(APIView):
    permission_classes=[IsAuthenticated,]
    def get(self, request,format=None):
        booking_job_id=request.data.get('booking_job')
        if not booking_job_id:
            return Response({'error':'booking_id required !'})
        try:
            rating = Rating.objects.get(booking_job_id=booking_job_id)
            serializer = RatingSerializer(rating)
            return Response(serializer.data)
        except Rating.DoesNotExist:
            return Response({'error': f'No rating found for booking_job with id {booking_job_id}'})
    
    def post(self, request):
        if request.user.user_type == 'Grahak':
            serializer = RatingSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors)
        else:
            return Response({'error':'only Grahak can post rating'})
        

class OngoingStatusApi(APIView):
    permission_classes=[IsAuthenticated,]
    def post(self,request,format=None):
        bookingid=request.data.get('booking_id')
        if not bookingid:
            return Response({'error':'booking_id required !'})
        if not bookingid.isdigit():
            return Response({'error':'booking_id must be numeric !'}) 
        if request.user.user_type == 'Grahak':
            try:
                job=JobBooking.objects.get(pk=bookingid)   
                job.status='Ongoing'
                job.save()
                return Response({'success':'changed status to Ongoing successfully !','status':job.status})
            except JobBooking.DoesNotExist:
                return Response({'error':'Booking does not exist !'})
        else:
            return Response({'error':'you are not Grahak,only Grahak can change status'})

class CompletedStatusApi(APIView):
    permission_classes=[IsAuthenticated,]
    def post(self,request,format=None):
        bookingid=request.data.get('booking_id')
        if not bookingid:
            return Response({'error':'booking_id required !'})
        if not bookingid.isdigit():
            return Response({'error':'booking_id must be numeric !'}) 
        if request.user.user_type == 'Grahak':
            try:
                job=JobBooking.objects.get(pk=bookingid)   
                job.status='Completed'
                job.save()
                return Response({'success':'changed status to Completed successfully !','status':job.status})
            except JobBooking.DoesNotExist:
                return Response({'error':'Booking does not exist !'})
        else:
            return Response({'error':'you are not Grahak,only Grahak can change status !'})        
        



# class RejectedBooking(APIView):
#     permission_classes=[IsAuthenticated,]
#     def post(self,request,format=None):
#         bookingid=request.data.get('booking_id')
#         count_male=request.data.get('count_male')
#         count_female=request.data.get('count_female')
#         status=request.data.get('status')

#         if not bookingid:
#             return Response({'error':'booking_id required !'})
#         if not bookingid.isdigit():
#             return Response({'error':'booking_id must be numeric !'})   
#         if not status:
#             return Response({'error':'status required !'}) 
#         if not status in ['Cancelled','Rejected','Cancelled-After-Payment','Rejected-After-Payment','Admin-Refunded']:
#             return Response({'error':'invilid status'})
#         if request.user.user_type == 'Sahayak':
#             try:
#                 job=JobBooking.objects.get(pk=bookingid)   
#             except JobBooking.DoesNotExist:
#                 return Response({'error':'Booking does not exist !'})
#             if job.jobsahayak:
#                 if job.jobsahayak.job_type == 'individual_sahayak':
#                     if not count_male and not count_female:
#                         return Response({'error':'count_male and count_female required !'})
#                     if not count_male.isdigit() and not count_female.isdigit():
#                         return Response({'error':'count_male and count_female should be numeric !'})
#                     if job.status == status:
#                         return Response({'msg':'status already up to date !'})    
#                     job.status=status
#                     job.save()
#                     if job.jobsahayak.status == 'Pending':     
#                         job.jobsahayak.count_male+=int(count_male)
#                         job.jobsahayak.count_female+=int(count_female)
#                         job.jobsahayak.save()
#                     else:
#                         job.jobsahayak.count_male=int(count_male) 
#                         job.jobsahayak.count_female=int(count_female)
#                         job.jobsahayak.status='Pending'   
#                         job.jobsahayak.save()
#                 else:
#                     job.jobsahayak.status='Pending'        
#                     job.jobsahayak.save()
#                     job.status=status
#                     job.save()
#         else:
#             return Response({'error':'you are not Sahayak'})
#         if request.user.user_type == 'MachineMalik':
#             pass     


 

            

# class RejectedThekePeKam(APIView):
#     def post(self,request,format=None):
#         pass 

# class RejectedMachineMalik(APIView):
#     def post(self,request,format=None):
#         pass 


# class CancelledPending(APIView):
#     def post(self,request,format=None):
#         pass

# class CancelledBooking(APIView):
#     def post(self,request,format=None):
#         pass        
