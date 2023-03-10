from django.shortcuts import render
from .models import *
from .models import JobMachine
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from rest_framework.permissions import IsAuthenticated
# Create your views here.

class BookingThekePeKam(APIView):
    permission_classes=[IsAuthenticated,]
    def post(self,request,format=None):
        if request.user.status == 'Grahak':
            serializers=PostJobThekePeKamSerializer(data=request.data)
            if serializers.is_valid(raise_exception=True):
                datetime=serializers.data.get('datetime')
                description=serializers.data.get('description')
                landtype=serializers.data.get('land_type')
                landarea=serializers.data.get('land_area')
                amount=serializers.data.get('total_amount')
                grahak=request.user
                existing_job = JobSahayak.objects.filter(
                    datetime=datetime,
                    description=description,
                    land_area=landarea,
                    land_type=landtype,
                    total_amount=amount,
                    job_type='theke_pe_kam',
                    grahak=grahak
                ).first()
                if existing_job:
                    return Response({'error': 'Booking already exists'})
                job=JobSahayak.objects.create(
                    datetime=datetime,
                    description=description,
                    land_area=landarea,
                    land_type=landtype,
                    total_amount=amount,
                    job_type='theke_pe_kam',
                    grahak=grahak
                )
                serial=GetJobThekePeKamSerializer(job)
                return Response({'success':'Booking created !','data':serial.data})
        else:
            return Response({'error':'You are not Grahak'})  

class BookingSahayakIndividuals(APIView):
    permission_classes=[IsAuthenticated,]
    def post(self,request,format=None):
        if request.user.status == 'Grahak':
            serializers=PostJobIndividualSerializer(data=request.data) 
            if serializers.is_valid(raise_exception=True):
                datetime=serializers.data.get('datetime')
                description=serializers.data.get('description')
                landtype=serializers.data.get('land_type')
                landarea=serializers.data.get('land_area')
                countmale=int(serializers.data.get('count_male'))
                countfemale=int(serializers.data.get('count_female'))
                payformale=int(serializers.data.get('pay_amount_male'))
                payforfemale=int(serializers.data.get('pay_amount_female'))
                noofdays=int(serializers.data.get('num_days'))
                grahak=request.user

                # Check if variables are not None
                if countmale is None or payformale is None or countfemale is None or payforfemale is None or noofdays is None:
                    return Response({'error':'One or more variables are None'})
                # total_amount=(countmale*payformale+countfemale*payforfemale)*noofdays
                existing_job=JobSahayak.objects.filter(
                    datetime=datetime,
                    description=description,
                    land_type=landtype,
                    land_area=landarea,
                    count_male=countmale,
                    count_female=countfemale,
                    pay_amount_male=payformale,
                    pay_amount_female=payforfemale,
                    num_days=noofdays,
                    # total_amount=total_amount,
                    job_type='individuals_sahayak',
                    grahak=grahak
                ).first()
                if existing_job:
                    return Response({'error':'Job already exist !'})
                job=JobSahayak.objects.create(
                    datetime=datetime,
                    description=description,
                    land_type=landtype,
                    land_area=landarea,
                    count_male=countmale,
                    count_female=countfemale,
                    pay_amount_male=payformale,
                    pay_amount_female=payforfemale,
                    num_days=noofdays,
                    # total_amount=total_amount,
                    job_type='individuals_sahayak',
                    grahak=grahak
                )
                serial=GetJobIndividualsSerializer(job)
                return Response({'success':'job created !','data':serial.data})
        else:
            return Response({'error':'You are not Grahak'})
        
class BookingJobMachine(APIView):
    permission_classes=[IsAuthenticated,]
    def post(self,request,format=None):
        if request.user.status == 'Grahak':
            serializers=JobMachineSerializers(data=request.data)
            if serializers.is_valid(raise_exception=True):
                landprepare=serializers.data.get('landpreparation')
                print(landprepare)
                harvesting=serializers.data.get('harvesting')
                sowing=serializers.data.get('sowing')
                others=serializers.data.get('others')
                datetime=serializers.data.get('datetime')
                landarea=serializers.data.get('land_area')
                landtype=serializers.data.get('land_type')
                amount=serializers.data.get('total_amount')
                grahak=request.user
                if landprepare is not None and harvesting is not None and sowing is not None:
                    lnd=LandPreparation.objects.get(name=landprepare)
                    harv=Harvesting.objects.get(name=harvesting)
                    sow=Sowing.objects.get(name=sowing)
                else:
                    return Response({"error":"provide valid creadientials"})    
                existing_job=JobMachine.objects.filter(
                    landpreparation=lnd,
                    harvesting=harv,
                    sowing=sow,
                    others=others,
                    datetime=datetime,
                    land_area=landarea,
                    land_type=landtype,
                    total_amount=amount,
                    grahak=grahak,

                )
                if existing_job:
                    return Response({'error':'job already exist !'})
                job=JobMachine.objects.create(
                    landpreparation=lnd,
                    harvesting=harv,
                    sowing=sow,
                    others=others,
                    datetime=datetime,
                    land_area=landarea,
                    land_type=landtype,
                    total_amount=amount,
                    grahak=grahak,
                )
                serial=GetJobMachineSerializer(job)    
                return Response({'success':'job created !','data':serial.data})
        else:
            return Response({'error':'You are not Grahak !'})        


###---------------------------------------------------------------------------###
# from django.contrib.gis.geos import Point
# from django.contrib.gis.measure import D
# from django.db.models import F
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from django.db.models.functions import Cast
# from django.http import JsonResponse
# from authentication.models import *
# from rest_framework import generics
# from django.db.models import FloatField
# from django.contrib.gis.db.models.functions import Distance
# from django.contrib.gis.geos import GEOSGeometry
# from django.db.models import Q


        


# class JobSahayakWithin5km(APIView):
#     def get(self, request):
#         # Get the user's latitude and longitude from the request
#         profile=Profile.objects.get(user=request.user)
#         user_latitude =profile.latitude
#         user_longitude = profile.longitude
        
#         # Create a Point object from the user's location
#         user_location = Point(user_longitude, user_latitude)

#         print(user_location)
        
#         # Find all jobs within 5km of the user's location
#         nearby_jobs = JobSahayak.objects.filter(Q(grahak__location__distance_lte=(user_location, D(km=5))) &
#             Q(grahak__is_active=True)  # assuming you have an "is_active" field for Grahak
#         ).annotate(
#             distance=Distance('grahak__location', user_location)
#         ).order_by('distance')
#         print(nearby_jobs)
#         # Serialize the jobs and return the response
#         # data = []
#         # for job in nearby_jobs:
#         #     serialized_job = {
#         #         'id': job.id,
#         #         'grahak': job.grahak.profile.name,
#         #         'job_type': job.job_type,
#         #         'status': job.status,
#         #         'village': job.village,
#         #         'date': job.date,
#         #         'distance': job.distance.m,
#         #     }
#         #     data.append(serialized_job)
#         return Response({"msg":"success"})
    
# class JobSahayakWithin5kms(generics.ListAPIView):
#     serializer_class = JobSahaykSerialiser

#     queryset = JobSahayak.objects.all()

#     def get_queryset(self):
#         user_latitude = self.request.query_params.get('latitude', None)
#         user_longitude = self.request.query_params.get('longitude', None)

#         if user_latitude and user_longitude:
#             user_location = GEOSGeometry(f"POINT({user_longitude} {user_latitude})")
#             queryset = JobSahayak.objects.annotate(distance=Distance('grahak__profile__location', user_location)).order_by('distance')
#         else:
#             queryset = JobSahayak.objects.all()
        
#         return queryset
    


# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# # from geopy.distance import distance

# @csrf_exempt
# def nearby_jobs(request):
#     if request.method == 'GET':
#         # Get the user's latitude and longitude from the request data
#         profile=Profile.objects.get(user=request.user)
#         user_lat = float(profile.latitude)
#         user_lon = float(profile.longitude)

#         # Get a queryset of all jobs
#         job_queryset = JobSahayak.objects.all().filter(status='Pending')

#         # Calculate the distance between the user's location and each job location
#         for job in job_queryset:
#             grahak=Profile.objects.get(user=job.grahak)
#             job_location = (grahak.latitude, grahak.longitude)
#             user_location = (user_lat, user_lon)
#             job.distance = distance(user_location, job_location).km

#         # Filter the queryset to include only jobs that are within 5km of the user's location
#         nearby_jobs = [job for job in job_queryset if job.distance <= 5]

#         # Create a list of dictionaries representing each nearby job
#         job_list = []
#         for job in nearby_jobs:
#             job_dict = {
#                 'id': job.id,
#                 'job_type': job.job_type,
#                 'status': job.status,
#                 'village': job.village,
#                 'distance': round(job.distance, 2)
#             }
#             job_list.append(job_dict)

#         # Return a JSON response of the nearby jobs
#         return JsonResponse({'jobs': job_list})
#     else:
#         # Return a 405 Method Not Allowed response for all other request methods
#         return JsonResponse({'error': 'Method Not Allowed'}, status=405)
import math

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

@csrf_exempt
def get_job_posts(request):
    sahayak = request.user
    sahayak_profile = sahayak.profile
    sahayak_lat = sahayak_profile.latitude
    sahayak_lon = sahayak_profile.longitude
    job_posts = JobSahayak.objects.filter(grahak=request.user,status='Pending')
    result = []
    for job_post in job_posts:
        grahak_profile = job_post.grahak.profile
        grahak_lat = grahak_profile.latitude
        grahak_lon = grahak_profile.longitude
        distance = calculate_distance(sahayak_lat, sahayak_lon, grahak_lat, grahak_lon)
        if distance <= 5:
            result.append({
                'id': job_post.id,
                'job_type': job_post.job_type,
                'status': job_post.status,
                'village': job_post.village,
                'datetime': job_post.formatted_datetime(),
                'description': job_post.description,
                'distance': distance
            })
    return JsonResponse(result, safe=False)
