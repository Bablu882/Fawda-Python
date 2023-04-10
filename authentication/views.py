from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from .models import *
from django.views import View
from datetime import datetime, date, timedelta
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate,login
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework.decorators import api_view,permission_classes,authentication_classes
import re
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.urls import reverse
from django.contrib.sessions.models import Session
from django.utils import timezone
import random
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions

class BearerTokenAuthentication(TokenAuthentication):
    keyword = 'Bearer'

    def authenticate_credentials(self, key):
        try:
            token = key
            if not isinstance(key, Token):
                token = Token.objects.get(key=key)
            if not token.user.is_active:
                raise exceptions.AuthenticationFailed('User inactive or deleted.')
            return (token.user, token)
        except Token.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token.')






def test(request):
    return render(request,'authentication/test.html')


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
        
        # Send OTP to user's phone number (use your own SMS gateway or API)
        # TODO: Implement SMS gateway/API integration to send OTP to user's phone number
        # ...

        # Return success response with OTP and tokens
        return Response({
            'success': True,
            'otp': otp_obj.otp,
        })
    

class VerifyMobile(APIView):
    permission_classes=[AllowAny,]

    def post(self, request, format=None):
        otp_input = request.data.get('otp')
        try:
            otp = OTP.objects.get(otp=otp_input)
            user = otp.user
        except OTP.DoesNotExist:
            return Response({'error': 'Invalid OTP'})

        # Create new token for the user
        use=Token.objects.filter(user=user)
        print(use)
        # Revoke any existing tokens for the user
        Token.objects.filter(user=user).delete()
        token, _ = Token.objects.get_or_create(user=user)
        # Update user properties
        user.is_verified = True
        user.is_active = True
        user.save()
        OTP.objects.filter(user=user).delete()
        return Response({'verified':True,'token': token.key})
    
@api_view(["POST"])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def User_logout(request):
    request.user.auth_token.delete()
    logout(request)
    response_data = {
        'msg': 'user logged out successfully !',
        'msg2':'previous token has been deleted !'
    }
    return Response(response_data)


class LoginApi(APIView):
    permission_classes = [AllowAny,]
    @method_decorator(never_cache)
    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone')
        if not phone:
            return Response({'error':'enter valid phone number !'})
        if not re.match(r'^\d{10}$', phone):
            return Response({'error': 'Phone number should be 10 digits.'})
        
        user = authenticate(request, mobile_no=phone)
        if user is not None:
            # get all sessions of the user and delete them
            sessions = Session.objects.filter(expire_date__gte=timezone.now(), session_key__contains=str(user.id))
            for session in sessions:
                session.delete()

            # delete all tokens of the user
            Token.objects.filter(user=user).delete()

            # authenticate and login the user
            login(request, user)

            # create OTP and send it to the user
            otp = random.randint(100000, 999999)
            otps = OTP.objects.create(otp=otp, user=user)
            # send OTP to the user's mobile number for verification

            return Response({'success':True,'otp':otps.otp,'user_type':user.user_type,'data':'Previous sessions and tokens deleted successfully'})
        else:
            return Response({'error': 'Invalid phone number or user not registered'})

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
    authentication_classes=[BearerTokenAuthentication,]
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

class DistrictApiView(APIView):
    authentication_classes=[BearerTokenAuthentication,]
    permission_classes=[AllowAny,]
    def post(self,request,format=None):
        state=request.data.get('state')
        if state:
            get_district=District.objects.filter(state__name=state)
            district_list=[]
            for district in get_district:
                district_list.append({
                    'district':district.name
                })

            return Response(district_list)
        else:
            return Response({'error':'state required !'})  

class ProfileApi(APIView):
    authentication_classes=[BearerTokenAuthentication]
    permission_classes=[IsOwnerOrReadOnly]
    def get(self,request,format=None):
        profile=Profile.objects.get(user=request.user)
        serializers=ProfileSerializers(profile)
        return Response(serializers.data)

def logout_view(request):
    logout(request)
    admin_login_url = reverse('admin:login') # generate URL for admin login page
    return redirect(admin_login_url)

