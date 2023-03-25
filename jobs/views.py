from django.shortcuts import render
from .models import *
from .models import JobMachine
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
import math
from rest_framework.permissions import IsAuthenticated,AllowAny
import uuid
# Create your views here.

class BookingThekePeKam(APIView):
    permission_classes=[IsAuthenticated,]
    def post(self,request,format=None):
        if request.user.user_type == 'Grahak':
            serializers=PostJobThekePeKamSerializer(data=request.data)
            if serializers.is_valid(raise_exception=True):
                datetime=serializers.data.get('datetime')
                description=serializers.data.get('description')
                landtype=serializers.data.get('land_type')
                landarea=serializers.data.get('land_area')
                amount=serializers.data.get('total_amount_theka')
                grahak=request.user
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
                    return Response({'error': 'Booking already exists'})
                    
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
                return Response({'success':'Booking created !','data':serial.data})
        else:
            return Response({'error':'You are not Grahak'})  

class BookingSahayakIndividuals(APIView):
    permission_classes=[IsAuthenticated,]
    def post(self, request, format=None):
        if request.user.user_type == 'Grahak':
            serializer = PostJobIndividualSerializer(data=request.data) 
            if serializer.is_valid(raise_exception=True):
                data = serializer.validated_data
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
                    pay_amount_male=data['pay_amount_male'],
                    pay_amount_female=data['pay_amount_female'],
                    num_days=data['num_days'],
                    # fawda_fee_percentage=data['fawda_fee_percentage']
                )
                if existing_jobs.exists():
                    return Response({'message': 'error', 'message': 'A job with the same details already exists.'})
                
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
                    pay_amount_male=data['pay_amount_male'],
                    pay_amount_female=data['pay_amount_female'],
                    num_days=data['num_days'],
                    job_number=job_number
                    # fawda_fee_percentage=data['fawda_fee_percentage']
                )
                job.save()
                serial=GetJobIndividualsSerializer(job)
                return Response({'message': 'success','data':serial.data})
        return Response({'message': 'You are not Grahak'})

        
class BookingJobMachine(APIView):
    permission_classes=[IsAuthenticated,]
    def post(self,request,format=None):
        if request.user.user_type == 'Grahak':
            serializers=JobMachineSerializers(data=request.data)
            if serializers.is_valid(raise_exception=True):
                worktype=serializers.data.get('work_type')
                machine=serializers.data.get('machine')
                others=serializers.data.get('others')
                datetime=serializers.data.get('datetime')
                landarea=serializers.data.get('land_area')
                landtype=serializers.data.get('land_type')
                amount=serializers.data.get('total_amount_machine')
                grahak=request.user  
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
                    return Response({'error':'job already exist !'})
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
                return Response({'success':'job created !','data':serial.data})
        else:
            return Response({'error':'You are not Grahak !'})        


###---------------------------------------------------------------------------###
class GetSahayakJobDetails(APIView):
    permission_classes=[IsAuthenticated,]
    def get(self,request,format=None):
        if request.user.user_type == 'Sahayak':
            jobid=request.data.get('job_id')
            if not jobid:
                return Response({'error':'jobid required !'})            
            try:
               getjob = JobSahayak.objects.get(pk=jobid)
            except JobSahayak.DoesNotExist:
                return Response({'error': 'Job does not exist !'})
            serial=JobSahaykSerialiser(getjob)    
            return Response({'seccess':True,'data':serial.data})
        return Response({'error':'you are not Sahayak'})
        
class GetMachineJobDetails(APIView):
    permission_classes=[IsAuthenticated,]
    def get(self,request,format=None):
        if request.user.user_type == 'MachineMalik':
            jobid=request.data.get('job_id')
            if not jobid:
                return Response({'error':'jobid required !'})            
            try:
               getjob = JobMachine.objects.get(pk=jobid)
            except JobMachine.DoesNotExist:
                return Response({'error': 'Job does not exist !'})
            serial=GetJobMachineSerializer(getjob)    
            return Response({'seccess':True,'data':serial.data})
        return Response({'error':'you are not MachineMalik'})



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
    permission_classes=[IsAuthenticated,]
    # @csrf_exempt
    def get(self,request,format=None):
        result = []
        sahayak = request.user
        sahayak_profile = sahayak.profile
        sahayak_lat = sahayak_profile.latitude
        sahayak_lon = sahayak_profile.longitude
        if sahayak.user_type == 'Sahayak':
            job_posts = JobSahayak.objects.all().filter(status='Pending')
            for job_post in job_posts:
                grahak_profile = job_post.grahak.profile
                grahak_lat = grahak_profile.latitude
                grahak_lon = grahak_profile.longitude
                # print(grahak_lat,grahak_lon)
                distance = calculate_distance(sahayak_lat, sahayak_lon, grahak_lat, grahak_lon)
                print(distance)
                if distance <= 5:
                    serial=GetJobIndividualsSerializer(job_post)
                    result.append(serial.data)
        elif sahayak.user_type == 'MachineMalik':
            job_posts_machin=JobMachine.objects.all().filter(status='Pending')
            for job_post in job_posts_machin:
                grahak_profile = job_post.grahak.profile
                # print(grahak_profile)
                grahak_lat = grahak_profile.latitude
                grahak_lon = grahak_profile.longitude
                distance = calculate_distance(sahayak_lat, sahayak_lon, grahak_lat, grahak_lon)
                # print(distance)
                if distance <= 10:
                    serial=GetJobMachineSerializer(job_post)
                    result.append(serial.data)        
        else:
            return Response({'error':'You are not Sahayak or MachinMalik'})            
        return Response(result)




class GetMachineDetails(APIView):
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


# class GetMachineDetails(APIView):
#     permission_classes=[AllowAny,]
#     def get(self,request,format=None):
#         harvesting=Harvesting.objects.all()
#         landpreparation=LandPreparation.objects.all()
#         sowing=Sowing.objects.all()
#         serial1=LandSerializers(landpreparation,many=True)
#         print(serial1.data)
#         serial2=HarvestingSerializers(harvesting,many=True)
#         serial3=SowingSerializers(sowing,many=True)
#         return Response({'landpreparation':serial1.data,'haevesting':serial2.data,'sowing':serial3.data})



###--------------------------------------------------------------------------------####
class Requestuser(APIView):
    def get(self,request):
        user=request.user
        return Response({'user':user.mobile_no,'user_type':user.user_type})
    








# result.append({
            #     'id': job_post.id,
            #     'job_type': job_post.job_type,
            #     'status': job_post.status,
            #     'village': job_post.village,
            #     'datetime': job_post.formatted_datetime(),
            #     'description': job_post.description,
            #     'distance': distance
            # })

