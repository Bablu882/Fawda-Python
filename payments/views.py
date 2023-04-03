from rest_framework.views import APIView
from rest_framework.response import Response
# import requests
from .models import Payment
from booking.models import JobBooking

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
    def post(self, request):
        if request.user.user_type == 'Grahak':
            booking_id = request.data.get('booking_id')
            amount = request.data.get('amount')
            upi_id = 'upi_id'  # Replace with the actual UPI ID
            beneficiary_name = 'beneficiary_name'  # Replace with the actual beneficiary name
            if not booking_id.isdigit():
                return Response({'error':'booking_id should be numeric !'})
            if not JobBooking.objects.filter(pk=booking_id).exists():
                return Response({'error':'booking_id not exists !'})
            # Simulate a successful payment by returning a JSON response with a payment ID and status
            response_data = {
                'booking_id': booking_id,
                'amount': str(amount),
                'upi_id': upi_id,
                'beneficiary_name': beneficiary_name,
                'payment_id': 'mock_payment_id',  # Replace with a mock payment ID
                'payment_status': 'success',  # Set the payment status to 'success'
            }

            # Save payment details to Payment table
            payment = Payment.objects.create(
                booking_id=booking_id,
                amount=str(amount),
                payment_id=response_data['payment_id'],
                payment_status=response_data['payment_status'],
                beneficiary_name=beneficiary_name
            )
            job=JobBooking.objects.get(pk=booking_id)
            job.status= 'Booked'
            job.save()
            if job.jobsahayak:
                if job.jobsahayak.job_type == 'individuals_sahayak':
                    if job.jobsahayak.count_male == '0' and job.jobsahayak.count_female == '0':
                        job.jobsahayak.status = 'Booked'
                        job.jobsahayak.save()
                else:
                    job.jobsahayak.status = 'Booked'
                    job.jobsahayak.save()        
            else:
                job.jobmachine.status='Booked'        
                job.jobmachine.save()

            return Response(response_data)