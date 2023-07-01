from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Payment
from booking.models import JobBooking
from rest_framework.permissions import AllowAny, IsAuthenticated
from authentication.views import BearerTokenAuthentication
from jobs.models import *
from django.db.models import Q
from rest_framework import status
from .ccavutil import encrypt, decrypt,res
import os
from jobs.views import send_push_notification
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from django.http import JsonResponse
import urllib.parse
from booking.views import limitedtime
from django.conf import settings







# class PaymentAPIView(APIView):
#     def post(self, request):
#         if request.user.user_type =='Grahak':
#             booking_id = request.POST.get('booking_id')
#             amount = request.POST.get('amount')

#             # Get the client's UPI details
#             upi_id = 'client@upi'  # Replace with the actual UPI ID
#             beneficiary_name = 'Acme Corporation'  # Replace with the actual beneficiary name

#             # Make an API call to HDFC UPI's payment API endpoint with the client's UPI details
#             response = requests.post('https://api.hdfcbank.com/upi/payments', data={
#                 'booking_id': booking_id,
#                 'amount': str(amount),
#                 'upi_id': upi_id,
#                 'beneficiary_name': beneficiary_name,
#                 # Add any other required parameters for HDFC UPI payment API
#             })

#             # If payment is successful, save payment details to Payment table
#             if response.status_code == 200 and response.json().get('status') == 'success':
#                 payment_id = response.json().get('payment_id')
#                 payment_status = response.json().get('payment_status')

#                 payment = Payment.objects.create(
#                     booking_id=booking_id,
#                     amount=str(amount),
#                     payment_id=payment_id,
#                     payment_status=payment_status,
#                     beneficiary_name=beneficiary_name
#                 )
#                 job=JobBooking.objects.get(pk=booking_id)
#                 job.status= 'Booked'
#                 job.save()
#                 if job.jobsahayak:
#                     if job.jobsahayak.job_type == 'individuals_sahayak':
#                         if job.jobsahayak.count_male == '0' and job.jobsahayak.count_female == '0':
#                             job.jobsahayak.status = 'Booked'
#                             job.save()
#                     else:
#                         job.jobsahayak.status = 'Booked'
#                         job.save()
#                 else:
#                     job.jobmachine.status='Booked'
#                     job.save()
#                 return Response({'status': 'success'})
#             else:
#                 # If payment fails, return an message message to the mobile app
#                 return Response({'status': 'message', 'message': 'Payment failed'})


class TestPaymentAPIView(APIView):
    authentication_classes = [BearerTokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        if request.user.user_type == 'Grahak':
            # booking_id = request.data.get('booking_id')
            job_id = request.data.get('job_id')
            job_number = request.data.get('job_number')
            amount = request.data.get('amount')
            upi_id = 'upi_id'  # Replace with the actual UPI ID
            # Replace with the actual beneficiary name
            beneficiary_name = 'beneficiary_name'
            if not job_id:
                return Response({'message': {'job_id required !'}})
            if not job_number:
                return Response({'message': {'job_number required !'}})
            if not job_id.isdigit():
                return Response({'message': {'booking_id should be numeric !'}})
            # if not JobBooking.objects.filter(pk=job_id).exists():
            #     return Response({'message':'booking_id not exists !'})
            # Simulate a successful payment by returning a JSON response with a payment ID and status
            if request.user.user_type != 'Grahak':
                return Response({'message': {'you are not Grahak, only Grahak can change status'}})

            # if not JobSahayak.objects.filter(pk=job_id).exists() or not JobMachine.objects.filter(pk=job_id).exists():
            #     return Response({'message':'job_id does not exists'})
            job_bookings = JobBooking.objects.filter(Q((Q(jobsahayak__id=job_id) & Q(
                jobsahayak__job_number=job_number)) | (Q(jobmachine__id=job_id) & Q(jobmachine__job_number=job_number))))
            is_booked = False
            for job in job_bookings:
                if job.status == 'Booked':
                    return Response({'message': {'Status already up to date !'}})
                if job.status != 'Accepted':
                    continue
                is_booked = True

                if job.jobsahayak:
                    if job.jobsahayak.grahak == request.user:
                        if not job.jobsahayak.status == 'Pending':
                            job.jobsahayak.status = 'Booked'
                            job.jobsahayak.save()
                    else:
                        return Response({'message': {'unauthorized grahak !'}})
                else:
                    if job.jobmachine.grahak == request.user:
                        if not job.jobmachine.status == 'Pending':
                            job.jobmachine.status = 'Booked'
                            job.jobmachine.save()
                    else:
                        return Response({'message': {'unauthorized grahak !'}})

                job.status = 'Booked'
                job.save()
                push_message = {
                    'to': job.booking_user.push_token,
                    'title': 'काम बुक किया गया!',
                    'body': f'आपका स्वीकृत किया गया काम ग्राहक द्वारा बुक किया गया है!',
                    'sound': 'default',
                    'data': {
                        'key': 'Booked'  # Add additional key-value pair
                    }
                }

                send_push_notification(push_message)
            response_data = {
                'booking_id': job_id,
                'amount': str(amount),
                'upi_id': upi_id,
                'beneficiary_name': beneficiary_name,
                'payment_id': 'mock_payment_id',  # Replace with a mock payment ID
                'payment_status': 'success',  # Set the payment status to 'success'
            }

            # Save payment details to Payment table
            payment = Payment.objects.create(
                booking_id=job_id,
                amount=str(amount),
                payment_id=response_data['payment_id'],
                payment_status=response_data['payment_status'],
                beneficiary_name=beneficiary_name
            )

            if not is_booked:
                return Response({'message': {'Booking status cannot be updated it should be Accepted before !'}})
            # send nortification here
            return Response({'message': 'changed status to Booked successfully!', 'booking-status': 'Booked', 'status': status.HTTP_200_OK})

################################################################################

class PaymentAPIView(APIView):
    authentication_classes = [BearerTokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        if request.user.user_type == 'Grahak':
            # booking_id = request.data.get('booking_id')
            job_id = request.data.get('job_id')
            job_number = request.data.get('job_number')
            amount = request.data.get('amount')
            p_redirect_url=request.build_absolute_uri('/ccavResponseHandler/')
            print(p_redirect_url)
            p_currency='INR'
            p_merchant_id=settings.MERCHANT_ID
            p_amount=amount
            p_order_id=job_id
            p_merchant_param1=job_number

            # upi_id = 'upi_id'  # Replace with the actual UPI ID
            # # Replace with the actual beneficiary name
            # beneficiary_name = 'beneficiary_name'
            if not job_id:
                return Response({'message': {'job_id required !'}})
            if not job_number:
                return Response({'message': {'job_number required !'}})
            if not job_id.isdigit():
                return Response({'message': {'booking_id should be numeric !'}})
            if request.user.user_type != 'Grahak':
                return Response({'message': {'you are not Grahak, only Grahak can change status'}})

            

            # if not JobSahayak.objects.filter(pk=job_id).exists() or not JobMachine.objects.filter(pk=job_id).exists():
            #     return Response({'message':'job_id does not exists'})
            job_bookings = JobBooking.objects.filter(Q((Q(jobsahayak__id=job_id) & Q(
                jobsahayak__job_number=job_number)) | (Q(jobmachine__id=job_id) & Q(jobmachine__job_number=job_number))))  
                          
            if not job_bookings.exists():
                return Response({'message': 'No matching job bookings found.'}) 
            for booking in job_bookings:
                if booking.jobsahayak:
                    diff=limitedtime(booking.jobsahayak.datetime)
                    if diff <= 0:
                        return Response({'message':'Can not Booked due to job datetime is exceed !'})

                    if booking.jobsahayak.grahak != request.user:
                        return Response({'message': 'Unauthorized user!'})
                else:
                    diff=limitedtime(booking.jobmachine.datetime)
                    if diff <= 0:
                        return Response({'message':'Can not Booked due to job datetime is exceed !'})
                    if booking.jobmachine.grahak != request.user:
                        return Response({'message': 'Unauthorized user!'})
 
            if any(job_booking.status == 'Booked' for job_booking in job_bookings):
                return Response({'message': 'Booking Status already marked as Booked !'})

            if any(job_booking.status != 'Accepted' for job_booking in job_bookings):
                return Response({'message': 'Booking status should be Accepted before proceeding.'})
            
  

            total_amount = sum(float(job_booking.total_amount) for job_booking in job_bookings)
            print('------',total_amount)

            if total_amount != float(amount):
                return Response({'message': 'Total amount of job bookings does not match the received amount!'})
            # is_booked = False
            # for job in job_bookings:
            #     if job.status == 'Booked':
            #         return Response({'message': {'Status already up to date !'}})
            #     if job.status != 'Accepted':
            #         continue
            #     is_booked = True

            #     if job.jobsahayak:
            #         if job.jobsahayak.grahak == request.user:
            #             if not job.jobsahayak.status == 'Pending':
            #                 job.jobsahayak.status = 'Booked'
            #                 job.jobsahayak.save()
            #         else:
            #             return Response({'message': {'unauthorized grahak !'}})
            #     else:
            #         if job.jobmachine.grahak == request.user:
            #             if not job.jobmachine.status == 'Pending':
            #                 job.jobmachine.status = 'Booked'
            #                 job.jobmachine.save()
            #         else:
            #             return Response({'message': {'unauthorized grahak !'}})

            #     job.status = 'Booked'
            #     job.save()
            #     push_message = {
            #         'to': job.booking_user.push_token,
            #         'title': 'काम बुक किया गया!',
            #         'body': f'आपका स्वीकृत किया गया काम ग्राहक द्वारा बुक किया गया है!',
            #         'sound': 'default',
            #         'data': {
            #             'key': 'Booked'  # Add additional key-value pair
            #         }
            #     }

            #     send_push_notification(push_message)
            # response_data = {
            #     'booking_id': job_id,
            #     'amount': str(amount),
            #     'upi_id': upi_id,
            #     'beneficiary_name': beneficiary_name,
            #     'payment_id': 'mock_payment_id',  # Replace with a mock payment ID
            #     'payment_status': 'success',  # Set the payment status to 'success'
            # }

            # # Save payment details to Payment table
            # payment = Payment.objects.create(
            #     booking_id=job_id,
            #     amount=str(amount),
            #     payment_id=response_data['payment_id'],
            #     payment_status=response_data['payment_status'],
            #     beneficiary_name=beneficiary_name
            # )

            # if not is_booked:
            #     return Response({'message': {'Booking status cannot be updated it should be Accepted before !'}})
            # send nortification here
            merchant_data = (
            'merchant_id=' + p_merchant_id + '&' +
            'order_id=' + p_order_id + '&' +
            'currency=' + p_currency + '&' +
            'amount=' + p_amount + '&' +
            'redirect_url=' + p_redirect_url + '&' +
            'merchant_param1=' + p_merchant_param1 + '&'
            # ... Include other form data
              )

            encryption = encrypt(merchant_data, workingKey)
            decription=decrypt(encryption,workingKey)
            print(decription)

            return Response(encryption)



@method_decorator(csrf_exempt, name='dispatch')
class PaymentRequestHandler(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        encryption=request.data.get('merchant_data')
        if not encryption:
            return Response({'message':'merchant data is required !'})
        html = '''\
        <html>
        <head>
            <title>Sub-merchant checkout page</title>
            <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js"></script>
        </head>
        <body>
            <form id="nonseamless" method="post" name="redirect" action="https://secure.ccavenue.com/transaction/transaction.do?command=initiateTransaction">
                <input type="hidden" id="encRequest" name="encRequest" value="$encReq">
                <input type="hidden" name="access_code" id="access_code" value="$xscode">
                <script language='javascript'>document.redirect.submit();</script>
            </form>
        </body>
        </html>
        '''

        fin = Template(html).safe_substitute(encReq=encryption, xscode=accessCode)
        return HttpResponse(fin)


# @csrf_exempt
# def ccav_response_handler(request):
#     if request.method == 'POST':
#         plain_text = res(request.POST.get('encResp'))
#         # print('-----all', plain_text)
#         data_dict = {}

#         for line in plain_text.split('\n'):
#             if line.startswith('{"response"'):
#                 nested_json = line.strip()
#                 data_dict = json.loads(nested_json)
#                 break

#         response_data = urllib.parse.parse_qs(data_dict.get('response', ''))
#         response_data = {key: value[0] for key, value in response_data.items()}

#         # print('-----', response_data)

#         status = response_data.get('order_status')
#         order_id = response_data.get('order_id')
#         tracking_id = response_data.get('tracking_id')
#         amount = response_data.get('amount')
#         job_number = response_data.get('merchant_param1')

#         print('-----', status, order_id, tracking_id, amount, job_number)

#         if status == 'Success':
#             # Payment is successful
#             return JsonResponse({'payment': 'success', 'data': response_data})
#         else:
#             # Payment is not successful
#             return JsonResponse({'payment': 'failed', 'data': response_data})

#     return JsonResponse({'message': 'Invalid request method'}, status=400)




@csrf_exempt
def ccav_response_handler(request):
    if request.method == 'POST':
        plain_text = res(request.POST.get('encResp'))
        # print('-----all', plain_text)
        data_dict = {}

        for line in plain_text.split('\n'):
            if line.startswith('{"response"'):
                nested_json = line.strip()
                data_dict = json.loads(nested_json)
                break

        response_data = urllib.parse.parse_qs(data_dict.get('response', ''))
        response_data = {key: value[0] for key, value in response_data.items()}

        order_status = response_data.get('order_status')
        job_id = response_data.get('order_id')
        tracking_id = response_data.get('tracking_id')
        amount = response_data.get('amount')
        payment_id=response_data.get('bank_ref_no')
        payment_date=response_data.get('trans_date')
        job_number = response_data.get('merchant_param1')  # Retrieve job_number from merchant_param1
        print('-----', order_status, job_id, tracking_id, amount, job_number)

        if order_status == 'Success':
            job_bookings = JobBooking.objects.filter(Q((Q(jobsahayak__id=job_id) & Q(
                jobsahayak__job_number=job_number)) | (Q(jobmachine__id=job_id) & Q(jobmachine__job_number=job_number))))  
            for booking in job_bookings:
                booking.status='Booked'    
                booking.save()
                if booking.jobsahayak:
                    booking.jobsahayak.status='Booked'
                    booking.jobsahayak.save()
                else:
                    booking.jobmachine.status='Booked'    
                    booking.jobmachine.save()
                create=Payment.objects.create(booking_id=booking.id,amount=booking.total_amount,payment_id=payment_id,payment_status=order_status,payment_date=payment_date,beneficiary_name='Fawda Agrisolutions Private Limited')    
                push_message = {
                        'to': booking.booking_user.push_token,
                        'title': 'काम बुक किया गया!',
                        'body': f'आपका स्वीकृत किया गया काम ग्राहक द्वारा बुक किया गया है!',
                        'sound': 'default',
                        'data': {
                            'key': 'Booked'  # Add additional key-value pair
                        }
                    }
                send_push_notification(push_message)
            # Payment is successful
            return JsonResponse({'message': 'Payment successfully !', 'data': response_data})
        else:
            # Payment is not successful
            return JsonResponse({'message': 'Payment failed !', 'data': response_data})

    return JsonResponse({'message': 'Invalid request method'}, status=400)

# @csrf_exempt
# def ccav_response_handler(request):
#     if request.method == 'POST':
#         return handle_request(request)
#     elif request.method == 'GET':
#         return handle_request(request)
#     else:
#         return JsonResponse({'message': 'Invalid request method'}, status=400)


# def handle_request(request):
#     if request.method == 'POST':
#         plain_text = res(request.POST.get('encResp'))
#     elif request.method == 'GET':
#         plain_text = res(request.GET.get('encResp'))

#     data_dict = {}

#     for line in plain_text.split('\n'):
#         if line.startswith('{"response"'):
#             nested_json = line.strip()
#             data_dict = json.loads(nested_json)
#             break

#     response_data = urllib.parse.parse_qs(data_dict.get('response', ''))
#     response_data = {key: value[0] for key, value in response_data.items()}

#     order_status = response_data.get('order_status')
#     job_id = response_data.get('order_id')
#     tracking_id = response_data.get('tracking_id')
#     amount = response_data.get('amount')
#     payment_id = response_data.get('bank_ref_no')
#     payment_date = response_data.get('trans_date')
#     job_number = response_data.get('merchant_param1')  # Retrieve job_number from merchant_param1
#     print('-----', order_status, job_id, tracking_id, amount, job_number)

#     if order_status == 'Success':
#         job_bookings = JobBooking.objects.filter(Q((Q(jobsahayak__id=job_id) & Q(
#             jobsahayak__job_number=job_number)) | (Q(jobmachine__id=job_id) & Q(jobmachine__job_number=job_number))))
#         for booking in job_bookings:
#             booking.status = 'Booked'
#             booking.save()
#             if booking.jobsahayak:
#                 booking.jobsahayak.status = 'Booked'
#                 booking.jobsahayak.save()
#             else:
#                 booking.jobmachine.status = 'Booked'
#                 booking.jobmachine.save()
#             create = Payment.objects.create(booking_id=booking.id, amount=booking.total_amount,
#                                             payment_id=payment_id, payment_status=order_status,
#                                             payment_date=payment_date, beneficiary_name='Fawda Agrisolutions Private Limited')
#             push_message = {
#                 'to': booking.booking_user.push_token,
#                 'title': 'काम बुक किया गया!',
#                 'body': f'आपका स्वीकृत किया गया काम ग्राहक द्वारा बुक किया गया है!',
#                 'sound': 'default',
#                 'data': {
#                     'key': 'Booked'  # Add additional key-value pair
#                 }
#             }
#             send_push_notification(push_message)
#         # Payment is successful
#         return JsonResponse({'message': 'Payment successfully!', 'data': response_data})
#     else:
#         # Payment is not successful
#         return JsonResponse({'message': 'Payment failed!', 'data': response_data})


################################################################################














class EncryptPaymentParamsView(APIView):
    authentication_classes = [BearerTokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def encrypt_data(self, data):
        working_key = settings.WORKING_KEY
        print(working_key)  # Replace with your working key
        encrypted_data = encrypt(data, working_key)
        return encrypted_data
    
    def decrypt_data(self, data):
        working_key = settings.WORKING_KEY  # Replace with your working key
        decrypted_data = decrypt(data, working_key)
        return decrypted_data

    def post(self, request):
        if request.user.user_type == 'Grahak':
            job_id = request.data.get('job_id')
            job_number = request.data.get('job_number')
            amount = request.data.get('amount')
            merchant_id = settings.MERCHANT_ID
            # merchant_param1 = request.data.get('job_number')
            if not job_id:
                return Response({'message': {'job_id required !'}})
            if not job_number:
                return Response({'message': {'job_number required !'}})
            if not job_id.isdigit():
                return Response({'message': {'booking_id should be numeric !'}})

            if request.user.user_type != 'Grahak':
                return Response({'message': {'you are not Grahak, only Grahak can change status'}})

            job_bookings = JobBooking.objects.filter(Q((Q(jobsahayak__id=job_id) & Q(
                jobsahayak__job_number=job_number)) | (Q(jobmachine__id=job_id) & Q(jobmachine__job_number=job_number))))

            is_booked = False
            encrypted_data = None
            for job in job_bookings:
                if job.status == 'Booked':
                    return Response({'message': {'Job is already booked, payment is completed'}})
                if job.status != 'Accepted':
                    continue
                is_booked = True

                if job.jobsahayak:
                    if job.jobsahayak.grahak == request.user:
                        if not job.jobsahayak.status == 'Pending':
                            job.jobsahayak.status = 'Booked'
                            job.jobsahayak.save()
                    else:
                        return Response({'message': {'unauthorized grahak !'}})
                else:
                    if job.jobmachine.grahak == request.user:
                        if not job.jobmachine.status == 'Pending':
                            job.jobmachine.status = 'Booked'
                            job.jobmachine.save()
                    else:
                        return Response({'message': {'unauthorized grahak !'}})

                job.save()

                # if job.total_amount != amount:
                #     return Response({'message': {'Amount is not correct !'}})
            
                data_to_encrypt = f'order_id={job_id}&amount={amount}&merchant_id={merchant_id}&currency=INR&redirect_url=https://example.com&cancel_url=https://example.com&language=EN&merchant_param1={job_number}'
                encrypted_data = self.encrypt_data(data_to_encrypt)
                # print('-----------en',encrypted_data)
                # x=self.decrypt_data(encrypted_data)
                # print('----------de',x)

                response_data = {
                    'encrypted_data': encrypted_data,
                }
                
                if not is_booked:
                    return Response({'message': {'Booking status cannot be updated it should be Accepted before !'}})

                return Response({'message': 'params encrypted successfully!', 'status': status.HTTP_200_OK, "encrypted_data": encrypted_data})



# https://secure.ccavenue.com/transaction/transaction.do?command=initiateTransaction










def payment_show(request):
    return render(request,'payments/dataFrom.html')



from django.http import HttpResponse
from string import Template

# Set your accessCode and workingKey
accessCode = settings.ACCESS_CODE
workingKey = settings.WORKING_KEY

# @csrf_exempt
# def ccav_response_handler(request):
#     if request.method == 'POST':
#         plain_text = res(request.POST.get('encResp'))
#         print(plain_text)
#         return HttpResponse(plain_text)
    
#     return HttpResponse("Invalid request method")


def ccav_request_handler(request):
    if request.method == 'POST':
        p_merchant_id = request.POST.get('merchant_id')
        p_order_id = request.POST.get('order_id')
        p_currency = request.POST.get('currency')
        p_amount = request.POST.get('amount')
        p_redirect_url = request.build_absolute_uri('/ccavResponseHandler/')
        # p_cancel_url = request.POST.get('cancel_url')
        # p_language = request.POST.get('language')
        p_billing_name = request.POST.get('billing_name')
        p_billing_address = request.POST.get('billing_address')
        p_billing_city = request.POST.get('billing_city')
        p_billing_state = request.POST.get('billing_state')
        p_billing_zip = request.POST.get('billing_zip')
        p_billing_country = request.POST.get('billing_country')
        p_billing_tel = request.POST.get('billing_tel')
        p_billing_email = request.POST.get('billing_email')
        p_merchant_param1='S-8935372'

        merchant_data = (
            'merchant_id=' + p_merchant_id + '&' +
            'order_id=' + p_order_id + '&' +
            'currency=' + p_currency + '&' +
            'amount=' + p_amount + '&' +
            'redirect_url=' + p_redirect_url + '&' +
            'billing_name=' + p_billing_name + '&' +
            'billing_address=' + p_billing_address + '&' +
            'billing_city=' + p_billing_city + '&' +
            'billing_state=' + p_billing_state + '&' +
            'billing_zip=' + p_billing_zip + '&' +
            'billing_country=' + p_billing_country + '&' +
            'billing_tel=' + p_billing_tel + '&' +
            'billing_email=' + p_billing_email + '&' +
            'merchant_param1=' + p_merchant_param1 + '&'

        )

        encryption = encrypt(merchant_data, workingKey)

        html = '''\
        <html>
        <head>
            <title>Sub-merchant checkout page</title>
            <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js"></script>
        </head>
        <body>
            <form id="nonseamless" method="post" name="redirect" action="https://secure.ccavenue.com/transaction/transaction.do?command=initiateTransaction">
                <input type="hidden" id="encRequest" name="encRequest" value="$encReq">
                <input type="hidden" name="access_code" id="access_code" value="$xscode">
                <script language='javascript'>document.redirect.submit();</script>
            </form>
        </body>
        </html>
        '''

        fin = Template(html).safe_substitute(encReq=encryption, xscode=accessCode)
        return HttpResponse(fin)
    else:
        return HttpResponse("Invalid request")
    

from django.http import HttpResponseRedirect
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.template.loader import render_to_string


@method_decorator(csrf_exempt, name='dispatch')
class CCAVRequestHandler(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        p_merchant_id = request.data.get('merchant_id')
        p_order_id = request.data.get('order_id')
        p_currency = request.data.get('currency')
        p_amount = request.data.get('amount')
        p_redirect_url = 'http://127.0.0.1:8000/ccavResponseHandler/'

        # ... Retrieve other form data

        merchant_data = (
            'merchant_id=' + p_merchant_id + '&' +
            'order_id=' + p_order_id + '&' +
            'currency=' + p_currency + '&' +
            'amount=' + p_amount + '&' +
            'redirect_url=' + p_redirect_url + '&' 
            # ... Include other form data
        )

        encryption = encrypt(merchant_data, workingKey)

        # html = '''\
        # <html>
        # <head>
        #     <title>Sub-merchant checkout page</title>
        #     <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js"></script>
        # </head>
        # <body>
        #     <form id="nonseamless" method="post" name="redirect" action="https://secure.ccavenue.com/transaction/transaction.do?command=initiateTransaction">
        #         <input type="hidden" id="encRequest" name="encRequest" value="$encReq">
        #         <input type="hidden" name="access_code" id="access_code" value="$xscode">
        #         <script language='javascript'>document.redirect.submit();</script>
        #     </form>
        # </body>
        # </html>
        # '''

        # fin = Template(html).safe_substitute(encReq=encryption, xscode=accessCode)
        return Response(encryption)



@csrf_exempt
class CCAVResponseHandler(APIView):
    permission_classes=[AllowAny]
    def post(self, request):
        encrypted_response = request.data.get('encResp')
        plain_text = res(encrypted_response)
        return HttpResponse(plain_text)


# from django.views.decorators.csrf import csrf_exempt

# def callback_handler(encResp):
#     '''
#     Please put in the 32 bit alphanumeric key in quotes provided by CCAvenues.
#     '''	 
#     workingKey = 'BA71ECCDFE4837050730D30DB224BF6C'
#     decResp = decrypt(encResp, workingKey)
#     return decResp

# ###--------------------------------------------------------------------------####
# # @csrf_exempt
# # def ccav_response_handler(request):
# #     encrypted_response = request.POST['encResp']
# #     # decrypted_response = callback_handler(encrypted_response)
# #     # print('------------',decrypted_response)
# #     result=res()
# #     return HttpResponse()

# # from string import Template

# # def res(request):
# #     '''
# #     Please put in the 32 bit alphanumeric key in quotes provided by CCAvenues.
# #     '''
# #     workingKey = 'BA71ECCDFE4837050730D30DB224BF6C'
# #     encrypted_response = request.POST.get('encResp')
# #     decResp = decrypt(encrypted_response, workingKey)
# #     data = '<table border=1 cellspacing=2 cellpadding=2><tr><td>'    
# #     data = data + decResp.replace('=', '</td><td>')
# #     data = data.replace('&', '</td></tr><tr><td>')
# #     data = data + '</td></tr></table>'
    
# #     html = f'''
# #     <html>
# #         <head>
# #             <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
# #             <title>Response Handler</title>
# #         </head>
# #         <body>
# #             <center>
# #                 <font size="4" color="blue"><b>Response Page</b></font>
# #                 <br>
# #                 {data}
# #             </center>
# #             <br>
# #         </body>
# #     </html>
# #     '''
# #     return HttpResponse(html)




# ###------------------------------------------------------------------------------###



# from django.shortcuts import render
# from django.views.decorators.csrf import csrf_exempt
# from .ccavutil import encrypt
# from string import Template

# @csrf_exempt
# def ccavRequestHandler(request):
#     '''
#     Please put in the 32 bit alphanumeric key and Access Code in quotes provided by CCAvenues.
#     '''
#     accessCode = ''
#     workingKey = ''

#     if request.method == 'POST':
#         p_merchant_id = request.POST.get('merchant_id', '')
#         p_order_id = request.POST.get('order_id', '')
#         p_currency = request.POST.get('currency', '')
#         p_amount = request.POST.get('amount', '')
#         p_redirect_url = request.POST.get('redirect_url', '')
#         p_cancel_url = request.POST.get('cancel_url', '')
#         p_language = request.POST.get('language', '')
#         p_billing_name = request.POST.get('billing_name', '')
#         p_billing_address = request.POST.get('billing_address', '')
#         p_billing_city = request.POST.get('billing_city', '')
#         p_billing_state = request.POST.get('billing_state', '')
#         p_billing_zip = request.POST.get('billing_zip', '')
#         p_billing_country = request.POST.get('billing_country', '')
#         p_billing_tel = request.POST.get('billing_tel', '')
#         p_billing_email = request.POST.get('billing_email', '')
#         p_delivery_name = request.POST.get('delivery_name', '')
#         p_delivery_address = request.POST.get('delivery_address', '')
#         p_delivery_city = request.POST.get('delivery_city', '')
#         p_delivery_state = request.POST.get('delivery_state', '')
#         p_delivery_zip = request.POST.get('delivery_zip', '')
#         p_delivery_country = request.POST.get('delivery_country', '')
#         p_delivery_tel = request.POST.get('delivery_tel', '')
#         p_merchant_param1 = request.POST.get('merchant_param1', '')
#         p_merchant_param2 = request.POST.get('merchant_param2', '')
#         p_merchant_param3 = request.POST.get('merchant_param3', '')
#         p_merchant_param4 = request.POST.get('merchant_param4', '')
#         p_merchant_param5 = request.POST.get('merchant_param5', '')
#         p_promo_code = request.POST.get('promo_code', '')
#         p_customer_identifier = request.POST.get('customer_identifier', '')

#         merchant_data = (
#             'merchant_id=' + p_merchant_id + '&' +
#             'order_id=' + p_order_id + '&' +
#             'currency=' + p_currency + '&' +
#             'amount=' + p_amount + '&' +
#             'redirect_url=' + p_redirect_url + '&' +
#             'cancel_url=' + p_cancel_url + '&' +
#             'language=' + p_language + '&' +
#             'billing_name=' + p_billing_name + '&' +
#             'billing_address=' + p_billing_address + '&' +
#             'billing_city=' + p_billing_city + '&' +
#             'billing_state=' + p_billing_state + '&' +
#             'billing_zip=' + p_billing_zip + '&' +
#             'billing_country=' + p_billing_country + '&' +
#             'billing_tel=' + p_billing_tel + '&' +
#             'billing_email=' + p_billing_email + '&' +
#             'delivery_name=' + p_delivery_name + '&' +
#             'delivery_address=' + p_delivery_address + '&' +
#             'delivery_city=' + p_delivery_city + '&' +
#             'delivery_state=' + p_delivery_state + '&' +
#             'delivery_zip=' + p_delivery_zip + '&' +
#             'delivery_country=' + p_delivery_country + '&' +
#             'delivery_tel=' + p_delivery_tel + '&' +
#             'merchant_param1=' + p_merchant_param1 + '&' +
#             'merchant_param2=' + p_merchant_param2 + '&' +
#             'merchant_param3=' + p_merchant_param3 + '&' +
#             'merchant_param4=' + p_merchant_param4 + '&' +
#             'merchant_param5=' + p_merchant_param5 + '&' +
#             'promo_code=' + p_promo_code + '&' +
#             'customer_identifier=' + p_customer_identifier + '&'
#         )

#         encryption = encrypt(merchant_data, workingKey)

#         html = '''\
#         <html>
#         <head>
#             <title>Sub-merchant checkout page</title>
#             <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js"></script>
#         </head>
#         <body>
#         <form id="nonseamless" method="post" name="redirect" action="https://test.ccavenue.com/transaction/transaction.do?command=initiateTransaction">
#                 <input type="hidden" id="encRequest" name="encRequest" value=$encReq>
#                 <input type="hidden" name="access_code" id="access_code" value=$xscode>
#                 <script language='javascript'>document.redirect.submit();</script>
#         </form>
#         </body>
#         </html>
#         '''

#         fin = Template(html).safe_substitute(encReq=encryption, xscode=accessCode)

#         return render(request, 'payment/payment_form.html', {'payment_form': fin})



