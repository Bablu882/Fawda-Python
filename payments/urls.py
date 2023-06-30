from django.urls import path,include
from .views import *
from . import views
from payments.views import payment_show
# from payments import views

urlpatterns=[
    # path('api/payment/',PaymentAPIView.as_view()),
    path('api/payment_test/',TestPaymentAPIView.as_view()),
    path('api/payment/',PaymentAPIView.as_view()),
    path('api/encrypt_data/',EncryptPaymentParamsView.as_view()),
    # path('ccavRequestHandler/', views.ccav_request_handler, name='ccav_request_handler'),
    path('ccavResponseHandler/', views.ccav_response_handler, name='ccav_response_handler'),
    path('webprint/',payment_show, name='web_print'),
    path('callback/',res,name='callback'),
    path('ccavRequestHandler/',PaymentRequestHandler.as_view(),name='ccav_request_handler'),
    # path('ccavResponseHandler/', views.CCAVResponseHandler, name='ccav_response_handler')

    
]