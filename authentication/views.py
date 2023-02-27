from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from .models import *

# Create your views here.
# @csrf_exempt
class Register(APIView):

    def post(self,request,format=None):
        seraializer=RegisterSerializer(data=request.data)
        if seraializer.is_valid(raise_exception=True):
            mobile_no=seraializer.data.get('mobile_no')
            # check if mobile_no is valid
            # if not re.match(r'^\+?[1-9]\d{1,14}$', mobile_no):
            #     return Response({'error': 'Invalid mobile number'})
            # check if mobile_no is unique
            if User.objects.filter(mobile_no=mobile_no).exists():
                return Response({'error': 'Mobile number already exists'})
            # generate OTP
            otp = random.randint(1000, 9999)
            # save user
            user = User.objects.create_user(username=mobile_no, mobile_no=mobile_no, is_verified=False, status='Grahak')
            user.set_password(mobile_no)
            user.save()
            OTP.objects.create(otp=otp,user=user)
        return Response({'message':True,'OTP':otp})