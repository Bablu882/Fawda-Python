from django.urls import path
from .views import *
from . import views
from django.contrib import admin
from django.conf import settings

# from .admin import custom_admin_site

urlpatterns=[
    path('job_details/',JobDetailsAdmin.as_view()),
    path('job_details_admin/',JobDetailsAdminPanel.as_view()),
    path('payment_status/',AdminPaymentStatus.as_view()),
]   
