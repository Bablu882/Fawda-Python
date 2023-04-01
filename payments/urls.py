from django.urls import path,include
from .views import *
from payments import views

urlpatterns=[
    path('api/payment/',PaymentAPIView.as_view()),
    path('api/payment_test/',TestPaymentAPIView.as_view())
    
]