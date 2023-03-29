from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from .models import *
from django.views import View
from datetime import datetime, date, timedelta
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate,login
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse
import re



import random
from rest_framework.permissions import AllowAny,IsAuthenticated
# from twilio.rest import Client


def test(request):
    return render(request,'authentication/test.html')


def get_token(user):
    refresh = RefreshToken.for_user(user)
    return {
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh),
    }

class RegisterApi(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        # Get data from request
        name = request.data.get('name')
        gender = request.data.get('gender')
        phone_number = request.data.get('phone')
        mohalla = request.data.get('mohalla')
        village = request.data.get('village')
        user_type = request.data.get('user_type')
        state = request.data.get('state')
        district = request.data.get('district')
        latitude= request.data.get('latitude')
        longitude=request.data.get('longitude')


        # Validate phone number
        if not phone_number:
            return Response({'error': 'Phone number is required.'})
        if not re.match(r'^\d{10}$', phone_number):
            return Response({'error': 'Phone number should be 10 digits.'})
        # Validate user_type
        if not user_type:
            return Response({'error': 'User type is required.'})
        if user_type not in ["Grahak", "Sahayak", "MachineMalik"]:
            return Response({'error': 'User type should be one of the following: Grahak, Sahayak, MachineMalik.'})

        # Validate other fields
        if not name:
            return Response({'error': 'Name is required.'})
        if not gender:
            return Response({'error': 'Gender is required.'})
        if gender not in ["Male", "Female"]:
            return Response({'error': 'Gender should be Male or Female'})    
        if not mohalla:
            return Response({'error': 'Mohalla is required.'})
        if not village:
            return Response({'error': 'Village is required.'})
        if not state:
            return Response({'error': 'State is required.'})
        if not district:
            return Response({'error': 'District is required.'})
        if not latitude or not longitude:
            return Response({'error':'latitude and longitude can not null'})
        if not re.match(r'^[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?)$', str(latitude)):
            return Response({'error': 'Invalid latitude format.'})
        if not re.match(r'^[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)$', str(longitude)):
            return Response({'error': 'Invalid longitude format.'})
        try:
            state = State.objects.get(name=state)
        except State.DoesNotExist:
            return Response({'error': f'State with name {state} does not exist in the database.'})
        
        # Check if district exists within the state
        try:
            district = District.objects.get(name=district, state=state)
        except District.DoesNotExist:
            return Response({'error': f'District with name {district} does not exist within the state {state}.'})
        # Check if user already exists
        if User.objects.filter(mobile_no=phone_number).exists():
            return Response({'error': 'User already exists'})

        # Generate OTP and create user, profile, and OTP objects
        otp = random.randint(100000, 999999)
        user = User.objects.create(
            username=phone_number,
            mobile_no=phone_number,
            user_type=user_type,
            is_active=False,
            is_verified=False,
        )
        profile = Profile.objects.create(
            user=user,
            name=name,
            gender=gender,
            mohalla=mohalla,
            village=village,
            state=state,
            district=district,
            latitude=latitude,
            longitude=longitude
        )
        otp_obj = OTP.objects.create(
            otp=otp,
            user=user
        )

        # Generate JWT tokens for the user
        token = RefreshToken.for_user(user)
        key = {
            'refresh': str(token),
            'access': str(token.access_token),
        }

        # Send OTP to user's phone number (use your own SMS gateway or API)
        # TODO: Implement SMS gateway/API integration to send OTP to user's phone number
        # ...

        # Return success response with OTP and tokens
        return Response({
            'success': True,
            'otp': otp_obj.otp,
            'token': key,
        })
    

class VerifyMobile(APIView):
    permission_classes=[AllowAny,]
    def post(self, request, format=None):
        otp_input = request.data.get('otp')
        # get the user associated with the OTP
        if not otp_input.isdigit():
            return Response({'error':'otp should be number'})
        try:
            otp = OTP.objects.get(otp=otp_input)
            user =otp.user
        except OTP.DoesNotExist:
            return Response({'error': 'Invalid OTP'})
        # mark user as verified and active
        user.is_verified = True
        user.is_active = True
        user.save()
        # delete the OTP
        otp.delete()
        return Response({'verified': True})

class LoginApi(APIView):
    permission_classes=[AllowAny,]
    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone')
        if not phone:
            return Response({'error':'enter valid phone number !'})
        if not re.match(r'^\d{10}$', phone):
            return Response({'error': 'Phone number should be 10 digits.'})   
        user = authenticate(request, mobile_no=phone)
        if user is not None:
            login(request, user)
            otp=random.randint(100000, 999999)
            otps=OTP.objects.create(
                otp=otp,
                user=user
            )
            #send here OTP to mobile no.for varification
            refresh = RefreshToken.for_user(user)
            tokens = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            return Response({'success':True,'otp':otps.otp,'user_type':user.user_type,'token':tokens})
        return Response({'message':'User not registered','success': False})
    

class MobileNoAuthBackend(BaseBackend):
    def authenticate(self, request, mobile_no=None):
        try:
            user = User.objects.get(mobile_no=mobile_no)
            return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
            if user.is_active:
                return user
            return None
        except User.DoesNotExist:
            return None
        
from rest_framework.permissions import BasePermission

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.method in ['GET','POST','PUT', 'HEAD', 'OPTIONS']        
###-------------------------------------------------------------------------------####
class chartJsonListView(View):
    def get(self, *args, **kwargs):
        today = date.today()
        vendor = Profile.objects.get(user=self.request.user)

        product_count_list = []
        order_count_list = []
        # for i in range(1, 13):
        #     product_count = Product.objects.filter(
        #         product_vendor=vendor,  date__year=today.year, date__month=i,).count()
        #     product_count_list.append(product_count)
        #     order_count = OrderSupplier.objects.all().filter(vendor=vendor, order_date__year=today.year,
        #                                                         order_date__month=i,).exclude(status="PENDING").count()
        #     order_count_list.append(order_count)

        return JsonResponse({"product_count_list": 12, "order_count_list": 12, }, safe=False)


class chartJsonListViewAdmin(View):
    def get(self, *args, **kwargs):
        today = date.today()
        user = User.objects.get(username=self.request.user.username)
        if user.is_superuser == True:
            # vendor = Profile.objects.get(user=self.request.user)
            product_count_list = []
            order_count_list = []
            # for i in range(1, 13):
            #     product_count = Product.objects.all().filter(
            #         date__year=today.year, date__month=i,).count()
            #     product_count_list.append(product_count)
            #     order_count = OrderSupplier.objects.all().filter(order_date__year=today.year,
            #                                                         order_date__month=i,).exclude(status="PENDING").count()
            #     order_count_list.append(order_count)

            return JsonResponse({"product_count_list": 12, "order_count_list": 12, }, safe=False)
###-------------------------------------------------------------------------------------------####





class StateViewSet(viewsets.ModelViewSet):
    permission_classes=[IsOwnerOrReadOnly,]
    queryset = State.objects.all()
    serializer_class = StateSerializer
    lookup_field = 'slug'

    @action(detail=True)
    def districts(self, request, slug=None):
        state = self.get_object()
        districts = state.district_set.all()
        serializer = DistrictSerializer(districts, many=True)
        return Response(serializer.data)

class DistrictViewSet(viewsets.ModelViewSet):
    permission_classes=[AllowAny,]
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    lookup_field = 'slug'

class ProfileApi(APIView):
    permission_classes=[IsOwnerOrReadOnly]
    def get(self,request,format=None):
        profile=Profile.objects.get(user=request.user)
        serializers=ProfileSerializers(profile)
        return Response(serializers.data)

def logout_view(request):
    logout(request)
    admin_login_url = reverse('admin:login') # generate URL for admin login page
    return redirect(admin_login_url)




