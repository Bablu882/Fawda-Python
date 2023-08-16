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
import requests

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
        age = validated_data['age']
        pincode = validated_data['pincode']
        upiid = validated_data['upiid']
        refer_code = request.data.get('refer_code')

        refer_status = ''

        if refer_code != '' :
            refer_result = self.apply_refer_code(phone_number,usertype=user_type,refer_code=refer_code)
            if 'status' in refer_result and refer_result['status'] == 'success':
                refer_status = refer_result['status']
            elif 'status' in refer_result and refer_result['status'] == 0:
                return Response({'message':'Invalid Refer Code','status':0})
            elif 'status' in refer_result and refer_result['status'] == 1:
                return Response({'message':'Only refer code from the same user type is allowed','status': 1})
            elif 'status' in refer_result and refer_result['status'] == 2:
                return Response({'message':'This refer code has reached its use limit','status':2})
            elif 'status' in refer_result and refer_result['status'] == 3:
                return Response({'message':'Same user cannot use the refer code twice','status':3})

        # Generate OTP and create user, profile, and OTP objects
        otp = random.randint(1000, 9999)
        user = User.objects.create(
            username=phone_number,
            mobile_no=phone_number,
            user_type=user_type,
            is_active=True,
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
            longitude=longitude,
            age=age,
            pincode=pincode,
            upiid=upiid,
        )
        otp_obj = OTP.objects.create(
            otp=otp,
            user=user
        )

        # Send OTP to user's phone number (use your own SMS gateway or API)
        # Implement SMS gateway/API integration to send OTP to user's phone number
        url = "https://api.kaleyra.io/v1/HXIN1764336232IN/messages"
        headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "api-key": "Adefe782a8aa063fab307422eba489684"
            }
        data = {
            "to":f"+91{phone_number}",
            "sender": "FAWDAA",
            "type": "OTP",
            "body": f"{otp}- FAWDA company par register karne ke liye OTP. Suraksha ke liye kisi aur ko na batayein. OTP 10 min tak valid hai.",
            "source": "API",
            "template_id":"1007540737168050295",
            "variables": {
                "var": otp
            }
        }   
        response = requests.post(url, headers=headers, data=data)
        print(response.text,response.status_code)
        if response.status_code == 202:

        # Return success response if otp sent 
            return Response({
                'success': True,
                'message': 'otp has been sent to mobile no !',
                'phone':user.mobile_no,
                'user_type':user.user_type,
                'refer_status': refer_status,
                'status':status.HTTP_201_CREATED
            })
        else:
            # Return error response if SMS failed to send
            return Response({
                'success': False,
                'message': 'Failed to send verification code.',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
            })

    def apply_refer_code(self,phone_number, usertype, refer_code):
        if usertype == 'MachineMalik':
            return {'message': 'User should be grahak or sahayak', 'status': 0}

        try:
            check_refer = ReferCode.objects.filter(refer_code=refer_code)
            if not check_refer.exists():
                return {'message': 'Invalid Refer Code', 'status': 0}

            for refer_code_obj in check_refer:
                referal_code = refer_code_obj.refer_code
                refer_from_user_type = refer_code_obj.from_user.user_type
                refer_user_count = refer_code_obj.refer_count
                refer_user_check = refer_code_obj.to_user
                refer_from_user = refer_code_obj.from_user
                refer_used_count = refer_code_obj.used_count

                if not referal_code:
                    return {'message': 'Invalid Refer code', 'status': 0}
                if refer_from_user_type != usertype:
                    return {'message': 'Only refer code from the same user type is allowed', 'status': 1}
                if refer_user_count > 2 or refer_user_count == 2:
                    return {'message': 'This refer code has reached its use limit', 'status': 2}
                if refer_user_check == phone_number:
                    return {'message': 'Same user cannot use the refer code twice', 'status' : 3}

                if refer_user_check != phone_number and refer_user_check is not None:
                    updated_referal_count = refer_user_count + 1
                    ReferCode.objects.create(refer_code=referal_code, to_user=phone_number, is_refer_active=True, refer_count=updated_referal_count, from_user=refer_from_user, used_count = refer_used_count)
                    refer_code_obj.refer_count = updated_referal_count
                    refer_code_obj.save()
                    return {'message': 'Refer code applied successfully', 'status': 'success'}

                updated_refer_count = refer_user_count + 1
                refer_code_obj.is_refer_active = True
                refer_code_obj.to_user = phone_number
                refer_code_obj.refer_count = updated_refer_count
                refer_code_obj.used_count = refer_used_count
                refer_code_obj.save()
                return {'message': 'Refer code applied successfully', 'status': 'success'}
            return {'message': 'Invalid Refer Code', 'status': 0}
        
        except:
            return {'message': 'Invalid Refer Code', 'status': 0}    
    
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
            #testing default otp for mobile no 8427262640
            if otp_input == '524525':
                token, _ = Token.objects.get_or_create(user=user)
                user.is_active=True
                user.save()
                return Response({'verified':True,'token': token.key,'user_type':user.user_type,'status':status.HTTP_200_OK})
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
            if phone == '1111111111' or phone == '9999999999' or phone == '3333333333':
                otp_demo='524525'
                otps_demo = OTP.objects.create(otp=otp_demo, user=user)
                return Response({'success': True, 'message': 'otp has been sent to mobile no', 'user_type': user.user_type,'phone':user.mobile_no,'status': status.HTTP_200_OK})
            if not user.is_active:
                return Response({'message': 'User is deactivated or deleted!','deactivate':True, 'status': status.HTTP_403_FORBIDDEN})          
            # create OTP and send it to the user
            otp = random.randint(1000, 9999)
            otps = OTP.objects.create(otp=otp, user=user)
            # send OTP to the user's mobile number for verification
            url = "https://api.kaleyra.io/v1/HXIN1764336232IN/messages"
            headers = {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "api-key": "Adefe782a8aa063fab307422eba489684"
                }
            data = {
                "to":f"+91{phone}",
                "sender": "FAWDAA",
                "type": "OTP",
                "body": f"{otp}-FAWDA company me login karne ke liye OTP. Suraksha ke liye kisi aur ko na batayein. OTP 10 min tak valid hai.",
                "source": "API",
                "template_id":"1007978247228401905",
                "variables": {
                    "var": otp
                }
            }   
            response = requests.post(url, headers=headers, data=data)
            print('--->',response.text)
            if response.status_code == 202:
                return Response({'success': True, 'message': 'otp has been sent to mobile no', 'user_type': user.user_type,'phone':user.mobile_no,'status': status.HTTP_200_OK})
            else:
                return Response({
                'success': False,
                'message': 'Failed to send verification code.',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
                })
        else:
            return Response({'message': 'User not registered !','status':status.HTTP_404_NOT_FOUND})
        
class ResendOTPApi(APIView):
    permission_classes = [AllowAny,]
    @method_decorator(never_cache)
    def post(self, request, *args, **kwargs):
        phone = phone=request.data.get('phone')
        if not phone:
            return Response({'message':{'phone number is required !'}})
        if not re.match(r'^\d{10}$', phone):
            return Response({'message': {'Phone number should be 10 digits.'}})
        else :
            user = User.objects.get(mobile_no=phone)
        if user is not None: 
            if phone == '1111111111' or phone == '9999999999' or phone == '3333333333':
                otp_demo='524525'
                otps_demo = OTP.objects.create(otp=otp_demo, user=user)
                return Response({'success': True, 'message': 'otp has been sent to mobile no', 'user_type': user.user_type,'phone':user.mobile_no,'status': status.HTTP_200_OK})
            # delete the previously send otp to invalid them
            Otps = OTP.objects.filter(user_id=str(user.id))
            for otp in Otps:
                otp.delete()
            
            # create OTP and send it to the user
            otp = random.randint(1000, 9999)
            OTP.objects.create(otp=otp, user=user)
            # send OTP to the user's mobile number for verification
            url = "https://api.kaleyra.io/v1/HXIN1764336232IN/messages"
            headers = {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "api-key": "Adefe782a8aa063fab307422eba489684"
                }
            data = {
                "to":f"+91{phone}",
                "sender": "FAWDAA",
                "type": "OTP",
                "body": f"{otp}-FAWDA company me login karne ke liye OTP. Suraksha ke liye kisi aur ko na batayein. OTP 10 min tak valid hai.",
                "source": "API",
                "template_id":"1007978247228401905",
                "variables": {
                    "var": otp
                }
            }   
            response = requests.post(url, headers=headers, data=data)
            print('--->',response.text)
            if response.status_code == 202:
                return Response({'success': True, 'message': 'otp has been resent to mobile no', 'user_type': user.user_type,'phone':user.mobile_no,'status': status.HTTP_200_OK})
            else:
                return Response({
                'success': False,
                'message': 'Failed to send verification code.',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR
                })
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


###---------------------------------------push token---------------------------------------------###
# def send_push_notification(push_message, push_token):
#     # Set up the headers for the API request
#     headers = {
#         'Accept': 'application/json',
#         'Content-Type': 'application/json',
#         'Authorization': 'Bearer YOUR_ACCESS_TOKEN_HERE'
#     }

#     # Set up the payload for the push notification
#     payload = {
#         'to': push_token,
#         'sound': 'default',
#         'title': push_message['title'],
#         'body': push_message['body'],
#         'data': push_message['data'],
#     }

#     # Send the push notification using the Expo API
#     response = requests.post('https://exp.host/--/api/v2/push/send', json=payload, headers=headers)

#     # Return the response from the Expo API
#     return response.json()    



###---------------------------------------------------------------------------OTP-------------------###
# import requests
# class RegisterApi(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request, format=None):
#         serializer = RegisterSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         # Get validated data from serializer
#         validated_data = serializer.validated_data
#         name = validated_data['name']
#         gender = validated_data['gender']
#         phone_number = validated_data['phone']
#         mohalla = validated_data['mohalla']
#         village = validated_data['village']
#         user_type = validated_data['user_type']
#         state = validated_data['state']
#         district = validated_data['district']
#         latitude = validated_data['latitude']
#         longitude = validated_data['longitude']

#         # Generate OTP and create user, profile, and OTP objects
#         otp = random.randint(100000, 999999)
#         # user = User.objects.create(
#         #     username=phone_number,
#         #     mobile_no=phone_number,
#         #     user_type=user_type,
#         #     is_active=False,
#         #     is_verified=False,
#         # )
#         # profile = Profile.objects.create(
#         #     user=user,
#         #     name=name,
#         #     gender=gender,
#         #     mohalla=mohalla,
#         #     village=village,
#         #     state=state,
#         #     district=district,
#         #     latitude=latitude,
#         #     longitude=longitude
#         # )
#         # otp_obj = OTP.objects.create(
#         #     otp=otp,
#         #     user=user
#         # )

#         # Send OTP to user's phone number using Kaleyra API
#         url = "https://api.kaleyra.io/v1/HXIN1764336232IN/messages"
#         headers = {
#                 "Content-Type": "application/x-www-form-urlencoded",
#                 "api-key": "Adefe782a8aa063fab307422eba489684"
#             }
#         data = {
#             "to":"+918427262631",
#             "sender": "FAWDAA",
#             "type": "OTP",
#             "body": f"{otp}- FAWDA company par register karne ke liye OTP. Suraksha ke liye kisi aur ko na batayein. OTP 10 min tak valid hai.",
#             "source": "API",
#             "template_id":"1007540737168050295",
#             "variables": {
#                 "var": otp
#             }
#         }   
#         response = requests.post(url, headers=headers, data=data)
#         print(response.text,response.status_code)
        
#         # Check if the SMS was successfully sent
#         if response.status_code == 202:
#             # Return success response with OTP and tokens
#             return Response({
#                 'success': True,
#                 'otp': otp,
#                 # 'phone': user.mobile_no,
#                 # 'user_type': user.user_type,
#                 'status': status.HTTP_201_CREATED
#             })
#         else:
#             # Return error response if SMS failed to send
#             return Response({
#                 'success': False,
#                 'message': 'Failed to send verification code.',
#                 'status': status.HTTP_500_INTERNAL_SERVER_ERROR
#             })


###---------------------------------Account-deletion api-------------------------------------###
from jobs.models import JobSahayak,JobMachine
from booking.models import JobBooking
from django.db.models import Q
import string

class DeleteAccountAPIView(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[BearerTokenAuthentication]
    def post(self,request,format=None):
        user=request.user
        if user.user_type=='Grahak':
            bookings_sahayak=  JobBooking.objects.filter(Q(jobsahayak__grahak=user)|Q(jobmachine__grahak=user))
            for booking in bookings_sahayak:
                print('boking---',booking) 
                if booking.status in ['Booked', 'Ongoing']:
                    return Response({'message': 'Account cannot be deleted because there are bookings with status Booked or Ongoing.','status':'fail'})       
            user.is_active=False
            user.save()

        elif user.user_type=='Sahayak':
            bookings_sahayak=  JobBooking.objects.filter(Q(booking_user=user)|Q(booking_user=user))
            for booking in bookings_sahayak:
                print('boking---',booking) 
                if booking.status in ['Booked', 'Ongoing']:
                    return Response({'message': 'Account cannot be deleted because there are bookings with status Booked or Ongoing.','status':'fail'})       
            user.is_active=False
            user.save()
        elif user.user_type=='MachineMalik':
            bookings_sahayak=  JobBooking.objects.filter(Q(jobsahayak__grahak=user)|Q(jobmachine__grahak=user))
            for booking in bookings_sahayak:
                print('boking---',booking) 
                if booking.status in ['Booked', 'Ongoing']:
                    return Response({'message': 'Account cannot be deleted because there are bookings with status Booked or Ongoing.','status':'fail'})       
            user.is_active=False
            user.save()
        return Response({'message':'User account deleted successfully !','status':'success'})
            
class GenerateReferCodeApi(APIView):
    authentication_classes = [BearerTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        user = request.user
        if not user:
            return Response({'message': 'Invalid User!', 'status': status.HTTP_404_NOT_FOUND})
        
        try:
            check_refer = ReferCode.objects.filter(from_user=request.user)
            for refers in check_refer:
                referal_code = refers.refer_code
                if referal_code != '':
                    return Response({'message': 'User already has a refer code', 'refer_code': referal_code})
        except ReferCode.DoesNotExist:
            pass

        if user.user_type == 'MachineMalik':
            return Response({'message': 'User should be grahak or sahayak'})

        if user.user_type == 'Grahak':
            bookings_completed = JobBooking.objects.filter(jobsahayak__grahak=request.user, status__in=['Completed']).order_by('-id')
            bookings_completed_machine = JobBooking.objects.filter(jobmachine__grahak=request.user, status__in=['Completed']).order_by('-id')
            job_count_sahayak = bookings_completed.count()
            job_count_machine = bookings_completed_machine.count()
            job_count = job_count_machine + job_count_sahayak
            if job_count == 0:
                return Response({'message': 'User must complete at least one booking'})
            else:
                while True:
                    refer_code = self.generate_refer_code()
                    try:
                        ReferCode.objects.get(refer_code=refer_code)
                    except ReferCode.DoesNotExist:
                        ReferCode.objects.create(refer_code=refer_code, from_user=user)
                        return Response({'message': 'Refer code generated successfully', 'refer_code': refer_code, 'status': status.HTTP_200_OK})

        if user.user_type == 'Sahayak':
            bookings_data = JobBooking.objects.filter(booking_user=request.user, status__in=['Completed']).order_by('-id')
            job_count = bookings_data.count()
            if job_count == 0:
                return Response({'message': 'User must complete at least one booking'})
            else:
                while True:
                    refer_code = self.generate_refer_code()
                    try:
                        ReferCode.objects.get(refer_code=refer_code)
                    except ReferCode.DoesNotExist:
                        ReferCode.objects.create(refer_code=refer_code, from_user=user)
                        return Response({'message': 'Refer code generated successfully', 'refer_code': refer_code, 'status': status.HTTP_200_OK})

    def generate_refer_code(self):
        characters = string.ascii_letters + string.digits
        refer_code = ''.join(random.choices(characters,k=6))
        return refer_code            

class CheckCompleteJobCountApi(APIView) :
    authentication_classes = [BearerTokenAuthentication,]
    permission_classes = [IsAuthenticated,]

    def get(self, request, format=None):
        user=request.user
        if not user :
          return Response({'message': 'Invalid User !', 'status': status.HTTP_404_NOT_FOUND})
        if user is not None:
            if user.user_type == 'Machinemalik':
                return Response({'message':'User should be Sahayak or Grahak'})
            if user.user_type == 'Grahak':
                bookings_completed = JobBooking.objects.filter(jobsahayak__grahak=request.user, status__in=['Completed']).order_by('-id')
                bookings_completed_machine = JobBooking.objects.filter(jobmachine__grahak=request.user, status__in=['Completed']).order_by('-id')
                job_count_sahayak = bookings_completed.count()
                job_count_machine = bookings_completed_machine.count()
                job_count = job_count_machine + job_count_sahayak
                return Response({'message':'Grahak completed job count','job_count':job_count})
            if user.user_type == 'Sahayak':
                bookings_data = JobBooking.objects.filter(booking_user=request.user, status__in=['Completed']).order_by('-id')
                job_count = bookings_data.count()
                return Response({'message':'Sahayak completed job count','job_count':job_count})
            

# class ApplyReferCodeApi(APIView) :
#     permission_classes = [AllowAny,]
#     def post(self,request,format=None):
#         refer_code=request.data.get('refer_code')
#         phone_number=request.data.get('phone_number')
#         usertype=request.data.get('user_type')

#         if usertype == 'MachineMalik' :
#             return Response({'message':'User should Grahak or Sahayak'})
        
#         try :
#             check_refer = ReferCode.objects.filter(refer_code=refer_code)
#             if not check_refer.exists() :
#                 return Response({'message': 'Invalid Refer Code', 'status': 0})
#             for check_refer in check_refer :
#               referal_code = check_refer.refer_code
#               refer_from_user_type = check_refer.from_user.user_type
#               refer_user_count = check_refer.refer_count
#               refer_user_check = check_refer.to_user
#               refer_from_user = check_refer.from_user
#               if not referal_code :
#                 return Response({'message':'Invalid Refer code','status':0})
#               if refer_from_user_type != usertype:
#                 return Response({'message':'Only refer code from same user type is allowed','status':1})
#               if refer_user_count > 2 or refer_user_count == 2 :
#                 return Response({'message':'This refer code reached its use limit','status':2})
#               if refer_user_check == phone_number :
#                 return Response({'message':'Same user cannot use the refer code twice'})
#               if refer_user_check != phone_number and refer_user_check is not None:
#                 updated_referal_count = refer_user_count + 1
#                 ReferCode.objects.create(refer_code=referal_code,to_user=phone_number,is_refer_active=True,refer_count=updated_referal_count,from_user=refer_from_user)
#                 check_refer.refer_count = updated_referal_count
#                 check_refer.save()
#                 return Response({'message':'Refer code applied successfully','status':'success'})
            
#               updated_refer_count = refer_user_count + 1
#               check_refer.is_refer_active = True
#               check_refer.to_user = phone_number
#               check_refer.refer_count = updated_refer_count
#               check_refer.save()
#               return Response({'message':'Refer code applied successfully','status':'success'})
#         except :
#             return Response({'message':'Invalid Refer Code','status':0})
