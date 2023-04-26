from django.shortcuts import render
from .models import *
from .models import JobMachine
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
import math
from decimal import Decimal
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated,AllowAny
import uuid
import re
from dateutil import parser
from authentication.views import BearerTokenAuthentication
from rest_framework import status
from booking.models import JobBooking
# Create your views here.
from django.db.models import Q

from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size = 10 # the number of results per page
    page_query_param = 'page' # the query parameter used for pagination
    page_size_query_param = 'page_size' # the query parameter used for specifying the number of results per page
    max_page_size = 1000# the maximum number of results per page

class BookingThekePeKam(APIView):
    authentication_classes=[BearerTokenAuthentication,]
    permission_classes=[IsAuthenticated,]
    def post(self,request,format=None):
        if request.user.user_type == 'Grahak':
            serializers=PostJobThekePeKamSerializer(data=request.data)
            if serializers.is_valid(raise_exception=True):
                datetime=serializers.data.get('datetime')
                description=serializers.data.get('description')
                landtype=serializers.data.get('land_type')
                landarea=serializers.data.get('land_area')
                amount=request.data.get('total_amount_theka')
                print(amount)
                grahak=request.user
                try:
                    amount = int(amount)
                except ValueError:
                    try:
                        amount = float(amount)
                    except ValueError:
                        return Response({'message': {'total_amount_theka should be numeric!'}})
                if not isinstance(amount, (float, int)):
                    return Response({'message': {'total_amount_theka should be a float or an int!'}})

                if amount <= 5:
                    return Response({'message': {'total_amount_theka should be greater than  5 !'}})

                existing_job = JobSahayak.objects.filter(
                    datetime=datetime,
                    description=description,
                    land_area=landarea,
                    land_type=landtype,
                    total_amount_theka=amount,
                    job_type='theke_pe_kam',
                    grahak=grahak
                ).first()
                if existing_job:
                    return Response({'message': {'Booking already exists'}})
                    
                unique_id = int(uuid.uuid4().hex[:6], 16)
                job_number='T-'+str(unique_id)
                job=JobSahayak.objects.create(
                    datetime=datetime,
                    description=description,
                    land_area=landarea,
                    land_type=landtype,
                    total_amount_theka=amount,
                    job_type='theke_pe_kam',
                    grahak=grahak,
                    job_number=job_number
                )
                serial=GetJobThekePeKamSerializer(job)
                return Response({'message':'Booking created !','data':serial.data,'status':status.HTTP_201_CREATED})
        else:
            return Response({'message':{'You are not Grahak'}})  

class EditThekePeKam(APIView):
    authentication_classes=[BearerTokenAuthentication,]
    permission_classes=[IsAuthenticated,]
    def post(self, request, format=None):
        job_id = request.data.get('job_id')
        amount = request.data.get('amount')
        if not job_id:
            return Response({'job_id':{'This field is required !'}})
        if not amount:
            return Response({'amount':{'This field is required !'}})    
        
        if not job_id.isdigit():
            # return a validation message response if the job_id is not a number
            return Response({'message': {'job_id should be a number'}})
        if not all(char.isdigit() or char == '.' for char in amount) or amount.count('.') > 1:
            return Response({'message': {'amount should be float or int !'}})

        try:
            amount_decimal = Decimal(amount)
        except (TypeError, ValueError):
            amount_decimal = None

        # If the amount value is not a valid decimal, use the original value
        if amount_decimal is None:
            amount_decimal = amount

        # Get the JobSahayak object or return a 404 message response
        job = get_object_or_404(JobSahayak, pk=job_id, job_type='theke_pe_kam')
        if not request.user == job.grahak:
            return Response({'message':{'unauthorised user !'}})
        if job.status =='Pending':
            job.total_amount_theka = amount_decimal
            job.save()
        else:
            return Response({'message':{'job can not be updated it is not Pending !'}})
        return Response({'message': 'Amount updated successfully!','status':status.HTTP_200_OK})
 

class BookingSahayakIndividuals(APIView):
    authentication_classes=[BearerTokenAuthentication,]
    permission_classes=[IsAuthenticated,]
    def post(self, request, format=None):
        if request.user.user_type == 'Grahak':
            serializer = PostJobIndividualSerializer(data=request.data) 
            if serializer.is_valid(raise_exception=True):
                data = serializer.validated_data
                datetime=serializer.data.get('datetime')
                pay_amount_male=serializer.data.get('pay_amount_male')
                pay_amount_female=serializer.data.get('pay_amount_female')
                try:
                    # Check if the datetime string is in the correct format
                    datetime_obj = parser.isoparse(datetime)
                except ValueError:
                    return Response({'detail': {'Invalid datetime format. Please use YYYY-MM-DDTHH:MM:SS.'}})
                # if not data['land_area'].isdigit():
                #     return Response({'message':'land_area should be integer !'})   
                if not data['count_male'].isdigit():
                    return Response({'message':{'count_male should be integer !'}})    
                if not data['count_female'].isdigit():
                    return Response({'message':{'count_female should be integer !'}})    
                if not data['num_days'].isdigit():
                    return Response({'message':{'num_days should be integer !'}})    
                    
                try:
                    pay_amount_male = int(pay_amount_male)
                except ValueError:
                    try:
                        pay_amount_male = float(pay_amount_male)
                    except ValueError:
                        return Response({'message': {'pay_amount_male should be integer!'}})
                try:
                    pay_amount_female = int(pay_amount_female)
                except ValueError:
                    try:
                        pay_amount_female = float(pay_amount_female)
                    except ValueError:
                        return Response({'message': {'pay_amount_female should be integer!'}})         
                if not isinstance(pay_amount_male, (float, int)) or not isinstance(pay_amount_female, (float, int)):
                    return Response({'message': {'pay_amount_male or pay_amount_female should be a float or an int!'}})
                if pay_amount_male == 0 and pay_amount_female == 0 :
                    return Response({'message': {'without pay_amount_male or pay_amount_female job can not be post !'}}) 
                if int(data['count_male']) == 0 and int(data['count_female']) == 0:
                    return Response({'message':{'without count_male or count_female job can not be post !'}})    
                # check if a job with the same details already exists
                existing_jobs = JobSahayak.objects.filter(
                    grahak=request.user,
                    job_type='individuals_sahayak',
                    datetime=data['datetime'],
                    description=data['description'],
                    land_type=data['land_type'],
                    land_area=data['land_area'],
                    count_male=data['count_male'],
                    count_female=data['count_female'],
                    pay_amount_male=pay_amount_male,
                    pay_amount_female=pay_amount_female,
                    num_days=data['num_days'],
                    # fawda_fee_percentage=data['fawda_fee_percentage']
                )
                if existing_jobs.exists():
                    return Response({'message': 'message', 'message': 'A job with the same details already exists.'})
                
                # create a new job if it doesn't already exist
                unique_id = int(uuid.uuid4().hex[:6], 16)
                job_number='S-'+str(unique_id)
                job = JobSahayak(
                    grahak=request.user,
                    job_type='individuals_sahayak',
                    datetime=data['datetime'],
                    description=data['description'],
                    land_type=data['land_type'],
                    land_area=data['land_area'],
                    count_male=data['count_male'],
                    count_female=data['count_female'],
                    pay_amount_male=pay_amount_male,
                    pay_amount_female=pay_amount_female,
                    num_days=data['num_days'],
                    job_number=job_number
                    # fawda_fee_percentage=data['fawda_fee_percentage']
                )
                job.save()
                serial=GetJobIndividualsSerializer(job)
                return Response({'message': 'success','data':serial.data,'status':status.HTTP_201_CREATED})
        return Response({'message': {'You are not Grahak'}})


class EditIndividualSahayak(APIView):
    authentication_classes=[BearerTokenAuthentication,]
    permission_classes=[IsAuthenticated,]
    def post(self, request, format=None):
        job_id = request.data.get('job_id')
        pay_amount_female = request.data.get('pay_amount_female')
        pay_amount_male =request.data.get('pay_amount_male')

        if not job_id:
            return Response({'job_id':{'This field is required !'}})
        if not pay_amount_female:
            return Response({'pay_amount_female':{'This field is requird !'}})    
        if not pay_amount_male:
            return Response({'pay_amount_male':{'This field is required !'}})    
        
        if not job_id.isdigit():
            # return a validation message response if the job_id is not a number
            return Response({'message': {'job_id should be a integer !'}})
        if not all(char.isdigit() or char == '.' for char in pay_amount_female) or pay_amount_female.count('.') > 1:
            return Response({'message': {'pay_amount_female should contain only digits and a single dot (".") as the decimal separator'}})
        if not all(char.isdigit() or char == '.' for char in pay_amount_male) or pay_amount_male.count('.') > 1:
            return Response({'message': {'pay_amount_male should contain only digits and a single dot (".") as the decimal separator'}})
        try:
            amount_female = Decimal(pay_amount_female)
            amount_male = Decimal(pay_amount_male)
        except (TypeError, ValueError):
            amount_female = None
            amount_male=None

        # If the amount value is not a valid decimal, use the original value
        if amount_male is None or amount_female is None:
            amount_female=pay_amount_female
            amount_male = pay_amount_male

        # Get the JobSahayak object or return a 404 message response
        job = get_object_or_404(JobSahayak, pk=job_id, job_type='individuals_sahayak')
        if not request.user == job.grahak:
            return Response({'message':{'unauthorised user !'}})
        if job.status == 'Pending':
            if not  JobBooking.objects.filter(jobsahayak=job).exists():   
                job.pay_amount_male = amount_male
                job.pay_amount_female=amount_female
                job.save()
            else:
                return Response({'message':{'job can not be edited one of the Sahayak Accepted'}})    
        else:
            return Response({'message':{'job can not be updated it is not Pending !'}})    

        return Response({'message': 'Amount updated successfully!','status':status.HTTP_200_OK})
 

        
class BookingJobMachine(APIView):
    authentication_classes=[BearerTokenAuthentication,]
    permission_classes=[IsAuthenticated,]
    def post(self,request,format=None):
        if request.user.user_type == 'Grahak':
            serializers=JobMachineSerializers(data=request.data)
            if serializers.is_valid(raise_exception=True):
                worktype=serializers.data.get('work_type')
                machine=serializers.data.get('machine')
                others=request.data.get('others')
                datetime=serializers.data.get('datetime')
                landarea=serializers.data.get('land_area')
                landtype=serializers.data.get('land_type')
                amount=serializers.data.get('total_amount_machine')
                grahak=request.user
                if not worktype or not machine or not datetime or not landarea or not landtype or not amount:
                    return Response({'message':{'all fields are required instead of others !'}})  
                if not landarea.isdigit():
                    return Response({'message':{'land_area should be integer !'}}) 
                if not re.match(r'^[a-zA-Z\s]+$', worktype):
                    return Response({'message': {'Invalid work_type, only letters and spaces allowed'}})
                if not re.match(r'^[a-zA-Z\s]+$', machine):
                    return Response({'message': {'Invalid machine, only letters and spaces allowed'}})
                try:
                    # Check if the datetime string is in the correct format
                    datetime_obj = parser.isoparse(datetime)
                except ValueError:
                    return Response({'detail': {'Invalid datetime format. Please use YYYY-MM-DDTHH:MM:SS.'}})    
                try:
                    amount = int(amount)
                except ValueError:
                    try:
                        amount = float(amount)
                    except ValueError:
                        return Response({'message': {'total_amount_theka should be numeric!'}}) 
                if not isinstance(amount, (float, int)):
                    return Response({'message': {'total_amount_machine should be a float or an int!'}})

                if amount <= 5:
                    return Response({'message': {'total_amount_machine should be greater than 5 !'}})     
                existing_job=JobMachine.objects.filter(
                    work_type=worktype,
                    machine=machine,
                    others=others,
                    datetime=datetime,
                    land_area=landarea,
                    land_type=landtype,
                    total_amount_machine=amount,
                    grahak=grahak,


                )
                if existing_job:
                    return Response({'message':{'job already exist !'}})
                unique_id = int(uuid.uuid4().hex[:6], 16)
                job_number='M-'+str(unique_id)
                job=JobMachine.objects.create(
                    work_type=worktype,
                    machine=machine,
                    others=others,
                    datetime=datetime,
                    land_area=landarea,
                    land_type=landtype,
                    total_amount_machine=amount,
                    grahak=grahak,
                    job_number=job_number
                )
                serial=GetJobMachineSerializer(job)    
                return Response({'message':'job created successfully !','status':status.HTTP_201_CREATED,'data':serial.data})
        else:
            return Response({'message':{'You are not Grahak !'}})        

class EditJobMachine(APIView):
    authentication_classes=[BearerTokenAuthentication,]
    permission_classes=[IsAuthenticated,]
    def post(self, request, format=None):
        job_id = request.data.get('job_id')
        amount = request.data.get('amount')
        if not job_id:
            return Response({'job_id':{'This field is required !'}})
        if not amount:
            return Response({'amount':{'This field is required !'}})    
        
        if not job_id.isdigit():
            # return a validation message response if the job_id is not a number
            return Response({'message': {'job_id should be a number'}})
        if not all(char.isdigit() or char == '.' for char in amount) or amount.count('.') > 1:
            return Response({'message': {'amount should be int or float !'}})

        try:
            amount_decimal = Decimal(amount)
        except (TypeError, ValueError):
            amount_decimal = None

        # If the amount value is not a valid decimal, use the original value
        if amount_decimal is None:
            amount_decimal = amount

        # Get the JobSahayak object or return a 404 message response
        job = get_object_or_404(JobMachine, pk=job_id, job_type='machine_malik')
        if not request.user == job.grahak:
            return Response({'message':{'unauthorised user'}})
        if job.status == 'Pending':
            job.total_amount_machine = amount_decimal
            job.save()
        else:
            return Response({'message':{'job can not be updated it is not Pending !'}})    

        return Response({'message': 'Amount updated successfully!','status':status.HTTP_200_OK})
 

###---------------------------------------------------------------------------###
class GetSahayakJobDetails(APIView):
    authentication_classes=[BearerTokenAuthentication,]
    permission_classes=[IsAuthenticated,]
    def get(self,request,format=None):
        if request.user.user_type == 'Sahayak':
            jobid=request.data.get('job_id')
            if not jobid:
                return Response({'message':{'jobid required !'}})            
            if not jobid.isdigit():
                return Response({'message':{'job_id should be numeric !'}})    
            try:
               getjob = JobSahayak.objects.get(pk=jobid)
            except JobSahayak.DoesNotExist:
                return Response({'message': {'Job does not exist !'}})
            serial=JobSahaykSerialiser(getjob)    
            return Response({'seccess':True,'data':serial.data})
        return Response({'message':{'you are not Sahayak'}})
        
class GetMachineJobDetails(APIView):
    authentication_classes=[BearerTokenAuthentication,]
    permission_classes=[IsAuthenticated,]
    def get(self,request,format=None):
        if request.user.user_type == 'MachineMalik':
            jobid=request.data.get('job_id')
            if not jobid:
                return Response({'message':{'jobid required !'}})  
            if not jobid.isdigit():
                return Response({'message':{'job_id should be numeric !'}})          
            try:
               getjob = JobMachine.objects.get(pk=jobid)
            except JobMachine.DoesNotExist:
                return Response({'message': {'Job does not exist !'}})
            serial=GetJobMachineSerializer(getjob)    
            return Response({'seccess':True,'data':serial.data})
        return Response({'message':{'you are not MachineMalik'}})



def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the earth in km
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dLon/2) * math.sin(dLon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c  # Distance in km
    return distance

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

class GetAllJob(APIView):
    authentication_classes=[BearerTokenAuthentication,]
    permission_classes=[IsAuthenticated,]
    PAGE_SIZE=10
    def get(self,request,format=None):
        result = []
        sahayak = request.user
        sahayak_profile = sahayak.profile
        sahayak_lat = sahayak_profile.latitude
        sahayak_lon = sahayak_profile.longitude
        if sahayak.user_type == 'Sahayak':
            job_posts = JobSahayak.objects.all().filter(status='Pending').order_by('-id')
            for job_post in job_posts:
                grahak_profile = job_post.grahak.profile
                grahak_lat = grahak_profile.latitude
                grahak_lon = grahak_profile.longitude
                # print(grahak_lat,grahak_lon)
                distance = calculate_distance(sahayak_lat, sahayak_lon, grahak_lat, grahak_lon)
                if distance <= 5:
                    # serial=GetJobIndividualsSerializer(job_post)
                    if not JobBooking.objects.filter(jobsahayak=job_post,booking_user=request.user).exists():
                        result.append({
                            "id":job_post.id,
                            "job_type":job_post.job_type,
                            "status":job_post.status,
                            "date":job_post.date,
                            "datetime":job_post.datetime,
                            "payment_your":job_post.payment_your,
                            "fawda_fee":job_post.fawda_fee,
                            "description":job_post.description,
                            "count_male":job_post.count_male,
                            "count_female":job_post.count_female,
                            "pay_amount_male":job_post.pay_amount_male,
                            "pay_amount_female":job_post.pay_amount_female,
                            "total_amount":job_post.total_amount,
                            "total_amount_theka":job_post.total_amount_theka,
                            "total_amount_sahayak":job_post.total_amount_sahayak,
                            "num_days":job_post.num_days,
                            "land_area":job_post.land_area,
                            "land_type":job_post.land_type,
                            "job_number":job_post.job_number,
                            "grahak":job_post.grahak.profile.name,
                            "village":job_post.grahak.profile.village
                        })
        elif sahayak.user_type == 'MachineMalik':
            job_posts_machin=JobMachine.objects.all().filter(status='Pending').order_by('-id')
            for job_post in job_posts_machin:
                grahak_profile = job_post.grahak.profile
                # print(grahak_profile)
                grahak_lat = grahak_profile.latitude
                grahak_lon = grahak_profile.longitude
                distance = calculate_distance(sahayak_lat, sahayak_lon, grahak_lat, grahak_lon)
                # print(distance)
                if distance <= 10:
                    # serial=GetJobMachineSerializer(job_post)
                    if not JobBooking.objects.filter(jobmachine=job_post,booking_user=request.user):
                        result.append({
                            "id":job_post.id,
                            "job_type":job_post.job_type,
                            "status":job_post.status,
                            "date":job_post.date,
                            "datetime":job_post.datetime,
                            "payment_your":job_post.payment_your,
                            "fawda_fee":job_post.fawda_fee,
                            "description":job_post.description,
                            "total_amount":job_post.total_amount,
                            "total_amount_machine":job_post.total_amount_machine,
                            "land_area":job_post.land_area,
                            "land_type":job_post.land_type,
                            "job_number":job_post.job_number,
                            "work_type":job_post.work_type,
                            "machine":job_post.machine,
                            "grahak":job_post.grahak.profile.name,
                            "village":job_post.grahak.profile.village

                        })        
        else:
            return Response({'message':{'You are not Sahayak or MachinMalik'}})    
        paginator = PageNumberPagination()
        paginator.page_size = self.PAGE_SIZE
        paginated_result = paginator.paginate_queryset(result, request)
        response_data = {'page': paginator.page.number, 'total_pages': paginator.page.paginator.num_pages, 'results': paginated_result}
    # Add next page URL to response
        if paginator.page.has_next():
            base_url = request.build_absolute_uri().split('?')[0]
            response_data['next'] = f"{base_url}?page={paginator.page.next_page_number()}"
        return Response(response_data)




class GetMachineDetails(APIView):
    authentication_classes=[BearerTokenAuthentication,]
    permission_classes=[AllowAny,]
    def get(self,request,format=None):
        work_type_id=request.data.get('id')
        if work_type_id:
            data=MachineType.objects.filter(worktype=work_type_id)
            serializers=MachineSerializers(data, many=True)
            return Response(serializers.data)
        else:
            data=MachineType.objects.all()    
            machines_by_work_type = {}
            for machine in data:
                work_type_str = str(machine.worktype)
                machine_dict = {"id": machine.id, "machine": machine.machine}
                if work_type_str in machines_by_work_type:
                    machines_by_work_type[work_type_str].append(machine_dict)
                else:
                    machines_by_work_type[work_type_str] = [machine_dict]
            return Response(machines_by_work_type)

class GetMachineDetailArray(APIView):
    authentication_classes=[BearerTokenAuthentication,]
    permission_classes=[IsAuthenticated,]
    def post(self,request,format=None):
        worktype=request.data.get('work_type')
        if worktype:
            get_machine=MachineType.objects.filter(worktype__name=worktype)    
            serializer=MachineSerializers(get_machine,many=True)
            return Response(serializer.data)
        else:
            return Response({'message':{'work_type required !'}})    

class GetWorkType(APIView):
    authentication_classes=[BearerTokenAuthentication,]
    permission_classes=[AllowAny,]
    def get(self,request,format=None):
        data=WorkType.objects.all()
        serializer=WorkTypeSerialiser(data,many=True)
        return Response(serializer.data)



###--------------------------------------------------------------------------------####

class Requestuser(APIView):
    authentication_classes = [BearerTokenAuthentication,]
    permission_classes=[IsAuthenticated,]
    def get(self,request):
        user=request.user
        return Response({'user':user.mobile_no,'user_type':user.user_type,'status':status.HTTP_200_OK})

from .serializers import JobBookingSerializers

class BookingDetailsAndJobDetails(APIView):
    permission_classes=[IsAuthenticated,]
    authentication_classes=[BearerTokenAuthentication,]
    def post(self,request,format=None):
        job_id=request.data.get('id')
        job_type=request.data.get('job_type')
        jobstatus=request.data.get('job_status')
        array=[]
        if not job_id:
            return Response({'id':{'This field is required !'}})
        if not job_type:
            return Response({'job_type':{'This field is required !'}})    
        if not jobstatus:
            return Response({'job_status':{'This field is required !'}})    
        if request.user.user_type not in ['Sahayak','MachineMalik','Grahak']:
            return Response({'message':{'unauthorised user !'}})    
        if job_type =='individuals_sahayak' and jobstatus =='Pending':
            try:
                get_data_sahayak=JobSahayak.objects.get(pk=job_id)
            except JobSahayak.DoesNotExist:
                return Response({'message':{'Job does not exist !'}})    
            serializer_sahayak=JobSahaykSerialiser(get_data_sahayak)
            array.append(serializer_sahayak.data)
        elif job_type == 'machine_malik' and job_type == 'Pending':
            try:
               get_data_machine=JobMachine.objects.get(pk=job_id)    
            except JobMachine.DoesNotExist:
                return Response({'message':{'job does not exist !'}})   
            serializer_machine=JobMachineSerializers(get_data_machine)
            array.append(serializer_machine.data)
        else:
            try:
               get_data_bookig=JobBooking.objects.get(pk=job_id)    
            except JobBooking.DoesNotExist:
                return Response({'message':{'booking does not exist !'}})   
            serializer_machine=JobBookingSerializers(get_data_bookig)
            array.append(serializer_machine.data)
        return Response({'data':array})    



# class BookingCompletedHistory(APIView):
#     permission_classes=[IsAuthenticated,]
#     authentication_classes=[BearerTokenAuthentication,]
#     def get(self,request,format=None):
#         array=[]
#         if request.user.user_type =='Sahayak':
#             get_booking=JobBooking.objects.all().filter(status='Completed')
#             for booking in get_booking:
#                 if booking.jobsahayak:
#                     if booking.jobsahayak.job_type == 'individuals_sahayak':
#                         array.append({
#                             'description',
#                             'village',
#                             'datetime',
#                             'land_area',
#                             'land_type',
#                             'pay_amount_male',
#                             'pay_amount_female',
#                             'num_days',
#                             'count_male',
#                             'count_female',
#                             'total_amount_sahayak',
#                             'payment_your',
#                             'fawda_fee',
#                             'status',
#                         })


# class RefreshDataMyBooking(APIView):
#     permission_classes=[IsAuthenticated,]
#     authentication_classes=[BearerTokenAuthentication,]
#     def post(self,request,format=None):
#         sahayak_job_id=request.data.get('sahayak_job_id')
#         machine_job_id=request.data.get('machine_job_id')
#         sahayak_job_number=request.data.get('sahayak_job_number')
#         machine_job_number=request.data.get('machine_job_number')
#         job_bookings = JobBooking.objects.filter(Q(jobsahayak__id=sahayak_job_id) & Q(jobsahayak__job_number=sahayak_job_number))
#         booking_data = {}
#         for booking in job_bookings:
#             job_id = booking.jobsahayak.id
#             if job_id not in booking_data:
#                 booking_data[job_id] = {
#                     'total_amount': 0,
#                     'count_male': 0,
#                     'count_female': 0,
#                     'total_amount_sahayak': 0,
#                     'payment_your': 0,
#                     'fawda_fee': 0,
#                     'job_type': booking.jobsahayak.job_type,
#                     'sahayaks': []
#                 }
#             if booking.jobsahayak.job_type == 'individuals_sahayak':
#                 booking_data[job_id]['total_amount'] += float(booking.total_amount) if booking.total_amount else 0
#                 booking_data[job_id]['count_male'] += int(booking.count_male) if booking.count_male else 0
#                 booking_data[job_id]['count_female'] += int(booking.count_female) if booking.count_female else 0
#                 booking_data[job_id]['total_amount_sahayak'] += int(booking.total_amount_sahayak) if booking.total_amount_sahayak else 0
#                 booking_data[job_id]['payment_your'] += float(booking.payment_your) if booking.payment_your else 0
#                 booking_data[job_id]['fawda_fee'] += float(booking.fawda_fee) if booking.fawda_fee else 0
#                 booking_data[job_id]['sahayaks'].append({
#                     'booking_id': booking.id,
#                     'job_id':booking.jobsahayak.id,
#                     'job_number':booking.jobsahayak.job_number,
#                     'status':booking.status,
#                     'booking_user_id': booking.booking_user.id,
#                     'sahayak_name': booking.booking_user.profile.name,
#                     'sahayak_village': booking.booking_user.profile.village,
#                     'sahayak_mobile_no': booking.booking_user.mobile_no,
#                     'pay_amount_male': booking.jobsahayak.pay_amount_male,
#                     'pay_amount_female': booking.jobsahayak.pay_amount_female,
#                     'count_male': booking.count_male,
#                     'count_female': booking.count_female,
#                     'job_type':booking.jobsahayak.job_type,
#                     'num_days':booking.jobsahayak.num_days,
#                     'datetime':booking.jobsahayak.datetime,
#                     'description':booking.jobsahayak.description,
#                     'land_area':booking.jobsahayak.land_area,
#                     'land_type':booking.jobsahayak.land_type
#                 })
#             else:
#                 booking_data[job_id]['total_amount'] += float(booking.total_amount) if booking.total_amount else 0
#                 booking_data[job_id]['total_amount_sahayak'] += float(booking.total_amount_theka) if booking.total_amount_theka else 0
#                 booking_data[job_id]['payment_your'] += float(booking.payment_your) if booking.payment_your else 0
#                 booking_data[job_id]['fawda_fee'] += float(booking.fawda_fee) if booking.fawda_fee else 0
#                 booking_data[job_id]['sahayaks'].append({
#                     'booking_id': booking.id,
#                     'job_id':booking.jobsahayak.id,
#                     'job_number':booking.jobsahayak.job_number,
#                     'status':booking.jobsahayak.status,
#                     'booking_user_id': booking.booking_user.id,
#                     'thekedar_name': booking.booking_user.profile.name,
#                     'thekedar_village': booking.booking_user.profile.village,
#                     'thekedar_mobile_no': booking.booking_user.mobile_no,
#                     'datetime':booking.jobsahayak.datetime,
#                     'job_type':booking.jobsahayak.job_type,
#                     'description':booking.jobsahayak.description,
#                 })

#         response_data = {
#             'bookings': list(booking_data.values())
#         }  
#         bookings1 = JobBooking.objects.filter(Q(jobmachine__id=machine_job_id) & Q(jobmachine__job_number=machine_job_number))
#         booking_data1=[]
#         if bookings1:
#             for booking in bookings1:
#                 booking_data1.append({
#                     'booking_id':booking.id,
#                     'job_id':booking.jobmachine.id,
#                     'work_type':booking.jobmachine.work_type,
#                     'job_type':booking.jobmachine.job_type,
#                     'machine':booking.jobmachine.machine,
#                     'datetime':booking.jobmachine.datetime,
#                     'land_area':booking.jobmachine.land_area,
#                     'total_amount':booking.total_amount,
#                     'total_amount_machine':booking.total_amount_machine,
#                     'payment_your':booking.payment_your,
#                     'fawda_fee':booking.fawda_fee,
#                     'status':booking.status,
#                     'machine_malik_name':booking.booking_user.profile.name,
#                     'machine_malik_village':booking.booking_user.profile.village,
#                     'machine_malik_mobile_no':booking.booking_user.mobile_no,
#                     'booking_user_id':booking.booking_user.id,
#                     'job_number':booking.jobmachine.job_number,
#                     'land_type':booking.jobmachine.land_type
                    
#                 })
#         booking2=JobSahayak.objects.filter(pk=sahayak_job_id,job_number=sahayak_job_number,status='Pending')
#         serializer1=JobSahaykSerialiser(booking2,many=True)
#         booking3=JobMachine.objects.filter(pk=machine_job_id,job_number=machine_job_number,status='Pending')
#         serializer2=GetJobMachineSerializer(booking3,many=True)
        
#         return Response({
#             'sahayk_booking_details':response_data,
#             'machine_malik_booking_details':booking_data1,
#             'sahayak_pending_booking_details':serializer1.data,
#             'machine_malik_pending_booking_details':serializer2.data
#         })









class RefreshfMyBookingDetails(APIView):
    permission_classes=[IsAuthenticated,]
    authentication_classes=[BearerTokenAuthentication,]
    global response_data
    response_data={}
    def post(self,request,format=None):
        global response_data
        response_data={
            'total_amount': 0,
            'count_male': 0,
            'count_female': 0,
            'total_amount_sahayak': 0,
            'payment_your': 0,
            'fawda_fee': 0,
            'bookings': 0,
        }
        sahayak_job_id=request.data.get('sahayak_job_id', 0) or 0
        machine_job_id=request.data.get('machine_job_id', 0) or 0
        sahayak_job_number=request.data.get('sahayak_job_number', 0) or 0
        machine_job_number=request.data.get('machine_job_number', 0) or 0
        if not request.user.user_type=='Grahak':
            return Response({'message':{'you are not Grahak !'}})
        bookings = JobBooking.objects.filter(Q((Q(jobsahayak__id=sahayak_job_id) & Q(jobsahayak__job_number=sahayak_job_number)) & Q(status__in=['Accepted','Booked','Ongoing','Completed'])| (Q(jobmachine__id=machine_job_id) & Q(jobmachine__job_number=machine_job_number)& Q(status__in=['Accepted','Booked','Ongoing','Completed']))))
        total_amount = 0
        count_male = 0
        count_female = 0
        total_amount_sahayak = 0
        payment_your = 0
        fawda_fee = 0
        booking_data = []
        booking_data1=[]
        booking_theka=[]
        for booking in bookings:
            if booking.jobsahayak:
                if booking.jobsahayak.job_type == 'individuals_sahayak':
                    total_amount += float(booking.total_amount) if booking.total_amount else 0
                    count_male += int(booking.count_male) if booking.count_male else 0
                    count_female += int(booking.count_female) if booking.count_female else 0
                    total_amount_sahayak += int(booking.total_amount_sahayak) if booking.total_amount_sahayak else 0
                    payment_your += float(booking.payment_your) if booking.payment_your else 0
                    fawda_fee += float(booking.fawda_fee) if booking.fawda_fee else 0
                    booking_data.append({
                        'booking_id': booking.id,
                        'job_id':booking.jobsahayak.id,
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
                        'land_type':booking.jobsahayak.land_type,
                        'pay_for_male':booking.jobsahayak.pay_amount_male,
                        'pay_for_female':booking.jobsahayak.pay_amount_female,
                        'num_days':booking.jobsahayak.num_days,
                        'job_type':booking.jobsahayak.job_type,
                        'user_type':booking.booking_user.user_type,
                        'sahayak_name':booking.booking_user.profile.name,
                        'sahayak_village':booking.booking_user.profile.village,
                        'sahayak_mobile_no':booking.booking_user.mobile_no,
                        'job_number':booking.jobsahayak.job_number
                    })
                else:
                    booking_theka.append({
                        'booking_id':booking.id,
                        'job_id':booking.jobsahayak.id,
                        'status':booking.status,
                        # 'total_amount':booking.total_amount,
                        # 'total_amount_theka':booking.total_amount_theka,
                        # 'payment_your':booking.payment_your,
                        # 'datetime':booking.jobsahayak.datetime,
                        # 'land_area':booking.jobsahayak.land_area,
                        # 'land_type':booking.jobsahayak.land_type,
                        # 'description':booking.jobsahayak.description,
                        # 'fawda_fee':booking.fawda_fee,
                        # 'booking_user_id':booking.booking_user.id,
                        'job_type':booking.jobsahayak.job_type,
                        # 'user_type':booking.booking_user.user_type,
                        # 'thekedar_name':booking.booking_user.profile.name,
                        # 'thekedar_village':booking.booking_user.profile.village,
                        # 'thekedar_mobile_no':booking.booking_user.mobile_no,
                        'job_number':booking.jobsahayak.job_number
                    })    
                # response_data = {
                #     'total_amount': total_amount,
                #     'count_male': count_male,
                #     'count_female': count_female,
                #     'total_amount_sahayak': total_amount_sahayak,
                #     'payment_your': payment_your,
                #     'fawda_fee': fawda_fee,
                #     'bookings': booking_data,
                # }

            else:
               
                booking_data1.append({
                    'booking_id':booking.id,
                    'job_id':booking.jobmachine.id,
                    # 'work_type':booking.jobmachine.work_type,
                    # 'description':booking.jobmachine.description,
                    # 'machine':booking.jobmachine.machine,
                    # 'datetime':booking.jobmachine.datetime,
                    # 'land_area':booking.jobmachine.land_area,
                    # 'land_type':booking.jobmachine.land_type,
                    'total_amount':booking.jobmachine.total_amount,
                    'total_amount_machine':booking.jobmachine.total_amount_machine,
                    # 'payment_your':booking.jobmachine.payment_your,
                    'status':booking.status,
                    # 'payment_your':booking.payment_your,
                    'job_type':booking.jobmachine.job_type,
                    # 'fawda_fee':booking.fawda_fee,
                    # 'user_type':booking.booking_user.user_type,
                    # 'machine_malik_name':booking.booking_user.profile.name,
                    # 'machine_malik_village':booking.booking_user.profile.village,
                    # 'machine_malik_mobile_no':booking.booking_user.mobile_no,
                    # 'booking_user_id':booking.booking_user.id,
                    'job_number':booking.jobmachine.job_number
                    
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
        booking2=JobSahayak.objects.filter(pk=sahayak_job_id,status='Pending')
        serializer1=JobSahaykSerialiser(booking2,many=True)
        booking3=JobMachine.objects.filter(pk=machine_job_id,status='Pending')    
        serializer2=GetJobMachineSerializer(booking3,many=True)
        return Response({
            'sahayk_booking_details':response_data,
            'booking_theke_pe_kam':booking_theka,
            'machine_malik_booking_details':booking_data1,
            'sahayak_pending_booking_details':serializer1.data,
            'machine_malik_pending_booking_details':serializer2.data
        })




class RefreshMyjobsDetails(APIView):
    permission_classes=[IsAuthenticated,]
    authentication_classes=[BearerTokenAuthentication,]
    def post(self,request,format=None):
        booking_id=request.data.get('booking_id')
        myjob_list=[]
        if not booking_id:
            return Response({'booking_id':{'This field is required !'}})
        if request.user.user_type not in ['Sahayak','MachineMalik']:
            return Response({'message':{'you are not Sahayak or MachineMalik !'}})
        try:
            job=JobBooking.objects.get(pk=booking_id)
        except JobBooking.DoesNotExist:
            return Response({'message':{'job does not exist !'}})   
        if job.jobsahayak:
            if job.booking_user == request.user:
                if job.jobsahayak.job_type =='individuals_sahayak':
                    myjob_list.append({
                        "booking_id":job.id,
                        "job_type":job.jobsahayak.job_type,
                        # "description":job.jobsahayak.description,
                        # "village":job.jobsahayak.grahak.profile.village,
                        # "land_area":job.jobsahayak.land_area,
                        # "land_type":job.jobsahayak.land_type,
                        # "pay_amount_male":job.pay_amount_male,
                        # "pay_amount_female":job.pay_amount_female,
                        # "fawda_fee":job.fawda_fee,
                        # "count_male":job.count_male,
                        # "count_female":job.count_female,
                        # "payment_your":job.payment_your,
                        # "total_amount_sahayak":job.total_amount_sahayak,
                        # "num_days":job.jobsahayak.num_days,
                        # "datetime":job.jobsahayak.datetime,
                        # "grahak_name":job.jobsahayak.grahak.profile.name,
                        # "grahak_phone":job.jobsahayak.grahak.mobile_no,
                        "status":job.status
                    })
                else:
                    myjob_list.append({
                        "booking_id":job.id,
                        "job_type":job.jobsahayak.job_type,
                        # "description":job.jobsahayak.description,
                        # "village":job.jobsahayak.grahak.profile.village,
                        # "datetime":job.jobsahayak.datetime,
                        # "land_area":job.jobsahayak.land_area,
                        # "land_type":job.jobsahayak.land_type,
                        # "fawda_fee":job.fawda_fee,
                        # "payment_your":job.payment_your,
                        # "total_amount_theka":job.total_amount_theka,
                        # "grahak_name":job.jobsahayak.grahak.profile.name,
                        # "grahak_phone":job.jobsahayak.grahak.mobile_no,
                        "status":job.status
                    })
                    
        else:
            if job.booking_user == request.user:
                myjob_list.append({
                    "booking_id":job.id,
                    "job_type":job.jobmachine.job_type,
                    # "description":job.jobmachine.description,
                    # "village":job.jobmachine.grahak.profile.village,
                    # "datetime":job.jobmachine.datetime,
                    # "land_area":job.jobmachine.land_area,
                    # "land_type":job.jobmachine.land_type,
                    # "fawda_fee":job.fawda_fee,
                    # "payment_your":job.payment_your,
                    # "total_amount_machine":job.total_amount_machine,
                    # "grahak_name":job.jobmachine.grahak.profile.name,
                    # "grahak_phone":job.jobmachine.grahak.mobile_no,
                    "status":job.status,
                    # "work_type":job.jobmachine.work_type,
                    # "machine":job.jobmachine.machine 
                })
        return Response(myjob_list)
    




