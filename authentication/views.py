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
from rest_framework import status


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
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get validated data from serializer
        validated_data = serializer.validated_data
        name = validated_data['name']
        gender = validated_data['gender']
        phone_number = validated_data['phone']
        mohalla = validated_data['mohalla']
        village = validated_data['village']
        user_type = validated_data['user_type']
        state = validated_data['state']
        district = validated_data['district']
        latitude = validated_data['latitude']
        longitude = validated_data['longitude']

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
            'phone':user.mobile_no,
            'user_type':user.user_type,
            'status':status.HTTP_201_CREATED
        })
    
class VerifyMobile(APIView):
    permission_classes=[AllowAny,]
    def post(self, request, format=None):
        otp_input = request.data.get('otp')
        phone=request.data.get('phone')
        if not otp_input or not phone:
            return Response({'message':{'otp and phone both is required !'}})
        if not re.match(r'^\d{10}$', phone):
            return Response({'message': {'Phone number should be 10 digits.'}})
        # Revoke any existing tokens for the user
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
        try:
            get_user=User.objects.get(mobile_no=phone)
            otp = OTP.objects.get(otp=otp_input,user=get_user)
            user_get = otp.user
        except User.DoesNotExist:
            return Response({'message':{'User does not exist !'}})    
        except OTP.DoesNotExist:
            return Response({'otp': {'Invalid OTP'}})    
        token, _ = Token.objects.get_or_create(user=user_get)
        # Update user properties
        user_get.is_verified = True
        user_get.is_active = True
        user_get.save()
        OTP.objects.filter(user=user_get).delete()
        return Response({'verified':True,'token': token.key,'user_type':user_get.user_type,'status':status.HTTP_200_OK})
    
@api_view(["POST"])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def User_logout(request):
    request.user.auth_token.delete()
    logout(request)
    response_data = {
        'msg': {'user logged out successfully !'},
        'status':status.HTTP_200_OK

    }
    return Response(response_data)

class LoginApi(APIView):
    permission_classes = [AllowAny,]
    @method_decorator(never_cache)
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        user = authenticate(request, mobile_no=phone)
        if user is not None:           
            # create OTP and send it to the user
            otp = random.randint(100000, 999999)
            otps = OTP.objects.create(otp=otp, user=user)
            # send OTP to the user's mobile number for verification

            return Response({'success': True, 'otp': otps.otp, 'user_type': user.user_type,'phone':user.mobile_no,'status': status.HTTP_200_OK})
        else:
            return Response({'message': 'User not registered !','status':status.HTTP_404_NOT_FOUND})
        
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
# class chartJsonListView(View):
#     def get(self, *args, **kwargs):
#         today = date.today()
#         vendor = Profile.objects.get(user=self.request.user)

#         product_count_list = []
#         order_count_list = []
#         # for i in range(1, 13):
#         #     product_count = Product.objects.filter(
#         #         product_vendor=vendor,  date__year=today.year, date__month=i,).count()
#         #     product_count_list.append(product_count)
#         #     order_count = OrderSupplier.objects.all().filter(vendor=vendor, order_date__year=today.year,
#         #                                                         order_date__month=i,).exclude(status="PENDING").count()
#         #     order_count_list.append(order_count)

#         return JsonResponse({"product_count_list": 12, "order_count_list": 12, }, safe=False)


# class chartJsonListViewAdmin(View):
#     def get(self, *args, **kwargs):
#         today = date.today()
#         user = User.objects.get(username=self.request.user.username)
#         if user.is_superuser == True:
#             # vendor = Profile.objects.get(user=self.request.user)
#             product_count_list = []
#             order_count_list = []
#             # for i in range(1, 13):
#             #     product_count = Product.objects.all().filter(
#             #         date__year=today.year, date__month=i,).count()
#             #     product_count_list.append(product_count)
#             #     order_count = OrderSupplier.objects.all().filter(order_date__year=today.year,
#             #                                                         order_date__month=i,).exclude(status="PENDING").count()
#             #     order_count_list.append(order_count)

#             return JsonResponse({"product_count_list": 12, "order_count_list": 12, }, safe=False)
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
            return Response({'message':{'state required !'}})  

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

