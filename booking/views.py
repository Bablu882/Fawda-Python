from django.shortcuts import render
from django.http import Http404
# Create your views here.
from .models import *
from jobs.models import *
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from rest_framework.permissions import IsAuthenticated,AllowAny
from jobs.serializers import JobSahaykSerialiser,GetJobMachineSerializer
from django.shortcuts import get_object_or_404
from django.db.models import Q
from authentication.views import BearerTokenAuthentication
from rest_framework import status
from jobs.views import CustomPagination
from rest_framework.pagination import PageNumberPagination



class JobAcceptMachin(APIView):
    authentication_classes=[BearerTokenAuthentication,]
    permission_classes=[IsAuthenticated,]
    def post(self,request,format=None):
        if request.user.user_type == 'MachineMalik':
            job_id=request.data.get('job_id')
            if not job_id:
                return Response({'message':{'job_id required !'}})
            machin_user=request.user
            #check job is exist or not 
            try:
                job = JobMachine.objects.get(pk=job_id)
            except JobMachine.DoesNotExist:
                return Response({'message': {'Job does not exist !'}})
            if not job.status == 'Pending':
                return Response({'message':{'job already Accepted !'}})
            if JobBooking.objects.filter(jobmachine=job, booking_user=machin_user).exists():
                return Response({'message': {'Job is already accepted !'}})
            booking=JobBooking.objects.create(jobmachine=job,booking_user=machin_user,status='Accepted')
            update_booking_amount_machine(booking)
            get_job=JobMachine.objects.get(pk=job_id)
            get_job.status= 'Accepted'
            get_job.save()
            serial=JobBookingSerializers(booking)
            return Response({'message':'Job accepted successfully !','data':serial.data,'status':status.HTTP_200_OK})
        else:
            return Response({'message':{'you are not MachineMalik'}})    
         
class JobAcceptedSahayakTheka(APIView):
    authentication_classes=[BearerTokenAuthentication,]
    permission_classes=[IsAuthenticated,]
    def post(self,request,format=None):
        job_id=request.data.get('job_id')
        if not job_id:
            return Response({'message':{'job_id required !'}})
        sahayak_user=request.user
        if not request.user.user_type == 'Sahayak':
            return Response({'message':{'only sahayak can accept !'}})
        #check if job is exists or not 
        try:
            job = JobSahayak.objects.get(pk=job_id,job_type='theke_pe_kam')
        except JobSahayak.DoesNotExist:
            return Response({'message': {'Job does not exist !'}})
        if not job.status == 'Pending':
            return Response({'message':{'job already accepted !'}}) 
        if JobBooking.objects.filter(jobsahayak=job, booking_user=sahayak_user).exists():
            return Response({'message': {'Job is already accepted !'}})
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
        return Response({'message':'Job accepted !','data':serial.data,'status':status.HTTP_200_OK})
        
class JobAcceptIndividuals(APIView):
    authentication_classes=[BearerTokenAuthentication,]
    permission_classes=[IsAuthenticated,]
    def post(self, request, format=None):
       serializer = JobAcceptSerializer(data=request.data)
       if serializer.is_valid():
            job_id = serializer.validated_data['job_id']
            male = serializer.validated_data['count_male']
            female = serializer.validated_data['count_female']
            print(male,female)    
            count_male = int(male)
            count_female = int(female)
            individual_user = request.user
            if count_male ==0 and count_female==0:
                return Response({'message':{'count_male and count_female both can not be zero !'}})
            if not request.user.user_type == 'Sahayak':
                return Response({'message':{'only sahayak can accept !'}})
            # Check if job exists
            try:
                job = JobSahayak.objects.get(pk=job_id,job_type='individuals_sahayak')
            except JobSahayak.DoesNotExist:
                return Response({'message': {'Job does not exist !'}})
            if not job.status == 'Pending':
                return Response({'message':{'job already Accepted !'}})
            # Check if job is already booked by the user
            if JobBooking.objects.filter(jobsahayak=job, booking_user=individual_user).exists():
                return Response({'message': {'Job is already accepted !'}})
            # Check if there are enough available workers for the job
            if int(job.count_male) < count_male or int(job.count_female) < count_female:
                return Response({'message': {'Not enough sahayak available for this job !'}})

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

            return Response({'message': 'Job accepted successfully !', 'data': serializer.data,'status':status.HTTP_200_OK})
       else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
        
        
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
    authentication_classes=[BearerTokenAuthentication,]
    permission_classes=[IsAuthenticated,]
    PAGE_SIZE = 10
    def get(self,request,format=None):
        if request.user.user_type == 'Sahayak' or request.user.user_type == 'MachineMalik':
            myjob_list=[]
            bookedjob=JobBooking.objects.all().filter(booking_user=request.user).order_by('-id')
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
                        "status":job.status,
                        "work_type":job.jobmachine.work_type,
                        "machine":job.jobmachine.machine 
                    })            
            paginator = PageNumberPagination()
            paginator.page_size = self.PAGE_SIZE
            paginated_result = paginator.paginate_queryset(myjob_list, request)
            response_data = {'page': paginator.page.number, 'total_pages': paginator.page.paginator.num_pages, 'results': paginated_result}
            # Add next page URL to response
            if paginator.page.has_next():
                base_url = request.build_absolute_uri().split('?')[0]
                response_data['next'] = f"{base_url}?page={paginator.page.next_page_number()}"
                print(response_data)
            return Response({'success':True,'data':response_data})
                
        return Response({'message':{'you are not Sahayak or MachineMalik !'}})    


class MyBookingDetailsSahayak(APIView):
    authentication_classes=[BearerTokenAuthentication,]
    permission_classes=[IsAuthenticated,]
    def get(self, request):
        if request.user.user_type == 'Grahak':
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
                        'description':booking.jobsahayak.description,
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
                        'description':booking.jobsahayak.description,
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
        return Response({'message':{'you are not grahak !'}})

class MyBookingDetailsMachine(APIView):
    authentication_classes=[BearerTokenAuthentication,]
    permission_classes=[IsAuthenticated,]
    def get(self,request,format=None):
        if request.user.user_type == 'Grahak':
            return Response({'message':{'you are not Grahak !'}})
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
    authentication_classes=[BearerTokenAuthentication,]
    permission_classes=[IsAuthenticated,]
    def get(self,request,format=None):
        if not request.user.user_type=='Grahak':
            return Response({'message':{'you are not Grahak !'}})
        bookings = JobBooking.objects.filter(jobsahayak__grahak=request.user, status__in=['Accepted','Booked','Ongoing','Completed']).order_by('-id')
        booking_data = {}
        for booking in bookings:
            job_id = booking.jobsahayak.id
            if job_id not in booking_data:
                booking_data[job_id] = {
                    'total_amount': 0,
                    'count_male': 0,
                    'count_female': 0,
                    'total_amount_sahayak': 0,
                    'payment_your': 0,
                    'fawda_fee': 0,
                    'job_type': booking.jobsahayak.job_type,
                    'sahayaks': []
                }
            if booking.jobsahayak.job_type == 'individuals_sahayak':
                booking_data[job_id]['total_amount'] += float(booking.total_amount) if booking.total_amount else 0
                booking_data[job_id]['count_male'] += int(booking.count_male) if booking.count_male else 0
                booking_data[job_id]['count_female'] += int(booking.count_female) if booking.count_female else 0
                booking_data[job_id]['total_amount_sahayak'] += int(booking.total_amount_sahayak) if booking.total_amount_sahayak else 0
                booking_data[job_id]['payment_your'] += float(booking.payment_your) if booking.payment_your else 0
                booking_data[job_id]['fawda_fee'] += float(booking.fawda_fee) if booking.fawda_fee else 0
                booking_data[job_id]['sahayaks'].append({
                    'booking_id': booking.id,
                    'job_id':booking.jobsahayak.id,
                    'job_number':booking.jobsahayak.job_number,
                    'status':booking.status,
                    'booking_user_id': booking.booking_user.id,
                    'sahayak_name': booking.booking_user.profile.name,
                    'sahayak_village': booking.booking_user.profile.village,
                    'sahayak_mobile_no': booking.booking_user.mobile_no,
                    'pay_amount_male': booking.jobsahayak.pay_amount_male,
                    'pay_amount_female': booking.jobsahayak.pay_amount_female,
                    'count_male': booking.count_male,
                    'count_female': booking.count_female,
                    'job_type':booking.jobsahayak.job_type,
                    'num_days':booking.jobsahayak.num_days,
                    'datetime':booking.jobsahayak.datetime,
                    'description':booking.jobsahayak.description,
                    'land_area':booking.jobsahayak.land_area,
                    'land_type':booking.jobsahayak.land_type
                })
            else:
                booking_data[job_id]['total_amount'] += float(booking.total_amount) if booking.total_amount else 0
                booking_data[job_id]['total_amount_sahayak'] += float(booking.total_amount_theka) if booking.total_amount_theka else 0
                booking_data[job_id]['payment_your'] += float(booking.payment_your) if booking.payment_your else 0
                booking_data[job_id]['fawda_fee'] += float(booking.fawda_fee) if booking.fawda_fee else 0
                booking_data[job_id]['sahayaks'].append({
                    'booking_id': booking.id,
                    'job_id':booking.jobsahayak.id,
                    'job_number':booking.jobsahayak.job_number,
                    'status':booking.jobsahayak.status,
                    'booking_user_id': booking.booking_user.id,
                    'thekedar_name': booking.booking_user.profile.name,
                    'thekedar_village': booking.booking_user.profile.village,
                    'thekedar_mobile_no': booking.booking_user.mobile_no,
                    'datetime':booking.jobsahayak.datetime,
                    'job_type':booking.jobsahayak.job_type,
                    'description':booking.jobsahayak.description,
                })

        response_data = {
            'bookings': list(booking_data.values())
        }
        bookings1=JobBooking.objects.filter(jobmachine__grahak=request.user,status__in=['Accepted','Booked','Ongoing','Completed']).order_by('-id')
        booking_data1=[]
        for booking in bookings1:
            booking_data1.append({
                'booking_id':booking.id,
                'job_id':booking.jobmachine.id,
                'work_type':booking.jobmachine.work_type,
                'job_type':booking.jobmachine.job_type,
                'machine':booking.jobmachine.machine,
                'datetime':booking.jobmachine.datetime,
                'land_area':booking.jobmachine.land_area,
                'total_amount':booking.total_amount,
                'total_amount_machine':booking.total_amount_machine,
                'payment_your':booking.payment_your,
                'fawda_fee':booking.fawda_fee,
                'status':booking.status,
                'machine_malik_name':booking.booking_user.profile.name,
                'machine_malik_village':booking.booking_user.profile.village,
                'machine_malik_mobile_no':booking.booking_user.mobile_no,
                'booking_user_id':booking.booking_user.id,
                'job_number':booking.jobmachine.job_number,
                'land_type':booking.jobmachine.land_type
                
            })
        booking2=JobSahayak.objects.filter(grahak=request.user,status='Pending').order_by('-id')
        serializer1=JobSahaykSerialiser(booking2,many=True)
        booking3=JobMachine.objects.filter(grahak=request.user,status='Pending').order_by('-id')   
        serializer2=GetJobMachineSerializer(booking3,many=True)
        
        return Response({
            'sahayk_booking_details':response_data,
            'machine_malik_booking_details':booking_data1,
            'sahayak_pending_booking_details':serializer1.data,
            'machine_malik_pending_booking_details':serializer2.data
        })



class RatingCreate(APIView):
    authentication_classes=[BearerTokenAuthentication,]
    permission_classes=[IsAuthenticated,]
    def get(self, request,format=None):
        booking_job_id=request.data.get('booking_id')
        if not request.user.user_type == 'Grahak':
            return Response({'message':{'only grahak can give rating !'}})
        if not booking_job_id:
            return Response({'message':{'booking_id required !'}})
        try:
            rating = Rating.objects.get(booking_job_id=booking_job_id)
            serializer = RatingSerializer(rating)
            return Response(serializer.data)
        except Rating.DoesNotExist:
            return Response({'message': f'No rating found for booking_job with id {booking_job_id}'})
    
    def post(self, request):
        if request.user.user_type == 'Grahak':
            job_id = request.data.get('job_id')
            job_number=request.data.get('job_number')
            rating_value = request.data.get('rating')
            comment_value = request.data.get('comment', '')
            if not job_id or not job_number:
                return Response({'message':{'job_id and job_number both is required !'}})
            job_bookings = JobBooking.objects.filter(Q((Q(jobsahayak__id=job_id) & Q(jobsahayak__job_number=job_number)) | (Q(jobmachine__id=job_id) & Q(jobmachine__job_number=job_number))))
            for booking in job_bookings:
                if booking.jobsahayak:
                    if not booking.jobsahayak.grahak == request.user:
                        return Response({'message':{'unauthorised user !'}})
                    if not booking.status == 'Completed':
                        return Response({'message':{'rating can not created it should be completed before !'}})    
                    if Rating.objects.filter(booking_job=booking).exists():
                        return Response({'message':{'Rating already created !'}})    
                    Rating.objects.create(
                        booking_job=booking,
                        rating=rating_value,
                        comment=comment_value
                    )    
                else:
                    if not booking.jobmachine.grahak == request.user:
                        return Response({'message':{'unauthorised user !'}}) 
                    if not booking.status == 'Completed':
                        return Response({'message':{'rating can not be created it should be Commpleted before !'}})  
                    if Rating.objects.filter(booking_job=booking).exists():
                        return Response({'message':{'Rating already created !'}})    
                    Rating.objects.create(
                        booking_job=booking,
                        rating=rating_value,
                        comment=comment_value
                    )         
            return Response({'message':'Rating created successfully!','status':status.HTTP_201_CREATED})

        
        
class RatingGet(APIView):
    permission_classes=[BearerTokenAuthentication,]
    permission_classes=[AllowAny,]
    def post(self, request,format=None):
        booking_job_id=request.data.get('booking_job')
        if not booking_job_id:
            return Response({'message':{'booking_id required !'}})
        try:
            rating = Rating.objects.get(booking_job_id=booking_job_id)
            serializer = RatingSerializer(rating)
            return Response(serializer.data)
        except Rating.DoesNotExist:
            return Response({'message': f'No rating found for booking_job with id {booking_job_id}'})

        
class OngoingStatusApi(APIView):
    authentication_classes = [BearerTokenAuthentication,]
    permission_classes = [IsAuthenticated,]
    def post(self, request,format=None):
        job_id=request.data.get('job_id')
        job_number=request.data.get('job_number')
        if not job_id or not job_number:
            return Response({'message': {'job_id and job_number both is required !'}})
        if not job_id.isdigit():
            return Response({'message': {'job_id must be numeric !'}})
        if request.user.user_type != 'Grahak':
            return Response({'message': {'you are not Grahak, only Grahak can change status'}})
        
        # if not JobSahayak.objects.filter(pk=job_id).exists() or not JobMachine.objects.filter(pk=job_id).exists():
        #     return Response({'message':'job_id does not exists'}) 
        job_bookings = JobBooking.objects.filter(Q((Q(jobsahayak__id=job_id) & Q(jobsahayak__job_number=job_number)) | (Q(jobmachine__id=job_id) & Q(jobmachine__job_number=job_number))))

        is_booked = False
        for job in job_bookings:
            if job.status == 'Ongoing':
                return Response({'message': {'Status already up to date!'}})
            if job.status != 'Booked':
                continue
            is_booked = True

            if job.jobsahayak:
                if job.jobsahayak.grahak == request.user:
                    if not job.jobsahayak.status == 'Pending':
                        job.jobsahayak.status = 'Ongoing'
                        job.jobsahayak.save()
                else:
                    return Response({'message': {'unauthorized grahak !'}})
            else:
                if job.jobmachine.grahak == request.user:
                    if not job.jobmachine.status == 'Pending':
                        job.jobmachine.status = 'Ongoing'
                        job.jobmachine.save()
                else:
                    return Response({'message': {'unauthorized grahak !'}})

            job.status = 'Ongoing'
            job.save()

        if not is_booked:
            return Response({'message': {'Booking status cannot be updated it should be Booked before !'}})

        return Response({'message': 'changed status to Ongoing successfully!','booking-status':'Ongoing','status':status.HTTP_200_OK})


class CompletedStatusApi(APIView):
    authentication_classes = [BearerTokenAuthentication,]
    permission_classes = [IsAuthenticated,]
    def post(self, request,format=None):
        job_id=request.data.get('job_id')
        job_number=request.data.get('job_number')
        if not job_id or not job_number:
            return Response({'message': {'job_id and job_number both is required !'}})
        if not job_id.isdigit():
            return Response({'message': {'job_id must be numeric !'}})
        if request.user.user_type != 'Grahak':
            return Response({'message': {'you are not Grahak, only Grahak can change status'}})
        
        # if not JobSahayak.objects.filter(pk=job_id).exists() or not JobMachine.objects.filter(pk=job_id).exists():
        #     return Response({'message':'job_id does not exists'}) 
        job_bookings = JobBooking.objects.filter(Q((Q(jobsahayak__id=job_id) & Q(jobsahayak__job_number=job_number)) | (Q(jobmachine__id=job_id) & Q(jobmachine__job_number=job_number))))

        is_ongoing = False
        for job in job_bookings:
            if job.status == 'Completed':
                return Response({'message': {'Status already up to date!'}})
            if job.status != 'Ongoing':
                continue
            is_ongoing = True

            if job.jobsahayak:
                if job.jobsahayak.grahak == request.user:
                    if not job.jobsahayak.status == 'Pending':
                        job.jobsahayak.status = 'Completed'
                        job.jobsahayak.save()
                else:
                    return Response({'message': {'unauthorized grahak !'}})
            else:
                if job.jobmachine.grahak == request.user:
                    if not job.jobmachine.status == 'Pending':
                        job.jobmachine.status = 'Completed'
                        job.jobmachine.save()
                else:
                    return Response({'message': {'unauthorized grahak !'}})

            job.status = 'Completed'
            job.save()

        if not is_ongoing:
            return Response({'message': {'Booking status cannot be updated it should be Ongoing before !'}})

        return Response({'message': 'changed status to Completed successfully!','booking-status':'Completed','status':status.HTTP_200_OK})
        


class RejectedBooking(APIView):
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = RejectedBookingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            job = JobBooking.objects.get(pk=data['booking_id'])
        except JobBooking.DoesNotExist:
            return Response({'message': {'Booking does not exist !'}})

        if request.user.user_type=='Sahayak' or request.user.user_type=='MachineMalik':
            # return Response({'message': 'You are not a Sahayak or MachineMalik.'})

            if request.user != job.booking_user:
                return Response({'message': {'You are not associated with this booking.'}})
            if job.status ==data['status']:
                return Response({'message':{'status already up to date'}})
            if job.status == 'Booked':
                if data['status'] == 'Rejected-After-Payment':
                    if job.status == data['status']:
                        return Response({'message': {'Status already up to date.'}})
                    job.status = data['status']
                    job.save()
                else:
                    return Response({'message': {'Cannot change status to {} it should be Accepted before'.format(data['status'])}})
            elif job.status == 'Accepted':
                if data['status'] == 'Rejected':
                    if job.status == data['status']:
                        return Response({'message': {'Status already up to date.'}})
                    job.status = data['status']
                    job.save()
                else:
                    return Response({'message': {'Cannot change status to {} it should be Booked before'.format(data['status'])}})
            else:
                return Response({'message': {'Job cannot be rejected, it should be Accepted or Booked first.'}})

            if job.jobsahayak:
                if job.jobsahayak.job_type == 'individuals_sahayak':

                    if job.jobsahayak.status == 'Pending':
                        job.jobsahayak.count_male = int(job.count_male)+int(job.jobsahayak.count_male)
                        job.jobsahayak.count_female = int(job.count_female)+int(job.jobsahayak.count_female)
                    else:
                        job.jobsahayak.count_male = int(job.count_male)
                        job.jobsahayak.count_female = int(job.count_female)
                        job.jobsahayak.status = 'Pending'
                    job.jobsahayak.save()
                else:
                    if not job.jobsahayak.status == 'Pending':
                        job.jobsahayak.status='Pending'
                        job.jobsahayak.save()    
            # elif job.jobsahayak and job.jobsahayak.status =='theke_pe_kam':
            #     if not job.jobsahayak.status == 'Pending':
            #         job.jobsahayak.status='Pending'
            #         job.jobsahayak.save()   
            else:
                if not job.jobmachine.status == 'Pending':
                    job.jobmachine.status = 'Pending'
                    job.jobmachine.save()
                # job.save()
        else:
            return Response({'errror':{'you are not sahayak or machine malik'}})
        return Response({'message': {'Booking rejected successfully.'}})

###-------------------------------------------------------------------------------------###
# class RejectedBooking(APIView):
#     authentication_classes=[BearerTokenAuthentication,]
#     permission_classes=[IsAuthenticated,]
#     def post(self,request,format=None):
#         bookingid=request.data.get('booking_id')
#         count_male=request.data.get('count_male')
#         print(type(count_male))
#         count_female=request.data.get('count_female')
#         status=request.data.get('status')
#         if not bookingid:
#             return Response({'message':'booking_id required !'})
#         if not bookingid.isdigit():
#             return Response({'message':'booking_id must be numeric !'})   
#         if not status:
#             return Response({'message':'status required !'}) 
#         if not status in ['Rejected','Rejected-After-Payment']:
#             return Response({'message':'invilid status'})
#         if request.user.user_type == 'Sahayak' or request.user.user_type == 'MachineMalik':
#             try:
#                 job=JobBooking.objects.get(pk=bookingid)   
#             except JobBooking.DoesNotExist:
#                 return Response({'message':'Booking does not exist !'})
#             if job.jobsahayak:
#                 if not request.user == job.booking_user:
#                     return Response({'message':'you are not existing Sahayak of this booking !'})
#                 if job.jobsahayak.job_type == 'individuals_sahayak':
#                     if not count_male and not count_female:
#                         return Response({'message':'count_male and count_female required !'})
#                     if not count_male.isdigit() and not count_female.isdigit():
#                         return Response({'message':'count_male and count_female should be numeric !'})
#                     if job.status == status:
#                         return Response({'message':'status already up to date !'})    
#                     if not job.status in ['Accepted','Booked']:
#                         return Response({'message':'job can not reject it should be Accepted or Booked before !'})    
#                     job.status=status
#                     job.save()
#                     if job.jobsahayak.status == 'Pending':     
#                         job.jobsahayak.count_male=int(job.jobsahayak.count_male)+int(job.count_male)
#                         job.jobsahayak.count_female=int(job.jobsahayak.count_female)+int(job.count_female)
#                         job.jobsahayak.save()
#                     else:
#                         job.jobsahayak.count_male=int(count_male) 
#                         job.jobsahayak.count_female=int(count_female)
#                         job.jobsahayak.status='Pending'   
#                         job.jobsahayak.save()
#                 else:
#                     if not job.status in ['Accepted','Booked']:
#                         return Response({'message':'job can not reject it should Accepted or Booked before !'})
#                     job.jobsahayak.status='Pending'        
#                     job.jobsahayak.save()
#                     job.status=status
#                     job.save()
#             else:
#                 if not request.user == job.booking_user:
#                     return Response({'message':'you are not existing MachineMalik of this booking !'})
#                 job.jobmachine.status='Pending'
#                 if job.jobmachine.status == status:
#                     return Response({'message':'status already up to date !'})
#                 if not job.status in ['Accepted','Booked']:
#                     return Response({'message':'job can not be rejected it should be Accepted or Booked before !'})    
#                 job.status=status
#                 job.jobmachine.save()
#                 job.save()
#                 return Response({'message':'status updated successfully !'})    
#         else:
#             return Response({'message':'you are not Sahayak or MachineMalik'})
            
#         # Add a return statement here
#         return Response({'msg':'Booking rejected successfully.'})



# class CancellationBookingJob(APIView):
#     authentication_classes=[BearerTokenAuthentication,]
#     permission_classes=[IsAuthenticated,]
#     def post(self,request,format=None):
#         jobid=request.data.get('job_id')
#         jobnumber=request.data.get('job_number')
#         status=request.data.get('status')
#         if not jobid and not jobid.isdigit():
#             return Response({'message':'job_id is required in numeric !'})
#         if not jobnumber:
#             return Response({'message':'job_number required !'})
#         if JobBooking.objects.filter(Q(jobsahayak__job_number=jobnumber, jobsahayak_id=jobid) | Q(jobmachine__job_number=jobnumber, jobmachine_id=jobid)).exists():
#             job_bookings = JobBooking.objects.filter(Q((Q(jobsahayak__id=jobid) & Q(jobsahayak__job_number=jobnumber)) | (Q(jobmachine__id=jobid) & Q(jobmachine__job_number=jobnumber))))
#             for booking in job_bookings:
#                 if booking.jobsahayak:
#                     if not booking.jobsahayak.grahak == request.user:
#                         return Response({'message':'unauthorised user !'})
#                     if not booking.status in ['Accepted','Booked']:
#                         return Response({'message':f"job already {booking.status} you can not cancel the job !"})    
#                     if booking.status == status:
#                         return Response({'message':'status already up to date !'})    
#                     booking.status = status
#                     booking.save()    
#                 else:
#                     if not booking.jobmachine.grahak == request.user:
#                         return Response({'message':'unauthorised user !'})
#                     if not booking.status in ['Accepted','Booked']:
#                         return Response({'message':f"job already {booking.status} you can not cancel the job !"})    
#                     if booking.status ==status:
#                         return Response({'message':'status already up to date !'})    
#                     booking.status=status
#                     booking.save()        
#         elif JobSahayak.objects.filter(pk=jobid,job_number=jobnumber).exists():
#             get_job=get_object_or_404(JobSahayak,pk=jobid,job_number=jobnumber)
#             if get_job.status == 'Cancelled':
#                 return Response({'message':'status already up to date !'})
#             if not request.user == get_job.grahak:
#                     return Response({'message':'you are not existing with this job !'})
#             if not get_job.status in  ['Pending','Accepted','Booked']:
#                 return Response({'message':f"job already {get_job.status} you can not cancel"})        
#             get_job.status='Cencelled'
#             get_job.save()
#             return Response({'message':'status updated successfully !'})
#         elif JobMachine.objects.filter(pk=jobid,job_number=jobnumber).exists():
#             get_job1=get_object_or_404(JobMachine,pk=jobid,job_number=jobnumber)
#             if get_job1.status == 'Cancelled':
#                 return Response({'message':'status already up to date !'})    
#             if not request.user == get_job1.grahak:
#                     return Response({'message':'you are not existing with this job !'})
#             if not get_job1.status in  ['Accepted','Pending','Booked']:
#                 return Response({'message':f"job already {get_job1.status} you can not cancel !"})        
#             get_job1.status='Cencelled'
#             get_job1.save()
#             return Response({'message':'status updated successfully !'})
#         else:
#             return Response({'message':'invilid job_id or job_number'}) 

###--------------------------------------------------------------------------------------###


class CancellationBookingJob(APIView):
    authentication_classes=[BearerTokenAuthentication,]
    permission_classes=[IsAuthenticated,]
    def post(self, request, format=None):
        serializer = CancellationBookingJobSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        job_id = validated_data['job_id']
        job_number = validated_data['job_number']
        status = validated_data['status']

        if JobBooking.objects.filter(Q(jobsahayak__job_number=job_number, jobsahayak_id=job_id) | Q(jobmachine__job_number=job_number, jobmachine_id=job_id)).exists():
            job_bookings = JobBooking.objects.filter(Q((Q(jobsahayak__id=job_id) & Q(jobsahayak__job_number=job_number)) | (Q(jobmachine__id=job_id) & Q(jobmachine__job_number=job_number))))
            for booking in job_bookings:
                if booking.status == status:
                    return Response({'message':{'already up to date'}})
                if booking.jobsahayak:
                    if not booking.jobsahayak.grahak == request.user:
                        return Response({'message': {'unauthorised user !'}})
                    if status == 'Cancelled-After-Payment':
                        if booking.status == 'Booked':
                            booking.status = status
                            booking.save()
                            booking.jobsahayak.status='Cancelled'
                            booking.jobsahayak.save()
                        else:
                            return Response({'message': {'Job must be in Booked status to update to Cancelled-After-Payment'}})
                    else:
                        if not booking.status == 'Accepted':
                            return Response({'message': {'Job must be in Accepted status to update to Cancelled'}})
                        booking.status = status
                        booking.save()
                        booking.jobsahayak.status='Cancelled'
                        booking.jobsahayak.save()
                else:
                    if not booking.jobmachine.grahak == request.user:
                        return Response({'message': {'unauthorised user !'}})
                    if status == 'Cancelled-After-Payment':
                        if booking.status == 'Booked':
                            booking.status = status
                            booking.save()
                            booking.jobmachine.status='Cancelled'
                            booking.jobmachine.save()
                        else:
                            return Response({'message': {'Job must be in Booked status to update to Cancelled-After-Payment'}})
                    else:
                        if not booking.status == 'Accepted':
                            return Response({'message': {'Job must be in Accepted status to update to Cancelled'}})
                        booking.status = status
                        booking.save()
                        booking.jobmachine.status='Cancelled'
                        booking.jobmachine.save()
        elif JobSahayak.objects.filter(pk=job_id, job_number=job_number).exists():
            get_job = get_object_or_404(JobSahayak, pk=job_id, job_number=job_number)
            if get_job.status == 'Cancelled':
                return Response({'message': {'status already up to date !'}})
            if not request.user == get_job.grahak:
                return Response({'message': {'you are not existing user with this job !'}})
            if get_job.status not in ['Pending', 'Accepted', 'Booked']:
                return Response({'message': f"job already {get_job.status} you can not cancel"})
            get_job.status = 'Cancelled'
            get_job.save()
        elif JobMachine.objects.filter(pk=job_id, job_number=job_number).exists():
            get_job = get_object_or_404(JobMachine, pk=job_id, job_number=job_number)
            if get_job.status == 'Cancelled':
                return Response({'message': {'status already up to date !'}})
            if not request.user == get_job.grahak:
                return Response({'message': {'you are not existing user with this job !'}})
            if get_job.status not in ['Accepted', 'Pending', 'Booked']:
                return Response({'message': f"job already {get_job.status} you can not cancel !"})
            get_job.status = 'Cancelled'
            get_job.save()
        else:
            return Response({'message': {'invalid job_id or job_number'}})

        return Response({'message': {'status updated successfully !'}})



###-----------------------------------------------------------------------------------###
def getrating(booking_id):
    try:
        rating=Rating.objects.get(booking_job=booking_id)
    except Rating.DoesNotExist:
        return Response({'message':{'does not exist'}}) 
    return {'rating': rating.rating,'comment':rating.comment}   


class MyBookingDetailsHistory(APIView):
    authentication_classes=[BearerTokenAuthentication,]
    permission_classes=[IsAuthenticated,]
    def get(self,request,format=None):
        if not request.user.user_type=='Grahak':
            return Response({'message':{'you are not Grahak !'}})
        ##booking history Completed--------------Sahayak
        booking_data_machine=[]
        booking_data_sahayak=[]
        bookings_completed = JobBooking.objects.filter(jobsahayak__grahak=request.user, status__in=['Completed']).order_by('-id')
        booking_data = {}
        for booking in bookings_completed:
            job_id = booking.jobsahayak.id
            if job_id not in booking_data:
                booking_data[job_id] = {
                    'total_amount': 0,
                    'count_male': 0,
                    'count_female': 0,
                    'total_amount_sahayak': 0,
                    'payment_your': 0,
                    'fawda_fee': 0,
                    'job_type': booking.jobsahayak.job_type,
                    'sahayaks': []
                }
                
            if booking.jobsahayak.job_type == 'individuals_sahayak':
                booking_data[job_id]['total_amount'] += float(booking.total_amount) if booking.total_amount else 0
                booking_data[job_id]['count_male'] += int(booking.count_male) if booking.count_male else 0
                booking_data[job_id]['count_female'] += int(booking.count_female) if booking.count_female else 0
                booking_data[job_id]['total_amount_sahayak'] += int(booking.total_amount_sahayak) if booking.total_amount_sahayak else 0
                booking_data[job_id]['payment_your'] += float(booking.payment_your) if booking.payment_your else 0
                booking_data[job_id]['fawda_fee'] += float(booking.fawda_fee) if booking.fawda_fee else 0
                booking_data[job_id]['sahayaks'].append({
                    'booking_id': booking.id,
                    'job_id':booking.jobsahayak.id,
                    'job_number':booking.jobsahayak.job_number,
                    'status':booking.status,
                    'booking_user_id': booking.booking_user.id,
                    'sahayak_name': booking.booking_user.profile.name,
                    'sahayak_village': booking.booking_user.profile.village,
                    'sahayak_mobile_no': booking.booking_user.mobile_no,
                    'pay_amount_male': booking.jobsahayak.pay_amount_male,
                    'pay_amount_female': booking.jobsahayak.pay_amount_female,
                    'count_male': booking.count_male,
                    'count_female': booking.count_female,
                    'job_type':booking.jobsahayak.job_type,
                    'num_days':booking.jobsahayak.num_days,
                    'datetime':booking.jobsahayak.datetime,
                    'description':booking.jobsahayak.description,
                    'land_area':booking.jobsahayak.land_area,
                    'land_type':booking.jobsahayak.land_type,
                    'rating':getrating(booking.id)['rating'] if Rating.objects.filter(booking_job=booking.id).exists() else "",
                    'comment':getrating(booking.id)['comment'] if Rating.objects.filter(booking_job=booking.id).exists() else ""
                    
                })
                
               
            else:
                booking_data[job_id]['total_amount'] += float(booking.total_amount) if booking.total_amount else 0
                booking_data[job_id]['total_amount_sahayak'] += float(booking.total_amount_theka) if booking.total_amount_theka else 0
                booking_data[job_id]['payment_your'] += float(booking.payment_your) if booking.payment_your else 0
                booking_data[job_id]['fawda_fee'] += float(booking.fawda_fee) if booking.fawda_fee else 0
                booking_data[job_id]['sahayaks'].append({
                    'booking_id': booking.id,
                    'job_id':booking.jobsahayak.id,
                    'job_number':booking.jobsahayak.job_number,
                    'status':booking.status,
                    'booking_user_id': booking.booking_user.id,
                    'thekedar_name': booking.booking_user.profile.name,
                    'thekedar_village': booking.booking_user.profile.village,
                    'thekedar_mobile_no': booking.booking_user.mobile_no,
                    'datetime':booking.jobsahayak.datetime,
                    'job_type':booking.jobsahayak.job_type,
                    'description':booking.jobsahayak.description,
                    'rating':getrating(booking.id)['rating'] if Rating.objects.filter(booking_job=booking.id).exists() else "",
                    'comment':getrating(booking.id)['comment'] if Rating.objects.filter(booking_job=booking.id).exists() else ""
                })

        response_data_completed = {
            'bookings_completed': list(booking_data.values())
        }
        ##Booking history Completed -----------------machine
        bookings1=JobBooking.objects.filter(jobmachine__grahak=request.user,status__in=['Completed']).order_by('-id')
        for booking in bookings1:
            booking_data_machine.append({
                'booking_id':booking.id,
                'job_id':booking.jobmachine.id,
                'work_type':booking.jobmachine.work_type,
                'job_type':booking.jobmachine.job_type,
                'machine':booking.jobmachine.machine,
                'datetime':booking.jobmachine.datetime,
                'land_area':booking.jobmachine.land_area,
                'total_amount':booking.total_amount,
                'total_amount_machine':booking.total_amount_machine,
                'payment_your':booking.payment_your,
                'fawda_fee':booking.fawda_fee,
                'status':booking.status,
                'machine_malik_name':booking.booking_user.profile.name,
                'machine_malik_village':booking.booking_user.profile.village,
                'machine_malik_mobile_no':booking.booking_user.mobile_no,
                'booking_user_id':booking.booking_user.id,
                'job_number':booking.jobmachine.job_number,
                'land_type':booking.jobmachine.land_type,
                'rating':getrating(booking.id)['rating'] if Rating.objects.filter(booking_job=booking.id).exists() else "",
                'comment':getrating(booking.id)['comment'] if Rating.objects.filter(booking_job=booking.id).exists() else ""

                
            })
        ##Rejected booking history--------------Sahayak    
        bookings_rejected = JobBooking.objects.filter(jobsahayak__grahak=request.user, status__in=['Rejected']).order_by('-id')
        booking_data_rejected = {}
        for booking in bookings_rejected:
            job_id = booking.jobsahayak.id
            if job_id not in booking_data:
                booking_data_rejected[job_id] = {
                    'total_amount': 0,
                    'count_male': 0,
                    'count_female': 0,
                    'total_amount_sahayak': 0,
                    'payment_your': 0,
                    'fawda_fee': 0,
                    'job_type': booking.jobsahayak.job_type,
                    'sahayaks': []
                }
                
            if booking.jobsahayak.job_type == 'individuals_sahayak':
                booking_data_rejected[job_id]['total_amount'] += float(booking.total_amount) if booking.total_amount else 0
                booking_data_rejected[job_id]['count_male'] += int(booking.count_male) if booking.count_male else 0
                booking_data_rejected[job_id]['count_female'] += int(booking.count_female) if booking.count_female else 0
                booking_data_rejected[job_id]['total_amount_sahayak'] += int(booking.total_amount_sahayak) if booking.total_amount_sahayak else 0
                booking_data_rejected[job_id]['payment_your'] += float(booking.payment_your) if booking.payment_your else 0
                booking_data_rejected[job_id]['fawda_fee'] += float(booking.fawda_fee) if booking.fawda_fee else 0
                booking_data_rejected[job_id]['sahayaks'].append({
                    'booking_id': booking.id,
                    'job_id':booking.jobsahayak.id,
                    'job_number':booking.jobsahayak.job_number,
                    'status':booking.status,
                    'booking_user_id': booking.booking_user.id,
                    'sahayak_name': booking.booking_user.profile.name,
                    'sahayak_village': booking.booking_user.profile.village,
                    'sahayak_mobile_no': booking.booking_user.mobile_no,
                    'pay_amount_male': booking.jobsahayak.pay_amount_male,
                    'pay_amount_female': booking.jobsahayak.pay_amount_female,
                    'count_male': booking.count_male,
                    'count_female': booking.count_female,
                    'job_type':booking.jobsahayak.job_type,
                    'num_days':booking.jobsahayak.num_days,
                    'datetime':booking.jobsahayak.datetime,
                    'description':booking.jobsahayak.description,
                    'land_area':booking.jobsahayak.land_area,
                    'land_type':booking.jobsahayak.land_type,
                    'rating':getrating(booking.id)['rating'] if Rating.objects.filter(booking_job=booking.id).exists() else "",
                    'comment':getrating(booking.id)['comment'] if Rating.objects.filter(booking_job=booking.id).exists() else ""
                })
               
            else:
                booking_data_rejected[job_id]['total_amount'] += float(booking.total_amount) if booking.total_amount else 0
                booking_data_rejected[job_id]['total_amount_sahayak'] += float(booking.total_amount_theka) if booking.total_amount_theka else 0
                booking_data_rejected[job_id]['payment_your'] += float(booking.payment_your) if booking.payment_your else 0
                booking_data_rejected[job_id]['fawda_fee'] += float(booking.fawda_fee) if booking.fawda_fee else 0
                booking_data_rejected[job_id]['sahayaks'].append({
                    'booking_id': booking.id,
                    'job_id':booking.jobsahayak.id,
                    'job_number':booking.jobsahayak.job_number,
                    'status':booking.status,
                    'booking_user_id': booking.booking_user.id,
                    'thekedar_name': booking.booking_user.profile.name,
                    'thekedar_village': booking.booking_user.profile.village,
                    'thekedar_mobile_no': booking.booking_user.mobile_no,
                    'datetime':booking.jobsahayak.datetime,
                    'job_type':booking.jobsahayak.job_type,
                    'description':booking.jobsahayak.description,
                    'rating':getrating(booking.id)['rating'] if Rating.objects.filter(booking_job=booking.id).exists() else "",
                    'comment':getrating(booking.id)['comment'] if Rating.objects.filter(booking_job=booking.id).exists() else ""
                })

        response_data_rejected = {
            'bookings_rejected': list(booking_data_rejected.values())
        }
        ##Rejected booking details-------------- machine
        bookings2=JobBooking.objects.filter(jobmachine__grahak=request.user,status__in=['Rejected']).order_by('-id')
        for booking in bookings2:
            booking_data_machine.append({
                'booking_id':booking.id,
                'job_id':booking.jobmachine.id,
                'work_type':booking.jobmachine.work_type,
                'job_type':booking.jobmachine.job_type,
                'machine':booking.jobmachine.machine,
                'datetime':booking.jobmachine.datetime,
                'land_area':booking.jobmachine.land_area,
                'total_amount':booking.total_amount,
                'total_amount_machine':booking.total_amount_machine,
                'payment_your':booking.payment_your,
                'fawda_fee':booking.fawda_fee,
                'status':booking.status,
                'machine_malik_name':booking.booking_user.profile.name,
                'machine_malik_village':booking.booking_user.profile.village,
                'machine_malik_mobile_no':booking.booking_user.mobile_no,
                'booking_user_id':booking.booking_user.id,
                'job_number':booking.jobmachine.job_number,
                'land_type':booking.jobmachine.land_type,
                'rating':getrating(booking.id)['rating'] if Rating.objects.filter(booking_job=booking.id).exists() else "",
                'comment':getrating(booking.id)['comment'] if Rating.objects.filter(booking_job=booking.id).exists() else ""

                
            })
        ##booking history rejected-after-payment-----------------Sahayak        
        bookings_rejected_after = JobBooking.objects.filter(jobsahayak__grahak=request.user, status__in=['Rejected-After-Payment']).order_by('-id')
        booking_data_rejected_after = {}
        for booking in bookings_rejected_after:
            job_id = booking.jobsahayak.id
            if job_id not in booking_data_rejected_after:
                booking_data_rejected_after[job_id] = {
                    'total_amount': 0,
                    'count_male': 0,
                    'count_female': 0,
                    'total_amount_sahayak': 0,
                    'payment_your': 0,
                    'fawda_fee': 0,
                    'job_type': booking.jobsahayak.job_type,
                    'sahayaks': []
                }
                
            if booking.jobsahayak.job_type == 'individuals_sahayak':
                booking_data_rejected_after[job_id]['total_amount'] += float(booking.total_amount) if booking.total_amount else 0
                booking_data_rejected_after[job_id]['count_male'] += int(booking.count_male) if booking.count_male else 0
                booking_data_rejected_after[job_id]['count_female'] += int(booking.count_female) if booking.count_female else 0
                booking_data_rejected_after[job_id]['total_amount_sahayak'] += int(booking.total_amount_sahayak) if booking.total_amount_sahayak else 0
                booking_data_rejected_after[job_id]['payment_your'] += float(booking.payment_your) if booking.payment_your else 0
                booking_data_rejected_after[job_id]['fawda_fee'] += float(booking.fawda_fee) if booking.fawda_fee else 0
                booking_data_rejected_after[job_id]['sahayaks'].append({
                    'booking_id': booking.id,
                    'job_id':booking.jobsahayak.id,
                    'job_number':booking.jobsahayak.job_number,
                    'status':booking.status,
                    'booking_user_id': booking.booking_user.id,
                    'sahayak_name': booking.booking_user.profile.name,
                    'sahayak_village': booking.booking_user.profile.village,
                    'sahayak_mobile_no': booking.booking_user.mobile_no,
                    'pay_amount_male': booking.jobsahayak.pay_amount_male,
                    'pay_amount_female': booking.jobsahayak.pay_amount_female,
                    'count_male': booking.count_male,
                    'count_female': booking.count_female,
                    'job_type':booking.jobsahayak.job_type,
                    'num_days':booking.jobsahayak.num_days,
                    'datetime':booking.jobsahayak.datetime,
                    'description':booking.jobsahayak.description,
                    'land_area':booking.jobsahayak.land_area,
                    'land_type':booking.jobsahayak.land_type,
                    'rating':getrating(booking.id)['rating'] if Rating.objects.filter(booking_job=booking.id).exists() else "",
                    'comment':getrating(booking.id)['comment'] if Rating.objects.filter(booking_job=booking.id).exists() else ""
                })
               
            else:
                booking_data_rejected_after[job_id]['total_amount'] += float(booking.total_amount) if booking.total_amount else 0
                booking_data_rejected_after[job_id]['total_amount_sahayak'] += float(booking.total_amount_theka) if booking.total_amount_theka else 0
                booking_data_rejected_after[job_id]['payment_your'] += float(booking.payment_your) if booking.payment_your else 0
                booking_data_rejected_after[job_id]['fawda_fee'] += float(booking.fawda_fee) if booking.fawda_fee else 0
                booking_data_rejected_after[job_id]['sahayaks'].append({
                    'booking_id': booking.id,
                    'job_id':booking.jobsahayak.id,
                    'job_number':booking.jobsahayak.job_number,
                    'status':booking.status,
                    'booking_user_id': booking.booking_user.id,
                    'thekedar_name': booking.booking_user.profile.name,
                    'thekedar_village': booking.booking_user.profile.village,
                    'thekedar_mobile_no': booking.booking_user.mobile_no,
                    'datetime':booking.jobsahayak.datetime,
                    'job_type':booking.jobsahayak.job_type,
                    'description':booking.jobsahayak.description,
                    'rating':getrating(booking.id)['rating'] if Rating.objects.filter(booking_job=booking.id).exists() else "",
                    'comment':getrating(booking.id)['comment'] if Rating.objects.filter(booking_job=booking.id).exists() else ""
                })

        response_data_rejected_after = {
            'bookings_rejected_after_payment': list(booking_data_rejected_after.values())
        }
        ##booking history rejected-after-payment--------------machine 
        bookings2=JobBooking.objects.filter(jobmachine__grahak=request.user,status__in=['Rejected-After-Payment']).order_by('-id')

        for booking in bookings2:
            booking_data_machine.append({
                'booking_id':booking.id,
                'job_id':booking.jobmachine.id,
                'work_type':booking.jobmachine.work_type,
                'job_type':booking.jobmachine.job_type,
                'machine':booking.jobmachine.machine,
                'datetime':booking.jobmachine.datetime,
                'land_area':booking.jobmachine.land_area,
                'total_amount':booking.total_amount,
                'total_amount_machine':booking.total_amount_machine,
                'payment_your':booking.payment_your,
                'fawda_fee':booking.fawda_fee,
                'status':booking.status,
                'machine_malik_name':booking.booking_user.profile.name,
                'machine_malik_village':booking.booking_user.profile.village,
                'machine_malik_mobile_no':booking.booking_user.mobile_no,
                'booking_user_id':booking.booking_user.id,
                'job_number':booking.jobmachine.job_number,
                'land_type':booking.jobmachine.land_type,
                'rating':getrating(booking.id)['rating'] if Rating.objects.filter(booking_job=booking.id).exists() else "",
                'comment':getrating(booking.id)['comment'] if Rating.objects.filter(booking_job=booking.id).exists() else ""

                
            })
        ##Cancelled booking history---------------Sahayak    
        bookings_cancelled = JobBooking.objects.filter(jobsahayak__grahak=request.user, status__in=['Cancelled']).order_by('-id')
        booking_data_cancelled = {}
        for booking in bookings_cancelled:
            job_id = booking.jobsahayak.id
            if job_id not in booking_data_cancelled:
                booking_data_cancelled[job_id] = {
                    'total_amount': 0,
                    'count_male': 0,
                    'count_female': 0,
                    'total_amount_sahayak': 0,
                    'payment_your': 0,
                    'fawda_fee': 0,
                    'job_type': booking.jobsahayak.job_type,
                    'sahayaks': []
                }
                
            if booking.jobsahayak.job_type == 'individuals_sahayak':
                booking_data_cancelled[job_id]['total_amount'] += float(booking.total_amount) if booking.total_amount else 0
                booking_data_cancelled[job_id]['count_male'] += int(booking.count_male) if booking.count_male else 0
                booking_data_cancelled[job_id]['count_female'] += int(booking.count_female) if booking.count_female else 0
                booking_data_cancelled[job_id]['total_amount_sahayak'] += int(booking.total_amount_sahayak) if booking.total_amount_sahayak else 0
                booking_data_cancelled[job_id]['payment_your'] += float(booking.payment_your) if booking.payment_your else 0
                booking_data_cancelled[job_id]['fawda_fee'] += float(booking.fawda_fee) if booking.fawda_fee else 0
                booking_data_cancelled[job_id]['sahayaks'].append({
                    'booking_id': booking.id,
                    'job_id':booking.jobsahayak.id,
                    'job_number':booking.jobsahayak.job_number,
                    'status':booking.status,
                    'booking_user_id': booking.booking_user.id,
                    'sahayak_name': booking.booking_user.profile.name,
                    'sahayak_village': booking.booking_user.profile.village,
                    'sahayak_mobile_no': booking.booking_user.mobile_no,
                    'pay_amount_male': booking.jobsahayak.pay_amount_male,
                    'pay_amount_female': booking.jobsahayak.pay_amount_female,
                    'count_male': booking.count_male,
                    'count_female': booking.count_female,
                    'job_type':booking.jobsahayak.job_type,
                    'num_days':booking.jobsahayak.num_days,
                    'datetime':booking.jobsahayak.datetime,
                    'description':booking.jobsahayak.description,
                    'land_area':booking.jobsahayak.land_area,
                    'land_type':booking.jobsahayak.land_type,
                    'rating':getrating(booking.id)['rating'] if Rating.objects.filter(booking_job=booking.id).exists() else "",
                    'comment':getrating(booking.id)['comment'] if Rating.objects.filter(booking_job=booking.id).exists() else ""
                })
               
            else:
                booking_data_cancelled[job_id]['total_amount'] += float(booking.total_amount) if booking.total_amount else 0
                booking_data_cancelled[job_id]['total_amount_sahayak'] += float(booking.total_amount_theka) if booking.total_amount_theka else 0
                booking_data_cancelled[job_id]['payment_your'] += float(booking.payment_your) if booking.payment_your else 0
                booking_data_cancelled[job_id]['fawda_fee'] += float(booking.fawda_fee) if booking.fawda_fee else 0
                booking_data_cancelled[job_id]['sahayaks'].append({
                    'booking_id': booking.id,
                    'job_id':booking.jobsahayak.id,
                    'job_number':booking.jobsahayak.job_number,
                    'status':booking.status,
                    'booking_user_id': booking.booking_user.id,
                    'thekedar_name': booking.booking_user.profile.name,
                    'thekedar_village': booking.booking_user.profile.village,
                    'thekedar_mobile_no': booking.booking_user.mobile_no,
                    'datetime':booking.jobsahayak.datetime,
                    'job_type':booking.jobsahayak.job_type,
                    'description':booking.jobsahayak.description,
                    'rating':getrating(booking.id)['rating'] if Rating.objects.filter(booking_job=booking.id).exists() else "",
                    'comment':getrating(booking.id)['comment'] if Rating.objects.filter(booking_job=booking.id).exists() else ""
                })

        response_data_cancelled = {
            'bookings_cancelled': list(booking_data_cancelled.values())
        }
        ##booking history-Cancelled ------------------machine
        bookings3=JobBooking.objects.filter(jobmachine__grahak=request.user,status__in=['Cancelled']).order_by('-id')

        for booking in bookings3:
            booking_data_machine.append({
                'booking_id':booking.id,
                'job_id':booking.jobmachine.id,
                'work_type':booking.jobmachine.work_type,
                'job_type':booking.jobmachine.job_type,
                'machine':booking.jobmachine.machine,
                'datetime':booking.jobmachine.datetime,
                'land_area':booking.jobmachine.land_area,
                'total_amount':booking.total_amount,
                'total_amount_machine':booking.total_amount_machine,
                'payment_your':booking.payment_your,
                'fawda_fee':booking.fawda_fee,
                'status':booking.status,
                'machine_malik_name':booking.booking_user.profile.name,
                'machine_malik_village':booking.booking_user.profile.village,
                'machine_malik_mobile_no':booking.booking_user.mobile_no,
                'booking_user_id':booking.booking_user.id,
                'job_number':booking.jobmachine.job_number,
                'land_type':booking.jobmachine.land_type,
                'rating':getrating(booking.id)['rating'] if Rating.objects.filter(booking_job=booking.id).exists() else "",
                'comment':getrating(booking.id)['comment'] if Rating.objects.filter(booking_job=booking.id).exists() else ""

                
            })
        ##booking-history cancelled-after-payments-----------------Sahayak    
        bookings_cancelled_after = JobBooking.objects.filter(jobsahayak__grahak=request.user, status__in=['Cancelled-After-Payment']).order_by('-id')
        booking_data_cancelled_after = {}
        for booking in bookings_cancelled_after:
            job_id = booking.jobsahayak.id
            if job_id not in booking_data_cancelled_after:
                booking_data_cancelled_after[job_id] = {
                    'total_amount': 0,
                    'count_male': 0,
                    'count_female': 0,
                    'total_amount_sahayak': 0,
                    'payment_your': 0,
                    'fawda_fee': 0,
                    'job_type': booking.jobsahayak.job_type,
                    'sahayaks': []
                }
                
            if booking.jobsahayak.job_type == 'individuals_sahayak':
                booking_data_cancelled_after[job_id]['total_amount'] += float(booking.total_amount) if booking.total_amount else 0
                booking_data_cancelled_after[job_id]['count_male'] += int(booking.count_male) if booking.count_male else 0
                booking_data_cancelled_after[job_id]['count_female'] += int(booking.count_female) if booking.count_female else 0
                booking_data_cancelled_after[job_id]['total_amount_sahayak'] += int(booking.total_amount_sahayak) if booking.total_amount_sahayak else 0
                booking_data_cancelled_after[job_id]['payment_your'] += float(booking.payment_your) if booking.payment_your else 0
                booking_data_cancelled_after[job_id]['fawda_fee'] += float(booking.fawda_fee) if booking.fawda_fee else 0
                booking_data_cancelled_after[job_id]['sahayaks'].append({
                    'booking_id': booking.id,
                    'job_id':booking.jobsahayak.id,
                    'job_number':booking.jobsahayak.job_number,
                    'status':booking.status,
                    'booking_user_id': booking.booking_user.id,
                    'sahayak_name': booking.booking_user.profile.name,
                    'sahayak_village': booking.booking_user.profile.village,
                    'sahayak_mobile_no': booking.booking_user.mobile_no,
                    'pay_amount_male': booking.jobsahayak.pay_amount_male,
                    'pay_amount_female': booking.jobsahayak.pay_amount_female,
                    'count_male': booking.count_male,
                    'count_female': booking.count_female,
                    'job_type':booking.jobsahayak.job_type,
                    'num_days':booking.jobsahayak.num_days,
                    'datetime':booking.jobsahayak.datetime,
                    'description':booking.jobsahayak.description,
                    'land_area':booking.jobsahayak.land_area,
                    'land_type':booking.jobsahayak.land_type,
                    'rating':getrating(booking.id)['rating'] if Rating.objects.filter(booking_job=booking.id).exists() else "",
                    'comment':getrating(booking.id)['comment'] if Rating.objects.filter(booking_job=booking.id).exists() else ""
                })
                
            else:
                booking_data_cancelled_after[job_id]['total_amount'] += float(booking.total_amount) if booking.total_amount else 0
                booking_data_cancelled_after[job_id]['total_amount_sahayak'] += float(booking.total_amount_theka) if booking.total_amount_theka else 0
                booking_data_cancelled_after[job_id]['payment_your'] += float(booking.payment_your) if booking.payment_your else 0
                booking_data_cancelled_after[job_id]['fawda_fee'] += float(booking.fawda_fee) if booking.fawda_fee else 0
                booking_data_cancelled_after[job_id]['sahayaks'].append({
                    'booking_id': booking.id,
                    'job_id':booking.jobsahayak.id,
                    'job_number':booking.jobsahayak.job_number,
                    'status':booking.status,
                    'booking_user_id': booking.booking_user.id,
                    'thekedar_name': booking.booking_user.profile.name,
                    'thekedar_village': booking.booking_user.profile.village,
                    'thekedar_mobile_no': booking.booking_user.mobile_no,
                    'datetime':booking.jobsahayak.datetime,
                    'job_type':booking.jobsahayak.job_type,
                    'description':booking.jobsahayak.description,
                    'rating':getrating(booking.id)['rating'] if Rating.objects.filter(booking_job=booking.id).exists() else "",
                    'comment':getrating(booking.id)['comment'] if Rating.objects.filter(booking_job=booking.id).exists() else ""
                })

        response_data_cancelled_after = {
            'bookings_cancelled_after_payment': list(booking_data_cancelled_after.values())
        }
        ##booking history Cancelled-After-Payment machine
        bookings4=JobBooking.objects.filter(jobmachine__grahak=request.user,status__in=['Cancelled-After-Payment']).order_by('-id')
        for booking in bookings4:
            booking_data_machine.append({
                'booking_id':booking.id,
                'job_id':booking.jobmachine.id,
                'work_type':booking.jobmachine.work_type,
                'job_type':booking.jobmachine.job_type,
                'machine':booking.jobmachine.machine,
                'datetime':booking.jobmachine.datetime,
                'land_area':booking.jobmachine.land_area,
                'total_amount':booking.total_amount,
                'total_amount_machine':booking.total_amount_machine,
                'payment_your':booking.payment_your,
                'fawda_fee':booking.fawda_fee,
                'status':booking.status,
                'machine_malik_name':booking.booking_user.profile.name,
                'machine_malik_village':booking.booking_user.profile.village,
                'machine_malik_mobile_no':booking.booking_user.mobile_no,
                'booking_user_id':booking.booking_user.id,
                'job_number':booking.jobmachine.job_number,
                'land_type':booking.jobmachine.land_type,
                'rating':getrating(booking.id)['rating'] if Rating.objects.filter(booking_job=booking.id).exists() else "",
                'comment':getrating(booking.id)['comment'] if Rating.objects.filter(booking_job=booking.id).exists() else "",
                
            })            
        cancelled_sahayak_job=JobSahayak.objects.filter(grahak=request.user,status='Cancelled')       
        cancelled_machine_job=JobMachine.objects.filter(grahak=request.user,status='Cancelled')
        serializer_sahayak=JobSahaykSerialiser(cancelled_sahayak_job,many=True)
        serializer_machine=JobMachineSerializers(cancelled_machine_job,many=True)
        return Response({
            'sahayk_booking_details':[response_data_completed,response_data_rejected,response_data_rejected_after,response_data_cancelled,response_data_cancelled_after],
            'machine_malik_booking_details':booking_data_machine,
            'sahayak_job_details':serializer_sahayak.data,
            'machine_malik_job_details':serializer_machine.data
        })





class MyjobsHistory(APIView):
    permission_classes=[IsAuthenticated,]
    authentication_classes=[BearerTokenAuthentication,]
    PAGE_SIZE=10
    def get(self,request,format=None):
        if not request.user.user_type in ['Sahayak','MachineMalik']:
            return Response({'message':{'you are not sahayak and MachineMalik'}})
        booking_array=[]    
        get_bookings_data=JobBooking.objects.filter(booking_user=request.user,status__in=['Completed','Rejected','Rejected-After-Payment','Cancelled','Cancelled-After-Payment']).order_by('-id')
        for booking_data in get_bookings_data:
            if booking_data.jobsahayak:
                if request.user.user_type == 'Sahayak':
                    if booking_data.jobsahayak.job_type =='individuals_sahayak':
                        booking_array.append({
                            'booking_id': booking_data.id,
                            'job_id':booking_data.jobsahayak.id,
                            'job_number':booking_data.jobsahayak.job_number,
                            'status':booking_data.status,
                            'booking_user_id': booking_data.booking_user.id,
                            'grahak_name': booking_data.jobsahayak.grahak.profile.name,
                            'grahak_village': booking_data.jobsahayak.grahak.profile.village,
                            'grahak_mobile_no': booking_data.booking_user.mobile_no,
                            'pay_amount_male': booking_data.jobsahayak.pay_amount_male,
                            'pay_amount_female': booking_data.jobsahayak.pay_amount_female,
                            'count_male': booking_data.count_male,
                            'count_female': booking_data.count_female,
                            'job_type':booking_data.jobsahayak.job_type,
                            'num_days':booking_data.jobsahayak.num_days,
                            'datetime':booking_data.jobsahayak.datetime,
                            'description':booking_data.jobsahayak.description,
                            'land_area':booking_data.jobsahayak.land_area,
                            'land_type':booking_data.jobsahayak.land_type,
                            'rating':getrating(booking_data.id)['rating'] if Rating.objects.filter(booking_job=booking_data.id).exists() else "",
                            'comment':getrating(booking_data.id)['comment'] if Rating.objects.filter(booking_job=booking_data.id).exists() else ""
                            })
                    else:
                        booking_array.append({
                            'booking_id': booking_data.id,
                            'job_id':booking_data.jobsahayak.id,
                            'job_number':booking_data.jobsahayak.job_number,
                            'status':booking_data.status,
                            'land_type':booking_data.jobsahayak.land_type,
                            'land_area':booking_data.jobsahayak.land_area,
                            'total_amount_theka':booking_data.total_amount_theka,
                            'total_amount':booking_data.total_amount,
                            'payment_your':booking_data.payment_your,
                            'booking_user_id':booking_data.booking_user.id,
                            'grahak_name':booking_data.jobsahayak.grahak.profile.name,
                            'grahak_village': booking_data.jobsahayak.grahak.profile.village,
                            'grahak_mobile_no':booking_data.jobsahayak.grahak.mobile_no,
                            'datetime':booking_data.jobsahayak.datetime,
                            'job_type':booking_data.jobsahayak.job_type,
                            'description':booking_data.jobsahayak.description,
                            'rating':getrating(booking_data.id)['rating'] if Rating.objects.filter(booking_job=booking_data.id).exists() else "",
                            'comment':getrating(booking_data.id)['comment'] if Rating.objects.filter(booking_job=booking_data.id).exists() else ""
                            })
            else:
                if request.user.user_type =='MachineMalik':
                    booking_array.append({
                        'booking_id':booking_data.id,
                        'job_id':booking_data.jobmachine.id,
                        'work_type':booking_data.jobmachine.work_type,
                        'job_type':booking_data.jobmachine.job_type,
                        'machine':booking_data.jobmachine.machine,
                        'datetime':booking_data.jobmachine.datetime,
                        'land_area':booking_data.jobmachine.land_area,
                        'total_amount':booking_data.total_amount,
                        'total_amount_machine':booking_data.total_amount_machine,
                        'payment_your':booking_data.payment_your,
                        'fawda_fee':booking_data.fawda_fee,
                        'status':booking_data.status,
                        'grahak_name':booking_data.jobmachine.grahak.profile.name,
                        'grahak_village':booking_data.jobmachine.grahak.profile.village,
                        'grahak_mobile_no':booking_data.jobmachine.grahak.mobile_no,
                        'booking_user_id':booking_data.booking_user.id,
                        'job_number':booking_data.jobmachine.job_number,
                        'land_type':booking_data.jobmachine.land_type,
                        'rating':getrating(booking_data.id)['rating'] if Rating.objects.filter(booking_job=booking_data.id).exists() else "",
                        'comment':getrating(booking_data.id)['comment'] if Rating.objects.filter(booking_job=booking_data.id).exists() else "",  
                        })
        paginator = PageNumberPagination()
        paginator.page_size = self.PAGE_SIZE
        paginated_result = paginator.paginate_queryset(booking_array, request)
        response_data = {'page': paginator.page.number, 'total_pages': paginator.page.paginator.num_pages, 'results': paginated_result}
    # Add next page URL to response
        if paginator.page.has_next():
            base_url = request.build_absolute_uri().split('?')[0]
            response_data['next'] = f"{base_url}?page={paginator.page.next_page_number()}"            
        return Response(response_data) 
                     


                



