from rest_framework.views import APIView
from rest_framework.response import Response
# import requests
from .models import Payment
from booking.models import JobBooking
from rest_framework.permissions import AllowAny,IsAuthenticated
from authentication.views import BearerTokenAuthentication
from jobs.models import *
from django.db.models import Q
from rest_framework import status

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
#                 # If payment fails, return an error message to the mobile app
#                 return Response({'status': 'error', 'message': 'Payment failed'})



class TestPaymentAPIView(APIView):
    authentication_classes=[BearerTokenAuthentication,]
    permission_classes=[IsAuthenticated,]
    def post(self, request):
        if request.user.user_type == 'Grahak':
            # booking_id = request.data.get('booking_id')
            job_id=request.data.get('job_id')
            job_number=request.data.get('job_number')
            amount = request.data.get('amount')
            upi_id = 'upi_id'  # Replace with the actual UPI ID
            beneficiary_name = 'beneficiary_name'  # Replace with the actual beneficiary name
            if not job_id:
                return Response({'error': 'job_id required !'})
            if not job_number:
                return Response({'error':'job_number required !'})    
            if not job_id.isdigit():
                return Response({'error':'booking_id should be numeric !'})
            # if not JobBooking.objects.filter(pk=job_id).exists():
            #     return Response({'error':'booking_id not exists !'})
            # Simulate a successful payment by returning a JSON response with a payment ID and status
            if request.user.user_type != 'Grahak':
                return Response({'message': 'you are not Grahak, only Grahak can change status'})
            
            try:
                get_job_sahayak=JobSahayak.objects.get(pk=job_id)
                get_job_machine=JobMachine.objects.get(pk=job_id)
            except JobSahayak.DoesNotExist:
                return Response({'error':f"job does not exist with job_id-{job_id}"})
            except JobMachine.DoesNotExist:
                return Response({'error':f"job does not exist with job_id-{job_id}"}) 
            job_bookings = JobBooking.objects.filter(Q((Q(jobsahayak=get_job_sahayak) & Q(jobsahayak__job_number=job_number)) | (Q(jobmachine=get_job_machine) & Q(jobmachine__job_number=job_number))))
            is_booked = False
            for job in job_bookings:
                if job.status == 'Booked':
                    return Response({'message': 'Status already up to date !'})
                if job.status != 'Accepted':
                    continue
                is_booked = True

                if job.jobsahayak:
                    if job.jobsahayak.grahak == request.user:
                        if not job.jobsahayak.status == 'Pending':
                            job.jobsahayak.status = 'Booked'
                            job.jobsahayak.save()
                    else:
                        return Response({'error': 'unauthorized grahak !'})
                else:
                    if job.jobmachine.grahak == request.user:
                        if not job.jobmachine.status == 'Pending':
                            job.jobmachine.status = 'Booked'
                            job.jobmachine.save()
                    else:
                        return Response({'error': 'unauthorized grahak !'})

                job.status = 'Booked'
                job.save()
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
                return Response({'error': 'Booking status cannot be updated it should be Accepted before !'})

            return Response({'message': 'changed status to Booked successfully!','booking_status':'Booked','status':status.HTTP_200_OK})
            