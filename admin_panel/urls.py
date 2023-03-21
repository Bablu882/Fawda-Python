from django.urls import path
from .views import *
from . import views
urlpatterns=[
    path('job_booking_list/', views.job_booking_list, name='job_booking_list'),
    path('job_details/',JobDetailsAdmin.as_view()),

]