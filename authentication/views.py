from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from .models import *
from django.views import View
from datetime import datetime, date, timedelta
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import action

def test(request):
    return render(request,'authentication/test.html')


# Create your views here.
# @csrf_exempt
class Register(APIView):

    def post(self,request,format=None):
        seraializer=RegisterSerializer(data=request.data)
        if seraializer.is_valid(raise_exception=True):
            mobile_no=seraializer.data.get('mobile_no')
            if User.objects.filter(mobile_no=mobile_no).exists():
                return Response({'error': 'Mobile number already exists'})
            # generate OTP
            otp = random.randint(1000, 9999)
            # save user
            user = User.objects.create_user(username=mobile_no, mobile_no=mobile_no, is_verified=False, is_active=False, status='Grahak')
            user.set_password(mobile_no)
            user.save()
            OTP.objects.create(otp=otp,user=user)
        return Response({'message':True,'OTP':otp})
    


class VerifyMobile(APIView):
    def post(self,request,format=None):
        serializers=MobileVerifySerializer(data=request.data)
        if serializers.is_valid(raise_exception=True):
            mobile=serializers.data.get('mobile_no')
            if not User.objects.filter(mobile_no=mobile).exists():
                return Response({'Message':'User not exist with this mobile_no','Status':False})
            else:
                return Response({'Message':'User exist with this mobile_no','Status':True})


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






class StateViewSet(viewsets.ModelViewSet):
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
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    lookup_field = 'slug'
